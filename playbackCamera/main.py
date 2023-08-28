import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Player import *
from OpenGLPlayer import *

def main():
	#cam = OpenGLPlayer()
	cam = Player() # クッソ遅い
	cam.start()

if __name__ == "__main__": 
	main()

# 動画が同期せずに高速化してしまう問題の対処
# FPSの表示を直す
# resultフォルダがなければ作るなど