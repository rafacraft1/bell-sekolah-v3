# scheduler.py
import threading
import pygame
import datetime
import os
import time
from data_manager import get_schedules
from logger import log_error

class BellScheduler:
    def __init__(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while self.running:
            now = datetime.datetime.now()
            # Hanya Senin-Sabtu
            if now.weekday() < 6:
                day_name = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"][now.weekday()]
                time_str = now.strftime("%H:%M")
                schedules = get_schedules().get(day_name, [])
                for time_val, path in schedules:
                    if time_val == time_str:
                        self._play_audio(path)
                        break
            time.sleep(30)  # Cek tiap 30 detik

    def _play_audio(self, path):
        try:
            if not os.path.exists(path):
                log_error(f"File audio tidak ditemukan: {path}")
                return

            # Selalu inisialisasi ulang mixer
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

            # Tunggu sampai selesai
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.quit()

        except Exception as e:
            log_error(f"Gagal memutar audio {path}: {e}")

    def play_test_sound(self, path):
        """Fungsi untuk memutar suara uji (opsional)"""
        try:
            if not os.path.exists(path):
                log_error(f"File audio tidak ditemukan: {path}")
                return

            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.quit()

        except Exception as e:
            log_error(f"Gagal memutar audio {path}: {e}")

    def stop(self):
        self.running = False
        if pygame.mixer.get_init():
            pygame.mixer.quit()