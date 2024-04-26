import tkinter

from PIL import Image, ImageTk
from tkinter import ttk, filedialog, messagebox
import threading
import cv2

class GIFMaker(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title("GIF Maker")
        self.geometry("820x900")

        self.video_path = ''
        self.output_path = ''
        self.frames = []
        self.preview_frame_index = 0

        self.select_video_button = tkinter.Button(self, text='Select video', command=self.select_video)
        self.select_video_button.pack(pady=10)

        self.preview_label = tkinter.Label(self, text='Video preview')
        self.preview_label.pack(pady=10)

        self.canvas = tkinter.Canvas(self, width=640, height=480, background="#000000")
        self.canvas.pack(pady=10)

        self.speed_label = tkinter.Label(self, text='Speed(fps): ')
        self.speed_label.pack(pady=10)

        self.speed_entry = tkinter.Entry(self)
        self.speed_entry.pack()
        self.speed_entry.insert(0, '10')

        self.scale_label = tkinter.Label(self, text='Scale(1.0 = 100%): ')
        self.scale_label.pack(pady=10)

        self.scale_entry = tkinter.Entry(self)
        self.scale_entry.pack()
        self.scale_entry.insert(0, '0.9')

        self.export_button = tkinter.Button(self, text='Export GIF', command=self.export_gif)
        self.export_button.pack(pady=20)

        self.progress = ttk.Progressbar(self, orient=tkinter.HORIZONTAL, length=110, mode='indeterminate')
        self.progress.pack(pady=20)

    def select_video(self):
        self.video_path = filedialog.askopenfile(title='Select video', filetypes=(("MP4 Files", "*.mp4"), ("All Files", "*.*")))
        if self.video_path:
            video_file_path = self.video_path.name
            self.process_video(video_file_path)

    def process_video(self, video_file_path):
        if not self.video_path:
            return

        print(self.video_path)
        cv = cv2.VideoCapture(video_file_path)
        self.frames = []

        while True:
            ret, frame = cv.read()

            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.frames.append(frame)

        cv.release()

        self.preview_frame_index = 0
        self.animate_preview()

    def animate_preview(self):
        if not self.frames:
            return

        frame = self.frames[self.preview_frame_index]
        frame_image = Image.fromarray(frame)
        frame_image = frame_image.resize((640, 480), Image.BICUBIC)
        frame_photo = ImageTk.PhotoImage(frame_image)

        self.canvas.create_image(0, 0, anchor=tkinter.NW, image=frame_photo)
        self.canvas.image = frame_photo
        self.preview_frame_index = (self.preview_frame_index + 1) % len(self.frames)
        self.after(100, self.animate_preview)

    def export_gif(self):
        fps = int(self.speed_entry.get())
        scale = float(self.scale_entry.get())

        if not self.frames or fps <= 0 or scale <=0:
            messagebox.showerror("Error", "Invalid options")
            return

        self.output_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=(("GIF Files", "*.gif"), ("All Files", "*.*")))

        if not self.output_path:
            return
        self.progress.start(10)
        threading.Thread(target=self.create_gif, args=(fps, scale), daemon=True).start()

    def create_gif(self, fps, scale):
        output_frames = []

        for frame in self.frames:
            print(frame)
            img = Image.fromarray(frame)
            img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
            output_frames.append(img)

        output_frames[0].save(self.output_path, save_all=True, append_images=output_frames[1:], optimize=False, duration=1000//fps, loop=0)
        self.after(0, self.progress.stop)
        messagebox.showinfo("Success", "GIF Successfully Exported!")





if __name__ == '__main__':
    app = GIFMaker()
    app.mainloop()