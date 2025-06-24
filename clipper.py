import yt_dlp
from moviepy.editor import VideoFileClip
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog


def download_video(url, resolution="720p"):
    ydl_opts = {
        "format": f"bestvideo[height<={resolution[:-1]}]+bestaudio/best[height<={resolution[:-1]}]",
        "outtmpl": "temp_video.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = ydl.prepare_filename(info)
    return downloaded_file, info.get("title", "output")


def save_video(video_clip, output_name):
    downloads_path = Path.home() / "Downloads"
    output_path = downloads_path / f"{output_name}.mp4"
    video_clip.write_videofile(str(output_path), audio=True, audio_codec="aac")
    return output_path


def process_download():
    url = url_entry.get().strip()
    start_time = start_entry.get().strip()
    end_time = end_entry.get().strip()
    should_trim = trim_var.get()

    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return

    try:
        downloaded_file, title = download_video(url)
        video = VideoFileClip(downloaded_file)

        if should_trim:
            if not start_time or not end_time:
                messagebox.showerror("Error", "Enter start and end times for trimming.")
                return
            start = convert_to_seconds(start_time)
            end = convert_to_seconds(end_time)
            if start >= end or end > video.duration:
                messagebox.showerror("Error", "Invalid trim times.")
                return
            video = video.subclip(start, end)
            output_name = f"{title}_trimmed"
        else:
            output_name = title

        output_path = save_video(video, output_name)
        video.close()
        os.remove(downloaded_file)

        messagebox.showinfo("Success", f"Video saved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {e}")


def convert_to_seconds(time_str):
    parts = list(map(int, time_str.split(":")))
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    else:
        raise ValueError("Invalid time format")


# --- GUI ---
root = tk.Tk()
root.title("YouTube Downloader & Trimmer")

tk.Label(root, text="YouTube URL:").grid(row=0, column=0, sticky="e")
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=5)

trim_var = tk.BooleanVar()
tk.Checkbutton(root, text="Trim video?", variable=trim_var).grid(
    row=1, column=1, sticky="w", pady=5
)

tk.Label(root, text="Start time (mm:ss):").grid(row=2, column=0, sticky="e")
start_entry = tk.Entry(root, width=15)
start_entry.grid(row=2, column=1, sticky="w")

tk.Label(root, text="End time (mm:ss):").grid(row=3, column=0, sticky="e")
end_entry = tk.Entry(root, width=15)
end_entry.grid(row=3, column=1, sticky="w")

download_btn = tk.Button(root, text="Download", command=process_download)
download_btn.grid(row=4, column=1, pady=10)

root.mainloop()
