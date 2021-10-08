from playbackCamera.VideoCapture import ThreadingVideoCaptureV2_1
import cv2
import numpy as np
import time
from VideoCapture import ThreadingVideoCapture, ThreadingVideoCaptureV2
import json
import configparser
import queue

class CameraV2():

	def __init__(self):
		# 動画の読み込み
		self.video = self.videoCapture()
		# <class 'cv2.VideoCapture'>
		# print(type(video))

		self.frame_rate = int(self.video.get(cv2.CAP_PROP_FPS))      # フレームレート
		self.size = (640, 480) # 動画の画面サイズ

		self.fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') # ファイル形式(ここではmp4)
		self.writer = cv2.VideoWriter('./result/outtest.mp4', self.fmt, self.frame_rate, self.size) # ライター作成

	def getImage(self):
		return self.video.read()[1]

	def endProcess(self):
		self.video.release()
		self.writer.release()

	def save(self):
		
		# lst = [None for _ in range(150)]
		lst = []

		idx = 0
		tien = 3 * 30
		while(True):

			# 1フレーム読み込み
			image = self.getImage()
			# cv2.imshow("image", image)
			if len(lst) < tien:
				lst.append(image)
			else:
				lst[(idx+tien-1)%tien] = image
				cv2.imshow("image", lst[idx])
			# # self.writer.write(image) # 画像を1フレーム分として書き込み

			# cv2.imshow("image", image)
			key = cv2.waitKey(10)
			if(key == 'q'):
				cv2.destroyAllWindows()
				break

			idx += 1
			if idx >= tien:
				idx = 0
		
		self.endProcess()

		return 0

	def videoCapture(self):
		self.video = None
		for i in range(10):
			self.video = cv2.VideoCapture(i)
			if self.video.isOpened():
				break
		return self.video

	def load(self):

		while(True):

			# 1フレーム読み込み
			image = self.getImage()
			self.writer.write(image) # 画像を1フレーム分として書き込み

			key = cv2.waitKey(10)
			if(key == 'q'):	
				cv2.destroyAllWindows()
				break
		
		self.endProcess()

		return 0

class CameraV3():
	JSON_CAMERA = "camera"
	JSON_DELAY_TIME = "delay_time"
	JSON_ADJUSTMENT_TIME="adjustment_time"

	def __init__(self):
		json_file = open('settings.json', 'r')
		json_data = json.load(json_file)
		self.srcs = []
		for src in json_data[self.JSON_CAMERA]:
			if src != "":
				self.srcs.append(src)
		self.captures = []
		self.delayTime = json_data[self.JSON_DELAY_TIME]
		self.adjutTime = json_data[self.JSON_ADJUSTMENT_TIME]

	def start(self):
		for i, src in enumerate( self.srcs ):
			capture = ThreadingVideoCaptureV2(src)
			if capture.isOpened():
				self.captures.append( capture )

		for i, capture in enumerate( self.captures ):
			capture.start()

		while(True):
			key = cv2.waitKey(1) & 0xFF
			if key == ord(' '):
				break
			frames = []
			for i, capture in enumerate( self.captures ):
				frames.append(capture.read()[1])
			
			# for i, frame in enumerate( frames ):
			# 	cv2.imshow( 'frame' + str(i), frame )
			# im_h = cv2.hconcat(frames)
			im_h = cv2.hconcat([frames[0], frames[1]])
			cv2.imshow( 'frame', im_h )

			# cv2.imwrite('data/dst/opencv_hconcat.jpg', im_h)

		capture.release()
		cv2.destroyAllWindows()

class CameraV3_2():
	DEBUG = True
	CONST_FPS = 30
	INI_SECTION = "DEFAULT"
	INI_CAMERA = "camera"
	INI_DELAY_TIME = "delay_time"
	INI_ADJUSTMENT_TIME = "adjustment_time"
	INI_FPS = "fps"
	INI_SYNCED_DIFF_TIME = "synced_diff_time"
	INI_SYNCED_MAX_COUNT = "synced_max_count"
	def __init__(self):
		self.loadIniFile()

		frames = int(self.CONST_FPS * (self.delayTime + self.adjutTime))
		self.captures = []
		self.queues = []
		for src in self.srcs.split(','):
			if src.strip() != "":
				capture = ThreadingVideoCaptureV2_1(src.strip(), 1000)
				if capture.isOpened():
					self.captures.append( capture )
					self.queues.append( queue.Queue(maxsize=frames) )
		self.syncCount = 3

	def loadIniFile(self):
		config = configparser.ConfigParser()
		config.read("settings.ini")
		self.delayTime = float(config.get(self.INI_SECTION, self.INI_DELAY_TIME))
		self.adjutTime = float(config.get(self.INI_SECTION, self.INI_ADJUSTMENT_TIME))
		self.syncedDiffTime = float(config.get(self.INI_SECTION, self.INI_SYNCED_DIFF_TIME))
		self.syncedMaxCount = int(config.get(self.INI_SECTION, self.INI_SYNCED_MAX_COUNT))
		self.srcs = config.get(self.INI_SECTION, self.INI_CAMERA)

	def start(self):

		while(True):
			key = cv2.waitKey(20) & 0xFF
			if key == ord(' '):
				break
			
			# 動画をキューに登録
			self.addQueue()
			
			# キューに登録した動画を再生
			self.showImage()

		for i, capture in enumerate( self.captures ):
			capture.release()

		cv2.destroyAllWindows()

	def addQueue(self):
		for i, capture in enumerate( self.captures ):
			if not self.queues[i].full():
				self.queues[i].put(capture.read())

	def showImage(self):
		
		if self.queues[0].qsize() < int(self.CONST_FPS * self.delayTime):
			# 読み込み中
			im_h = np.zeros((480, 640, 3))
			cv2.imshow( 'frame', im_h )
			return

		# # 同期 
		# for i, q in enumerate( self.queues ):
					
		# 	if i == 0:
		# 		bfTime = q.queue[0][0]
		# 		continue
		# 	else:
		# 		if q.queue[0][0] is not None:
		# 			pass
		# 			self.debug("0=" + str(self.queues[0].qsize()))
		# 			self.debug(str(i) + "=" + str(self.queues[i].qsize()))
		# 			# self.debug("0=" + str(self.queues[0].queue[0][0]))
		# 			# self.debug(str(i) + "=" + str(q.queue[0][0]))

		# 	if q.queue[0][0] is not None:
		# 		tm = bfTime - q.queue[0][0]
		# 		if abs(tm) >= self.syncedDiffTime:
		# 			# 指定以上の時間差が発生した場合、
		# 			# 同期処理を行う。
		# 			self.syncTime(tm, self.queues[i])

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
			"""
			動画の再生タイミングが早いため、
			黒い画像を挿入し、調整
			"""
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
			"""
			動画の再生タイミングが遅いため、
			動画を削り、調整
			"""
			self.debug("動画の再生タイミング: 遅い :" + str(frame))
			self.debug(queue.qsize())
			for i in range(abs(frame)):
				if not queue.empty():
					# 映像を削る
					queue.get()
			self.debug(queue.qsize())
		self.debug("syncTime end")

	def debug(self, mes):
		if self.DEBUG:
			print(mes)

