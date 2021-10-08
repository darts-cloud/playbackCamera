import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from TestVideo import CameraV3_2Test

def main():
	cam = CameraV3_2Test()
	cam.start()

if __name__ == "__main__":
	main()
