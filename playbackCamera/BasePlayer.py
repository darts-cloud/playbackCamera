import logging
logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.INFO)
from screeninfo import get_monitors
from enum import Enum
import fpstimer
from VideoCapture import *
import configparser
import queue
import sys
import datetime

class Mode(Enum):
	ALL = 0
	DISP_1 = 1
	DISP_2 = 2
	DISP_3 = 3
	DISP_4 = 4

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
	def __init__(self):
		logging.debug("__init__ start")
		self.loadIniFile()
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

		self.initVideoSoruce()
		self.Mode = Mode.ALL
		self.fpsCount = CountFps()
		self.createWriter()
		logging.debug("__init__ end")
	
	def loadIniFile(self):
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
		self.GlidLineFlg = bool(config.get(self.INI_SECTION, self.INI_GRID_LINE))

	def initVideoSoruce(self):
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

	def createWriter(self):
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

	def concatImage(self, frames):
		logging.debug("concatImage start")
		if len(frames) <= 1:
			return self.resize(frames[0], dsize=(self.sizeW, self.sizeH))
		
		sizeH = (int(self.sizeH / 2))
		sizeW = (int(self.sizeW / 2))
		img1 = self.resize(frames[0], dsize=(sizeW, sizeH))
		img2 = self.resize(frames[1], dsize=(sizeW, sizeH))
		h, w, channels = img1.shape[:3]
		img_tmp = np.zeros((h, w, 3)).astype(b'uint8')
		im_h1 = self.hconcat([img1, img2])
		if len(frames) > 2:
			img3 = self.resize(frames[2], dsize=(sizeW, sizeH))
			if len(frames) == 3:
				im_h2 = self.hconcat([img3, img_tmp])
			else:
				img4 = self.resize(frames[3], dsize=(sizeW, sizeH))
				im_h2 = self.hconcat([img3, img4])
			img = self.vconcat([im_h1, im_h2])
		else:
			im_h2 = self.hconcat([img_tmp, img_tmp])
			img = self.vconcat([im_h1, im_h2])
			# img = im_h1
		logging.debug("concatImage end")
		return img

	def show(self, frames, allimg):	
		logging.debug("show start")
		img = None
		# fps1 = 0
		fps2 = 0
		# 押したキーにより、表示を切り替え
		try:
			if (self.Mode == Mode.DISP_1):
				img = frames[0]
				# fps1 = frames[0][2]
			elif (self.Mode == Mode.DISP_2):
				img = frames[1]
				# fps1 = frames[1][2]
			elif (self.Mode == Mode.DISP_3):
				img = frames[2]
				# fps1 = frames[2][2]
			elif (self.Mode == Mode.DISP_4):
				img = frames[3]
				# fps1 = frames[3][2]
		except IndexError as ie:
			pass

		if img is None:
			img = allimg
		
		fps2 = self.fpsCount.CountFps()
		
		height, width, channels = img.shape[:3]
		white = (255, 255, 255)
		# cv2.putText(img, "{:.2f} fps".format(fps1), (  0, height - 35), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
		cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  60), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
		black = (0, 0, 0)
		# cv2.putText(img, "{:.2f} fps".format(fps1), (  0, height - 35), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)
		cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  60), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)

		img = self.resize(img, dsize=(self.dispSizeW, self.dispSizeH))
		self.img = img
		# 高解像度で表示すると描画が遅いことが判明
		self.imshow('frame', img)
		logging.debug("show end")

	def resize(self, img, dsize):
		logging.debug("resize start")
		# aspect_ratio = float(img.shape[1])/float(img.shape[0])
		# window_width = dsize[1]/aspect_ratio
		# img = cv2.resize(img, (int(dsize[1]),int(window_width)))	
		img = cv2.resize(img, dsize, interpolation=cv2.INTER_LINEAR)
		logging.debug("resize end")
		return img

	def drawGlidLine(self, img):
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

	def hconcat(self, imgs):
		logging.debug("hconcat start")
		img = cv2.hconcat(imgs)
		# img = np.hstack(imgs)
		logging.debug("hconcat end")
		return img

	def vconcat(self, imgs):
		logging.debug("vconcat start")
		img = cv2.vconcat(imgs)
		# img = np.vstack(imgs)
		logging.debug("vconcat end")
		return img

	def addQueue(self):
		for i, capture in enumerate( self.captures ):
			if not self.queues[i].full():
				try:
					# 常に最新のフレームを読み込む
					self.queues[i].put_nowait(capture.read())
				except queue.Full:
					pass

	def useQueue(self):

		if len(self.queues) <= 0:
			# 読み込み中
			im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			str = "There are no streams that can be displayed."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			
			self.imshow('frame', im_h)
			return

		if self.queues[0].qsize() < int(self.fps * self.delayTime):
			# 読み込み中
			im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			str = "Now loading please wait..."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			self.imshow('frame', im_h)
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
		allimg = self.concatImage(frames)
		if self.GlidLineFlg:
			alpha = 0.2
			allimg = cv2.addWeighted(self.mask, alpha, allimg, 1 - alpha, 0)
			allimg = self.drawGlidLine(allimg)

		self.show(frames, allimg)

		if len(self.captures) >= 2:
			frames.append(allimg)

		self.save(frames)