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
class MediaPipePlayer(BasePlayer):

	def __init__(self):
		super().__init__()

		self.mp_drawing = mp.solutions.drawing_utils
		self.mp_drawing_styles = mp.solutions.drawing_styles
		self.mp_hands = mp.solutions.hands

	def _decorationImage(self, image):
		with self.mp_hands.Hands(
			static_image_mode=False,
			model_complexity=0,
			min_detection_confidence=0.1,
			min_tracking_confidence=0.1) as hands:

			image.flags.writeable = False
			bgr = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			results = hands.process(bgr)
		
			# 検出された手の骨格をカメラ画像に重ねて描画
			image.flags.writeable = True
			if results.multi_hand_landmarks:
				for hand_landmarks in results.multi_hand_landmarks:
					self.mp_drawing.draw_landmarks(
						image,
						hand_landmarks,
						self.mp_hands.HAND_CONNECTIONS,
						self.mp_drawing_styles.get_default_hand_landmarks_style(),
						self.mp_drawing_styles.get_default_hand_connections_style())
		return image
