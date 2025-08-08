# constants.py
import os

# Direktori
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
DEFAULT_AUDIO_DIR = os.path.join(BASE_DIR, "audio", "default")
LOGS_DIR = BASE_DIR

# File
DB_NAME = os.path.join(BASE_DIR, "bell_sekolah.db")
LOG_FILE = os.path.join(BASE_DIR, "bell_sekolah.log")

# Icon
BELL_ICON = "logo.ico"

# Audio
AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.flac']

# Jadwal
DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# Waktu
SCHEDULE_CHECK_INTERVAL = 30  # detik

# GitHub
REPO_URL = "https://github.com/username/bell-sekolah-audio.git"

# Versi
VERSION = "2.0.0"