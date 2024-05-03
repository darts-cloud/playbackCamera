import threading
import queue
import cv2
import time
from playbackCamera.util.CountFps import *

"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCapture:

	"""コンストラクタ"""
	def __init__(self, src, max_queue_size=256):
		if src is not None:
			print("Connect:" + src)
			if self._isCameraNo(src):
				src = int(src, 10)
			self.src = src

			self.video = cv2.VideoCapture(src)
			self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
			self.video.set(cv2.CAP_PROP_FPS, 30) 
			if not self.video.isOpened():
				print("Connect Error.")
				return
		
		self.max_queue_size = max_queue_size

		print("Connected.")
		self.bef = None
		self.q = queue.Queue(maxsize=max_queue_size)
		self.stopped = False
		self.fpsCount = CountFps()
		thread = threading.Thread(target=self.update, daemon=True)
		thread.start()

	""" 
	ソース元より、常に動画を受け取り、
	最新の動画のみ、Queueに登録する。
	別スレッドで実行する。
	"""
	def update(self):

		# self._load()
		while True:
			try:
				logging.warning(f"{self.src}: update start")
				if self.stopped:
					time.sleep(10)
					self.video = cv2.VideoCapture(self.src)
					if self.video.isOpened():
						print("ReConnect.")
						self.stopped = False
						# self._load()
					continue
				
				logging.warning(f"{self.src}: read start")
				ret, img = self.video.read()
				logging.warning(f"{self.src}: read end")
				self.fpsCount.CountFrame()

				if not ret:
					self.stop()
					print(self.src + ":stop")
					continue
				
				times = time.time()
				fps = self.fpsCount.CountFps()
				self.q.put([times, img, fps])
				# print(fps)
				logging.warning(f"{self.src}: update end")

			except Exception as e:
				print(e)
				print("通信エラーが発生")


	"""
	OpenCvは内部バッファーを持っている。
	常に最新のフレームを取得したい場合、
	このバッファーが邪魔となるため、
	常に全フレームを読み込み、不要となるフレームを
	内部的に読み込むことで内部バッファー内の映像を
	全て吐き出している。
	"""
	def load(self):
		while not self.q.empty():
			ret = self.q.get_nowait()

	"""
	Queueより最新のフレームを取得する。
	"""
	def read(self):
		if not self.q.empty():
			try:
				ret = self.q.get_nowait()

				# self.bef = ret
				self.bef = [ret[0], cv2.bitwise_not(ret[1]), ret[2]]
				return ret
			except queue.Empty:
				pass

		if self.bef is None:
			ret = self.q.get()
			self.bef = ret
			return ret

		return self.bef
	
	"""映像出力を止める。"""
	def stop(self):
		self.stopped = True
	
	"""映像リソースをリリースする。"""
	def release(self):
		self.stopped = True
		self.video.release()
	
	"""映像リソースが開けているか、返す。"""
	def isOpened(self):
		return self.video.isOpened()

	"""OpenCvで取得できる映像リソース情報を返す。"""
	def get(self, i):
		return self.video.get(i)
	
	def _isCameraNo(self, s):  # 整数値を表しているかどうかを判定
		try:
			int(s, 10)  # 文字列を実際にint関数で変換してみる
		except ValueError:
			return False
		else:
			return True

import fpstimer
"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCapture2(ThreadingVideoCapture):

	"""コンストラクタ"""
	def __init__(self, src, fps, max_queue_size=256):
		super().__init__(src, max_queue_size)
		self.fpsTimer = fpstimer.FPSTimer(fps)

	""" 
	ソース元より、常に動画を受け取り、
	最新の動画のみ、Queueに登録する。
	別スレッドで実行する。
	"""
	def update(self):
		
		while True:

			try:
				if self.stopped:
					time.sleep(10)
					self.video = cv2.VideoCapture(self.src)
					if self.video.isOpened():
						print("ReConnect.")
						self.stopped = False
					continue
				
				ret, img = self.video.read()
				self.fpsCount.CountFrame()

				if not ret:
					self.stop()
					print(self.src + ":stop")
					continue
				
				"""
				OpenCvは内部バッファーを持っている。
				常に最新のフレームを取得したい場合、
				このバッファーが邪魔となるため、
				常に全フレームを読み込み、不要となるフレームを
				内部的に読み込むことで内部バッファー内の映像を
				全て吐き出している。
				"""
				while not self.q.empty():
					try:
						# 常に最新のフレームを読み込む
						self.q.get_nowait()
					except queue.Empty:
						pass
				
				times = time.time()
				fps = self.fpsCount.CountFps()

				height, width, channels = img.shape[:3]
				white = (255, 255, 255)
				cv2.putText(img, "{:.2f} fps".format(fps), (  0, height -  10), cv2.FONT_HERSHEY_TRIPLEX, 2, white, 3, cv2.LINE_AA)
				black = (0, 0, 0)
				cv2.putText(img, "{:.2f} fps".format(fps), (  0, height -  10), cv2.FONT_HERSHEY_TRIPLEX, 2, black, 1, cv2.LINE_AA)

				self.q.put([times, img, fps])
			except Exception:
				pass

			self.fpsTimer.sleep()

import logging
import av
logging.basicConfig()
logging.getLogger('libav').setLevel(logging.ERROR)
"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCaptureForPyAv(ThreadingVideoCapture):

	"""コンストラクタ"""
	def __init__(self, src, max_queue_size=256):
		print("Connect:" + src)
		if self._isCameraNo(src):
			src = int(src, 10)
		self.src = src
		self.video = av.open(src)
		
		self.max_queue_size = max_queue_size

		print("Connected.")
		self.bef = None
		self.q = queue.Queue(maxsize=max_queue_size)
		self.stopped = False
		self.fpsCount = CountFps()
		thread = threading.Thread(target=self.update, daemon=True)
		thread.start()

	""" 
	ソース元より、常に動画を受け取り、
	最新の動画のみ、Queueに登録する。
	別スレッドで実行する。
	"""
	def update(self):
		
		for frame in self.video.decode(video=0):

			try:
				if self.stopped:
					time.sleep(10)
					self.video = cv2.VideoCapture(self.src)
					if self.video.isOpened():
						print("ReConnect.")
						self.stopped = False
					continue
				
				img = frame.to_ndarray(format='bgr24')
				self.fpsCount.CountFrame()
								
				times = time.time()
				fps = self.fpsCount.CountFps()

				self.q.put([times, img, fps])

			except KeyboardInterrupt:
				print("KeyboardInterrupt")
				break
	
	# """
	# OpenCvは内部バッファーを持っている。
	# 常に最新のフレームを取得したい場合、
	# このバッファーが邪魔となるため、
	# 常に全フレームを読み込み、不要となるフレームを
	# 内部的に読み込むことで内部バッファー内の映像を
	# 全て吐き出している。
	# """
	# def _load(self):
	# 	for i in range(10):
	# 		ret, img = self.video.read()

	"""映像リソースをリリースする。"""
	def release(self):
		self.stopped = True
	
	"""映像リソースが開けているか、返す。"""
	def isOpened(self):
		return True

	"""OpenCvで取得できる映像リソース情報を返す。"""
	def get(self, i):
		return ""
