import cv2
import numpy as np
import time
import datetime
from VideoCapture import *
from BasePlayer import *
import json
import configparser
import queue
import sys
from playbackCamera.CountFps import *
from screeninfo import get_monitors
import fpstimer

from enum import Enum
class Player(BasePlayer):

	def start(self):
		self.fpsTimer = fpstimer.FPSTimer(self.fps)
		if self.GlidLineFlg:
			mask = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			self.mask = self._drawGlidLine(mask)

		while(True):
			key = cv2.waitKey(1) & 0xFF
			if key == ord(' '):
				break
			elif key == ord('0'):
				self.Mode = Mode.ALL
			elif key == ord('1'):
				self.Mode = Mode.DISP_1
			elif key == ord('2'):
				self.Mode = Mode.DISP_2
			elif key == ord('3'):
				self.Mode = Mode.DISP_3
			elif key == ord('4'):
				self.Mode = Mode.DISP_4
			
			self.fpsTimer.sleep()

			# Fps計算用にフレーム計算
			self.fpsCount.CountFrame()
			
			# 動画をキューに登録
			self.addQueue()
			
			# キューに入れた（遅延した）動画を使用
			self.useQueue()

		for i, capture in enumerate( self.captures ):
			capture.release()

		self.endProcess()

	def _imshow(self, windowName, img):
		logging.debug("imshow start")
		cv2.namedWindow(windowName, cv2.WINDOW_FULLSCREEN)
		cv2.imshow(windowName, img)
		logging.debug("imshow end")

	def save(self, frames):
		for i, writer in enumerate( self.writers ):
			writer.write(frames[i][1]) # 画像を1フレーム分として書き込み

	def endProcess(self):
		for i, capture in enumerate( self.captures ):
			capture.release()
		if self.saveMovie:
			for i, writer in enumerate( self.writers ):
				writer.release()
		
		cv2.destroyAllWindows()

	def debug(self, mes):
		if self.DEBUG:
			print(mes)
