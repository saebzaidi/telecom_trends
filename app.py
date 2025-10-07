import os
import sys
import subprocess
import threading
import webbrowser
import time

def open_browser():
    """Automatically open the app in the default browser"""
    time.sleep(2)
    webbrowser.open_new("http://localhost:8501")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()

    # Detect base path for bundled or normal run
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # PyInstaller temp dir
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Launch Streamlit with full control over runtime settings
    app_path = os.path.join(base_path, "dashboard_app.py")

    cmd = [
    sys.executable,
    "-m", "streamlit", "run", "dashboard_app.py",
    "--server.fileWatcherType", "none"
    ]

    subprocess.run(cmd)
