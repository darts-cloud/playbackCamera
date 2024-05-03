import unittest
from playbackCamera.capture.VideoCapture import ThreadingVideoCapture, ThreadingVideoCapture2, ThreadingVideoCaptureForPyAv

class TestVideoCapture(unittest.TestCase):

    def test_threading_video_capture(self):
        video_capture = ThreadingVideoCapture(0)
        self.assertTrue(video_capture.isOpened())
        video_capture.release()

    def test_threading_video_capture2(self):
        video_capture2 = ThreadingVideoCapture2(0, 30)
        self.assertTrue(video_capture2.isOpened())
        video_capture2.release()

    def test_threading_video_capture_for_pyav(self):
        video_capture_for_pyav = ThreadingVideoCaptureForPyAv(0)
        self.assertTrue(video_capture_for_pyav.isOpened())
        video_capture_for_pyav.release()

if __name__ == '__main__':
    unittest.main()