import cv2
import numpy as np
import time
import datetime
from playbackCamera.capture.VideoCapture import *
from playbackCamera.player.Player import *
import json
import configparser
import queue
import sys
from playbackCamera.util.CountFps import *
import fpstimer
import mediapipe as mp

from enum import Enum
class MediaPipePlayer(Player):

	def __init__(self):
		super().__init__()

		self.mp_drawing = mp.solutions.drawing_utils
		self.mp_pose = mp.solutions.pose

	def _decorationImage(self, image):
		with self.mp_pose.Pose(
			min_detection_confidence=0.5,
			min_tracking_confidence=0.5) as pose:

			# 後で自分撮りビューを表示するために画像を水平方向に反転し、BGR画像をRGBに変換
			image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			# パフォーマンスを向上させるには、オプションで、参照渡しのためにイメージを書き込み不可としてマーク
			image.flags.writeable = False
			results = pose.process(image) 

			# 画像にポーズアノテーションを描画
			image.flags.writeable = True
			image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
			self.mp_drawing.draw_landmarks(
				image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
		return image
