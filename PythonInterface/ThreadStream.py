# class ThreadStream
# this will open a cv2 steam in a thread when initialized
# it will have a function to grab a frame from the stream
# make it have a ThreadStream.read() like cv2.VideoCapture.read()

import cv2
import threading

class ThreadStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.start()  # Start the thread automatically

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()  # Making the thread a daemon thread
        return self

    def update(self):
        while True:
            if self.stopped:
                break
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.grabbed, self.frame  # Return both status and frame for consistency with cv2.VideoCapture.read()

    def stop(self):
        self.stopped = True

    def __del__(self):
        self.stop()
        self.stream.release()  # Ensure resources are released properly
