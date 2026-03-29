import sys
import os
import threading
import webview
import time
from server import create_app, find_free_port

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def main():
    port = find_free_port()
    app = create_app(get_resource_path)

    server_thread = threading.Thread(
        target=lambda: app.run(port=port, debug=False, use_reloader=False),
        daemon=True
    )
    server_thread.start()

    time.sleep(1)

    window = webview.create_window(
        title='YTDL — Clip Cutter',
        url=f'http://localhost:{port}',
        width=720,
        height=640,
        resizable=True,
        min_size=(560, 500),
        background_color='#0a0a0a',
    )

    webview.start(debug=False)

if __name__ == '__main__':
    main()