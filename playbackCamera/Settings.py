from screeninfo import get_monitors
import configparser

'''

'''
class Settings():
	VIDEO_WIDTH = 640
	VIDEO_HEIGHT = 480
	INI_SECTION = "DEFAULT"
	INI_CAMERA = "camera"
	INI_DELAY_TIME = "delay_time"
	INI_ADJUSTMENT_TIME = "adjustment_time"
	INI_FPS = "fps"
	INI_SYNCED_DIFF_TIME = "synced_diff_time"
	INI_SYNCED_MAX_COUNT = "synced_max_count"
	INI_SIZE_W = "size_w"
	INI_SIZE_H = "size_h"
	INI_GRID_LINE = "grid_line"
	INI_SAVE_MOVIE = "save_movie"
	
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read("settings.ini")

		self._loadIniFile()
		self.dispSizeH = None
		self.dispSizeW = None
		for m in get_monitors():
			self.dispSizeH = m.height
			self.dispSizeW = m.width
			print(str(m))
			break
		
		if self.dispSizeH is None:
			self.dispSizeH = self.sizeH
			self.dispSizeW = self.sizeW

	def _loadIniFile(self):
		self.delayTime = float(self.config.get(self.INI_SECTION, self.INI_DELAY_TIME))
		self.adjutTime = float(self.config.get(self.INI_SECTION, self.INI_ADJUSTMENT_TIME))
		self.fps = int(self.config.get(self.INI_SECTION, self.INI_FPS))
		self.syncedDiffTime = float(self.config.get(self.INI_SECTION, self.INI_SYNCED_DIFF_TIME))
		self.syncedMaxCount = int(self.config.get(self.INI_SECTION, self.INI_SYNCED_MAX_COUNT))
		self.srcs = self.config.get(self.INI_SECTION, self.INI_CAMERA)
		self.sizeW = int(self.config.get(self.INI_SECTION, self.INI_SIZE_W))
		self.sizeH = int(self.config.get(self.INI_SECTION, self.INI_SIZE_H))
		if int(self.config.get(self.INI_SECTION, self.INI_GRID_LINE)) == 1:
			self.glidLineFlg = True
		self.saveMovie = False
		if int(self.config.get(self.INI_SECTION, self.INI_SAVE_MOVIE)) == 1:
			self.saveMovie = True