# data_manager.py
import sqlite3
import os
import shutil
import subprocess
import hashlib
import time as time_module
from constants import (
    DB_NAME, DEFAULT_AUDIO_DIR, REPO_URL, DAYS, AUDIO_DIR
)
from logger import log_error, log_info, log_warning

class DataManager:
    def __init__(self):
        self._schedule_cache = {}
        self._settings_cache = {}
        self._last_cache_update = None
        self._cache_lifetime = 60  # detik
        
    def init_db(self) -> None:
        """Inisialisasi database"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS schedules
                         (id INTEGER PRIMARY KEY, day TEXT, time TEXT, audio_path TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS settings
                         (key TEXT PRIMARY KEY, value TEXT)''')
            conn.commit()
            conn.close()
            log_info("Database diinisialisasi")
        except Exception as e:
            log_error(f"Gagal inisialisasi database: {e}")
            raise

    def is_database_empty(self) -> bool:
        """Cek apakah database kosong"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM schedules")
            count = c.fetchone()[0]
            conn.close()
            is_empty = count == 0
            if is_empty:
                log_info("Database kosong")
            return is_empty
        except Exception as e:
            log_error(f"Gagal cek database kosong: {e}")
            return True

    def calculate_file_hash(self, filepath: str) -> str:
        """Hitung hash SHA256 dari file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            log_error(f"Gagal menghitung hash {filepath}: {e}")
            return None

    def get_github_file_hashes(self) -> dict:
        """Daftar hash file dari repo GitHub"""
        return {
            "bel_masuk.mp3": "dummy_hash_1",
            "bel_istirahat.mp3": "dummy_hash_2",
            "bel_pulang.mp3": "dummy_hash_3"
        }

    def clone_or_update_audio(self) -> bool:
        """Clone atau update audio dari GitHub ke folder default"""
        try:
            os.makedirs(AUDIO_DIR, exist_ok=True)
            
            if os.path.exists(DEFAULT_AUDIO_DIR):
                if not os.listdir(DEFAULT_AUDIO_DIR):
                    log_info("Folder audio/default kosong. Menghapus...")
                    os.rmdir(DEFAULT_AUDIO_DIR)
                else:
                    try:
                        log_info("Melakukan git pull untuk update audio...")
                        result = subprocess.run(
                            ["git", "-C", DEFAULT_AUDIO_DIR, "pull"],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        log_info(f"Update audio berhasil: {result.stdout}")
                        return True
                    except subprocess.CalledProcessError as e:
                        log_warning(f"Update gagal: {e.stderr}. Clone ulang.")
                        shutil.rmtree(DEFAULT_AUDIO_DIR)
            
            log_info("Cloning audio dari GitHub...")
            result = subprocess.run(
                ["git", "clone", "--depth", "1", REPO_URL, DEFAULT_AUDIO_DIR],
                capture_output=True,
                text=True,
                check=True
            )
            
            audio_source = os.path.join(DEFAULT_AUDIO_DIR, "audio")
            if os.path.exists(audio_source):
                for item in os.listdir(audio_source):
                    src = os.path.join(audio_source, item)
                    dst = os.path.join(DEFAULT_AUDIO_DIR, item)
                    if os.path.isfile(src):
                        shutil.move(src, dst)
                os.rmdir(audio_source)
            
            log_info("Clone audio berhasil")
            return True
        except Exception as e:
            log_error(f"Clone audio gagal: {e}")
            os.makedirs(DEFAULT_AUDIO_DIR, exist_ok=True)
            return False

    def insert_dummy_data(self) -> None:
        """Masukkan data dummy"""
        try:
            self.clone_or_update_audio()
            for item in os.listdir(DEFAULT_AUDIO_DIR):
                src = os.path.join(DEFAULT_AUDIO_DIR, item)
                dst = os.path.join(AUDIO_DIR, item)
                if os.path.isfile(src) and not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    log_info(f"File default disalin: {item}")
            
            dummy_schedules = [
                ("Senin", "06:10", os.path.join(AUDIO_DIR, "Upacara.mp3")),
                ("Senin", "06:45", os.path.join(AUDIO_DIR, "Pembuka.mp3")),
                ("Selasa", "06:10", os.path.join(AUDIO_DIR, "Upacara.mp3")),
                ("Rabu", "06:10", os.path.join(AUDIO_DIR, "Upacara.mp3")),
                ("Kamis", "06:10", os.path.join(AUDIO_DIR, "Upacara.mp3")),
                ("Jumat", "06:10", os.path.join(AUDIO_DIR, "Upacara.mp3")),
                ("Sabtu", "06:10", os.path.join(AUDIO_DIR, "Akhir Pekan.mp3")),
            ]
            
            for _, _, path in dummy_schedules:
                if not os.path.exists(path):
                    with open(path, "w") as f:
                        f.write("dummy")
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.executemany("INSERT INTO schedules (day, time, audio_path) VALUES (?, ?, ?)", dummy_schedules)
            conn.commit()
            conn.close()
            log_info("Data dummy ditambahkan")
        except Exception as e:
            log_error(f"Gagal insert dummy data: {e}")
            raise

    def get_schedules(self, force_refresh=False) -> dict:
        """Ambil semua jadwal dengan caching"""
        now = time_module.time()
        if (force_refresh or 
            self._last_cache_update is None or 
            now - self._last_cache_update > self._cache_lifetime):
            
            try:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("SELECT day, time, audio_path FROM schedules ORDER BY day, time")
                rows = c.fetchall()
                conn.close()
                
                schedule = {}
                for day, schedule_time, path in rows:
                    schedule.setdefault(day, []).append((schedule_time, path))
                
                self._schedule_cache = schedule
                self._last_cache_update = now
                return schedule
            except Exception as e:
                log_error(f"Gagal mengambil jadwal: {e}")
                return self._schedule_cache
        else:
            return self._schedule_cache

    def add_schedule(self, day: str, schedule_time: str, path: str) -> bool:
        """Tambah jadwal baru"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO schedules (day, time, audio_path) VALUES (?, ?, ?)",
                      (day, schedule_time, path))
            conn.commit()
            conn.close()
            log_info(f"Jadwal ditambahkan: {day} {schedule_time} -> {path}")
            self._schedule_cache = {}  # Invalidate cache
            return True
        except Exception as e:
            log_error(f"Gagal tambah jadwal: {e}")
            return False

    def delete_day(self, day: str) -> bool:
        """Hapus semua jadwal hari tertentu"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM schedules WHERE day=?", (day,))
            conn.commit()
            conn.close()
            log_info(f"Jadwal hari {day} dihapus")
            self._schedule_cache = {}  # Invalidate cache
            return True
        except Exception as e:
            log_error(f"Gagal hapus jadwal hari {day}: {e}")
            return False

    def delete_schedule(self, day: str, schedule_time: str, audio_path: str) -> bool:
        """Hapus jadwal spesifik"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM schedules WHERE day=? AND time=? AND audio_path LIKE ?", 
                      (day, schedule_time, f"%{audio_path}"))
            conn.commit()
            conn.close()
            log_info(f"Jadwal dihapus: {day} {schedule_time} -> {audio_path}")
            self._schedule_cache = {}  # Invalidate cache
            return True
        except Exception as e:
            log_error(f"Gagal hapus jadwal: {e}")
            return False

    def get_setting(self, key: str) -> str:
        """Ambil setting"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT value FROM settings WHERE key=?", (key,))
            result = c.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            log_error(f"Gagal ambil setting {key}: {e}")
            return None

    def set_setting(self, key: str, value: str) -> bool:
        """Simpan setting"""
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
            log_info(f"Setting disimpan: {key} = {value}")
            return True
        except Exception as e:
            log_error(f"Gagal simpan setting: {e}")
            return False

    def reset_to_default(self) -> bool:
        """Reset ke konfigurasi default"""
        try:
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM schedules")
            conn.execute("DELETE FROM settings WHERE key='autostart'")
            conn.commit()
            conn.close()

            audio_dir = AUDIO_DIR
            for item in os.listdir(audio_dir):
                item_path = os.path.join(audio_dir, item)
                if item != "default":
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)

            default_audio_dir = DEFAULT_AUDIO_DIR
            if os.path.exists(default_audio_dir):
                for f in os.listdir(default_audio_dir):
                    src = os.path.join(default_audio_dir, f)
                    dst = os.path.join(audio_dir, f)
                    if os.path.isfile(src) and not os.path.exists(dst):
                        shutil.copy2(src, dst)

            self.insert_dummy_data()
            log_info("Aplikasi direset ke konfigurasi default.")
            self._schedule_cache = {}  # Invalidate cache
            return True
        except Exception as e:
            log_error(f"Gagal reset ke default: {e}")
            return False

# Instance global
data_manager = DataManager()