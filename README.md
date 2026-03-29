# ClipForge
A fast, minimal YouTube downloader with clip extraction, high-quality encoding, and support for restricted videos using cookies.

⚡ ClipForge
Cut. Encode. Done.
ClipForge is a high-performance YouTube downloader and clip extractor built using Flask, yt-dlp, and FFmpeg.
It provides fast downloads, precise timestamp clipping, and high-quality encoding — all wrapped in a minimal, modern UI.
🚀 Features
🎥 Full Video Download – Download entire videos in high quality
✂️ Timestamp Clipping – Extract specific segments using start & end time
⚡ Quick Clip Mode – Download only the required portion (faster, efficient)
🎧 Audio Extraction – Convert videos to high-quality MP3 (320kbps)
🎚 Quality Control – Choose between 480p, 720p, 1080p
🔐 Cookies Support – Download age-restricted/private videos using cookies.txt
📂 Custom Download Folder – Choose where files are saved
📊 Live Progress Tracking – Real-time status, speed, and percentage
🧠 Smart File Naming – Clean titles with duplicate handling
🔄 Multi-threaded Downloads – Non-blocking background jobs
🖥 Tech Stack
Backend: Flask (Python)
Downloader: yt-dlp
Media Processing: FFmpeg
Frontend: HTML, CSS, JavaScript (custom UI)
System Integration: Tkinter (file/folder picker)
📸 UI Preview
Minimal, distraction-free interface focused on speed and usability.
Paste URL → Select Mode → Choose Quality → Download

⚙️ Installation
1. Clone the repository
git clone https://github.com/your-username/clipforge.git
cd clipforge

2. Install dependencies
pip install -r requirements.txt

If you don’t have a requirements file:
pip install flask yt-dlp imageio-ffmpeg

▶️ Run the App
python server.py

Then open:
http://127.0.0.1:<port>

📂 Project Structure
clipforge/
│
├── server.py
├── ui/
│   └── index.html
├── ffmpeg/ (optional bundled binary)
├── cookies.txt (optional)
└── README.md

🔐 Cookies Support (Important)
To download age-restricted or private videos:
Steps:
Install browser extension: Get cookies.txt
Export cookies from YouTube
Save as cookies.txt
Select it inside the app
🎬 Download Modes Explained
ModeDescriptionFullDownloads entire videoCutDownloads full video, then trimsQuickDownloads only selected segment (fastest)⏱ Timestamp Format
Supported formats:
MM:SS
HH:MM:SS
seconds (e.g., 90)

Example:
Start: 0:30
End:   1:45

📦 Build as EXE (Optional)
Using PyInstaller:
pip install pyinstaller
pyinstaller --onefile --noconsole server.py

Note: Use cookies.txt instead of browser cookies to avoid DPAPI issues.
⚠️ Known Issues
Browser cookie extraction may fail on Windows (DPAPI restriction)
Some videos may not support selected resolution
FFmpeg must be available (auto-handled via imageio-ffmpeg or bundled)
🧠 Future Improvements
Drag & drop cookies file
Download queue management
Video preview before download
Subtitle support
Dark/light theme toggle
🤝 Contributing
Pull requests are welcome. For major changes, open an issue first.
📜 License
MIT License
⭐ Support
If you like this project, consider giving it a ⭐ on GitHub!
