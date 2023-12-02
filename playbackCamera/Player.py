from playbackCamera.BasePlayer import *

class Player(BasePlayer):

	def _initVideoSoruce(self):
		self.captures = []
		self.queues = []
		frames = int(self.conf.fps * (self.conf.delayTime + self.conf.adjutTime))
		for i, s in enumerate( self.conf.srcs.split(',') ):
			src = s.strip()
			if src != "":
				capture = ThreadingVideoCapture4(src, 1000)
				if capture.isOpened():
					self.captures.append( capture )
					self.queues.append( queue.Queue(maxsize=frames) )

