import threading
import queue
import numpy as np
import cv2
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playbackCamera.VideoUtil import VideoUtil
import configparser

class ThreadingVideoCapture:
	DEBUG = True
	CONST_FPS = 30
	INI_SECTION = "DEFAULT"
	INI_CAMERA = "camera"
	INI_DELAY_TIME = "delay_time"
	INI_ADJUSTMENT_TIME = "adjustment_time"
	INI_FPS = "fps"
	INI_SYNCED_DIFF_TIME = "synced_diff_time"
	INI_SYNCED_MAX_COUNT = "synced_max_count"
	def __init__(self, src):
		self.src = src
		config = configparser.ConfigParser()
		config.read("settings.ini")
		self.delayTime = float(config.get(self.INI_SECTION, self.INI_DELAY_TIME))
		self.adjutTime = float(config.get(self.INI_SECTION, self.INI_ADJUSTMENT_TIME))
		self.syncedDiffTime = float(config.get(self.INI_SECTION, self.INI_SYNCED_DIFF_TIME))
		self.syncedMaxCount = int(config.get(self.INI_SECTION, self.INI_SYNCED_MAX_COUNT))
		self.srcs = config.get(self.INI_SECTION, self.INI_CAMERA)

		self.videos = []
		self.srcNum = 0
		self.frames = 0
		self.surveyFpsFrames = 300
		self.surveyFlag = True

	# def read(self):
	#     return self.q.get()
	
	# def start(self):
	#     # 開始時間
	#     self.startTime = time.time()
	#     self.started = True

	# def stop(self):
	#     self.stopped = True

	# def release(self):
	#     self.stopped = True
	#     for i, video in enumerate( self.videos ):
	#         video.release()

	# def isOpened(self):
	#     return self.video.isOpened()

	# def get(self, i):
	#     ret = []
	#     for i, video in enumerate( self.videos ):
	#         ret.append(video.get(i))
	#     return ret

	def update(self):
		
		start = time.time()
		frames = 1
		while True:

			key = cv2.waitKey(1) & 0xFF

			video = cv2.VideoCapture(self.src)
			if video.isOpened():
				self.srcNum += 1
			else:
				continue
			# time.sleep(0.016)
			# if self.stopped:
			#     return
			# if not self.started:
			#     continue
			# if self.q.full():
			#     continue
			# if key == ord(' '):
			# 	break

			flag, frame = video.read()
			# if not flag:
			#     self.stop()
			#     return
			fps = VideoUtil.CountFps(start, time.time(), "", frames)
			cv2.putText(frame, "{:.3f}".format(fps), (  0, 50), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4, cv2.LINE_AA)
		
			cv2.imshow("frame", frame)

			# self.q.put((time.time(), ret))

			frames += 1
			video.release()
			# if self.surveyFlag and self.frames >= self.surveyFpsFrames:
			#     print("VideoCapture:")
			#     VideoUtil.CountFps(self.startTime, time.time(), "", self.surveyFpsFrames)
			#     self.surveyFlag = False

cap = ThreadingVideoCapture("rtsp://192.168.1.113")
cap.update()
