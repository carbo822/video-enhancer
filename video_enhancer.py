import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageEnhance
import os

class VideoEnhancerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Enhancer")
        self.root.geometry("800x700")
        screen_width = 800
        self.screen_height = 700
        self.file_path = None

        # Tkinter variables (after root is set)
        self.progress = tk.DoubleVar(value=0)
        self.brightness = tk.DoubleVar(value=1.2)
        self.contrast = tk.DoubleVar(value=1.2)
        self.sharpness = tk.DoubleVar(value=1.0)
        self.upscale = tk.StringVar(value="1x")

        # Set pale blue background
        self.canvas = tk.Canvas(self.root, width=screen_width, height=self.screen_height, bg="#e0f7fa")
        self.canvas.pack(fill="both", expand=True)

        # Place widgets on canvas
        center_x = screen_width // 2
        self.num_label = tk.Label(self.root, text="Select a video to enhance:", bg="#ffffff", font=("Arial", 12, "bold"))
        self.file_label = tk.Label(self.root, text="No video selected", bg="#ffffff", font=("Arial", 11))
        self.select_btn = tk.Button(self.root, text="Select Video", command=self.select_video)
        self.brightness_label = tk.Label(self.root, text="Brightness (1.0 = original)", bg="#ffffff")
        self.brightness_entry = tk.Entry(self.root, textvariable=self.brightness)
        self.contrast_label = tk.Label(self.root, text="Contrast (1.0 = original)", bg="#ffffff")
        self.contrast_entry = tk.Entry(self.root, textvariable=self.contrast)
        self.sharpness_label = tk.Label(self.root, text="Sharpness (1.0 = original)", bg="#ffffff")
        self.sharpness_entry = tk.Entry(self.root, textvariable=self.sharpness)
        self.upscale_label = tk.Label(self.root, text="Upscale", bg="#ffffff")
        upscale_menu = tk.OptionMenu(self.root, self.upscale, "1x", "2x", "4x")
        self.enhance_btn = tk.Button(self.root, text="Enhance Video", command=self.enhance_video)
        self.quit_btn = tk.Button(self.root, text="Quit", command=self.root.quit, bg="#ff4444", font=("Arial", 12, "bold"))
        self.progress_bar = tk.Scale(self.root, variable=self.progress, from_=0, to=100, orient="horizontal", length=300, showvalue=0, state="disabled")

        self.canvas.create_window(center_x, 40, window=self.num_label)
        self.canvas.create_window(center_x, 70, window=self.file_label)
        self.canvas.create_window(center_x, 100, window=self.select_btn)
        self.canvas.create_window(center_x, 140, window=self.brightness_label)
        self.canvas.create_window(center_x, 170, window=self.brightness_entry)
        self.canvas.create_window(center_x, 210, window=self.contrast_label)
        self.canvas.create_window(center_x, 240, window=self.contrast_entry)
        self.canvas.create_window(center_x, 280, window=self.sharpness_label)
        self.canvas.create_window(center_x, 310, window=self.sharpness_entry)
        self.canvas.create_window(center_x, 350, window=self.upscale_label)
        self.canvas.create_window(center_x, 380, window=upscale_menu)
        self.canvas.create_window(center_x, 430, window=self.enhance_btn)
        self.canvas.create_window(center_x, self.screen_height - 120, window=self.progress_bar)
        self.canvas.create_window(center_x, self.screen_height - 60, window=self.quit_btn)
    def update_progress(self, value):
        self.progress.set(value)
        self.root.update_idletasks()

    def enhance_video(self):
        import numpy as np
        if not self.file_path:
            messagebox.showerror("Error", "No video selected.")
            return
        brightness = self.brightness.get()
        contrast = self.contrast.get()
        sharpness = self.sharpness.get()
        upscale_str = self.upscale.get()
        upscale = 1.0
        if upscale_str == "2x":
            upscale = 2.0
        elif upscale_str == "4x":
            upscale = 4.0
        input_path = self.file_path
        base, ext = os.path.splitext(input_path)
        # Ask user for save location and name
        output_path = filedialog.asksaveasfilename(
            title="Save Enhanced Video As",
            defaultextension=ext,
            filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv"), ("All files", "*.*")],
            initialfile=f"{os.path.basename(base)}_enhanced{ext}"
        )
        if not output_path:
            return

        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_width = int(width * upscale)
        out_height = int(height * upscale)
        out = cv2.VideoWriter(output_path, fourcc, fps, (out_width, out_height))

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        processed = 0
        self.progress_bar.config(state="normal")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Convert to PIL for enhancement
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img = ImageEnhance.Brightness(img).enhance(brightness)
            img = ImageEnhance.Contrast(img).enhance(contrast)
            img = ImageEnhance.Sharpness(img).enhance(sharpness)
            # Upscale if needed
            if upscale != 1.0:
                img = img.resize((out_width, out_height), Image.LANCZOS)
            # Convert back to OpenCV
            frame_enhanced = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame_enhanced)
            processed += 1
            percent = int((processed / frame_count) * 100) if frame_count else 0
            self.update_progress(percent)
        cap.release()
        out.release()
        self.progress_bar.config(state="disabled")
        self.update_progress(0)
        messagebox.showinfo("Done", f"Enhanced video saved as:\n{output_path}")

    def select_video(self):
        path = filedialog.askopenfilename(title="Select Video", filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv"), ("All files", "*.*")])
        if path:
            self.file_path = path
            filename = os.path.basename(path)
            self.file_label.config(text=f"Selected: {filename}")

# Main block
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEnhancerApp(root)
    root.mainloop()
