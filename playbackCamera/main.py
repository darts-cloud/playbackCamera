import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Player import *
from OpenGLPlayer import *
from MediaPipePlayer_pose import *
from PerfomanceTestPlayer import *	

def main():
	# cam = OpenGLPlayer()
	# cam = MediaPipePlayer() # クッソ遅い
	cam = Player() # クッソ遅い
	# cam = PerfomanceTestPlayer()
	cam.start()

if __name__ == "__main__": 
	main()

# 動画が同期せずに高速化してしまう問題の対処
# FPSの表示を直す
# resultフォルダがなければ作るなど