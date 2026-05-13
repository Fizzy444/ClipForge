import os
import re
import uuid
import socket
import threading
import sys
import subprocess
import yt_dlp
from flask import Flask, request, jsonify, render_template_string
from tkinter import Tk, filedialog

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def get_ffmpeg_path(get_resource_path):
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(path): return path
    except: pass
    ext = '.exe' if sys.platform == 'win32' else ''
    bundled = get_resource_path(os.path.join('ffmpeg', f'ffmpeg{ext}'))
    if os.path.exists(bundled): return bundled
    return 'ffmpeg'

def parse_time(t):
    if not t or str(t).strip() == "": return None
    t = str(t).strip()
    try:
        if re.match(r'^\d+$', t): return int(t)
        parts = list(map(int, t.split(':')))
        if len(parts) == 2: return parts[0] * 60 + parts[1]
        if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except: return None
    return None

def format_bytes_per_second(value):
    if not value or value <= 0:
        return 'Speed --'

    units = ['B/s', 'KB/s', 'MB/s', 'GB/s']
    speed = float(value)
    unit_index = 0
    while speed >= 1024 and unit_index < len(units) - 1:
        speed /= 1024
        unit_index += 1

    if unit_index == 0:
        return f'{speed:.0f} {units[unit_index]}'
    return f'{speed:.1f} {units[unit_index]}'

def format_eta(value):
    if value is None:
        return 'ETA --'

    try:
        seconds = int(value)
    except (TypeError, ValueError, OverflowError):
        return 'ETA --'

    if seconds < 0:
        return 'ETA --'

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f'ETA {hours:d}:{minutes:02d}:{seconds:02d}'
    return f'ETA {minutes:02d}:{seconds:02d}'

def clean_percent(value):
    value = str(value or '0').replace('%', '').strip()
    try:
        return f'{float(value):.1f}'.rstrip('0').rstrip('.')
    except ValueError:
        return '0'

def calculate_percent(progress):
    downloaded = progress.get('downloaded_bytes') or 0
    total = progress.get('total_bytes') or progress.get('total_bytes_estimate') or 0

    if downloaded and total:
        percent = min(max((downloaded / total) * 100, 0), 100)
        return f'{percent:.1f}'.rstrip('0').rstrip('.')

    return clean_percent(progress.get('_percent_str', '0%'))

def parse_ffmpeg_time(value):
    if not value:
        return None

    value = str(value).strip()
    try:
        if ':' not in value:
            return float(value)
        hours, minutes, seconds = value.split(':')
        return (int(hours) * 3600) + (int(minutes) * 60) + float(seconds)
    except (TypeError, ValueError):
        return None

def parse_ffmpeg_progress_seconds(key, value):
    if key in ('out_time_us', 'out_time_ms'):
        try:
            return int(value) / 1000000
        except (TypeError, ValueError):
            return None

    if key == 'out_time':
        return parse_ffmpeg_time(value)

    return None

def calculate_trim_duration(start, end, source_duration):
    start = start or 0
    if end is not None:
        return max(end - start, 0)
    if source_duration:
        return max(float(source_duration) - start, 0)
    return None

def build_format_options(fmt, quality, mode):
    if fmt == 'audio':
        return 'bestaudio/best', ['abr', 'asr', 'filesize']

    if quality in ['480', '720', '1080', '1440', '2160']:
        height_filter = f'[height<={quality}]'
    else:
        height_filter = ''

    if height_filter:
        format_str = f'bestvideo{height_filter}+bestaudio/best{height_filter}'
    else:
        format_str = 'bestvideo+bestaudio/best'

    sort_order = ['res', 'fps', 'hdr', 'vbr', 'abr', 'filesize']
    if mode != 'full':
        sort_order = ['res', 'fps', 'vcodec:h264,hevc,vp9,av01', 'vbr', 'abr', 'filesize']

    return format_str, sort_order

