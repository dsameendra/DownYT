import tkinter as tk
from tkinter import ttk, filedialog
import yt_dlp
import os

# Function to download video
def download_video():
    url = url_entry.get().strip()
    resolution = resolution_var.get()
    format_type = format_var.get()
    file_format = format_options_var.get()
    bitrate = bitrate_var.get()
    download_path = download_path_entry.get().strip()
    
    if not url:
        status_label.config(text="Error: Please enter a valid URL")
        return

    if not download_path:
        download_path = os.path.expanduser('~/Downloads')  # Default to Downloads folder if empty
    
    # Check if the provided path is valid
    if not os.path.exists(download_path):
        status_label.config(text="Error: Invalid download path")
        return
    
    download_button.config(state=tk.DISABLED)
    filename_template = "%(title)s_%(format)s"
    if format_type == "Video":
        filename_template += f"_{resolution}p"
    else:
        filename_template += f"_{bitrate}kbps"
    filename_template += ".%(ext)s"
    
    ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg")

    options = {
        'ffmpeg_location': ffmpeg_path,
        'outtmpl': os.path.join(download_path, filename_template),
        'progress_hooks': [progress_hook]
    }
    
    if format_type == "Video":
        if resolution == "best":
            options['format'] = 'bestvideo+bestaudio/best'
        else:
            options['format'] = f'bestvideo[height={resolution}]+bestaudio/best'
        if file_format != "mp4":
            options['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': file_format
            }]
    elif format_type == "Audio":
        options['format'] = 'bestaudio'
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': file_format,
            'preferredquality': bitrate,
        }]
    
    progress_bar['value'] = 0
    status_label.config(text="Downloading...")
    root.update_idletasks()
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        status_label.config(text="Download Completed!")
    except Exception as e:
        status_label.config(text=f"Download Failed: {e}")
    
    download_button.config(state=tk.NORMAL)

# Update format options based on selected type
def update_format_options(*args):
    format_type = format_var.get()
    if format_type == "Video":
        format_options_menu["values"] = ["mp4", "mkv", "webm"]
        format_options_var.set("mp4")
        resolution_menu["state"] = "readonly"
        bitrate_menu["state"] = "disabled"
    else:
        format_options_menu["values"] = ["mp3", "wav", "aac"]
        format_options_var.set("mp3")
        resolution_menu["state"] = "disabled"
        bitrate_menu["state"] = "readonly"

# Progress hook for download status
def progress_hook(d):
    if d['status'] == 'downloading':
        if 'total_bytes' in d and 'downloaded_bytes' in d:
            total = d['total_bytes']
            downloaded = d['downloaded_bytes']
            progress_percent = (downloaded / total) * 100
            progress_bar['value'] = progress_percent
            status_label.config(text=f"Downloading... {int(progress_percent)}%")
            root.update_idletasks()

# Open file dialog to choose download folder
def browse_folder():
    folder_selected = filedialog.askdirectory(initialdir=os.path.expanduser('~/Downloads'))
    if folder_selected:
        download_path_entry.delete(0, tk.END)
        download_path_entry.insert(0, folder_selected)

# GUI setup
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("500x600")

# URL input
tk.Label(root, text="Enter YouTube Video URL:").pack(padx=20, pady=(20, 5), anchor="w")
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5, padx=20)

# Frame for inputs to improve layout
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
format_menu = ttk.Combobox(left_column, 
                            textvariable=format_var, 
                            values=["Video", "Audio"], 
                            state="readonly", 
                            width=18)
format_menu.pack(pady=5)
format_menu.current(0)
format_var.trace("w", update_format_options)

# File format selection
tk.Label(right_column, text="Select File Format:").pack(anchor="w")
format_options_var = tk.StringVar(value="mp4")
format_options_menu = ttk.Combobox(right_column, 
                                   textvariable=format_options_var, 
                                   values=["mp4", "mkv", "webm"], 
                                   state="readonly", 
                                   width=18)
format_options_menu.pack(pady=5)
format_options_menu.current(0)

# Resolution selection
tk.Label(left_column, text="Select Resolution:").pack(anchor="w")
resolution_var = tk.StringVar(value="best")
resolution_menu = ttk.Combobox(left_column, 
                                textvariable=resolution_var, 
                                values=["720", "1080", "1440", "2160", "best"], 
                                state="readonly", 
                                width=18)
resolution_menu.pack(pady=5)
resolution_menu.current(4)

# Bitrate selection
tk.Label(right_column, text="Select Audio Bitrate:").pack(anchor="w")
bitrate_var = tk.StringVar(value="192")
bitrate_menu = ttk.Combobox(right_column, 
                             textvariable=bitrate_var, 
                             values=["128", "192", "256", "320"], 
                             state="disabled", 
                             width=18)
bitrate_menu.pack(pady=5)
bitrate_menu.current(1)

# Download location input
tk.Label(root, text="Select Download Location:").pack(padx=20, pady=(10, 5), anchor="w")
download_path_entry = tk.Entry(root, width=50)
download_path_entry.pack(pady=5, padx=20)
download_path_entry.insert(0, os.path.expanduser('~/Downloads'))  # Default to Downloads folder

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