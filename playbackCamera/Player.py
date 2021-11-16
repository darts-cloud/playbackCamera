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
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import fpstimer

from enum import Enum
class Player(BasePlayer):

	def start(self):
		self.fpsTimer = fpstimer.FPSTimer(self.fps)
		if self.GlidLineFlg:
			mask = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
			self.mask = self.drawGlidLine(mask)

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

	# def addQueue(self):
	# 	for i, capture in enumerate( self.captures ):
	# 		if not self.queues[i].full():
	# 			try:
	# 				# 常に最新のフレームを読み込む
	# 				self.queues[i].put_nowait(capture.read())
	# 			except queue.Full:
	# 				pass

	# def useQueue(self):

	# 	if len(self.queues) <= 0:
	# 		# 読み込み中
	# 		im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
	# 		str = "There are no streams that can be displayed."
	# 		white = (255, 255, 255)
	# 		cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
			
	# 		self.imshow('frame', im_h)
	# 		return

	# 	if self.queues[0].qsize() < int(self.fps * self.delayTime):
	# 		# 読み込み中
	# 		im_h = np.zeros((self.sizeH, self.sizeW, 3)).astype('uint8')
	# 		str = "Now loading please wait..."
	# 		white = (255, 255, 255)
	# 		cv2.putText(im_h, str, (100, 100), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 1, cv2.LINE_AA)
	# 		self.imshow('frame', im_h)
	# 		return
		
	# 	# Queueより動画を取得
	# 	frames = []
	# 	white = (255, 255, 255)
	# 	black = (0, 0, 0)
	# 	for i, queue in enumerate( self.queues ):
	# 		try:
	# 			frame = queue.get_nowait()[1]
	# 			# debug
	# 			# qs = queue.qsize()
	# 			# text = "{} frames in array".format(qs)
	# 			# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
	# 			# cv2.putText(frame, text, (  0, 20), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)

	# 			frames.append(frame)
	# 		except queue.Empty:
	# 			pass
			
	# 	# 動画を表示
	# 	allimg = self.concatImage(frames)
	# 	if self.GlidLineFlg:
	# 		alpha = 0.2
	# 		allimg = cv2.addWeighted(self.mask, alpha, allimg, 1 - alpha, 0)
	# 		allimg = self.drawGlidLine(allimg)

	# 	self.show(frames, allimg)

	# 	if len(self.captures) >= 2:
	# 		frames.append(allimg)

	# 	self.save(frames)

	# def concatImage(self, frames):
	# 	logging.debug("concatImage start")
	# 	if len(frames) <= 1:
	# 		return self.resize(frames[0][1], dsize=(self.sizeW, self.sizeH))
		
	# 	# self.tw.weigh("1")
	# 	sizeH = (int(self.sizeH / 2))
	# 	sizeW = (int(self.sizeW / 2))
	# 	img_tmp = np.zeros((sizeH, sizeW, 3)).astype('uint8')
	# 	img1 = self.resize(frames[0][1], dsize=(sizeW, sizeH))
	# 	img2 = self.resize(frames[1][1], dsize=(sizeW, sizeH))
	# 	im_h1 = self.hconcat([img1, img2])
	# 	# self.tw.weigh("2")
	# 	if len(frames) > 2:
	# 		img3 = self.resize(frames[2][1], dsize=(sizeW, sizeH))
	# 		if len(frames) == 3:
	# 			im_h2 = self.hconcat([img3, img_tmp])
	# 			# self.tw.weigh("3")
	# 		else:
	# 			img4 = self.resize(frames[3][1], dsize=(sizeW, sizeH))
	# 			im_h2 = self.hconcat([img3, img4])
	# 			# self.tw.weigh("3")
	# 		img = self.vconcat([im_h1, im_h2])
	# 		# self.tw.weigh("4")
	# 	else:
	# 		im_h2 = self.hconcat([img_tmp, img_tmp])
	# 		img = self.vconcat([im_h1, im_h2])
	# 		# img = im_h1
	# 		# self.tw.weigh("3")
	# 	logging.debug("concatImage end")
	# 	return img

	# def resize(self, imgs, dsize):
	# 	logging.debug("resize start")
	# 	img = cv2.resize(imgs, dsize, interpolation=cv2.INTER_LINEAR)
	# 	logging.debug("resize end")
	# 	return img

	# def hconcat(self, imgs):
	# 	logging.debug("hconcat start")
	# 	img = cv2.hconcat(imgs)
	# 	# img = np.hstack(imgs)
	# 	logging.debug("hconcat end")
	# 	return img

	# def vconcat(self, imgs):
	# 	logging.debug("vconcat start")
	# 	img = cv2.vconcat(imgs)
	# 	# img = np.vstack(imgs)
	# 	logging.debug("vconcat end")
	# 	return img

	def imshow(self, windowName, img):
		logging.debug("imshow start")
		cv2.namedWindow(windowName, cv2.WINDOW_FULLSCREEN)
		cv2.imshow(windowName, img)
		logging.debug("imshow end")

	# def show(self, frames, allimg):	
	# 	logging.debug("show start")
	# 	img = None
	# 	fps1 = 0
	# 	fps2 = 0
	# 	# 押したキーにより、表示を切り替え
	# 	try:
	# 		if (self.Mode == Mode.DISP_1):
	# 			img = frames[0][1]
	# 			fps1 = frames[0][2]
	# 		elif (self.Mode == Mode.DISP_2):
	# 			img = frames[1][1]
	# 			fps1 = frames[1][2]
	# 		elif (self.Mode == Mode.DISP_3):
	# 			img = frames[2][1]
	# 			fps1 = frames[2][2]
	# 		elif (self.Mode == Mode.DISP_4):
	# 			img = frames[3][1]
	# 			fps1 = frames[3][2]
	# 	except IndexError as ie:
	# 		pass

	# 	if img is None:
	# 		img = allimg
		
	# 	fps2 = self.fpsCount.CountFps()
		
	# 	height, width, channels = img.shape[:3]
	# 	white = (255, 255, 255)
	# 	cv2.putText(img, "{:.2f} fps".format(fps1), (  0, height - 35), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
	# 	cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  5), cv2.FONT_HERSHEY_TRIPLEX, 1, white, 3, cv2.LINE_AA)
	# 	black = (0, 0, 0)
	# 	cv2.putText(img, "{:.2f} fps".format(fps1), (  0, height - 35), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)
	# 	cv2.putText(img, "{:.2f} fps".format(fps2), (  0, height -  5), cv2.FONT_HERSHEY_TRIPLEX, 1, black, 1, cv2.LINE_AA)

	# 	self.img = img
	# 	# 高解像度で表示すると描画が遅いことが判明
	# 	self.imshow('frame', img)
	# 	logging.debug("show end")
		
	def save(self, frames):
		for i, writer in enumerate( self.writers ):
			writer.write(frames[i][1]) # 画像を1フレーム分として書き込み

	def endProcess(self):
		for i, capture in enumerate( self.captures ):
			capture.release()

		for i, writer in enumerate( self.writers ):
			writer.release()
		
		cv2.destroyAllWindows()

	def debug(self, mes):
		if self.DEBUG:
			print(mes)
