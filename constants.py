# constants.py
import os

# Aplikasi
APP_NAME = "Bell Sekolah Otomatis"
VERSION = "v2.0.0"

# Database
DB_NAME = "bell.db"

# Folder
AUDIO_DIR = "audio"
DEFAULT_AUDIO_DIR = os.path.join(AUDIO_DIR, "default")
LOGS_DIR = "logs"
ASSETS_DIR = "assets"

# File
BELL_ICON = "bell.ico"
#BELL_ICON = "bell.png"
BELL_ICO = "bell.ico"

# GitHub
REPO_URL = "https://github.com/rafacraft1/N-tend-Bell-Edu.git"

# Waktu
SCHEDULE_CHECK_INTERVAL = 30  # detik

# Hari
DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]

# Audio
AUDIO_FORMATS = [".mp3", ".wav", ".ogg"]