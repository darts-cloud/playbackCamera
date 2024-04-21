import logging
logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.INFO)
from enum import *
import fpstimer
from playbackCamera.VideoCapture import *
import queue
import datetime
from playbackCamera.Settings import *
import numpy as np

class Mode(IntEnum):
	ALL = 99
	DISP_1 = 0
	DISP_2 = 1
	DISP_3 = 2
	DISP_4 = 3

class WindowSize(Enum):
	FULL = 0
	WINDOW = 1

'''

'''
class BasePlayer():
	DEBUG = True
	
	def __init__(self):
		logging.debug("__init__ start")
		self.conf = Settings()
		self.stopped = False
		self.Mode = Mode.ALL
		self.WindowSize = WindowSize.WINDOW
		self.fpsCount = CountFps()
		self.imshowed = False
		
		self._initVideoSoruce()
		if self.conf.saveMovie:
			self._createWriter()
		logging.debug("__init__ end")
	
	def start(self):
		self.fpsTimer = fpstimer.FPSTimer(self.conf.fps)

		while(True):
			key = cv2.waitKey(1) & 0xFF
			if key == ord(' '):
				break
			elif key == ord('0'):
				self.Mode = Mode.ALL
			elif key == ord('1'):
				self.Mode = Mode.DISP_1
			elif key == ord('2'):
				self.Mode = Mode.DISP_2
			elif key == ord('3'):
				self.Mode = Mode.DISP_3
			elif key == ord('4'):
				self.Mode = Mode.DISP_4
			elif key == ord('F') or key == ord('f'):
				self.imshowed = False
				if self.WindowSize == WindowSize.FULL:
					self.WindowSize = WindowSize.WINDOW
				else:
					self.WindowSize = WindowSize.FULL
			
			self.fpsTimer.sleep()

			# Fps計算用にフレーム計算
			self.fpsCount.CountFrame()
			
			# 動画をキューに登録
			self._addQueue()
			
			# キューに入れた（遅延した）動画を使用
			self._useQueue()

		self._endProcess()

	def _initVideoSoruce(self):
		self.captures = []
		self.queues = []
		frames = int(self.conf.fps * (self.conf.delayTime + self.conf.adjutTime))
		for i, s in enumerate( self.conf.srcs.split(',') ):
			src = s.strip()
			if src != "":
				capture = ThreadingVideoCaptureForPyAv(src, 1000)
				if capture.isOpened():
					self.captures.append( capture )
					self.queues.append( queue.Queue(maxsize=frames) )

	def _createWriter(self):
		codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') # ファイル形式(ここではmp4)
		now = datetime.datetime.now()
		ymd = now.strftime("%Y%m%d%H%M%S")
		fileName = './result/{}_{}.mp4'
		
		self.writers = []
		for i, capture in enumerate( self.captures ):
			writer = cv2.VideoWriter(fileName.format(ymd, str(i)), codec, self.conf.fps, (self.conf.VIDEO_WIDTH, self.conf.VIDEO_HEIGHT))
			self.writers.append(writer)

		if len(self.captures) >= 2:
			writer = cv2.VideoWriter(fileName.format(ymd, "all"), codec, self.conf.fps, (self.conf.sizeW, self.conf.sizeH))
			self.writers.append(writer)

	def _show(self, frames, allimg):
		logging.debug("_show start")
		img = None
		# fps1 = 0
		fps2 = 0
		# 押したキーにより、表示を切り替え
		try:
			if (self.Mode == Mode.ALL):
				pass
			else:
				img = frames[int(self.Mode)]
		except IndexError as ie:
			pass

		if img is None:
			img = allimg
		
		# img = self._resize(img, dsize=(self.conf.dispSizeW, self.conf.dispSizeH))

		if self.conf.glidLineFlg:
			alpha = 0.2
			# img = cv2.addWeighted(self.mask, alpha, img, 1 - alpha, 0)
			img = self._drawGlidLine(img)

		fps2 = self.fpsCount.CountFps()

		height, width, channels = img.shape[:3]
		white = (255, 255, 255)
		# cv2.putText(img, "{:.2f} fps".format(fps1), (  0, height - 35), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
		cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  60), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
		black = (0, 0, 0)
		# cv2.putText(img, "{:.2f} fps".format(fps1), (  0, height - 35), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)
		cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  60), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)

		self.img = img
		# 高解像度で表示すると描画が遅いことが判明
		self._imshow('frame', img)
		logging.debug("_show end")

	def _drawGlidLine(self, img):
		logging.debug("_drawGlidLine start")
		alpha = 0.3
		y_step = 40 #高さ方向のグリッド間隔(単位はピクセル)
		x_step = 40 #幅方向のグリッド間隔(単位はピクセル)
		step = 40

		tmp = img.copy()

		#オブジェクトimgのshapeメソッドの1つ目の戻り値(画像の高さ)をimg_yに、2つ目の戻り値(画像の幅)をimg_xに
		img_y , img_x = tmp.shape[:2]  

		# for i in range(int(self.sizeW / step)):
		# 	x = i * step
		# 	tmp = cv2.line(tmp, (x, 0),(x, self.sizeH), (200, 200, 200), 1)

		# for i in range(int(self.sizeH / step)):
		# 	y = i * step
		# 	tmp = cv2.line(tmp, (0, y),(self.sizeW, y), (200, 200, 200), 1)

		#横線を引く：y_stepからimg_yの手前までy_stepおきに白い(BGRすべて255)横線を引く
		tmp[y_step:img_y:y_step, :, :] = 128
		#縦線を引く：x_stepからimg_xの手前までx_stepおきに白い(BGRすべて255)縦線を引く
		tmp[:, x_step:img_x:x_step, :] = 128

		# img = cv2.addWeighted(tmp, alpha, img, 1 - alpha, 0, img)

		logging.debug("_drawGlidLine end")
		return tmp

	def _addQueue(self):
		logging.debug("_addQueue start")
		for i, capture in enumerate( self.captures ):
			if not self.queues[i].full():
				try:
					# 常に最新のフレームを読み込む
					self.queues[i].put_nowait(capture.read())
				except queue.Full:
					pass
		logging.debug("_addQueue end")

	def _useQueue(self):
		logging.debug("_useQueue start")

		if len(self.queues) <= 0:
			# 読み込み中
			im_h = np.zeros((self.conf.sizeH, self.conf.sizeW, 3)).astype('uint8')
			str = "There are no streams that can be displayed."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			
			self._imshow('frame', im_h)
			logging.debug("_useQueue end")
			return

		if self.queues[0].qsize() < int(self.conf.fps * self.conf.delayTime):
			# 読み込み中
			im_h = np.zeros((self.conf.sizeH, self.conf.sizeW, 3)).astype('uint8')
			str = "Now loading please wait..."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			self._imshow('frame', im_h)
			logging.debug("_useQueue end")
			return
		
		# Queueより動画を取得
		frames = []
		white = (255, 255, 255)
		black = (0, 0, 0)
		for i, queue in enumerate( self.queues ):
			try:
				q = queue.get_nowait()
				frame = q[1]
				# fps = q[2]
				# debug
				# qs = queue.qsize()
				# text = "{} frames in array, {}fps".format(qs, fps)
				# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
				# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)
				frame = self._decorationImage(frame)

				frames.append(frame)
			except queue.Empty:
				pass
			
		# 動画を表示
		allimg = self._concatImage(frames, self.conf.sizeW, self.conf.sizeH)
		self._show(frames, allimg)

		if len(self.captures) >= 2:
			frames.append(allimg)

		if self.conf.saveMovie:
			self._save(frames)
		logging.debug("_useQueue end")

	def _imshow(self, windowName, img):
		logging.debug("imshow start")
		if self.imshowed == False:
			if self.WindowSize == WindowSize.FULL:
				cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
				cv2.setWindowProperty(windowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
			else:
				cv2.namedWindow(windowName, cv2.WND_PROP_FULLSCREEN)
				cv2.setWindowProperty(windowName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_NORMAL)
		self.imshowed = True
		cv2.imshow(windowName, img)
		logging.debug("imshow end")

	def _endProcess(self):
		for i, capture in enumerate( self.captures ):
			capture.release()
		if self.conf.saveMovie:
			for i, writer in enumerate( self.writers ):
				writer.release()
		
		cv2.destroyAllWindows()
	
	def _resize(self, img, dsize):
		logging.debug("_resize start")
		# aspect_ratio = float(img.shape[1])/float(img.shape[0])
		# window_width = dsize[1]/aspect_ratio
		# img = cv2.resize(img, (int(dsize[1]),int(window_width)))	
		img = cv2.resize(img, dsize, interpolation=cv2.INTER_LINEAR)
		logging.debug("_resize end")
		return img

	def _resizeDefSize(self, img):
		logging.debug("_resizeDefSize start")
		height, width, channels = img.shape[:3]
		if width != self.conf.VIDEO_WIDTH or height != self.conf.VIDEO_HEIGHT:
			img = self._resize(img, dsize=(self.conf.VIDEO_WIDTH, self.conf.VIDEO_HEIGHT))
		logging.debug("_resizeDefSize end")
		return img

	def _debug(self, mes):
		if self.DEBUG:
			logging.debug(mes)
			print(mes)

	def _decorationImage(self, image):
		return image

	def _concatImage(self, frames, sizeW, sizeH):
		logging.debug("_concatImage start")
		if len(frames) <= 1:
			img = frames[0]
			# img = self._resize(img, dsize=(sizeW, sizeH))
			logging.debug("_concatImage end")
			return img
		
		img1 = self._resizeDefSize(frames[0])
		img2 = self._resizeDefSize(frames[1])

		img_tmp = np.zeros((self.conf.VIDEO_HEIGHT, self.conf.VIDEO_WIDTH, 3)).astype(b'uint8')
		im_h1 = self.__hconcat([img1, img2])
		if len(frames) > 2:
			img3 = self._resizeDefSize(frames[2])
			if len(frames) == 3:
				im_h2 = self.__hconcat([img3, img_tmp])
			else:
				img4 = self._resizeDefSize(frames[3])
				im_h2 = self.__hconcat([img3, img4])
			img = self.__vconcat([im_h1, im_h2])
		else:
			im_h2 = self.__hconcat([img_tmp, img_tmp])
			img = self.__vconcat([im_h1, im_h2])
			# img = im_h1
		logging.debug("_concatImage end")
		return img

	def __hconcat(self, imgs):
		logging.debug("__hconcat start")
		img = cv2.hconcat(imgs)
		# img = np.hstack(imgs)
		logging.debug("__hconcat end")
		return img

	def __vconcat(self, imgs):
		logging.debug("__vconcat start")
		img = cv2.vconcat(imgs)
		# img = np.vstack(imgs)
		logging.debug("__vconcat end")
		return img
	
	def _save(self, frames):
		logging.debug("_save start")
		for i, writer in enumerate( self.writers ):
			writer.write(frames[i][1]) # 画像を1フレーム分として書き込み
		logging.debug("_save end")