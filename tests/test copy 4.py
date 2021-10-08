#! /usr/bin/python3

import cv2, threading, time

class Measure():
  def __init__(self, regular):
    self._regular = regular
    self._number = 1
    self._start = time.time()

  def elapsed(self):
    return (time.time() - self._start)

  def difference(self):
    diff = (self._regular * self._number) - self.elapsed()
    return diff if diff > 0 else 0

  def fps(self):
    return self._number / self.elapsed()

  def next(self):
    self._number += 1

class VideoThread():
  def __init__(self, index, name):
    self._index = index
    self._camera = cv2.VideoCapture(index)
    self._name = name
    
    number = 0
    while number != 10: # Wait for the transfer to stabilize.
      if self._camera.grab():
        number += 1
      
    self._alive = True
    self._thread = threading.Thread(target=self.grabber)
    self._thread.daemon = True
    self._thread.start()

  def name(self):
    return self._name + "[" + str(self._index) + "]"

  def grabber(self):
    measure = Measure(regular=1/120)
    while self._alive and self._camera.grab():
      #time.sleep(measure.difference())
      print("fps(" + self.name() + ") {0:.3f}".format(measure.fps()))
      measure.next()

  def retrieve(self):
    _, frame = self._camera.retrieve()
    return frame

  def close(self):
    self._alive = False
    self._thread.join()
    self._camera.release()

def main():
  video_thread_0 = VideoThread("rtsp://192.168.1.109", "camera")
#   video_thread_1 = VideoThread(1, "camera")
  
  # Wait for the window to stabilize.
  cv2.imshow(video_thread_0.name(), video_thread_0.retrieve())
#   cv2.imshow(video_thread_1.name(), video_thread_1.retrieve())
  cv2.waitKey(1)

  measure = Measure(regular=1/120)
  while chr(cv2.waitKey(1) & 255) != 'q':
    frame = video_thread_0.retrieve()
    if frame is not None:
        cv2.imshow(video_thread_0.name(), frame)
    # cv2.imshow(video_thread_1.name(), video_thread_1.retrieve())
    time.sleep(measure.difference())
    print("fps(draw) {0:.3f}".format(measure.fps()))
    measure.next()

  video_thread_0.close()
#   video_thread_1.close()
    
if __name__ == "__main__":
  main()