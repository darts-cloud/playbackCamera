import cv2
import numpy as np
import time
import datetime
from VideoCapture import *
from Player import *
import json
import configparser
import queue
import sys
from playbackCamera.CountFps import *
from screeninfo import get_monitors
import fpstimer
import mediapipe as mp

from enum import Enum
class MediaPipePlayer_Pose(Player):

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
			self._addQueue()
			
			# キューに入れた（遅延した）動画を使用
			self._useQueue()

		for i, capture in enumerate( self.captures ):
			capture.release()

		self._endProcess()

	def _showMessage(self, windowName, img):
		logging.debug("imshow start")
		cv2.namedWindow(windowName, cv2.WINDOW_FULLSCREEN)
		cv2.imshow(windowName, img)
		logging.debug("imshow end")

	def _useQueue(self):

		if len(self.queues) <= 0:
			# 読み込み中
			im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			str = "There are no streams that can be displayed."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			
			self._showMessage('frame', im_h)
			return

		if self.queues[0].qsize() < int(self.fps * self.delayTime):
			# 読み込み中
			im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			str = "Now loading please wait..."
			white = (255, 255, 255)
			cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			self._showMessage('frame', im_h)
			return
		
		# Queueより動画を取得
		frames = []
		white = (255, 255, 255)
		black = (0, 0, 0)

		mp_drawing = mp.solutions.drawing_utils
		mp_pose = mp.solutions.pose

		for i, queue in enumerate( self.queues ):
			try:
				frame = queue.get_nowait()[1]
				# debug
				# qs = queue.qsize()
				# text = "{} frames in array".format(qs)
				# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
				# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)

				image = frame
				with mp_pose.Pose(
					min_detection_confidence=0.5,
					min_tracking_confidence=0.5) as pose:

					# 後で自分撮りビューを表示するために画像を水平方向に反転し、BGR画像をRGBに変換
					image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
					# パフォーマンスを向上させるには、オプションで、参照渡しのためにイメージを書き込み不可としてマーク
					image.flags.writeable = False
					results = pose.process(image) 

					# 画像にポーズアノテーションを描画
					image.flags.writeable = True
					image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
					mp_drawing.draw_landmarks(
						image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
					cv2.imshow('MediaPipe Pose', image)

				frames.append(image)
			except queue.Empty:
				pass
			
		# 動画を表示
		allimg = self.__concatImage(frames)
		if self.GlidLineFlg:
			alpha = 0.2
			allimg = cv2.addWeighted(self.mask, alpha, allimg, 1 - alpha, 0)
			allimg = self._drawGlidLine(allimg)

		self._show(frames, allimg)

		if len(self.captures) >= 2:
			frames.append(allimg)

		if self.saveMovie:
			self.save(frames)
