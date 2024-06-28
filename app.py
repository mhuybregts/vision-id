import os
import shutil
import customtkinter as ck
from PIL import Image
from tkinter import filedialog

from analyzer import Analyzer
from image_analyzer import ImageAnalyzer


class App(ck.CTk):

    frame_size = (960, 720)
    filename = None
    analyzer = Analyzer("known_faces", "hog", 0.6)
    image_analyzer = ImageAnalyzer(analyzer)

    def __init__(self):
        super().__init__()

        print("Processing known faces...")
        self.analyzer.load_faces()

        # Initialize
        self.title("Vision ID")
        self.grid_columnconfigure(0, weight=1)

        # Display logo by default
        logo = Image.open("photos/vision-id.png")
        self.display = ck.CTkImage(light_image=logo, size=self.frame_size)
        self.label = ck.CTkLabel(self, image=self.display, text='')
        self.label.grid(padx=20, pady=20, columnspan=3, sticky="ew")

        self.button_frame = ck.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=5, pady=20, columnspan=3,
                               sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Button 1: Default is image select
        self.button1 = ck.CTkButton(self.button_frame, text="Image",
                                    command=self.get_image)
        self.button1.grid(row=0, column=0, padx=5, sticky="ew")

        # Button 2: Default is video select
        self.button2 = ck.CTkButton(self.button_frame, text="Video",
                                    command=self.get_video)
        self.button2.grid(row=0, column=1, padx=5, sticky="ew")

        # Button 3: Default is live select
        self.button3 = ck.CTkButton(self.button_frame, text="Live",
                                    command=self.get_live)
        self.button3.grid(row=0, column=2, padx=5, sticky="ew")

    def analyze_image(self):
        if self.filename is not None:
            img = self.image_analyzer.analyze_image(self.filename)
            self.display.configure(light_image=img)

    def add_face(self):
        name = self.name_entry.get()
        dir = f"known_faces/{name}"
        if not os.path.exists(dir):
            os.mkdir(dir)
        shutil.copy(self.filename, dir)
        self.analyzer.load_faces()

    def add_face_dialog(self):
        self.name_dialog = ck.CTkFrame(self)
        self.name_dialog.grid(row=2, column=0, pady=5)
        self.name_entry = ck.CTkEntry(self.name_dialog, width=200,
                                      placeholder_text="Enter name")
        self.add_button = ck.CTkButton(self.name_dialog, text="Add",
                                       command=self.add_face, width=50)
        self.name_entry.grid(row=0, column=0, padx=1)
        self.add_button.grid(row=0, column=1, padx=1)

    def set_image_buttons(self):
        self.button1.configure(text="New Image")
        self.button2.configure(text="Analyze", command=self.analyze_image)
        self.button3.configure(text="Add Face", command=self.add_face_dialog)

    def set_preview(self, filepath):
        self.filename = filepath
        img = Image.open(filepath)
        self.display.configure(light_image=img, size=img.size)

    def get_image(self):
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select an Image",
            filetypes=[("image files", "*.png *.jpg *.jpeg")]
        )
        if len(filename) > 0:
            self.set_preview(filename)
            self.set_image_buttons()

    def get_video(self):
        print("Video Button Pressed")

    def get_live(self):
        print("Live button pressed")


if __name__ == "__main__":
    app = App()
    app.mainloop()
