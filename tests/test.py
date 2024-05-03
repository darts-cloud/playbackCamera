import cv2
from playbackCamera.util.CountFps import *

#カメラの設定　デバイスIDは0
cap = cv2.VideoCapture("rtsp://192.168.1.111")
fpsCount = CountFps()

#繰り返しのためのwhile文
while True:
    #カメラからの画像取得
    ret, frame = cap.read()

    if not ret:
         continue
    
    fpsCount.CountFrame()
	#カメラの画像の出力
    cv2.imshow('camera' , frame)
    fps = fpsCount.CountFps()
    print(fps)

    #繰り返し分から抜けるためのif文
    key =cv2.waitKey(1)
    if key == 27:
        break

#メモリを解放して終了するためのコマンド
cap.release()
cv2.destroyAllWindows()
