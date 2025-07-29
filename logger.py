# logger.py
import logging
import os

# Buat folder logs jika belum ada
os.makedirs("logs", exist_ok=True)

# Konfigurasi logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)-8s - %(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

def log_debug(msg):
    logging.debug(msg)

def log_info(msg):
    logging.info(msg)

def log_warning(msg):
    logging.warning(msg)

def log_error(msg):
    logging.error(msg)

def log_critical(msg):
    logging.critical(msg)