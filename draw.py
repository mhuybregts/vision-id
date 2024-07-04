import cv2


class Draw:
    """
    Draw is a wrapper class for the opencv functions that draw
    rectangles and add text to images
    """
    def __init__(self, frame_thickness, font_thickness):
        self.frame_thickness = frame_thickness
        self.font_thickness = font_thickness

    def draw_rectangle(self, image, top_left: tuple[int],
                       bottom_right: tuple[int], color: tuple[int],
                       filled: bool) -> None:
        """
        Draw a rectangle on top of an image.
        """
        if filled:
            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
        else:
            cv2.rectangle(image, top_left, bottom_right, color,
                          self.frame_thickness)

    def add_text(self, image, text: str, origin: tuple[int],
                 color: tuple[int]) -> None:
        """
        Add text to an image.
        """
        cv2.putText(image, text, origin, cv2.FONT_HERSHEY_COMPLEX, 0.4, color,
                    self.font_thickness)


if __name__ == "__main__":

    FRAME_THICKNESS = 4
    FONT_THICKNESS = 1
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    draw = Draw(FRAME_THICKNESS, FONT_THICKNESS)
    image = cv2.imread("photos/draw_test.jpg")

    # NOTE: tl = Top Left, br = Bottom Right
    padding = FRAME_THICKNESS//2
    tl1, br1 = (250, 250), (500, 500)
    tl2, br2 = (250 - padding, 500), (500 + padding, 500 + 22)
    origin = (250 + 10, 500 + 15)

    # Test draw functions
    draw.draw_rectangle(image, tl1, br1, BLACK, filled=False)
    draw.draw_rectangle(image, tl2, br2, BLACK, filled=True)
    draw.add_text(image, "Press any key", origin, WHITE)

    # Show images
    cv2.imshow("TEST", image)
    cv2.waitKey(0)
    cv2.destroyWindow("TEST")
