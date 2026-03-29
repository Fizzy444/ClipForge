# ⚡ ClipForge

### Cut. Encode. Done.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![yt-dlp](https://img.shields.io/badge/yt--dlp-Downloader-orange)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Media-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Overview

**ClipForge** is a fast and minimal YouTube downloader and clip extractor built with **Flask**, **yt-dlp**, and **FFmpeg**.

It allows you to download full videos or extract precise clips using timestamps, with high-quality encoding and real-time progress tracking — all in a clean, modern interface.

---

## ✨ Features

* 🎥 Download full videos in high quality
* ✂️ Clip videos using start & end timestamps
* ⚡ Quick Clip mode (downloads only required segment)
* 🎧 Extract audio (MP3 320kbps)
* 🎚 Select video quality (480p / 720p / 1080p)
* 🔐 Supports `cookies.txt` for restricted videos
* 📂 Custom download directory
* 📊 Live progress tracking
* 🔄 Multi-threaded background downloads
* 🧠 Clean file naming with duplicate handling

---

## 🖥 Tech Stack

| Layer      | Technology            |
| ---------- | --------------------- |
| Backend    | Flask (Python)        |
| Downloader | yt-dlp                |
| Encoding   | FFmpeg                |
| Frontend   | HTML, CSS, JavaScript |
| System UI  | Tkinter               |

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-username/clipforge.git
cd clipforge
```

### 2. Install dependencies

```bash
pip install flask yt-dlp imageio-ffmpeg
```

---

## ▶️ Run the App

```bash
python server.py
```

Open in browser:

```
http://127.0.0.1:<port>
```

---

## 📂 Project Structure

```
clipforge/
│
├── server.py
├── ui/
│   └── index.html
├── ffmpeg/          # optional
├── cookies.txt      # optional
└── README.md
```

---

## 🔐 Cookies Support

To download **age-restricted or private videos**:

1. Install extension: **Get cookies.txt**
2. Export cookies from YouTube
3. Save as `cookies.txt`
4. Select it in the app

> ⚠️ Avoid browser cookie extraction — it may fail on Windows due to DPAPI encryption.

---

## 🎬 Download Modes

| Mode  | Description                    |
| ----- | ------------------------------ |
| Full  | Download entire video          |
| Cut   | Download full video, then trim |
| Quick | Download only selected segment |

---

## ⏱ Timestamp Format

Supported formats:

```
MM:SS
HH:MM:SS
seconds (e.g., 90)
```

Example:

```
Start: 0:30
End:   1:45
```

---

## 📦 Build EXE (Optional)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole server.py
```

---

## ⚠️ Known Issues

* Browser cookies may fail (use `cookies.txt`)
* Some videos may not support selected resolution
* FFmpeg must be available

---

## 🧠 Future Improvements

* Drag & drop cookies file
* Download queue system
* Subtitle download support
* Video preview before download
* UI animations & themes

---

## 🤝 Contributing

Contributions are welcome!
Feel free to open issues or submit pull requests.

---

## 📜 License

MIT License

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

---
