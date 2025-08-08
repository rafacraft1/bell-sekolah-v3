# main.py
import tkinter as tk
from gui.splash_screen import SplashScreen
from gui.main_window import SchoolBellApp
from data_manager import data_manager
from logger import log_info, log_error
from gui.tray_icon import TrayIcon
import sys
import time
import os

def main():
    # Inisialisasi database terlebih dahulu
    data_manager.init_db()
    
    # Cek database kosong
    if data_manager.is_database_empty():
        data_manager.insert_dummy_data()
    
    # Buat splash screen terlebih dahulu
    splash = SplashScreen()
    
    # Update progress untuk setiap langkah
    try:
        # Langkah 1: Membuat folder aplikasi
        log_info("Langkah 1: Membuat folder aplikasi...")
        splash.update_progress("Membuat folder aplikasi...", 10)
        splash.root.update()
        time.sleep(1)
        
        # Langkah 2: Menginisialisasi database
        log_info("Langkah 2: Menginisialisasi database...")
        splash.update_progress("Menginisialisasi database...", 20)
        splash.root.update()
        time.sleep(1)
        
        # Langkah 3: Memeriksa database
        log_info("Langkah 3: Memeriksa database...")
        splash.update_progress("Memeriksa database...", 30)
        splash.root.update()
        time.sleep(1)
        
        # Langkah 4: Memuat data default
        log_info("Langkah 4: Memuat data default...")
        splash.update_progress("Memuat data default...", 40)
        splash.root.update()
        time.sleep(1)
        
        # Langkah 5: Mempersiapkan antarmuka
        log_info("Langkah 5: Mempersiapkan antarmuka...")
        splash.update_progress("Mempersiapkan antarmuka...", 50)
        splash.root.update()
        
        # Buat root window
        root = tk.Tk()
        root.withdraw()  # Sembunyikan dulu
        
        # Buat aplikasi
        app = SchoolBellApp(root)
        time.sleep(1)
        
        # Langkah 6: Memuat file audio
        log_info("Langkah 6: Memuat file audio...")
        splash.update_progress("Memuat file audio...", 60)
        splash.root.update()
        time.sleep(1)
        
        # Langkah 7: Memuat jadwal
        log_info("Langkah 7: Memuat jadwal...")
        splash.update_progress("Memuat jadwal...", 70)
        splash.root.update()
        time.sleep(1)
        
        # Langkah 8: Menginisialisasi pemutar audio
        log_info("Langkah 8: Menginisialisasi pemutar audio...")
        splash.update_progress("Menginisialisasi pemutar audio...", 80)
        splash.root.update()
        time.sleep(1)
        
        # Langkah 9: Mengatur sistem tray
        log_info("Langkah 9: Mengatur sistem tray...")
        splash.update_progress("Mengatur sistem tray...", 90)
        try:
            tray_icon = TrayIcon(app)
            icon = tray_icon.setup()
            
            if icon:
                # Simpan referensi tray icon di app
                app.tray_icon = tray_icon
                
                # Jalankan tray icon
                tray_icon.run()
                
                # Tunggu sebentar agar tray icon sempat berjalan
                time.sleep(1)
                
                log_info("Tray icon berhasil dijalankan")
            else:
                log_error("Gagal membuat tray icon")
                app.tray_icon = None
        except Exception as e:
            log_error(f"Error setting up tray: {e}")
            app.tray_icon = None
        
        splash.root.update()
        time.sleep(1)
        
        # Langkah 10: Menyelesaikan inisialisasi
        log_info("Langkah 10: Menyelesaikan inisialisasi...")
        splash.update_progress("Menyelesaikan inisialisasi...", 100)
        splash.root.update()
        time.sleep(2)
        
        # Tutup splash screen
        splash.close()
        
        # Tampilkan jendela utama
        root.deiconify()
        root.mainloop()
        
    except Exception as e:
        log_error(f"Error during initialization: {e}")
        # Tampilkan error di splash screen
        try:
            splash.update_progress(f"Error: {str(e)}", 0)
            splash.root.update()
            # Tunggu 5 detik sebelum menutup
            time.sleep(5)
            splash.close()
        except:
            # Jika gagal menampilkan error, langsung tutup splash screen
            try:
                splash.close()
            except:
                pass
            # Tampilkan error di console
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()