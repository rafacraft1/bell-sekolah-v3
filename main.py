# main.py
import os
import sys
import tkinter as tk
from data_manager import data_manager
from scheduler import BellScheduler
from gui.main_window import SchoolBellApp
from gui.tray_icon import TrayIcon
from logger import log_info, log_error
from constants import AUDIO_DIR, LOGS_DIR

def main():
    try:
        # Buat folder yang diperlukan
        os.makedirs(AUDIO_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        
        # Inisialisasi database
        data_manager.init_db()
        
        # Cek apakah database kosong
        if data_manager.is_database_empty():
            data_manager.insert_dummy_data()
        
        # Setup GUI
        root = tk.Tk()
        app = SchoolBellApp(root)
        
        # Setup scheduler
        scheduler = BellScheduler(app.audio_player)
        
        # Setup tray icon
        tray = TrayIcon(app)
        
        # Run main loop
        root.mainloop()
    except Exception as e:
        log_error(f"Fatal error di main: {e}")
        raise

if __name__ == "__main__":
    main()