"""
日志系统模块

提供统一的日志记录功能，支持控制台输出和文件记录，
包含日志级别过滤和格式化功能。
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.core.config import settings


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    COLORS = {
        "DEBUG": "\033[36m",      # 青色
        "INFO": "\033[32m",       # 绿色
        "WARNING": "\033[33m",    # 黄色
        "ERROR": "\033[31m",      # 红色
        "CRITICAL": "\033[35m",   # 紫色
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.name = f"\033[34m{record.name}\033[0m"
        return super().format(record)


class FileHandlerWithRotation(logging.handlers.RotatingFileHandler):
    """带轮转功能的文件处理器"""

    def __init__(
        self,
        filename: str,
        maxBytes: int = 10485760,  # 10MB
        backupCount: int = 5,
        encoding: str = "utf-8"
    ):
        """初始化文件处理器"""
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(
            filename,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding
        )


def setup_logging(
    name: Optional[str] = None,
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    配置日志记录器

    Args:
        name: 日志记录器名称，默认为根记录器
        level: 日志级别，默认为配置中的级别
        log_file: 日志文件路径，默认为配置中的路径

    Returns:
        配置好的日志记录器实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, (level or settings.server.log_level).upper()))

    if logger.handlers:
        logger.handlers.clear()

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter(log_format, datefmt=date_format))
    logger.addHandler(console_handler)

    if log_file or settings.logging.file:
        file_path = log_file or settings.logging.file
        file_handler = FileHandlerWithRotation(
            file_path,
            maxBytes=settings.logging.max_bytes,
            backupCount=settings.logging.backup_count
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)


class LogContext:
    """日志上下文管理器，用于添加日志上下文信息"""

    def __init__(self, logger: logging.Logger, **context):
        """
        初始化日志上下文

        Args:
            logger: 日志记录器实例
            **context: 上下文键值对
        """
        self.logger = logger
        self.context = context
        self.old_factory = None

    def __enter__(self):
        """进入上下文"""
        self.old_factory = self.logger.factory
        self.logger.factory = lambda: {**self.old_factory(), **self.context}
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        self.logger.factory = self.old_factory
        return False
