"""Logging module for Monday"""
import logging
import sys
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}[{record.levelname}]{self.RESET}"
        return super().format(record)

def setup_logger(name="Monday"):
    """Setup logger with colored output"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = ColoredFormatter(
        '%(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    logger.addHandler(handler)
    
    return logger

# Global logger instance
logger = setup_logger()

def log_step(step_name: str, details: str = ""):
    """Log a processing step"""
    msg = f"→ {step_name}"
    if details:
        msg += f" | {details}"
    logger.info(msg)

def log_success(message: str):
    """Log success"""
    logger.info(f"✓ {message}")

def log_error(message: str):
    """Log error"""
    logger.error(f"✗ {message}")

def log_file_operation(operation: str, path: str, count: int = 0):
    """Log file operation result"""
    msg = f"📁 {operation} '{path}'"
    if count > 0:
        msg += f" | Found: {count} items"
    logger.info(msg)
