# utils.py
import os
import sys
import platform
import subprocess
from logger import log_info, log_error

def resource_path(relative_path: str) -> str:
    """Dapatkan path absolut, bekerja untuk dev dan PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_autostart(enable: bool = True) -> bool:
    """Setup autostart aplikasi"""
    try:
        if platform.system() == "Windows":
            import winreg as reg
            key = reg.HKEY_CURRENT_USER
            sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            app_name = "SchoolBell"
            exe_path = os.path.abspath(sys.argv[0])
            
            if enable:
                reg.SetValue(key, sub_key + "\\" + app_name, reg.REG_SZ, exe_path)
                log_info("Autostart diaktifkan")
            else:
                try:
                    reg.DeleteValue(key, sub_key + "\\" + app_name)
                    log_info("Autostart dinonaktifkan")
                except:
                    pass
            return True
        elif platform.system() == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_file = os.path.join(autostart_dir, "bell-sekolah.desktop")
            
            if enable:
                with open(desktop_file, "w") as f:
                    f.write(f"""[Desktop Entry]
Type=Application
Name=Bell Sekolah
Exec={os.path.abspath(sys.argv[0])}
Terminal=false
StartupNotify=false
""")
                log_info("Autostart diaktifkan")
            else:
                if os.path.exists(desktop_file):
                    os.remove(desktop_file)
                    log_info("Autostart dinonaktifkan")
            return True
    except Exception as e:
        log_error(f"Gagal setup autostart: {e}")
        return False

def show_notification(title: str, message: str) -> None:
    """Tampilkan notifikasi desktop"""
    try:
        if sys.platform == 'win32':
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5)
        elif sys.platform.startswith('linux'):
            subprocess.Popen(['notify-send', title, message])
    except Exception as e:
        log_error(f"Gagal menampilkan notifikasi: {e}")