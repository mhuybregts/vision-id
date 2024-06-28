import os
import face_recognition as fr
import cv2

from draw import Draw

FRAME_THICKNESS = 4
FONT_THICKNESS = 1
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [0, 255, 0]


class Analyzer:

    def __init__(self, known_faces_dir, model, tolerance):
        self.known_faces_dir = known_faces_dir
        self.model = model
        self.tolerance = tolerance
        self.known_faces = []
        self.known_names = []
        self.draw = Draw(FRAME_THICKNESS, FONT_THICKNESS)

    def load_faces(self):
        for name in os.listdir(self.known_faces_dir):
            for filename in os.listdir(f"{self.known_faces_dir}/{name}"):
                path = f"{self.known_faces_dir}/{name}/{filename}"
                image = fr.load_image_file(path)
                encdoding = fr.face_encodings(image)[0]
                self.known_faces.append(encdoding)
                self.known_names.append(name)

    def analyze_frame(self, image):

        locations = fr.face_locations(image, model=self.model)
        encodings = fr.face_encodings(image, locations)

        for face_encoding, face_location in zip(encodings, locations):
            results = fr.compare_faces(self.known_faces, face_encoding,
                                       self.tolerance)
            match = None
            if True in results:
                match = self.known_names[results.index(True)]

                # NOTE: tl = Top Left, br = Bottom Right
                tl = (face_location[3], face_location[0])
                br = (face_location[1], face_location[2])
                self.draw.draw_rectangle(image, tl, br, RED, filled=False)

                padding = FRAME_THICKNESS // 2
                tl = (face_location[3] - padding, face_location[2])
                br = (face_location[1] + padding, face_location[2] + 22)
                self.draw.draw_rectangle(image, tl, br, RED, filled=True)

                org = (face_location[3] + 5, face_location[2] + 15)
                self.draw.add_text(image, match, org, WHITE)

        return image


if __name__ == "__main__":

    KNOWN_FACES_DIR = "known_faces"
    MODEL = "hog"  # cnn
    TOLERANCE = 0.6  # Default value is 0.6

    analyzer = Analyzer(KNOWN_FACES_DIR, MODEL, TOLERANCE)
    analyzer.load_faces()

    for filename in os.listdir("unknown_faces"):

        image = fr.load_image_file(f"unknown_faces/{filename}")
        image = analyzer.analyze_frame(image)
        image = Draw.to_bgr(image)

        cv2.imshow(filename, image)
        cv2.waitKey(0)
        cv2.destroyWindow(filename)
