"""
統一的日誌配置
"""
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """設置日誌 - 從環境變數讀取 context name"""
    
    # 從環境變數讀取 context name
    context_name = os.getenv("CONTEXT_NAME", "app")
    
    log_dir = os.getenv("LOG_DIR", "./logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"{context_name}.log")
    error_log_file = os.path.join(log_dir, f"{context_name}_error.log")
    
    logger = logging.getLogger()  # root logger
    logger.setLevel(logging.INFO)
    
    # 避免重複添加
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error File Handler
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info(f"Logger initialized for context: {context_name}")
    logger.info(f"Log file: {log_file}")
    
    return logger
