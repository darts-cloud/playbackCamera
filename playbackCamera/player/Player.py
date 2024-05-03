from playbackCamera.player.BasePlayer import *
from playbackCamera.capture.DummyCapture import *

class Player(BasePlayer):

	def __init__(self):
		super().__init__()
		self.isinit = True

	def _initVideoSoruce(self):
		self.captures = []
		self.queues = []
		frames = int(self.conf.fps * (self.conf.delayTime + self.conf.adjutTime))
		for i, s in enumerate( self.conf.srcs.split(',') ):
			src = s.strip()
			if src != "":
				# capture = DummyCapture(None, 1000)
				capture = ThreadingVideoCapture(src, 1000)
				if capture.isOpened():
					self.captures.append( capture )
					self.queues.append( queue.Queue(maxsize=frames) )

	def _addQueue(self):
		logging.debug("_addQueue start")
		for i, capture in enumerate( self.captures ):
			if not self.queues[i].full():
				try:
					if self.isinit:
						capture.load()
					# 常に最新のフレームを読み込む
					self.queues[i].put_nowait(capture.read())
				except queue.Full:
					pass
				self.isinit = False
		logging.debug("_addQueue end")

class RealtimePlayer(BasePlayer):

	def _initVideoSoruce(self):
		self.captures = []
		self.queues = []
		for i, s in enumerate( self.conf.srcs.split(',') ):
			src = s.strip()
			if src != "":
				capture = ThreadingVideoCaptureForPyAv(src, 1000)
				if capture.isOpened():
					self.captures.append( capture )
					self.queues.append( None )

	def _addQueue(self):
		logging.debug("_addQueue start")
		for i, capture in enumerate( self.captures ):
			# 常に最新のフレームを読み込む
			self.queues[i] = capture.read()
		logging.debug("_addQueue end")

	def _useQueue(self):
		logging.debug("_useQueue start")
		
		# Queueより動画を取得
		frames = []
		white = (255, 255, 255)
		black = (0, 0, 0)
		for i, queue in enumerate( self.queues ):
			try:
				frame = queue[1]
				# fps = queue[2]
				# debug
				# qs = queue.qsize()
				# text = "{} frames in array, {}fps".format(qs, fps)
				# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
				# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)
				frame = self._decorationImage(frame)

				frames.append(frame)
			except queue.Empty:
				pass
			
		# 動画を表示
		allimg = self._concatImage(frames, self.conf.sizeW, self.conf.sizeH)
		self._show(frames, allimg)

		if len(self.captures) >= 2:
			frames.append(allimg)

		if self.conf.saveMovie:
			self._save(frames)
		logging.debug("_useQueue end")
