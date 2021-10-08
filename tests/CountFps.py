import cv2
import time

# カメラを起動する
video = cv2.VideoCapture("rtsp://192.168.1.113")
# video = cv2.VideoCapture("rtsp://192.168.1.113")

fps = video.get(cv2.CAP_PROP_FPS)
print("FPSの設定値、video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

# 取得するフレームの数
num_frames = 120

print("取得中 {0} frames".format(num_frames))

# 開始時間
start = time.time()

# フレームを取得する
for i in range(0, num_frames):
    ret, frame = video.read()

# 終了時間
end = time.time()

# Time elapsed
seconds = end - start
print("経過時間: {0} seconds".format(seconds))

# Calculate frames per second
fps = num_frames / seconds
print("計算したFPS : {0}".format(fps))

# Release video
video.release()
