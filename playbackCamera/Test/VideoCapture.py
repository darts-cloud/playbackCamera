import threading
import queue
import numpy as np
import cv2
import time
from CountFps import *

def main():
	# cam = OpenGLPlayer()
	cam = VideoCapture("rtsp://192.168.1.144:8554/unicast") # クッソ遅い
	cam.update()

if __name__ == "__main__": 
	main()

"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class VideoCapture:

	"""コンストラクタ"""
	def __init__(self, src):
		self.src = src
		print("Connect:" + src)
		self.video = cv2.VideoCapture(src)
		if not self.video.isOpened():
			print("Connect Error.")
			return

		print("Connected.")
		self.stopped = False
		self.fpsCount = CountFps()

	""" 
	ソース元より、常に動画を受け取り、
	最新の動画のみ、Queueに登録する。
	別スレッドで実行する。
	"""
	def update(self):
		
		while True:

			try:
				if self.stopped:
					time.sleep(1000)
					continue
				
				ret, img = self.video.read()
				self.fpsCount.CountFrame()

				if not ret:
					self.stop()
					print(self.src + ":stop")
					continue
				
				times = time.time()
				fps = self.fpsCount.CountFps()
				print(fps)
			except Exception:
				pass

	"""映像リソースをリリースする。"""
	def release(self):
		self.stopped = True
		self.video.release()
	
	"""映像リソースが開けているか、返す。"""
	def isOpened(self):
		return self.video.isOpened()


"""
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCapture2(VideoCapture):

	"""コンストラクタ"""
	def __init__(self, src):
		super().__init__(src)
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
	def __init__(self, src):
		super().__init__(src)

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
映像リソースより最新のフレームを読み込むためのクラス
FPSが異なる複数リソースにアクセスする場合、
常に最新のフレームを取得することができる。
"""
class ThreadingVideoCapture4(ThreadingVideoCapture3):

	"""コンストラクタ"""
	def __init__(self, src):
		super().__init__(src)
		self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
