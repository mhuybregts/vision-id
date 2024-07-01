import cv2
from threading import Thread
from PIL import Image, ImageTk

import customtkinter as ck
from pygrabber.dshow_graph import FilterGraph

from analyzer import Analyzer


class VideoAnalyzer():

    frame_size = (960, 720)
    graph = FilterGraph()

    def __init__(self, analyzer: Analyzer):
        self.analyzer = analyzer
        self.running = False

    def get_frame(video: str | int) -> Image:
        capture = cv2.VideoCapture(video)
        ret, frame = capture.read()
        if ret:
            return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            return None

    def list_cameras(self) -> list[str]:
        return self.graph.get_input_devices()

    def load_video(self, video: str) -> None:
        self.capture = cv2.VideoCapture(video)

    def load_live(self, feed: str) -> None:
        device = self.graph.get_input_devices().index(feed)
        self.capture = cv2.VideoCapture(device)
        return device

    def analyze(self, frame: ck.CTkImage):
        while self.running:
            ret, image = self.capture.read()
            if ret:
                new_image = self.analyzer.analyze_frame(image)
                img = Image.fromarray(cv2.cvtColor(new_image,
                                                   cv2.COLOR_BGR2RGB))
                dimensions = min(img.size, self.frame_size)
                frame.configure(image=ImageTk.PhotoImage(img, size=dimensions))
            else:
                break
        self.running = False

    def start_analyzing(self, frame: ck.CTkImage):
        if not self.running:
            self.thread = Thread(target=self.analyze, args=(frame,))
            self.running = True
            self.thread.start()

    def stop_analyzing(self):
        self.running = False
