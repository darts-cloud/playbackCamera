import cv2
import numpy as np
import time
import datetime
from VideoCapture import *
import json
import configparser
import queue
import sys
from playbackCamera.CountFps import *
from screeninfo import get_monitors
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import fpstimer

from enum import Enum
class Mode(Enum):
	ALL = 0
	DISP_1 = 1
	DISP_2 = 2
	DISP_3 = 3
	DISP_4 = 4

class Player:
	DEBUG = True
	CONST_FPS = 30
	INI_SECTION = "DEFAULT"
	INI_CAMERA = "camera"
	INI_DELAY_TIME = "delay_time"
	INI_ADJUSTMENT_TIME = "adjustment_time"
	INI_FPS = "fps"
	INI_SYNCED_DIFF_TIME = "synced_diff_time"
	INI_SYNCED_MAX_COUNT = "synced_max_count"
	INI_SIZE_W = "size_w"
	INI_SIZE_H = "size_h"
	def __init__(self):
		logging.debug("__init__ start")
		self.loadIniFile()

		for m in get_monitors():
			self.sizeH = m.height - 100
			self.sizeW = m.width
			print(str(m))
			break
		
		self.initVideoSoruce()
		self.Mode = Mode.ALL
		self.fpsCount = CountFps()
		self._createWriter()
		# self.tw = TimeWeigh()
		logging.debug("__init__ end")
	
	def initVideoSoruce(self):
		self.captures = []
		self.queues = []
		frames = int(self.CONST_FPS * (self.delayTime + self.adjutTime))
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
			writer = cv2.VideoWriter(fileName.format(ymd, str(i)), codec, self.CONST_FPS, (self.sizeW, self.sizeH))
			self.writers.append(writer)

		writer = cv2.VideoWriter(fileName.format(ymd, "all"), codec, self.CONST_FPS, (self.sizeW, self.sizeH))
		self.writers.append(writer)

	def loadIniFile(self):
		config = configparser.ConfigParser()
		config.read("settings.ini")
		self.delayTime = float(config.get(self.INI_SECTION, self.INI_DELAY_TIME))
		self.adjutTime = float(config.get(self.INI_SECTION, self.INI_ADJUSTMENT_TIME))
		self.syncedDiffTime = float(config.get(self.INI_SECTION, self.INI_SYNCED_DIFF_TIME))
		self.syncedMaxCount = int(config.get(self.INI_SECTION, self.INI_SYNCED_MAX_COUNT))
		self.srcs = config.get(self.INI_SECTION, self.INI_CAMERA)
		self.sizeW = int(config.get(self.INI_SECTION, self.INI_SIZE_W))
		self.sizeH = int(config.get(self.INI_SECTION, self.INI_SIZE_H))

	def start(self):

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
			
			self.fpsCount.CountFrame()
			
			# 動画をキューに登録
			self.addQueue()
			
			# キューに入れた（遅延した）動画を使用
			self.useQueue()

		for i, capture in enumerate( self.captures ):
			capture.release()

		self.endProcess()

	def addQueue(self):
		for i, capture in enumerate( self.captures ):
			if not self.queues[i].full():
				self.queues[i].put(capture.read())

	def useQueue(self):

		if self.queues[0].qsize() < int(self.CONST_FPS * self.delayTime):
			# 読み込み中
			im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			self.imshow('frame', im_h)
			return
		
		# Queueより動画を取得
		frames = []
		for i, queue in enumerate( self.queues ):
			frames.append(queue.get())
		
		# 動画を表示
		allimg = self.concatImage(frames)
		self.show(frames, allimg)
		frames.append(allimg)

		self.save(frames)

	def concatImage(self, frames):
		logging.debug("concatImage start")
		if len(frames) <= 1:
			return frames[0][1]
		
		# self.tw.weigh("1")
		sizeH = (int(self.sizeH / 2))
		sizeW = (int(self.sizeW / 2))
		img_tmp = np.zeros((sizeH, sizeW, 3)).astype('uint8')
		img1 = self.resize(frames[0][1], dsize=(sizeW, sizeH))
		img2 = self.resize(frames[1][1], dsize=(sizeW, sizeH))
		im_h1 = self.hconcat([img1, img2])
		# self.tw.weigh("2")
		if len(frames) > 2:
			img3 = self.resize(frames[2][1], dsize=(sizeW, sizeH))
			if len(frames) == 3:
				im_h2 = self.hconcat([img3, img_tmp])
				# self.tw.weigh("3")
			else:
				img4 = self.resize(frames[3][1], dsize=(sizeW, sizeH))
				im_h2 = self.hconcat([img3, img4])
				# self.tw.weigh("3")
			img = self.vconcat([im_h1, im_h2])
			# self.tw.weigh("4")
		else:
			im_h2 = self.hconcat([img_tmp, img_tmp])
			img = self.vconcat([im_h1, im_h2])
			# img = im_h1
			# self.tw.weigh("3")
		logging.debug("concatImage end")
		return img

	def resize(self, imgs, dsize):
		logging.debug("resize start")
		img = cv2.resize(imgs, dsize, interpolation=cv2.INTER_LINEAR)
		logging.debug("resize end")
		return img

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

	def imshow(self, windowName, img):
		logging.debug("imshow start")
		cv2.namedWindow(windowName, cv2.WINDOW_FULLSCREEN)
		cv2.imshow(windowName, img)
		logging.debug("imshow end")

	def show(self, frames, allimg):	
		logging.debug("show start")
		img = None
		fps1 = 0
		fps2 = 0
		# 押したキーにより、表示を切り替え
		try:
			if (self.Mode == Mode.DISP_1):
				img = frames[0][1]
				fps1 = frames[0][2]
			elif (self.Mode == Mode.DISP_2):
				img = frames[1][1]
				fps1 = frames[1][2]
			elif (self.Mode == Mode.DISP_3):
				img = frames[2][1]
				fps1 = frames[2][2]
			elif (self.Mode == Mode.DISP_4):
				img = frames[3][1]
				fps1 = frames[3][2]
		except IndexError as ie:
			pass

		if img is None:
			img = allimg
		
		fps2 = self.fpsCount.CountFps()
		
		height, width, channels = img.shape[:3]
		white = (255, 255, 255)
		cv2.putText(img, "{:.2f} fps".format(fps1), (  0, height - 35), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
		cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  5), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
		black = (0, 0, 0)
		cv2.putText(img, "{:.2f} fps".format(fps1), (  0, height - 35), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)
		cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  5), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)

		self.img = img
		# 高解像度で表示すると描画が遅いことが判明
		self.imshow('frame', img)
		logging.debug("show end")
		
	def save(self, frames):
		for i, writer in enumerate( self.writers ):
			writer.write(frames[i][1]) # 画像を1フレーム分として書き込み

	def endProcess(self):
		for i, capture in enumerate( self.captures ):
			capture.release()

		for i, writer in enumerate( self.writers ):
			writer.release()
		
		cv2.destroyAllWindows()

	def debug(self, mes):
		if self.DEBUG:
			print(mes)

