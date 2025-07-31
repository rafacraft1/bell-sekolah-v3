# logger.py
import logging
import os
from constants import LOGS_DIR

# Buat folder logs jika belum ada
os.makedirs(LOGS_DIR, exist_ok=True)

# Konfigurasi logging
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "app.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)-8s - %(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

# Tambahkan console handler untuk debugging
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

def log_debug(msg: str) -> None:
    """Log debug message"""
    logging.debug(msg)

def log_info(msg: str) -> None:
    """Log info message"""
    logging.info(msg)

def log_warning(msg: str) -> None:
    """Log warning message"""
    logging.warning(msg)

def log_error(msg: str) -> None:
    """Log error message"""
    logging.error(msg)

def log_critical(msg: str) -> None:
    """Log critical message"""
    logging.critical(msg)