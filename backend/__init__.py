"""
多模态数据分析可视化 Agent 系统 - 后端模块

该模块提供系统的核心功能，包括 Agent 协调、多模态处理、
数据分析和可视化生成等组件。
"""

__version__ = "1.0.0"
__author__ = "Multimodal Analysis Team"

from backend.core.config import Settings
from backend.core.logging import setup_logging

__all__ = ["Settings", "setup_logging"]