class Camera2(Player):

	def __init__(self):
		super().__init__()
	"""
	# 	def hconcat(self, imgs):
	# 		return cv2.hconcat(imgs)

	# 	def vconcat(self, imgs):
	# 		return cv2.vconcat(imgs)

	# 	def show(self, frames, allimg):	
	# 		img = None

	# 		fps = self.fpsCount.CountFps()
	# 		# for i, img in enumerate( frames ):
	# 		# 	height, width, channels = img[1].shape[:3]
	# 		# 	color = (0, 0 ,0)
	# 		# 	cv2.putText(img[1], "{:.2f} fps".format(fps), (  0, height - 5), cv2.FONT_HERSHEY_TRIPLEX, 1, color, 1, cv2.LINE_AA)
	# 		# 	cv2.imshow( 'screen' + str(i), img[1] )
	# 		height, width, channels = frames[0][1].shape[:3]
	# 		color = (0, 0 ,0)
	# 		cv2.putText(frames[0][1], "{:.2f} fps".format(fps), (  0, height - 5), cv2.FONT_HERSHEY_TRIPLEX, 1, color, 1, cv2.LINE_AA)
	# 		cv2.imshow( 'screen', frames[0][1] )
	"""
	def asdf():
		pass

class SyncCamera():
	def __init__(self):
		super().__init__()
		self.syncCount = 3
	"""
		def show(self):
			
			if self.queues[0].qsize() < int(self.CONST_FPS * self.delayTime):
				# 読み込み中
				im_h = np.zeros((480, 640, 3))
				cv2.imshow( 'frame', im_h )
				return

			# 同期 
			for i, q in enumerate( self.queues ):
						
				if i == 0:
					bfTime = q.queue[0][0]
					continue
				else:
					if q.queue[0][0] is not None:
						pass
						self.debug("0=" + str(self.queues[0].qsize()))
						self.debug(str(i) + "=" + str(self.queues[i].qsize()))
						# self.debug("0=" + str(self.queues[0].queue[0][0]))
						# self.debug(str(i) + "=" + str(q.queue[0][0]))

				if q.queue[0][0] is not None:
					tm = bfTime - q.queue[0][0]
					if abs(tm) >= self.syncedDiffTime:
						# 指定以上の時間差が発生した場合、
						# 同期処理を行う。
						self.syncTime(tm, self.queues[i])

			if len(self.queues) > 1:
				im_h = cv2.hconcat([self.queues[0].get()[1], self.queues[1].get()[1]])
				# print(str(self.queues[0].qsize()) + ":" + str(self.queues[1].qsize()))
			else:
				im_h = self.queues[0].get()[1]
			
			cv2.imshow( 'frame', im_h )

		def syncTime(self, time, queue:queue.Queue):
			if self.syncedMaxCount <= 0:
				# INIで回数制限を指定可能。
				# 多すぎるとFrameを削りすぎて落ちる。
				return
			
			self.debug("syncTime start")
			self.debug("time:" + str(time))
			frame = int(self.CONST_FPS * time)
			if queue.maxsize < frame:
				raise ValueError("内部キャッシュのサイズ不足です。設定を見直してください。")
			
			# 回数デクリメント
			self.syncedMaxCount -= 1
			if time < 0:
				""
				動画の再生タイミングが早いため、
				黒い画像を挿入し、調整
				""
				self.debug("動画の再生タイミング: 早い :" + str(frame))

				img = np.zeros((480, 640, 3)).astype('uint8')
				wkList = []
				self.debug(queue.qsize())
				# 一度リストに移動
				self.debug("一度リストに移動")
				while not queue.empty():
					wkList.append(queue.get())
				# 黒画像を追加
				self.debug("黒画像を追加")
				for i in range(abs(frame)):
					if not queue.full():
						queue.put((None, img))
				# キューが満タンになるまで、画像を追加
				self.debug("キューが満タンになるまで、画像を追加")
				while not queue.full():
					queue.put(wkList.pop())
				self.debug(queue.qsize())
			else:
				""
				動画の再生タイミングが遅いため、
				動画を削り、調整
				""
				self.debug("動画の再生タイミング: 遅い :" + str(frame))
				self.debug(queue.qsize())
				for i in range(abs(frame)):
					if not queue.empty():
						# 映像を削る
						queue.get()
				self.debug(queue.qsize())
			self.debug("syncTime end")
	"""
	def asdf():
		pass

