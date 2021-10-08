import threading
import queue
import numpy as np
import cv2
import time
from playbackCamera.CountFps import *

"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCapture:

	"""コンストラクタ"""
	def __init__(self, src, max_queue_size=256):
		self.src = src
		self.video = cv2.VideoCapture(src)
		if not self.video.isOpened():
			print("Connect Error:" + src)
			return

		print("Connected:" + src)
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
		
		while True:

			try:
				if self.stopped:
					return
				
				ret, img = self.video.read()
				self.fpsCount.CountFrame()

				if not ret:
					self.stop()
					return
				
				"""
				OpenCvは内部バッファーを持っている。
				常に最新のフレームを取得したい場合、
				このバッファーが邪魔となるため、
				常に全フレームを読み込み、不要となるフレームを
				内部的に読み込むことで内部バッファー内の映像を
				全て吐き出している。
				"""
				if not self.q.empty():
					try:
						# 常に最新のフレームを読み込む
						self.q.get_nowait()
					except queue.Empty:
						pass
				
				times = time.time()
				fps = self.fpsCount.CountFps()
				self.q.put([times, img, fps])
			except Exception:
				pass

	"""
	Queueより最新のフレームを取得する。
	"""
	def read(self):
		return self.q.get()
	
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

"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCapture2(ThreadingVideoCapture):

	"""コンストラクタ"""
	def __init__(self, src, max_queue_size=256):
		super().__init__(src, max_queue_size)
		self.bef = None

	"""
	Queueより最新のフレームを取得する。
	"""
	def read(self):
		if not self.q.empty():
			try:
				# 常に最新のフレームを読み込む
				ret = self.q.get_nowait()
				self.bef = ret
				return ret
			except queue.Empty:
				pass

		if self.bef is None:
			ret = self.q.get()
			self.bef = ret
			return ret

		return self.bef

"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCapture3(ThreadingVideoCapture2):

	"""コンストラクタ"""
	def __init__(self, src, max_queue_size=256):
		super().__init__(src, max_queue_size)

	"""
	Queueより最新のフレームを取得する。
	"""
	def read(self):
		if not self.q.empty():
			try:
				# 常に最新のフレームを読み込む
				ret = self.q.get_nowait()
				ret[1] = cv2.resize(ret[1], dsize=(640, 480))
				self.bef = ret
				return ret
			except queue.Empty:
				pass

		if self.bef is None:
			ret = self.q.get()
			self.bef = ret
			return ret

		return self.bef

"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCapture4(ThreadingVideoCapture2):

	"""コンストラクタ"""
	def __init__(self, src, max_queue_size=256):
		super().__init__(src, max_queue_size)
		self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
