# gui/tray_icon.py
import pystray
from PIL import Image, ImageDraw
import os
import sys
import threading
from constants import ASSETS_DIR
from utils import resource_path

class TrayIcon:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.running = False
        self.icon_thread = None
        
    def create_icon_image(self):
        """Create tray icon using logo.ico"""
        # Gunakan logo.ico
        icon_path = resource_path(os.path.join(ASSETS_DIR, "logo.ico"))
        
        if os.path.exists(icon_path):
            # Gunakan logo.ico langsung
            try:
                icon_image = Image.open(icon_path)
                # Resize untuk memastikan ukuran yang tepat untuk tray icon
                icon_image = icon_image.resize((64, 64), Image.LANCZOS)
                return icon_image
            except Exception as e:
                print(f"Error loading icon: {e}")
        
        # Fallback: buat icon sederhana
        icon_image = Image.new('RGB', (64, 64), color=(0, 0, 0))
        draw = ImageDraw.Draw(icon_image)
        draw.ellipse((8, 8, 56, 56), fill=(255, 215, 0))  # Lingkaran emas
        draw.rectangle((28, 4, 36, 20), fill=(139, 69, 19))  # Gagang coklat
        return icon_image
    
    def show_window(self, icon=None, item=None):
        """Tampilkan jendela utama"""
        self.app.root.deiconify()
        self.app.root.lift()
    
    def quit_app(self, icon=None, item=None):
        """Keluar dari aplikasi melalui tray menu"""
        self.running = False
        # Schedule quit di main thread
        self.app.root.after(100, self.app.on_close)
    
    def setup(self):
        """Setup system tray"""
        try:
            icon_image = self.create_icon_image()
            
            menu = pystray.Menu(
                pystray.MenuItem("Tampilkan", self.show_window),
                pystray.MenuItem("Keluar", self.quit_app)
            )
            
            self.icon = pystray.Icon(
                "bell_sekolah",
                icon_image,
                "Bell Sekolah Otomatis",
                menu
            )
            
            return self.icon
        except Exception as e:
            print(f"Error setting up tray icon: {e}")
            return None
    
    def run(self):
        """Jalankan system tray"""
        if self.icon:
            try:
                self.running = True
                # Jalankan di thread terpisah
                self.icon_thread = threading.Thread(target=self._run_icon, daemon=True)
                self.icon_thread.start()
            except Exception as e:
                print(f"Error running tray icon: {e}")
    
    def _run_icon(self):
        """Fungsi internal untuk menjalankan icon"""
        try:
            # Cek platform untuk pendekatan yang berbeda
            if sys.platform == "win32":
                # Untuk Windows, gunakan pendekatan khusus
                self.icon.run()
            else:
                # Untuk platform lain
                self.icon.run()
        except Exception as e:
            print(f"Error in icon thread: {e}")
    
    def stop(self):
        """Hentikan system tray"""
        if self.icon and self.running:
            try:
                self.icon.stop()
                self.running = False
                # Tunggu thread selesai
                if self.icon_thread and self.icon_thread.is_alive():
                    self.icon_thread.join(timeout=1.0)
            except Exception as e:
                print(f"Error stopping tray icon: {e}")