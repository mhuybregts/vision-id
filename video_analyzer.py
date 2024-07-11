import cv2
from threading import Thread
from PIL import Image

import customtkinter as ck
from pygrabber.dshow_graph import FilterGraph

from analyzer import Analyzer


class VideoAnalyzer():

    frame_size = (960, 720)
    graph = FilterGraph()

    def __init__(self, analyzer: Analyzer):
        self.analyzer = analyzer
        self.running = False
        self.type = None

    def get_frame(video: str | int) -> Image.Image:
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
        self.running = False
        self.type = "video"

    def load_live(self, feed: str) -> None:
        device = self.graph.get_input_devices().index(feed)
        self.capture = cv2.VideoCapture(device)
        self.running = False
        self.type = "live"
        return device

    def _analyze(self, frame: ck.CTkLabel):
        while self.running:
            ret, image = self.capture.read()
            if ret:
                new_image = self.analyzer.analyze_frame(image)
                img = Image.fromarray(cv2.cvtColor(new_image,
                                                   cv2.COLOR_BGR2RGB))
                dimensions = min(img.size, self.frame_size)
                frame.configure(image=ck.CTkImage(img, size=dimensions),
                                require_redraw=True)
            else:
                self.type = None
                break
        self.running = False

    def start_analyzing(self, frame: ck.CTkImage):
        if not self.running:
            self.thread = Thread(target=self._analyze, args=(frame,))
            self.running = True
            self.thread.start()

    def stop_analyzing(self):
        self.running = False
