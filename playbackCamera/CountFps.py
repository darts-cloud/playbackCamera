import time
import logging

class CountFps:

    CONST_BASE_SEC = 10

    def __init__(self):
        self.startTime = time.time()
        self.frame = 0
        self.fps = 0

    def CountFrame(self):
        self.frame += 1
        if self.fps <= 0:
            return
        if self.frame / self.fps > self.CONST_BASE_SEC:
            self.startTime = time.time()
            self.frame = 0

    def CountFps(self):

        # Time elapsed
        sec = time.time() - self.startTime
        if sec == 0:
            return 0
        
        # Calculate frames per second
        self.fps = self.frame / sec

        return self.fps

