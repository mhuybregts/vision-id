import os
import shutil
import customtkinter as ck
from PIL import Image
from tkinter import filedialog
from threading import Thread

from analyzer import Analyzer
from image_analyzer import ImageAnalyzer
from video_analyzer import VideoAnalyzer


class App(ck.CTk):

    def __init__(self):
        super().__init__()

        # Setup the analyzers
        self.analyzer = Analyzer("known_faces", "hog", 0.6)
        self.image_analyzer = ImageAnalyzer(self.analyzer)
        self.video_analyzer = VideoAnalyzer(self.analyzer)

        # Process known faces
        self.analyzer.load_faces()

        # Initialize
        self.title("Vision ID")
        self.after(0, lambda: self.state('zoomed'))
        self.grid_columnconfigure(0, weight=1)

        # Display logo by default
        logo = Image.open("photos/vision-id.png")
        self.display = ck.CTkImage(logo, size=self.video_analyzer.frame_size)
        self.label = ck.CTkLabel(self, image=self.display, text='')
        self.label.grid(padx=20, pady=20, columnspan=3, sticky="ew")

        # Initialize buttons and progress bar
        self.frame = ck.CTkFrame(self, fg_color="transparent")
        self.frame.grid(row=1, padx=5, pady=20, columnspan=3, sticky="ew")
        self.frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.button1 = ck.CTkButton(self.frame)
        self.button2 = ck.CTkButton(self.frame)
        self.button3 = ck.CTkButton(self.frame)

        self.button1.grid(row=0, column=0, padx=5, sticky="ew")
        self.button2.grid(row=0, column=1, padx=5, sticky="ew")
        self.button3.grid(row=0, column=2, padx=5, sticky="ew")

        self.name_dialog = ck.CTkFrame(self)
        self.entry = ck.CTkEntry(self.name_dialog, placeholder_text="Name")
        self.add_button = ck.CTkButton(self.name_dialog, text="Add", width=50)
        self.status = ck.CTkLabel(self, text="", fg_color="transparent")

        self.live_dialog = ck.CTkFrame(self)
        cams = self.video_analyzer.list_cameras()
        self.menu = ck.CTkComboBox(self.live_dialog, values=cams, width=200)
        self.live_button = ck.CTkButton(self.live_dialog, width=60)
        self.progress_bar = ck.CTkProgressBar(self)

        self.set_defaults()

    def hide_extras(self):
        self.name_dialog.grid_forget()
        self.live_dialog.grid_forget()
        self.status.grid_forget()

    def set_defaults(self):
        # Set the buttons to their defaults
        self.button1.configure(text="Image", command=self.get_image)
        self.button2.configure(text="Video", command=self.get_video)
        self.button3.configure(text="Live", command=self.get_live)
        # Make sure the name and live dialogs are not visible
        self.hide_extras()
        self.type = None

    def set_btn_state(self, state: str):
        self.button1.configure(state=state)
        self.button2.configure(state=state)
        self.button3.configure(state=state)
        self.add_button.configure(state=state)
        self.live_button.configure(state=state)

    # Progress bar functions
    def start_progress(self):
        self.progress_bar.grid(row=3, column=0)
        self.progress_bar.start()
        self.set_btn_state("disabled")

    def stop_progress(self):
        self.progress_bar.stop()
        self.progress_bar.grid_forget()
        self.progress_bar.set(0)
        self.set_btn_state("normal")

    def show_status(self, text: str):
        self.status.configure(text=text)
        self.status.grid(row=4, column=0, pady=5)

    # Image functions
    def analyze_image(self, filename):
        if filename is not None:
            img = self.image_analyzer.analyze_image(filename)
            self.label.configure(image=ck.CTkImage(img, size=img.size))

    def add_face(self):
        name = self.entry.get()
        dir = f"known_faces/{name}"
        if not os.path.exists(dir):
            os.mkdir(dir)
        shutil.copy(self.filename, dir)
        self.analyzer.load_faces()
        self.show_status("Face added successfully")

    def add_face_dialog(self):
        self.name_dialog.grid(row=2, column=0, pady=5)
        self.add_button.configure(command=self.add_face)
        self.entry.grid(row=0, column=0, padx=1)
        self.add_button.grid(row=0, column=1, padx=1)

    def set_image_buttons(self):
        self.button1.configure(text="New Image", command=self.get_image)
        self.button2.configure(text="Add Face", command=self.add_face_dialog)
        self.button3.configure(text="Back", command=self.set_defaults)
        self.hide_extras()

    def get_image(self):
        self.filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select an Image",
            filetypes=[("image files", "*.png *.jpg *.jpeg")]
        )
        if len(self.filename) > 0:
            self.analyze_image(self.filename)
            self.set_image_buttons()
            self.type = "image"

    # Video functions
    def video_add_face(self):
        name = self.entry.get()
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
        self.name_dialog.grid(row=2, column=0, pady=5)
        self.add_button.configure(command=self.video_add_face)
        self.entry.grid(row=0, column=0, padx=1)
        self.add_button.grid(row=0, column=1, padx=1)

    def pause(self):
        self.video_analyzer.stop_analyzing()
        self.button2.configure(text="Play", command=self.analyze_video)
        self.button3.configure(state="normal")
        self.live_dialog.grid_forget()
        self.video_add_face_dialog()

    def analyze_video(self):
        self.video_analyzer.start_analyzing(self.label)
        self.button2.configure(text="Pause", command=self.pause)
        self.button3.configure(state="disabled")
        self.name_dialog.grid_forget()
        self.live_dialog.grid_forget()

    def preview_video(self, filepath):
        self.start_progress()
        Thread(target=self._preview_video_step, args=(filepath,)).start()

    def _preview_video_step(self, filepath):
        frame = VideoAnalyzer.get_frame(filepath)
        dimensions = min(frame.size, self.video_analyzer.frame_size)
        self.label.configure(image=ck.CTkImage(frame, size=dimensions))
        self.stop_progress()

    def set_video_buttons(self):
        self.button1.configure(text="New Video", command=self.get_video)
        if self.video_analyzer.running:
            self.button2.configure(text="Pause", command=self.pause)
        else:
            self.button2.configure(text="Play", command=self.analyze_video)
        self.button3.configure(text="Back", command=self.set_defaults)
        self.hide_extras()

    def get_video(self):

        if self.type != "video" and self.video_analyzer.type == "video":
            self.set_video_buttons()
            return

        filename = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            title="Select a Video",
            filetypes=[("video files", "*.mp4 *.mov *.avi")]
        )
        if len(filename) > 0:
            self.video_analyzer.load_video(filename)
            self.preview_video(filename)
            self.set_video_buttons()
            self.type = "video"

    # Live Functions
    def set_live_buttons(self):
        self.button1.configure(text="New Feed", command=self.get_live)
        self.button2.configure(text="Play")
        if self.video_analyzer.type == "live":
            self.button2.configure(state="normal")
            if self.video_analyzer.running:
                self.button2.configure(text="Pause", command=self.pause)
            else:
                self.button2.configure(command=self.analyze_video)
        else:
            self.button2.configure(state="disabled")
        self.button3.configure(text="Back", command=self.set_defaults)
        self.hide_extras()

    def preview_live(self):
        self.start_progress()
        Thread(target=self._preview_live_step).start()

    def _preview_live_step(self):
        source = self.menu.get()
        device = self.video_analyzer.load_live(source)
        frame = VideoAnalyzer.get_frame(device)
        dimensions = min(frame.size, self.video_analyzer.frame_size)
        self.label.configure(image=ck.CTkImage(frame, size=dimensions))
        self.stop_progress()
        self.live_dialog.grid_forget()
        self.set_live_buttons()

    def get_live(self):
        self.set_live_buttons()
        self.live_dialog.grid(row=2, column=0, pady=5)
        cams = self.video_analyzer.list_cameras()
        self.menu.configure(values=cams)
        self.live_button.configure(text="Stream", command=self.preview_live)
        self.menu.grid(row=0, column=0, padx=1)
        self.live_button.grid(row=0, column=1, padx=1)
        self.type = "live"


if __name__ == "__main__":

    if not os.path.exists("known_faces"):
        os.mkdir("known_faces")

    app = App()
    app.mainloop()
