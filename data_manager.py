# data_manager.py
import sqlite3
import os
import shutil
import subprocess
import hashlib
from config import __version__
from logger import log_error, log_info, log_warning

DB = "bell.db"
DEFAULT_AUDIO_DIR = os.path.join("audio", "default")
REPO_URL = "https://github.com/rafacraft1/N-tend-Bell-Edu.git"

def init_db():
    """Inisialisasi database"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS schedules
                 (id INTEGER PRIMARY KEY, day TEXT, time TEXT, audio_path TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value TEXT)''')
    conn.commit()
    conn.close()
    log_info("Database diinisialisasi")

def is_database_empty():
    """Cek apakah database kosong"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM schedules")
    count = c.fetchone()[0]
    conn.close()
    is_empty = count == 0
    if is_empty:
        log_info("Database kosong")
    return is_empty

def calculate_file_hash(filepath):
    """Hitung hash SHA256 dari file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        log_error(f"Gagal menghitung hash {filepath}: {e}")
        return None

def get_github_file_hashes():
    """Daftar hash file dari repo GitHub (untuk validasi)"""
    return {
        "bel_masuk.mp3": "dummy_hash_1",
        "bel_istirahat.mp3": "dummy_hash_2",
        "bel_pulang.mp3": "dummy_hash_3"
    }

def clone_or_update_audio():
    """Clone atau update audio dari GitHub ke folder default"""
    os.makedirs("audio", exist_ok=True)
    if os.path.exists(DEFAULT_AUDIO_DIR):
        if not os.listdir(DEFAULT_AUDIO_DIR):
            log_info("Folder audio/default kosong. Menghapus...")
            os.rmdir(DEFAULT_AUDIO_DIR)
        else:
            try:
                log_info("Melakukan git pull untuk update audio...")
                subprocess.run(["git", "-C", DEFAULT_AUDIO_DIR, "pull"], check=True, stdout=subprocess.DEVNULL)
                log_info("Audio diperbarui.")
                return
            except Exception as e:
                log_warning(f"Update gagal: {e}. Clone ulang.")
                shutil.rmtree(DEFAULT_AUDIO_DIR)
    try:
        log_info("Cloning audio dari GitHub...")
        subprocess.run([
            "git", "clone", "--depth", "1", REPO_URL, DEFAULT_AUDIO_DIR
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        audio_source = os.path.join(DEFAULT_AUDIO_DIR, "audio")
        if os.path.exists(audio_source):
            for item in os.listdir(audio_source):
                src = os.path.join(audio_source, item)
                dst = os.path.join(DEFAULT_AUDIO_DIR, item)
                if os.path.isfile(src):
                    shutil.move(src, dst)
            os.rmdir(audio_source)
        log_info("Clone audio berhasil")
    except Exception as e:
        log_error(f"Clone audio gagal: {e}")
        os.makedirs(DEFAULT_AUDIO_DIR, exist_ok=True)

def insert_dummy_data():
    """Masukkan data dummy"""
    clone_or_update_audio()
    for item in os.listdir(DEFAULT_AUDIO_DIR):
        src = os.path.join(DEFAULT_AUDIO_DIR, item)
        dst = os.path.join("audio", item)
        if os.path.isfile(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            log_info(f"File default disalin: {item}")
    dummy_schedules = [
        ("Senin", "06:10", os.path.join("audio", "Upacara.mp3")),
        ("Senin", "06:45", os.path.join("audio", "Pembuka.mp3")),
        ("Selasa", "06:10", os.path.join("audio", "Upacara.mp3")),
        ("Rabu", "06:10", os.path.join("audio", "Upacara.mp3")),
        ("Kamis", "06:10", os.path.join("audio", "Upacara.mp3")),
        ("Jumat", "06:10", os.path.join("audio", "Upacara.mp3")),
        ("Sabtu", "06:10", os.path.join("audio", "Akhir Pekan.mp3")),
    ]
    for _, _, path in dummy_schedules:
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("dummy")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executemany("INSERT INTO schedules (day, time, audio_path) VALUES (?, ?, ?)", dummy_schedules)
    conn.commit()
    conn.close()
    log_info("Data dummy ditambahkan")

def get_schedules():
    """Ambil semua jadwal"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT day, time, audio_path FROM schedules ORDER BY day, time")
    rows = c.fetchall()
    conn.close()
    schedule = {}
    for day, time, path in rows:
        schedule.setdefault(day, []).append((time, path))
    return schedule

def add_schedule(day, time, path):
    """Tambah jadwal baru"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO schedules (day, time, audio_path) VALUES (?, ?, ?)",
              (day, time, path))
    conn.commit()
    conn.close()
    log_info(f"Jadwal ditambahkan: {day} {time} -> {path}")

def delete_day(day):
    """Hapus semua jadwal hari tertentu"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM schedules WHERE day=?", (day,))
    conn.commit()
    conn.close()
    log_info(f"Jadwal hari {day} dihapus")

def delete_schedule(day, time, audio_path):
    """Hapus jadwal spesifik"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM schedules WHERE day=? AND time=? AND audio_path LIKE ?", 
              (day, time, f"%{audio_path}"))
    conn.commit()
    conn.close()
    log_info(f"Jadwal dihapus: {day} {time} -> {audio_path}")

def get_setting(key):
    """Ambil setting"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def set_setting(key, value):
    """Simpan setting"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
    log_info(f"Setting disimpan: {key} = {value}")

def reset_to_default():
    """Reset ke konfigurasi default"""
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM schedules")
    conn.execute("DELETE FROM settings WHERE key='autostart'")
    conn.commit()
    conn.close()

    audio_dir = "audio"
    for item in os.listdir(audio_dir):
        item_path = os.path.join(audio_dir, item)
        if item != "default":
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    default_audio_dir = os.path.join(audio_dir, "default")
    if os.path.exists(default_audio_dir):
        for f in os.listdir(default_audio_dir):
            src = os.path.join(default_audio_dir, f)
            dst = os.path.join(audio_dir, f)
            if os.path.isfile(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)

    insert_dummy_data()
    log_info("Aplikasi direset ke konfigurasi default.")