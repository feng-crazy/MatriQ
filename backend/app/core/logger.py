import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from app.core.config import Settings, get_settings

# 创建logs目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(
    name: str = "matriq",
    log_level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    设置并返回配置好的logger
    
    Args:
        name: logger名称
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径
        
    Returns:
        配置好的logger实例
    """
    settings = get_settings()
    # 获取日志级别
    if log_level is None:
        log_level = settings.log_level
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件handler (如果启用了文件日志)
    if settings.enable_file_logging:
        file_log_name = log_file if log_file else settings.log_file
        file_path = LOG_DIR / file_log_name
        file_handler = logging.handlers.RotatingFileHandler(
            file_path, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 创建默认logger
logger = setup_logger()

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的logger"""
    return setup_logger(name)