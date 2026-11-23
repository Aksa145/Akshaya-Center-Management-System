# import subprocess
# import sys
# import os
# import time
# import webview
# import socket

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PYTHON = sys.executable

# # ---- SINGLE INSTANCE LOCK (prevents multiple opens) ----
# def single_instance():
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         s.bind(("127.0.0.1", 65432))
#     except OSError:
#         sys.exit(0)
#     return s

# def start_django():
#     subprocess.Popen(
#         [
#             PYTHON,
#             "manage.py",
#             "runserver",
#             "127.0.0.1:8000",
#             "--noreload"   # 🔴 THIS IS THE KEY FIX
#         ],
#         cwd=BASE_DIR,
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL,
#     )
#     time.sleep(5)

# if __name__ == "__main__":
#     lock = single_instance()
#     start_django()

#     window = webview.create_window(
#         "Akshaya Center Software",
#         "http://127.0.0.1:8000",
#         width=1200,
#         height=800
#     )

#     webview.start()
import subprocess
import sys
import os
import time
import webview

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

def start_django():
    subprocess.Popen(
        [PYTHON, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(4)

start_django()

webview.create_window(
    "Akshaya Center Software",
    "http://127.0.0.1:8000",
    width=1200,
    height=800
)

webview.start()