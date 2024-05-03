from capture.VideoCapture import ThreadingVideoCapture
import numpy as np
import time
import cv2

class DummyCapture(ThreadingVideoCapture):
    def __init__(self, src, max_queue_size=256):
        super().__init__(src, max_queue_size)
        self.video = None  # ネットワークカメラではなく、黒い画像を生成するためには不要

    def update(self):
        while True:
            try:
                if self.stopped:
                    time.sleep(10)
                    self.stopped = False
                    continue

                # 黒い画像を生成
                img = np.zeros((480, 640, 3), dtype=np.uint8)
                times = time.time()
                fps = self.fpsCount.CountFps()
                self.q.put([times, img, fps])

            except Exception as e:
                print(e)
                print("通信エラーが発生")

    def isOpened(self):
        return True  # 常に開いているとする

    def get(self, i):
        if i == cv2.CAP_PROP_FRAME_WIDTH:
            return 640  # 画像の幅
        elif i == cv2.CAP_PROP_FRAME_HEIGHT:
            return 480  # 画像の高さ
        else:
            return None  # その他のプロパティは未定義