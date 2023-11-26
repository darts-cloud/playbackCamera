from BasePlayer import *

class PerfomanceTestPlayer(BasePlayer):

	def __init__(self):
		super().__init__()
		self.conf.saveMovie = False

	def _drawGlidLine(self, img):
		return img

	def _useQueue(self):
		logging.debug("_useQueue start")

		if len(self.queues) <= 0:
			# 読み込み中
			im_h = np.zeros((self.conf.sizeH, self.conf.sizeW, 3)).astype('uint8')
			str = "There are no streams that can be displayed."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			
			self._imshow('frame', im_h)
			return

		if self.queues[0].qsize() < int(self.conf.fps * self.conf.delayTime):
			# 読み込み中
			im_h = np.zeros((self.conf.sizeH, self.conf.sizeW, 3)).astype('uint8')
			str = "Now loading please wait..."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			self._imshow('frame', im_h)
			return
		
		# Queueより動画を取得
		try:
			frames = [self.queues[0].get_nowait()[1]]
		except queue.Empty:
			pass
		white = (255, 255, 255)
			
		# 動画を表示
		self._show(frames, None)

		logging.debug("_useQueue end")


	def _show(self, frames, allimg):
		logging.debug("show start")
		# img = self._resize(frames[int(0)], dsize=(self.conf.dispSizeW, self.conf.dispSizeH))

		if self.conf.glidLineFlg:
			img = self._drawGlidLine(frames[int(0)])

		fps2 = self.fpsCount.CountFps()
		
		height, width, channels = img.shape[:3]
		white = (255, 255, 255)
		black = (0, 0, 0)
		cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  60), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
		cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  60), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)

		self.img = img
		# 高解像度で表示すると描画が遅いことが判明
		self._imshow('frame', img)
		logging.debug("show end")