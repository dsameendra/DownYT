import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import threading

def fetch_available_qualities():
    url = url_entry.get().strip()

    if not url:
        messagebox.showerror("Error", "Please enter a valid YouTube URL")
        return

    update_status("Fetching available qualities...")

    def fetch_thread():
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Extract video formats (exclude None values)
                video_qualities = sorted(
                    {f"{fmt['height']}p" for fmt in info['formats'] if fmt.get('height')},
                    key=lambda x: int(x.replace('p', '')) if x.replace('p', '').isdigit() else 0
                )
                video_qualities.append("best")

                # Extract audio bitrates safely
                audio_bitrates = sorted(
                    {int(fmt['abr']) for fmt in info['formats'] if 'abr' in fmt and fmt['abr'] is not None},
                    key=int
                )

                root.after(0, lambda: update_format_options(video_qualities, audio_bitrates))
                update_status("Qualities fetched successfully.")
        except Exception as e:
            update_status(f"Failed to fetch qualities: {e}")

    threading.Thread(target=fetch_thread, daemon=True).start()

# Function to update available format options
def update_format_options(video_qualities, audio_bitrates):
    if video_qualities:
        resolution_menu["values"] = video_qualities
        resolution_var.set(video_qualities[-1])  # Set to highest available resolution

    if audio_bitrates:
        bitrate_menu["values"] = [str(int(b)) for b in audio_bitrates]  # Convert float to int
        bitrate_var.set(str(int(audio_bitrates[-1])))  # Set to highest available bitrate

# Function to download video
def download_video():
    thread = threading.Thread(target=download_video_thread, daemon=True)
    thread.start()

# Function to handle video download
def download_video_thread():
    url = url_entry.get().strip()
    resolution = resolution_var.get()
    format_type = format_var.get()
    file_format = format_options_var.get()
    bitrate = bitrate_var.get()
    download_path = download_path_entry.get().strip()
    print(url, resolution, format_type, file_format, bitrate, download_path)

    if not url:
        update_status("Error: Please enter a valid URL")
        return

    if not download_path:
        download_path = os.path.expanduser('~/Downloads')

    if not os.path.exists(download_path):
        update_status("Error: Invalid download path")
        return

    download_button.config(state=tk.DISABLED)

    filename_template = "%(title)s_%(format)s.%(ext)s"
    options = {
        'outtmpl': os.path.join(download_path, filename_template),
        'progress_hooks': [progress_hook],
    }

    if format_type == "Video":
        options['format'] = f'bestvideo[height<={resolution}]+bestaudio/best' if format_type == "Video" else f'bestaudio[abr<={bitrate}]'        
        options['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': file_format}]
        options['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': file_format,
            'preferredquality': bitrate,
        })
    else:
        options['format'] = f'bestaudio[abr<={bitrate}]'
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': file_format,
            'preferredquality': bitrate,
        }]

    update_status("Downloading...")

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        update_status("Download Completed!")
    except Exception as e:
        update_status(f"Download Failed: {e}")

    download_button.config(state=tk.NORMAL)

# Function to safely update the UI from another thread
def update_status(message):
    root.after(0, lambda: status_label.config(text=message))

# Open file dialog to choose download folder
def browse_folder():
    folder_selected = filedialog.askdirectory(initialdir=os.path.expanduser('~/Downloads'))
    if folder_selected:
        download_path_entry.delete(0, tk.END)
        download_path_entry.insert(0, folder_selected)

def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes', d.get('total_bytes_estimate', 1))
        percent = (downloaded / total) * 100 if total else 0
        root.after(0, lambda: progress_bar.config(value=percent))
        root.after(0, lambda: update_status(f"Downloading... {percent:.2f}%"))

    elif d['status'] == 'finished':
        root.after(0, lambda: progress_bar.config(value=100))
        root.after(0, lambda: update_status("Download Completed!"))

# GUI setup
root = tk.Tk()
root.title("DownYT")
root.geometry("500x650")

# URL input
tk.Label(root, text="Enter YouTube Video URL:").pack(padx=20, pady=(20, 5), anchor="w")
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5, padx=20)

# Fetch qualities button
fetch_button = tk.Button(root, text="Check Available Qualities", command=fetch_available_qualities)
fetch_button.pack(pady=10)

# Frame for inputs
input_frame = tk.Frame(root)
input_frame.pack(padx=20, fill=tk.X)

# Left and right columns
left_column = tk.Frame(input_frame)
right_column = tk.Frame(input_frame)
left_column.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
right_column.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))

# Format selection
tk.Label(left_column, text="Select Format:").pack(anchor="w")
format_var = tk.StringVar(value="Video")
format_menu = ttk.Combobox(left_column, textvariable=format_var, values=["Video", "Audio"], state="readonly", width=18)
format_menu.pack(pady=5)
format_menu.current(0)

# File format selection
tk.Label(right_column, text="Select File Format:").pack(anchor="w")
format_options_var = tk.StringVar(value="mp4")
format_options_menu = ttk.Combobox(right_column, textvariable=format_options_var, values=["mp4", "mkv", "webm"], state="readonly", width=18)
format_options_menu.pack(pady=5)
format_options_menu.current(0)

# Resolution selection
tk.Label(left_column, text="Select Resolution:").pack(anchor="w")
resolution_var = tk.StringVar(value="best")
resolution_menu = ttk.Combobox(left_column, textvariable=resolution_var, values=[], state="readonly", width=18)
resolution_menu.pack(pady=5)

# Bitrate selection
tk.Label(right_column, text="Select Audio Bitrate:").pack(anchor="w")
bitrate_var = tk.StringVar(value="192")
bitrate_menu = ttk.Combobox(right_column, textvariable=bitrate_var, values=[], state="readonly", width=18)
bitrate_menu.pack(pady=5)

# Download location input
tk.Label(root, text="Select Download Location:").pack(padx=20, pady=(10, 5), anchor="w")
download_path_entry = tk.Entry(root, width=50)
download_path_entry.pack(pady=5, padx=20)
download_path_entry.insert(0, os.path.expanduser('~/Downloads')) 

# Browse button
browse_button = tk.Button(root, text="Browse", command=browse_folder)
browse_button.pack(pady=5)

# Download button
download_button = tk.Button(root, text="Download", command=download_video)
download_button.pack(pady=15)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Status label
status_label = tk.Label(root, text="")
status_label.pack(pady=5)

root.mainloop()