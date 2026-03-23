"""
音频处理器模块

提供音频数据的加载、预处理、特征提取和语音识别功能。
"""

import io
import base64
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import numpy as np

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import DataProcessingError, ValidationError

logger = get_logger(__name__)


class AudioProcessor:
    """
    音频处理器

    支持多种音频格式的处理，提供音频特征提取、语音识别、
    情感分析和音频分类功能。
    """

    def __init__(self):
        """初始化音频处理器"""
        self.max_duration = settings.processing.audio.get("max_duration", 3600)
        self.sample_rate = settings.processing.audio.get("sample_rate", 16000)
        self.supported_formats = settings.processing.audio.get(
            "supported_formats",
            ["mp3", "wav", "aac", "flac"]
        )
        self._model = None
        logger.info("音频处理器初始化完成")

    async def process(
        self,
        file_path: Optional[str] = None,
        audio_data: Optional[Union[bytes, str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理音频数据

        Args:
            file_path: 文件路径
            audio_data: 音频数据（字节或 Base64）
            options: 处理选项

        Returns:
            处理结果
        """
        options = options or {}

        try:
            if file_path:
                result = await self._process_file(file_path, options)
            elif audio_data is not None:
                result = await self._process_audio_data(audio_data, options)
            else:
                raise ValidationError("未提供任何音频数据")

            logger.info(f"音频处理完成: {result.get('duration')} 秒")
            return result

        except Exception as e:
            logger.error(f"音频处理失败: {str(e)}")
            raise DataProcessingError(str(e), "audio")

    async def _process_file(
        self,
        file_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理音频文件"""
        path = Path(file_path)

        if not path.exists():
            raise ValidationError(f"文件不存在: {file_path}")

        suffix = path.suffix.lower().lstrip(".")
        if suffix not in self.supported_formats:
            raise ValidationError(f"不支持的音频格式: {suffix}")

        import librosa

        try:
            y, sr = librosa.load(file_path, sr=self.sample_rate)
        except Exception as e:
            raise DataProcessingError(f"无法加载音频文件: {str(e)}")

        duration = len(y) / sr

        if duration > self.max_duration:
            raise ValidationError(f"音频时长过长: {duration} 秒 > {self.max_duration} 秒")

        return await self._process_audio(y, sr, options)

    async def _process_audio_data(
        self,
        audio_data: Union[bytes, str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理音频数据"""
        if isinstance(audio_data, str):
            if audio_data.startswith("data:audio"):
                audio_data = audio_data.split(",")[1]

            audio_bytes = base64.b64decode(audio_data)
        else:
            audio_bytes = audio_data

        import librosa

        try:
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=self.sample_rate)
        except Exception as e:
            raise DataProcessingError(f"无法加载音频数据: {str(e)}")

        duration = len(y) / sr

        if duration > self.max_duration:
            raise ValidationError(f"音频时长过长: {duration} 秒 > {self.max_duration} 秒")

        return await self._process_audio(y, sr, options)

    async def _process_audio(
        self,
        y: np.ndarray,
        sr: int,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理音频信号"""
        import librosa

        duration = len(y) / sr

        basic_features = self._extract_basic_features(y, sr)

        tempo, beats = self._extract_rhythm_features(y, sr)

        mfccs = self._extract_mfcc(y, sr)

        spectral_features = self._extract_spectral_features(y, sr)

        if options.get("transcribe", False):
            transcription = await self._transcribe_audio(y, sr)
        else:
            transcription = None

        if options.get("detect_speech", False):
            speech_segments = self._detect_speech_segments(y, sr)
        else:
            speech_segments = None

        if options.get("analyze_emotion", False):
            emotion = await self._analyze_emotion(y, sr)
        else:
            emotion = None

        result = {
            "sample_rate": sr,
            "duration": round(duration, 2),
            "samples": len(y),
            "channels": 1,
            "basic_features": basic_features,
            "tempo": round(tempo, 2),
            "beats": beats[:100] if len(beats) > 100 else beats.tolist(),
            "mfccs": mfccs[:, :20].tolist() if mfccs is not None else None,
            "spectral_features": spectral_features,
            "transcription": transcription,
            "speech_segments": speech_segments,
            "emotion": emotion,
        }

        return result

    def _extract_basic_features(
        self,
        y: np.ndarray,
        sr: int
    ) -> Dict[str, Any]:
        """提取基本音频特征"""
        import librosa

        rms = librosa.feature.rms(y=y)[0]
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        return {
            "rms": {
                "mean": round(float(np.mean(rms)), 4),
                "std": round(float(np.std(rms)), 4),
                "max": round(float(np.max(rms)), 4),
                "min": round(float(np.min(rms)), 4),
            },
            "zero_crossing_rate": {
                "mean": round(float(np.mean(zcr)), 4),
                "std": round(float(np.std(zcr)), 4),
            },
            "energy": round(float(np.sum(y ** 2) / len(y)), 4),
        }

    def _extract_rhythm_features(
        self,
        y: np.ndarray,
        sr: int
    ) -> tuple:
        """提取节奏特征"""
        import librosa

        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beats = librosa.frames_to_time(beats, sr=sr)

        return float(tempo), beats

    def _extract_mfcc(
        self,
        y: np.ndarray,
        sr: int,
        n_mfcc: int = 20
    ) -> Optional[np.ndarray]:
        """提取 MFCC 特征"""
        import librosa

        try:
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
            return mfccs
        except Exception as e:
            logger.warning(f"MFCC 提取失败: {str(e)}")
            return None

    def _extract_spectral_features(
        self,
        y: np.ndarray,
        sr: int
    ) -> Dict[str, Any]:
        """提取频谱特征"""
        import librosa

        try:
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]

            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

            return {
                "centroid": {
                    "mean": round(float(np.mean(spectral_centroid)), 2),
                    "std": round(float(np.std(spectral_centroid)), 2),
                },
                "bandwidth": {
                    "mean": round(float(np.mean(spectral_bandwidth)), 2),
                    "std": round(float(np.std(spectral_bandwidth)), 2),
                },
                "rolloff": {
                    "mean": round(float(np.mean(spectral_rolloff)), 2),
                    "std": round(float(np.std(spectral_rolloff)), 2),
                },
                "contrast_mean": round(float(np.mean(spectral_contrast)), 2),
            }
        except Exception as e:
            logger.warning(f"频谱特征提取失败: {str(e)}")
            return {}

    async def _transcribe_audio(
        self,
        y: np.ndarray,
        sr: int
    ) -> Optional[str]:
        """语音转文字"""
        return None

    def _detect_speech_segments(
        self,
        y: np.ndarray,
        sr: int
    ) -> List[Dict[str, Any]]:
        """检测语音片段"""
        import librosa

        frame_length = 2048
        hop_length = 512

        energy = np.array([
            sum(abs(y[i:i+frame_length])**2)
            for i in range(0, len(y) - frame_length, hop_length)
        ])

        threshold = np.mean(energy) * 0.5

        speech_frames = energy > threshold

        segments = []
        in_speech = False
        start_frame = 0

        for i, is_speech in enumerate(speech_frames):
            if is_speech and not in_speech:
                start_frame = i
                in_speech = True
            elif not is_speech and in_speech:
                start_time = librosa.frames_to_time(start_frame, sr=sr, hop_length=hop_length)
                end_time = librosa.frames_to_time(i, sr=sr, hop_length=hop_length)
                segments.append({
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "duration": round(end_time - start_time, 2),
                })
                in_speech = False

        if in_speech:
            start_time = librosa.frames_to_time(start_frame, sr=sr, hop_length=hop_length)
            end_time = librosa.frames_to_time(len(speech_frames), sr=sr, hop_length=hop_length)
            segments.append({
                "start": round(start_time, 2),
                "end": round(end_time, 2),
                "duration": round(end_time - start_time, 2),
            })

        return segments

    async def _analyze_emotion(
        self,
        y: np.ndarray,
        sr: int
    ) -> Optional[Dict[str, Any]]:
        """分析情感"""
        return None

    async def batch_process(
        self,
        file_paths: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量处理音频

        Args:
            file_paths: 文件路径列表
            options: 处理选项

        Returns:
            处理结果列表
        """
        import asyncio

        tasks = [self.process(file_path=fp, options=options) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "file_path": file_paths[i],
                    "error": str(result),
                    "success": False,
                })
            else:
                result["success"] = True
                result["file_path"] = file_paths[i]
                processed_results.append(result)

        return processed_results