def create_app(get_resource_path):
    app = Flask(__name__)
    app.config['DOWNLOAD_DIR'] = os.path.join(os.path.expanduser('~'), 'Downloads', 'YTDL')
    app.config['COOKIE_FILE'] = None
    os.makedirs(app.config['DOWNLOAD_DIR'], exist_ok=True)

    jobs = {}
    ffmpeg_bin = get_ffmpeg_path(get_resource_path)

    def trim_with_ffmpeg(input_path, output_path, start, end, source_duration, job):
        trim_duration = calculate_trim_duration(start, end, source_duration)
        if not trim_duration:
            return input_path

        command = [
            ffmpeg_bin,
            '-hide_banner',
            '-nostdin',
            '-y',
        ]
        if start:
            command.extend(['-ss', str(start)])
        command.extend(['-i', input_path, '-t', str(trim_duration)])
        command.extend([
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-progress', 'pipe:1',
            '-nostats',
            '-loglevel', 'error',
            output_path,
        ])

        job.update({'percent': '0', 'progress': 'Trimming: 0%'})
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )

        if process.stdout:
            for line in process.stdout:
                line = line.strip()
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                seconds_done = parse_ffmpeg_progress_seconds(key, value)
                if seconds_done is None:
                    continue
                percent = min(max((seconds_done / trim_duration) * 100, 0), 100)
                p_raw = f'{percent:.1f}'.rstrip('0').rstrip('.')
                job.update({'percent': p_raw, 'progress': f'Trimming: {p_raw}%'})

        _, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(stderr.strip() or 'FFmpeg trim failed.')

        job.update({'percent': '100', 'progress': 'Trimming: 100%'})
        return output_path

    def do_download(job_id, url, start, end, fmt, quality, mode, browser):
        job = jobs[job_id]
        download_path = app.config['DOWNLOAD_DIR']
        job.update({'percent': '0', 'status': 'running', 'progress': 'Initializing...'})
        
        container = 'mkv' if mode == 'full' else 'mp4'

        try:
            uid = str(uuid.uuid4())[:8]
            raw_template = os.path.join(download_path, f'tmp_{uid}.%(ext)s')
            format_str, sort_order = build_format_options(fmt, quality, mode)

            ydl_opts = {
                'format': format_str,
                'format_sort': sort_order, 
                'format_sort_force': True,
                'outtmpl': raw_template,
                'quiet': True,
                'no_warnings': True,
                'ffmpeg_location': ffmpeg_bin,
                'noplaylist': True,
                'merge_output_format': container,
                'postprocessor_args': {
                    'merger': ['-c', 'copy'] 
                },
            }


            if browser == 'file' and app.config['COOKIE_FILE']:
                ydl_opts['cookiefile'] = app.config['COOKIE_FILE']
            elif browser == 'firefox':
                ydl_opts['cookiesfrombrowser'] = ('firefox', None, None, None)

            if fmt == 'audio':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }]

            if (start is not None or end is not None) and mode == 'quick':
                s = start if start is not None else 0
                e = end if end is not None else float('inf')
                ydl_opts['download_ranges'] = yt_dlp.utils.download_range_func(None, [(s, e)])
                ydl_opts['force_keyframes_at_cuts'] = True

            def progress_hook(d):
                if d['status'] == 'downloading':
                    p_raw = calculate_percent(d)
                    speed = format_bytes_per_second(d.get('speed'))
                    eta = format_eta(d.get('eta'))
                    job.update({
                        'percent': p_raw,
                        'speed': speed,
                        'eta': eta,
                        'progress': f'Downloading: {p_raw}% | {speed} | {eta}',
                    })
                elif d['status'] == 'finished':
                    job['progress'] = 'Merging...'

            ydl_opts['progress_hooks'] = [progress_hook]

            # RUN YT-DLP
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise Exception("Could not fetch video info.")
                title = info.get('title', 'video')
                clean_title = re.sub(r'[^\w\s\-]', '', title).strip()[:50]

            # 2. Locate the file on disk to see what was ACTUALLY created
            downloaded_file = None
            disk_ext = 'mp4' # Default fallback
            for f in os.listdir(download_path):
                if f.startswith(f'tmp_{uid}'):
                    downloaded_file = os.path.join(download_path, f)
                    disk_ext = f.split('.')[-1] # Grabs 'mkv', 'webm', or 'mp4'
                    break

            if not downloaded_file:
                raise FileNotFoundError('Process finished but output file not found.')

            if mode == 'cut' and (start is not None or end is not None):
                trim_ext = 'mp3' if fmt == 'audio' else disk_ext
                trimmed_file = os.path.join(download_path, f'tmp_{uid}_trimmed.{trim_ext}')
                source_file = downloaded_file
                downloaded_file = trim_with_ffmpeg(
                    downloaded_file,
                    trimmed_file,
                    start,
                    end,
                    info.get('duration'),
                    job,
                )
                if downloaded_file != source_file and os.path.exists(source_file):
                    os.remove(source_file)
                disk_ext = trim_ext

            # 3. Final Renaming (Uses the extension found on disk)
            final_ext = 'mp3' if fmt == 'audio' else disk_ext
            final_path = os.path.join(download_path, f"{clean_title}.{final_ext}")

            counter = 1
            while os.path.exists(final_path):
                final_path = os.path.join(download_path, f"{clean_title} ({counter}).{final_ext}")
                counter += 1

            os.rename(downloaded_file, final_path)
            job.update({'status': 'done', 'progress': 'Ready!', 'filename': os.path.basename(final_path)})

        except Exception as e:
            job.update({'status': 'error', 'progress': str(e)})

    @app.route('/')
    def index():
        ui_path = get_resource_path(os.path.join('ui', 'index.html'))
        if os.path.exists(ui_path):
            with open(ui_path, 'r', encoding='utf-8') as f: return render_template_string(f.read())
        return "UI index.html not found."

    @app.route('/api/config')
    def get_config(): return jsonify({'download_dir': app.config['DOWNLOAD_DIR']})

    @app.route('/api/select_folder', methods=['POST'])
    def select_folder():
        try:
            root = Tk(); root.withdraw(); root.attributes("-topmost", True)
            f = filedialog.askdirectory(initialdir=os.path.abspath(app.config['DOWNLOAD_DIR']))
            root.destroy()
            if f: app.config['DOWNLOAD_DIR'] = os.path.abspath(f)
            return jsonify({'download_dir': app.config['DOWNLOAD_DIR']})
        except: return jsonify({'error': 'Failed'}), 500

    @app.route('/api/select_cookie_file', methods=['POST'])
    def select_cookie_file():
        try:
            root = Tk(); root.withdraw(); root.attributes("-topmost", True)
            f = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            root.destroy()
            if f: app.config['COOKIE_FILE'] = os.path.abspath(f)
            return jsonify({'filename': os.path.basename(f) if f else None})
        except: return jsonify({'error': 'Failed'}), 500

    @app.route('/api/download', methods=['POST'])
    def start_download():
        data = request.json
        job_id = str(uuid.uuid4())
        jobs[job_id] = {'status': 'queued', 'progress': 'Preparing...'}
        threading.Thread(
            target=do_download,
            args=(job_id, data.get('url'), parse_time(data.get('start')), parse_time(data.get('end')),
                  data.get('format'), data.get('quality'), data.get('mode'), data.get('browser')),
            daemon=True
        ).start()
        return jsonify({'job_id': job_id})

    @app.route('/api/status/<job_id>')
    def status(job_id): return jsonify(jobs.get(job_id, {'status': 'error', 'progress': 'Job missing'}))

    @app.route('/api/open_folder', methods=['POST'])
    def open_folder():
        target = app.config['DOWNLOAD_DIR']
        if sys.platform == 'win32': os.startfile(target)
        else: subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', target])
        return jsonify({'ok': True})

    return app
