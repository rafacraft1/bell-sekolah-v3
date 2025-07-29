# utils.py
import os
import sys

def resource_path(relative_path):
    """Dapatkan path absolut, bekerja untuk dev dan PyInstaller."""
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)