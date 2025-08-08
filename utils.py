# utils.py
import os
import sys
import platform

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def show_notification(title, message):
    """Tampilkan notifikasi desktop"""
    try:
        if platform.system() == "Windows":
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5)
        elif platform.system() == "Darwin":  # macOS
            import subprocess
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ])
        else:  # Linux
            try:
                import subprocess
                subprocess.run([
                    "notify-send", title, message
                ])
            except:
                print("Tidak bisa menampilkan notifikasi")
    except Exception as e:
        print(f"Tidak bisa menampilkan notifikasi: {e}")