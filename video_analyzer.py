import cv2
from threading import Thread
import customtkinter as ck
from PIL import Image

from analyzer import Analyzer


class VideoAnalyzer():

    def __init__(self, analyzer: Analyzer):
        self.analyzer = analyzer
        self.running = False

    def get_frame(self, video: str):
        capture = cv2.VideoCapture(video)
        ret, frame = capture.read()
        if ret:
            return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            return None

    def load_video(self, video: str):
        self.capture = cv2.VideoCapture(video)

    def analyze(self, frame: ck.CTkImage):
        while self.running:
            ret, image = self.capture.read()
            if ret:
                new_image = self.analyzer.analyze_frame(image)
                img = Image.fromarray(cv2.cvtColor(new_image,
                                                   cv2.COLOR_BGR2RGB))
                frame.configure(light_image=img)
            else:
                break
        self.running = False

    def start_analyzing(self, frame):
        if not self.running:
            self.thread = Thread(target=self.analyze, args=(frame,))
            self.running = True
            self.thread.start()

    def stop_analyzing(self):
        self.running = False
