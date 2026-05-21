"""
Logging system for Mini-ERP
Provides structured logging with file rotation and console output
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from .config import LOGGING_CONFIG

class ERPLogger:
    """Centralized logging for the ERP system"""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.log_dir = LOGGING_CONFIG['log_dir']
        self.log_level = getattr(logging, LOGGING_CONFIG['log_level'])
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name"""
        if name in self._loggers:
            return self._loggers[name]
        
        logger = logging.Logger(name, level=self.log_level)
        
        # File handler with rotation
        log_file = self.log_dir / f"{name}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOGGING_CONFIG['max_log_size_mb'] * 1024 * 1024,
            backupCount=LOGGING_CONFIG['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        self._loggers[name] = logger
        return logger

# Global logger instance
_logger_instance = ERPLogger()

def get_logger(name: str = 'erp') -> logging.Logger:
    """Get a logger instance"""
    return _logger_instance.get_logger(name)

# Convenience functions
def log_info(message: str, logger_name: str = 'erp'):
    """Log info message"""
    get_logger(logger_name).info(message)

def log_error(message: str, logger_name: str = 'erp', exc_info=False):
    """Log error message"""
    get_logger(logger_name).error(message, exc_info=exc_info)

def log_warning(message: str, logger_name: str = 'erp'):
    """Log warning message"""
    get_logger(logger_name).warning(message)

def log_debug(message: str, logger_name: str = 'erp'):
    """Log debug message"""
    get_logger(logger_name).debug(message)

def log_critical(message: str, logger_name: str = 'erp', exc_info=False):
    """Log critical message"""
    get_logger(logger_name).critical(message, exc_info=exc_info)
