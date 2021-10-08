import threading
import queue
import numpy as np
import cv2
import time
from playbackCamera.VideoUtil import VideoUtil

class ThreadingVideoCapture:

	def __init__(self, src, max_queue_size=256):
		self.src = src
		self.video = cv2.VideoCapture(src)
		self.q = queue.Queue(maxsize=max_queue_size)
		self.started = False
		self.stopped = False
		self.frames = 0
		self.surveyFpsFrames = 300
		self.surveyFlag = True
		thread = threading.Thread(target=self.update, daemon=True)
		thread.start()

	def update(self):
		
		while True:

			if self.stopped:
				return

			if not self.started:
				continue

			if self.q.full():
				continue
			
			ret, frame = self.video.read()
			self.q.put((time.time(), frame))

			self.frames += 1
			if self.surveyFlag and self.frames >= self.surveyFpsFrames:
				VideoUtil.CountFps(self.startTime, time.time(), self.src, self.surveyFpsFrames)
				self.surveyFlag = False

			if not ret:
				self.stop()
				return

	def read(self):
		return self.q.get()
	
	def start(self):
		# 開始時間
		self.startTime = time.time()
		self.started = True

	def stop(self):
		self.stopped = True

	def release(self):
		self.stopped = True
		self.video.release()

	def isOpened(self):
		return self.video.isOpened()

	def get(self, i):
		return self.video.get(i)

class ThreadingVideoCaptureV2_1:

	def __init__(self, src, max_queue_size=256):
		self.src = src
		self.video = cv2.VideoCapture(src)
		self.q = queue.Queue(maxsize=max_queue_size)
		self.started = False
		self.stopped = False
		self.frames = 0
		self.surveyFpsFrames = 300
		self.surveyFlag = True
		self.startTime = time.time()
		thread = threading.Thread(target=self.update, daemon=True)
		thread.start()

	def update(self):
		
		while True:

			if self.stopped:
				return
			
			ret, frame = self.video.read()
			if not ret:
				self.stop()
				return
			if not self.q.empty():
				try:
					self.q.get_nowait()   # discard previous (unprocessed) frame
				except queue.Empty:
					pass
			self.q.put((time.time(), frame))
			
			# self.frames += 1
			# if self.surveyFlag and self.frames >= self.surveyFpsFrames:
			# 	VideoUtil.CountFps(self.startTime, time.time(), self.src, self.surveyFpsFrames)
			# 	self.surveyFlag = False

	def read(self):
		return self.q.get()
	
	def stop(self):
		self.stopped = True

	def release(self):
		self.stopped = True
		self.video.release()

	def isOpened(self):
		return self.video.isOpened()

	def get(self, i):
		return self.video.get(i)

class ThreadingVideoCaptureV2(ThreadingVideoCapture):

	def __init__(self, src, max_queue_size=256):
		super().__init__(src, max_queue_size)

	def update(self):
		
		while True:

			time.sleep(0.0285)

			if self.stopped:
				return

			if not self.started:
				continue

			if self.q.full():
				print(self.src + ":" + time.time())
				continue
			
			ret, frame = self.video.read()
			self.q.put((time.time(), frame))
			# print(self.src + ":" + str(self.frames))
			self.frames += 1
			if self.surveyFlag and self.frames >= self.surveyFpsFrames:
				print("VideoCapture:")
				VideoUtil.CountFps(self.startTime, time.time(), self.src, self.surveyFpsFrames)
				self.surveyFlag = False

			if not ret:
				self.stop()
				return

class ThreadingVideoCaptureV3:

	def __init__(self, srcs, max_queue_size=256):
		self.src = srcs
		self.videos = []
		self.srcNum = 0
		for i, src in enumerate( srcs ):
			video = cv2.VideoCapture(src)
			if video.isOpened():
				self.videos.append(video)
				self.srcNum += 1
		self.q = queue.Queue(maxsize=max_queue_size)
		self.started = False
		self.stopped = False
		self.frames = 0
		self.surveyFpsFrames = 300
		self.surveyFlag = True
		thread = threading.Thread(target=self.update, daemon=True)
		thread.start()

	def read(self):
		return self.q.get()
	
	def start(self):
		# 開始時間
		self.startTime = time.time()
		self.started = True

	def stop(self):
		self.stopped = True

	def release(self):
		self.stopped = True
		for i, video in enumerate( self.videos ):
			video.release()

	def isOpened(self):
		return self.video.isOpened()

	def get(self, i):
		ret = []
		for i, video in enumerate( self.videos ):
			ret.append(video.get(i))
		return ret

	def update(self):
		
		while True:

			if self.stopped:
				return

			if not self.started:
				continue

			if self.q.full():
				continue

			ret = []
			for i, video in enumerate( self.videos ):
				flag, frame = video.read()
				ret.append(frame)
				if not flag:
					self.stop()
					return

			self.q.put((time.time(), ret))

			self.frames += 1
			if self.surveyFlag and self.frames >= self.surveyFpsFrames:
				print("VideoCapture:")
				VideoUtil.CountFps(self.startTime, time.time(), "", self.surveyFpsFrames)
				self.surveyFlag = False
