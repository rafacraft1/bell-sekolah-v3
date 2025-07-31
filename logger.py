# logger.py
import os
import logging
import logging.handlers
from datetime import datetime
from constants import LOGS_DIR

# Buat folder logs jika belum ada
os.makedirs(LOGS_DIR, exist_ok=True)

# Setup logging
def setup_logger():
    """Setup logger dengan file dan console handler"""
    # Format log
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Buat logger
    logger = logging.getLogger("bell_sekolah")
    logger.setLevel(logging.INFO)
    
    # Hapus handler yang sudah ada untuk menghindari duplikasi
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # File handler dengan rotasi harian
    log_file = os.path.join(LOGS_DIR, f"bell_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, 
        when="midnight", 
        interval=1, 
        backupCount=30
    )
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)
    
    return logger

# Inisialisasi logger
logger = setup_logger()

# Fungsi helper untuk logging
def log_info(message):
    """Log info message"""
    logger.info(message)

def log_error(message):
    """Log error message"""
    logger.error(message)

def log_warning(message):
    """Log warning message"""
    logger.warning(message)