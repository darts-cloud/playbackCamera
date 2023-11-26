import logging
logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.INFO)
from screeninfo import get_monitors
from enum import IntEnum
import fpstimer
from VideoCapture import *
import configparser
import queue
import sys
import datetime

class Mode(IntEnum):
	ALL = 99
	DISP_1 = 0
	DISP_2 = 1
	DISP_3 = 2
	DISP_4 = 3

'''

'''
class BasePlayer():
	DEBUG = True
	VIDEO_WIDTH = 640
	VIDEO_HEIGHT = 480
	INI_SECTION = "DEFAULT"
	INI_CAMERA = "camera"
	INI_DELAY_TIME = "delay_time"
	INI_ADJUSTMENT_TIME = "adjustment_time"
	INI_FPS = "fps"
	INI_SYNCED_DIFF_TIME = "synced_diff_time"
	INI_SYNCED_MAX_COUNT = "synced_max_count"
	INI_SIZE_W = "size_w"
	INI_SIZE_H = "size_h"
	INI_GRID_LINE = "grid_line"
	INI_SAVE_MOVIE = "save_movie"
	
	def __init__(self):
		logging.debug("__init__ start")
		self._loadIniFile()
		self.stopped = False
		self.dispSizeH = None
		self.dispSizeW = None
		
		for m in get_monitors():
			self.dispSizeH = m.height
			self.dispSizeW = m.width
			print(str(m))
			break
		
		if self.dispSizeH is None:
			self.dispSizeH = self.sizeH
			self.dispSizeW = self.sizeW

		self._initVideoSoruce()
		self.Mode = Mode.ALL
		self.fpsCount = CountFps()
		if self.saveMovie:
			self._createWriter()
		logging.debug("__init__ end")
	
	def start(self):
		self.fpsTimer = fpstimer.FPSTimer(self.fps)
		if self.GlidLineFlg:
			mask = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			self.mask = self._drawGlidLine(mask)

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
			
			self.fpsTimer.sleep()

			# Fps計算用にフレーム計算
			self.fpsCount.CountFrame()
			
			# 動画をキューに登録
			self._addQueue()
			
			# キューに入れた（遅延した）動画を使用
			self._useQueue()

		self._endProcess()

	def _loadIniFile(self):
		config = configparser.ConfigParser()
		config.read("settings.ini")
		self.delayTime = float(config.get(self.INI_SECTION, self.INI_DELAY_TIME))
		self.adjutTime = float(config.get(self.INI_SECTION, self.INI_ADJUSTMENT_TIME))
		self.fps = int(config.get(self.INI_SECTION, self.INI_FPS))
		self.syncedDiffTime = float(config.get(self.INI_SECTION, self.INI_SYNCED_DIFF_TIME))
		self.syncedMaxCount = int(config.get(self.INI_SECTION, self.INI_SYNCED_MAX_COUNT))
		self.srcs = config.get(self.INI_SECTION, self.INI_CAMERA)
		self.sizeW = int(config.get(self.INI_SECTION, self.INI_SIZE_W))
		self.sizeH = int(config.get(self.INI_SECTION, self.INI_SIZE_H))
		if int(config.get(self.INI_SECTION, self.INI_GRID_LINE)) == 1:
			self.GlidLineFlg = True
		self.saveMovie = False
		if int(config.get(self.INI_SECTION, self.INI_SAVE_MOVIE)) == 1:
			self.saveMovie = True

	def _initVideoSoruce(self):
		self.captures = []
		self.queues = []
		frames = int(self.fps * (self.delayTime + self.adjutTime))
		for i, s in enumerate( self.srcs.split(',') ):
			src = s.strip()
			if src != "":
				capture = ThreadingVideoCapture3(src, 1000)
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
			writer = cv2.VideoWriter(fileName.format(ymd, str(i)), codec, self.fps, (self.VIDEO_WIDTH, self.VIDEO_HEIGHT))
			self.writers.append(writer)

		if len(self.captures) >= 2:
			writer = cv2.VideoWriter(fileName.format(ymd, "all"), codec, self.fps, (self.sizeW, self.sizeH))
			self.writers.append(writer)

	def _show(self, frames, allimg):
		logging.debug("show start")
		img = None
		# fps1 = 0
		fps2 = 0
		# 押したキーにより、表示を切り替え
		try:
			if (self.Mode == Mode.ALL):
				pass
			else:
				img = self.__resize(frames[int(self.Mode)], dsize=(self.sizeW, self.sizeH))
		except IndexError as ie:
			pass

		if img is None:
			img = allimg
		
		if self.GlidLineFlg:
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

		img = self.__resize(img, dsize=(self.dispSizeW, self.dispSizeH))
		self.img = img
		# 高解像度で表示すると描画が遅いことが判明
		self._showMessage('frame', img)
		logging.debug("show end")

	def _drawGlidLine(self, img):
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

		return tmp

	def _addQueue(self):
		for i, capture in enumerate( self.captures ):
			if not self.queues[i].full():
				try:
					# 常に最新のフレームを読み込む
					self.queues[i].put_nowait(capture.read())
				except queue.Full:
					pass

	def _useQueue(self):

		if len(self.queues) <= 0:
			# 読み込み中
			im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			str = "There are no streams that can be displayed."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			
			self._showMessage('frame', im_h)
			return

		if self.queues[0].qsize() < int(self.fps * self.delayTime):
			# 読み込み中
			im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			str = "Now loading please wait..."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			self._showMessage('frame', im_h)
			return
		
		# Queueより動画を取得
		frames = []
		white = (255, 255, 255)
		black = (0, 0, 0)
		for i, queue in enumerate( self.queues ):
			try:
				frame = queue.get_nowait()[1]
				# debug
				# qs = queue.qsize()
				# text = "{} frames in array".format(qs)
				# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
				# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)

				frames.append(frame)
			except queue.Empty:
				pass
			
		# 動画を表示
		allimg = self.__concatImage(frames)
		self._show(frames, allimg)

		if len(self.captures) >= 2:
			frames.append(allimg)

		if self.saveMovie:
			self.__save(frames)

	def _showMessage(self, windowName, img):
		logging.debug("imshow start")
		cv2.namedWindow(windowName, cv2.WINDOW_FULLSCREEN)
		cv2.imshow(windowName, img)
		logging.debug("imshow end")


	def _endProcess(self):
		for i, capture in enumerate( self.captures ):
			capture.release()
		if self.saveMovie:
			for i, writer in enumerate( self.writers ):
				writer.release()
		
		cv2.destroyAllWindows()

	def _debug(self, mes):
		if self.DEBUG:
			logging.debug(mes)
			print(mes)

	def __concatImage(self, frames):
		logging.debug("__concatImage start")
		if len(frames) <= 1:
			return self.__resize(frames[0], dsize=(self.sizeW, self.sizeH))
		
		sizeH = (int(self.sizeH / 2))
		sizeW = (int(self.sizeW / 2))
		img1 = self.__resize(frames[0], dsize=(sizeW, sizeH))
		img2 = self.__resize(frames[1], dsize=(sizeW, sizeH))
		h, w, channels = img1.shape[:3]
		img_tmp = np.zeros((h, w, 3)).astype(b'uint8')
		im_h1 = self.__hconcat([img1, img2])
		if len(frames) > 2:
			img3 = self.__resize(frames[2], dsize=(sizeW, sizeH))
			if len(frames) == 3:
				im_h2 = self.__hconcat([img3, img_tmp])
			else:
				img4 = self.__resize(frames[3], dsize=(sizeW, sizeH))
				im_h2 = self.__hconcat([img3, img4])
			img = self.__vconcat([im_h1, im_h2])
		else:
			im_h2 = self.__hconcat([img_tmp, img_tmp])
			img = self.__vconcat([im_h1, im_h2])
			# img = im_h1
		logging.debug("__concatImage end")
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
	
	def __resize(self, img, dsize):
		logging.debug("__resize start")
		# aspect_ratio = float(img.shape[1])/float(img.shape[0])
		# window_width = dsize[1]/aspect_ratio
		# img = cv2.resize(img, (int(dsize[1]),int(window_width)))	
		img = cv2.resize(img, dsize, interpolation=cv2.INTER_LINEAR)
		logging.debug("__resize end")
		return img
	
	def __save(self, frames):
		for i, writer in enumerate( self.writers ):
			writer.write(frames[i][1]) # 画像を1フレーム分として書き込み