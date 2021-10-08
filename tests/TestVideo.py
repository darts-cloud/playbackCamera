import cv2
import numpy as np
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playbackCamera.VideoCapture import ThreadingVideoCapture, ThreadingVideoCaptureV2, ThreadingVideoCaptureV3, ThreadingVideoCaptureV2_1
import json
import configparser
import queue
from playbackCamera.VideoUtil import VideoUtil

class CameraV3_1Test():
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
				capture = ThreadingVideoCapture(src.strip(), 1000)
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

		for i, capture in enumerate( self.captures ):
			capture.start()
	
		while(True):
			key = cv2.waitKey(20) & 0xFF
			if key == ord(' '):
				break
			
			# キューに登録した動画を再生
			self.showImage()

		for i, capture in enumerate( self.captures ):
			capture.release()

		cv2.destroyAllWindows()

	def showImage(self):

		for i, capture in enumerate( self.captures ):
			im_h = capture.read()[1]					
			cv2.imshow( 'frame' + str(i), im_h )

	def debug(self, mes):
		if self.DEBUG:
			print(mes)

class CameraV3_2Test():
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
		self.frames = 0
		self.surveyFpsFrames = 300
		self.surveyFlag = True
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
		
		self.startTime = time.time()
		
		while(True):
			key = cv2.waitKey(1) & 0xFF
			if key == ord(' '):
				break
			time.sleep(0.028)

			# キューに登録した動画を再生
			self.showImage()

			self.frames += 1
			if self.surveyFlag and self.frames >= self.surveyFpsFrames:
				print("TestVideo:")
				VideoUtil.CountFps(self.startTime, time.time(), "", self.surveyFpsFrames)
				self.surveyFlag = False
			
		for i, capture in enumerate( self.captures ):
			capture.release()

		cv2.destroyAllWindows()

	def showImage(self):

		if len(self.captures) > 1:
			q0 = self.captures[0].read()
			q1 = self.captures[1].read()
			im_h = cv2.hconcat([q0[1], q1[1]])
			cv2.putText(im_h, str(q0[0]), (  0, 50), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 5, cv2.LINE_AA)
			cv2.putText(im_h, str(q1[0]), (700, 50), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 5, cv2.LINE_AA)

		else:
			im_h = self.captures[0].read()[1]
		
		cv2.imshow( 'frame', im_h )

	def debug(self, mes):
		if self.DEBUG:
			print(mes)


class CameraV3_3Test():
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
		self.frames = 0
		self.surveyFpsFrames = 300
		self.surveyFlag = True
		frames = int(self.CONST_FPS * (self.delayTime + self.adjutTime))
		self.queue = queue.Queue(maxsize=frames)
		self.srcList = []
		for src in self.srcs.split(','):
			if src.strip() != "":
				self.srcList.append(src.strip())
		self.capture = ThreadingVideoCaptureV3(self.srcList, 1000)
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

		self.capture.start()
		
		self.startTime = time.time()
		
		while(True):
			key = cv2.waitKey(300) & 0xFF
			if key == ord(' '):
				break
			# time.sleep(0.028)

			# キューに登録した動画を再生
			self.showImage()

			self.frames += 1
			if self.surveyFlag and self.frames >= self.surveyFpsFrames:
				print("TestVideo:")
				VideoUtil.CountFps(self.startTime, time.time(), "", self.surveyFpsFrames)
				self.surveyFlag = False
			
		self.capture.release()

		cv2.destroyAllWindows()

	def showImage(self):

		if self.capture.srcNum > 1:
			q = self.capture.read()
			im_h = cv2.hconcat([q[1][0], q[1][1]])
			cv2.putText(im_h, str(q[1]), (  0, 50), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 5, cv2.LINE_AA)

		else:
			im_h = self.captures[0].read()[1]
		
		cv2.imshow( 'frame', im_h )

	def debug(self, mes):
		if self.DEBUG:
			print(mes)

