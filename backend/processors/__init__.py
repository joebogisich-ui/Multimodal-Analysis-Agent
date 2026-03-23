"""
数据处理器模块

提供多模态数据的处理功能，包括文本、图像、音频和视频处理。
"""

from backend.processors.text_processor import TextProcessor
from backend.processors.image_processor import ImageProcessor
from backend.processors.audio_processor import AudioProcessor
from backend.processors.video_processor import VideoProcessor

__all__ = [
    "TextProcessor",
    "ImageProcessor",
    "AudioProcessor",
    "VideoProcessor",
]
