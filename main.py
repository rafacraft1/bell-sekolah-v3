# main.py
import tkinter as tk
from gui.splash_screen import SplashScreen
from gui.main_window import SchoolBellApp
from data_manager import data_manager
from logger import log_info
from gui.tray_icon import TrayIcon
import threading
import sys
import time

def main():
    # Inisialisasi database
    data_manager.init_db()
    
    # Cek database kosong
    if data_manager.is_database_empty():
        data_manager.insert_dummy_data()
    
    # Buat root window
    root = tk.Tk()
    root.withdraw()  # Sembunyikan dulu
    
    # Fungsi callback untuk splash screen
    def start_app():
        # Buat aplikasi setelah splash screen selesai
        app = SchoolBellApp(root)
        
        # Setup system tray
        try:
            tray_icon = TrayIcon(app)
            icon = tray_icon.setup()
            
            if icon:
                # Simpan referensi tray icon di app
                app.tray_icon = tray_icon
                
                # Jalankan tray icon
                tray_icon.run()
                
                # Tunggu sebentar agar tray icon sempat berjalan
                time.sleep(1.0)  # Tambah waktu tunggu
                
                print("Tray icon berhasil dijalankan")
            else:
                print("Gagal membuat tray icon")
                app.tray_icon = None
        except Exception as e:
            print(f"Error setting up tray: {e}")
            app.tray_icon = None
        
        # Tampilkan jendela utama
        root.deiconify()
        
        # Jalankan aplikasi
        root.mainloop()
    
    # Buat splash screen
    splash = SplashScreen(start_app)
    splash.run()

if __name__ == "__main__":
    main()