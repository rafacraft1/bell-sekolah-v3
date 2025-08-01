# main.py
import os
import sys
import tkinter as tk
import time
import pygame
from data_manager import data_manager
from scheduler import BellScheduler
from gui.main_window import SchoolBellApp
from gui.tray_icon import TrayIcon
from gui.splash_screen import SplashScreen
from logger import log_info, log_error
from constants import AUDIO_DIR, LOGS_DIR

def run_main_app():
    """Jalankan aplikasi utama setelah splash screen selesai"""
    try:
        # Langkah 5: Mempersiapkan antarmuka
        root = tk.Tk()
        app = SchoolBellApp(root)
        
        # Langkah 6: Memuat file audio
        app.load_audio_files()
        
        # Langkah 7: Memuat jadwal
        app.load_schedule()
        
        # Langkah 8: Menginisialisasi pemutar audio
        audio_player = app.audio_player
        
        # Langkah 9: Mengatur sistem tray
        scheduler = BellScheduler(audio_player)
        tray = TrayIcon(app)
        
        # Langkah 10: Menyelesaikan inisialisasi
        log_info("Aplikasi berhasil diinisialisasi")
        
        # Jalankan aplikasi utama
        root.mainloop()
        
    except Exception as e:
        log_error(f"Fatal error di main: {e}")
        raise

def main():
    try:
        # Inisialisasi pygame mixer untuk audio
        pygame.init()
        
        # Langkah 1: Membuat folder aplikasi
        os.makedirs(AUDIO_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        # Langkah 2: Menginisialisasi database
        data_manager.init_db()
        
        # Langkah 3: Memeriksa database
        is_empty = data_manager.is_database_empty()
        
        # Langkah 4: Memuat data default
        if is_empty:
            data_manager.insert_dummy_data()
        
        # Buat dan tampilkan splash screen
        splash = SplashScreen(callback=run_main_app)
        splash.run()
        
    except Exception as e:
        log_error(f"Fatal error di main: {e}")
        raise

if __name__ == "__main__":
    main()