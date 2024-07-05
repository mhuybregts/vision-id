import os
import shutil
import customtkinter as ck
from PIL import Image
from tkinter import filedialog

from analyzer import Analyzer
from image_analyzer import ImageAnalyzer
from video_analyzer import VideoAnalyzer


class App(ck.CTk):

    filename = None
    analyzer = Analyzer("known_faces", "hog", 0.6)
    image_analyzer = ImageAnalyzer(analyzer)
    video_analyzer = VideoAnalyzer(analyzer)

    def __init__(self):
        super().__init__()

        # Process known faces
        self.analyzer.load_faces()

        # Initialize
        self.title("Vision ID")
        self.after(0, lambda: self.state('zoomed'))
        self.grid_columnconfigure(0, weight=1)
        self.name_dialog = ck.CTkFrame(self)
        self.live_dialog = ck.CTkFrame(self)

        # Display logo by default
        logo = Image.open("photos/vision-id.png")
        self.display = ck.CTkImage(light_image=logo,
                                   size=self.video_analyzer.frame_size)
        self.label = ck.CTkLabel(self, image=self.display, text='')
        self.label.grid(padx=20, pady=20, columnspan=3, sticky="ew")

        # Initialize the buttons
        self.button_frame = ck.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, padx=5, pady=20, columnspan=3,
                               sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.button1 = ck.CTkButton(self.button_frame)
        self.button1.grid(row=0, column=0, padx=5, sticky="ew")
        self.button2 = ck.CTkButton(self.button_frame)
        self.button2.grid(row=0, column=1, padx=5, sticky="ew")
        self.button3 = ck.CTkButton(self.button_frame)
        self.button3.grid(row=0, column=2, padx=5, sticky="ew")
        self.set_btn_defaults()

    def set_btn_defaults(self):
        self.button1.configure(text="Image", command=self.get_image)
        self.button2.configure(text="Video", command=self.get_video)
        self.button3.configure(text="Live", command=self.get_live)
        self.name_dialog.grid_forget()
        self.live_dialog.grid_forget()

    # Image Functions

    def analyze_image(self, filename):
        if filename is not None:
            img = self.image_analyzer.analyze_image(filename)
            self.label.configure(image=ck.CTkImage(img, size=img.size))

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
        self.button1.configure(text="New Image", command=self.get_image)
        self.button2.configure(text="Add Face", command=self.add_face_dialog)
        self.button3.configure(text="Back", command=self.set_btn_defaults)

    def get_image(self):
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select an Image",
            filetypes=[("image files", "*.png *.jpg *.jpeg")]
        )
        if len(filename) > 0:
            self.analyze_image(filename)
            self.set_image_buttons()

    # Video Functions

    def video_add_face(self):
        name = self.name_entry.get()
        dir = f"known_faces/{name}"
        if not os.path.exists(dir):
            os.mkdir(dir)
        i = 0
        while True:
            path = f"{dir}/{name}_{i}.png"
            if not os.path.exists(path):
                self.label.cget("image").cget("light_image").save(path)
                self.analyzer.load_faces()
                break
            i += 1

    def video_add_face_dialog(self):
        self.name_dialog = ck.CTkFrame(self)
        self.name_dialog.grid(row=2, column=0, pady=5)
        self.name_entry = ck.CTkEntry(self.name_dialog, width=200,
                                      placeholder_text="Enter name")
        self.add_button = ck.CTkButton(self.name_dialog, text="Add",
                                       command=self.video_add_face, width=50)
        self.name_entry.grid(row=0, column=0, padx=1)
        self.add_button.grid(row=0, column=1, padx=1)

    def pause(self):
        self.video_analyzer.stop_analyzing()
        self.button2.configure(text="Play", command=self.analyze_video)
        self.live_dialog.grid_forget()
        self.video_add_face_dialog()

    def analyze_video(self):
        self.video_analyzer.start_analyzing(self.label)
        self.button2.configure(text="Pause", command=self.pause)
        self.name_dialog.grid_forget()
        self.live_dialog.grid_forget()

    def preview_video(self, filepath):
        self.filename = filepath
        frame = VideoAnalyzer.get_frame(filepath)
        dimensions = min(frame.size, self.video_analyzer.frame_size)
        self.label.configure(image=ck.CTkImage(frame, size=dimensions))

    def set_video_buttons(self):
        self.button1.configure(text="New Video", command=self.get_video)
        self.button2.configure(text="Play", command=self.analyze_video)
        self.button3.configure(text="Back", command=self.set_btn_defaults)

    def get_video(self):
        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select a Video",
            filetypes=[("video files", "*.mp4 *.mov *.avi")]
        )
        if len(filename) > 0:
            self.set_video_buttons()
            self.preview_video(filename)
            self.video_analyzer.load_video(filename)

    # Live Functions

    def set_live_buttons(self):
        self.button1.configure(text="New Feed", command=self.get_live)
        self.button2.configure(text="Play", command=self.analyze_video)
        self.button3.configure(text="Back", command=self.set_btn_defaults)

    def preview_live(self):
        source = self.menu.get()
        device = self.video_analyzer.load_live(source)
        frame = VideoAnalyzer.get_frame(device)
        dimensions = min(frame.size, self.video_analyzer.frame_size)
        self.label.configure(image=ck.CTkImage(frame, size=dimensions))

    def get_live(self):
        self.set_live_buttons()
        self.live_dialog.grid_forget()
        self.live_dialog = ck.CTkFrame(self)
        self.live_dialog.grid(row=2, column=0, pady=5)
        cams = self.video_analyzer.list_cameras()
        self.menu = ck.CTkComboBox(self.live_dialog, values=cams, width=200)
        self.live_button = ck.CTkButton(self.live_dialog, text="Stream",
                                        command=self.preview_live, width=50)
        self.menu.grid(row=0, column=0, padx=1)
        self.live_button.grid(row=0, column=1, padx=1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
