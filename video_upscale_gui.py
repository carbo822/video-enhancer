import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import json

# You may need to install real-esrgan: pip install realesrgan
# And ensure ffmpeg is installed and in PATH

UPSCALE_FACTOR = 2  # You can change this
MODEL_NAME = "RealESRGAN_x4plus"  # Default model

class VideoUpscaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Video Upscaler (Real-ESRGAN)")
        self.root.geometry("450x250")
        self.file_path = None
        self.realesrgan_path = None
        self.config_file = os.path.join(os.path.dirname(__file__), "realesrgan_config.json")

        self.label = tk.Label(root, text="Select a video to upscale and enhance:")
        self.label.pack(pady=10)

        self.select_btn = tk.Button(root, text="Select Video", command=self.select_video)
        self.select_btn.pack(pady=5)

        self.upscale_btn = tk.Button(root, text="Upscale Video", command=self.upscale_video, state=tk.DISABLED)
        self.upscale_btn.pack(pady=5)

        self.exe_btn = tk.Button(root, text="Set Real-ESRGAN Executable", command=self.set_realesrgan_path)
        self.exe_btn.pack(pady=5)

        self.load_realesrgan_path()

    def set_realesrgan_path(self):
        exe_path = filedialog.askopenfilename(title="Select Real-ESRGAN Executable", filetypes=[("Executable", "*.exe;*.bat;*.cmd;*.sh"), ("All files", "*.*")])
        if exe_path:
            self.realesrgan_path = exe_path
            self.save_realesrgan_path()
            messagebox.showinfo("Executable Set", f"Real-ESRGAN executable set to:\n{exe_path}")

    def save_realesrgan_path(self):
        with open(self.config_file, "w") as f:
            json.dump({"realesrgan_path": self.realesrgan_path}, f)

    def load_realesrgan_path(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.realesrgan_path = data.get("realesrgan_path")
            except Exception:
                self.realesrgan_path = None

    def select_video(self):
        filetypes = [
            ("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.webm"),
            ("All files", "*.*")
        ]
        path = filedialog.askopenfilename(title="Select Video", filetypes=filetypes)
        if path:
            self.file_path = path
            self.label.config(text=f"Selected: {os.path.basename(path)}")
            self.upscale_btn.config(state=tk.NORMAL)

    def upscale_video(self):
        if not self.file_path:
            messagebox.showerror("Error", "No video selected.")
            return
        input_path = self.file_path
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_upscaled{ext}"
        temp_frames = f"{base}_frames"
        upscaled_frames = f"{base}_frames_upscaled"
        os.makedirs(temp_frames, exist_ok=True)
        os.makedirs(upscaled_frames, exist_ok=True)

        # 1. Extract frames
        extract_cmd = [
            "ffmpeg", "-i", input_path,
            os.path.join(temp_frames, "frame_%06d.png")
        ]
        try:
            subprocess.run(extract_cmd, check=True)
        except Exception as e:
            messagebox.showerror("FFmpeg Error (Extract)", str(e))
            return

        # 2. Upscale frames with Real-ESRGAN CLI
        if not self.realesrgan_path or not os.path.exists(self.realesrgan_path):
            messagebox.showerror("Executable Not Set", "Please set the Real-ESRGAN executable using the button below.")
            return
        try:
            import glob
            frame_files = sorted(glob.glob(os.path.join(temp_frames, "frame_*.png")))
            for frame in frame_files:
                output_frame = os.path.join(upscaled_frames, os.path.basename(frame))
                cmd = [
                    self.realesrgan_path,
                    "-i", frame,
                    "-o", output_frame,
                    "-n", "realesrgan-x4plus",
                    "-s", str(UPSCALE_FACTOR)
                ]
                subprocess.run(cmd, check=True)
        except Exception as e:
            messagebox.showerror("Real-ESRGAN Error", str(e))
            return

        # 3. Recombine frames into video
        combine_cmd = [
            "ffmpeg", "-framerate", "30", "-i",
            os.path.join(upscaled_frames, "frame_%06d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path
        ]
        try:
            subprocess.run(combine_cmd, check=True)
            messagebox.showinfo("Success", f"Upscaled video saved as:\n{output_path}")
        except Exception as e:
            messagebox.showerror("FFmpeg Error (Combine)", str(e))
            return

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoUpscaleApp(root)
    root.mainloop()
