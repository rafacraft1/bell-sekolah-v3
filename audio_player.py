# audio_player.py
import pygame
import os
import time
import threading
from logger import log_error, log_info

class AudioPlayer:
    def __init__(self):
        self.currently_playing = False
        self.play_lock = threading.Lock()
        
    def play_audio(self, path: str, blocking: bool = False) -> bool:
        """Putar file audio"""
        if not os.path.exists(path):
            log_error(f"File audio tidak ditemukan: {path}")
            return False
            
        with self.play_lock:
            if self.currently_playing:
                log_info("Audio sedang diputar, menunggu selesai...")
                
            if blocking:
                return self._play_audio_blocking(path)
            else:
                threading.Thread(target=self._play_audio_blocking, args=(path,), daemon=True).start()
                return True
                
    def _play_audio_blocking(self, path: str) -> bool:
        """Putar audio dengan cara blocking"""
        try:
            self.currently_playing = True
            
            # Inisialisasi mixer
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            
            # Load dan putar
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            log_info(f"Memutar audio: {os.path.basename(path)}")
            
            # Tunggu sampai selesai
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            pygame.mixer.quit()
            self.currently_playing = False
            return True
        except Exception as e:
            log_error(f"Gagal memutar audio {path}: {e}")
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            self.currently_playing = False
            return False