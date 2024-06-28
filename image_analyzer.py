import os
import time
import face_recognition as fr
from PIL import Image

from analyzer import Analyzer


class ImageAnalyzer():

    def __init__(self, analyzer: Analyzer):
        self.analyzer = analyzer

    def analyze_image(self, image: str):

        img = fr.load_image_file(image)
        return Image.fromarray(self.analyzer.analyze_frame(img))


if __name__ == "__main__":

    KNOWN_FACES_DIR = "known_faces"
    MODEL = "hog"  # cnn
    TOLERANCE = 0.6  # Default value is 0.6

    analyzer = Analyzer(KNOWN_FACES_DIR, MODEL, TOLERANCE)
    analyzer.load_faces()

    image_analyzer = ImageAnalyzer(analyzer)

    for filename in os.listdir("unknown_faces"):
        image_path = f"unknown_faces/{filename}"
        image = image_analyzer.analyze_image(image_path)
        image.show()
        time.sleep(2)
