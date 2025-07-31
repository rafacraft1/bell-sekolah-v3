# gui/tray_icon.py
import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import datetime
import pystray
from PIL import Image, ImageDraw
from data_manager import data_manager
from logger import log_error, log_info
from utils import resource_path, setup_autostart
from constants import ASSETS_DIR, BELL_ICON, VERSION

class TrayIcon:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.setup_tray()

    def setup_tray(self):
        """Setup system tray icon"""
        try:
            image_path = resource_path(os.path.join(ASSETS_DIR, BELL_ICON))
            if os.path.exists(image_path):
                image = Image.open(image_path)
            else:
                image = Image.new('RGB', (64, 64), 'orange')
                d = ImageDraw.Draw(image)
                d.text((10, 25), "BELL", fill="white")
            
            menu = (
                pystray.MenuItem('Buka Aplikasi', self.show_window),
                pystray.MenuItem('Lihat Jadwal Hari Ini', self.show_schedule),
                pystray.MenuItem('Reset ke Default', self.reset_to_default),
                pystray.MenuItem('Autostart', self.toggle_autostart, checked=lambda item: self.is_autostart_enabled()),
                pystray.MenuItem('Keluar', self.quit_app)
            )
            
            self.icon = pystray.Icon("bell", image, f"Bell Sekolah {VERSION}", menu)
            threading.Thread(target=self.icon.run, daemon=True).start()
            log_info("System tray icon diinisialisasi")
        except Exception as e:
            log_error(f"Gagal setup tray icon: {e}")

    def show_window(self, icon, item):
        """Show main window"""
        self.app.root.deiconify()

    def show_schedule(self, icon, item):
        """Show today's schedule"""
        try:
            day_map = {
                "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
                "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu"
            }
            today = day_map.get(datetime.datetime.now().strftime("%A"), "Senin")
            schedules = data_manager.get_schedules().get(today, [])
            msg = "\n".join([f"{t} - {os.path.basename(p)}" for t, p in schedules])
            if not msg:
                msg = "Tidak ada jadwal hari ini."
            messagebox.showinfo(f"Jadwal {today}", msg)
        except Exception as e:
            log_error(f"Gagal menampilkan jadwal: {e}")

    def reset_to_default(self, icon, item):
        """Reset to default configuration"""
        try:
            confirm = messagebox.askyesno("Reset", "Yakin ingin reset ke konfigurasi default?")
            if confirm:
                if data_manager.reset_to_default():
                    # Refresh schedule table immediately
                    self.app.load_schedule(force_refresh=True)
                    messagebox.showinfo("Reset", "Aplikasi telah direset ke konfigurasi default.")
                else:
                    messagebox.showerror("Error", "Gagal reset ke konfigurasi default.")
        except Exception as e:
            log_error(f"Gagal reset: {e}")

    def toggle_autostart(self, icon, item):
        """Toggle autostart"""
        try:
            current_state = self.is_autostart_enabled()
            setup_autostart(not current_state)
        except Exception as e:
            log_error(f"Gagal toggle autostart: {e}")

    def is_autostart_enabled(self):
        """Check if autostart is enabled"""
        try:
            if sys.platform == 'win32':
                import winreg as reg
                key = reg.HKEY_CURRENT_USER
                sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                app_name = "SchoolBell"
                try:
                    reg.OpenKey(key, sub_key + "\\" + app_name)
                    return True
                except:
                    return False
            elif sys.platform.startswith('linux'):
                autostart_file = os.path.expanduser("~/.config/autostart/bell-sekolah.desktop")
                return os.path.exists(autostart_file)
            return False
        except Exception as e:
            log_error(f"Gagal cek autostart: {e}")
            return False

    def quit_app(self, icon, item):
        """Quit application"""
        try:
            self.app.quit_app()
            if self.icon:
                self.icon.stop()
        except Exception as e:
            log_error(f"Gagal keluar: {e}")
            sys.exit(1)