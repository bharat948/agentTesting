import os
import logging
from logging.handlers import RotatingFileHandler
from app.core.config import settings
import datetime

def setup_logging():
    """Setup global logging configuration"""
    # Create logs directory if it doesn't exist
    logs_dir = settings.LOGS_DIR
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                os.path.join(logs_dir, "app.log"),
                maxBytes=5*1024*1024,  # 5 MB
                backupCount=3
            )
        ]
    )

global_logger = logging.getLogger(__name__)

def get_user_logger(username: str) -> logging.Logger:
    """Get a logger for a specific user"""
    logger_name = f"agent.{username}"
    user_logger = logging.getLogger(logger_name)
    if not user_logger.handlers:
        file_handler = RotatingFileHandler(
            os.path.join(settings.LOGS_DIR, f"{username}.log"),
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        user_logger.addHandler(file_handler)
        user_logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
    return user_logger

class SimpleLogger:
    def __init__(self, log_file='app.log'):
        self.log_file = log_file

    def _log(self, level, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - {level} - {message}\n"
        with open(self.log_file, 'a') as file:
            file.write(log_message)
        print(log_message, end='')

    def info(self, message):
        self._log('INFO', message)

    def warning(self, message):
        self._log('WARNING', message)

    def error(self, message):
        self._log('ERROR', message)

# Function to get a logger instance
def get_user_logger():
    return SimpleLogger()

# Initialize the new logger
logger = SimpleLogger()