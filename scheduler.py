# scheduler.py
import threading
import datetime
import time as time_module
import sys
from data_manager import data_manager
from audio_player import AudioPlayer
from logger import log_error, log_info
from utils import show_notification
from constants import DAYS, SCHEDULE_CHECK_INTERVAL

class BellScheduler:
    def __init__(self, audio_player=None):
        self.running = True
        self.audio_player = audio_player or AudioPlayer()
        self.last_played = {}  # Track last played time to avoid repeats
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        log_info("Scheduler diinisialisasi")

    def _run(self) -> None:
        """Main scheduler loop"""
        while self.running:
            try:
                now = datetime.datetime.now()
                # Hanya Senin-Sabtu (0-5)
                if now.weekday() < 6:
                    day_name = DAYS[now.weekday()]
                    current_time_str = now.strftime("%H:%M")
                    
                    # Check if we've already played a bell for this time
                    last_key = f"{day_name}_{current_time_str}"
                    if last_key not in self.last_played or \
                       (now - self.last_played[last_key]).total_seconds() > 60:
                        
                        schedules = data_manager.get_schedules().get(day_name, [])
                        for schedule_time, path in schedules:
                            if schedule_time == current_time_str:
                                # Tampilkan notifikasi
                                show_notification(f"Bell Sekolah", f"Memutar bell untuk {day_name} pukul {schedule_time}")
                                
                                # Putar audio
                                self.audio_player.play_audio(path)
                                self.last_played[last_key] = now
                                break
                
                time_module.sleep(SCHEDULE_CHECK_INTERVAL)
            except Exception as e:
                log_error(f"Error di scheduler: {e}")
                time_module.sleep(SCHEDULE_CHECK_INTERVAL)
    
    def stop(self) -> None:
        """Stop scheduler"""
        self.running = False
        log_info("Scheduler dihentikan")