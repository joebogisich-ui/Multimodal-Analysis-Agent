"""
视频处理器模块

提供视频数据的加载、帧提取、场景检测和内容分析功能。
"""

import io
import base64
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path

import numpy as np
from PIL import Image

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import DataProcessingError, ValidationError

logger = get_logger(__name__)


class VideoProcessor:
    """
    视频处理器

    支持多种视频格式的处理，提供帧提取、场景检测、视频摘要、
    对象跟踪和动作识别等功能。
    """

    def __init__(self):
        """初始化视频处理器"""
        self.max_duration = settings.processing.video.get("max_duration", 7200)
        self.max_frames = settings.processing.video.get("max_frames", 1000)
        self.thumbnail_interval = settings.processing.video.get("thumbnail_interval", 10)
        self._model = None
        self._capture = None
        logger.info("视频处理器初始化完成")

    async def process(
        self,
        file_path: Optional[str] = None,
        video_data: Optional[Union[bytes, str]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理视频数据

        Args:
            file_path: 文件路径
            video_data: 视频数据（字节或 Base64）
            options: 处理选项

        Returns:
            处理结果
        """
        options = options or {}

        try:
            if file_path:
                result = await self._process_file(file_path, options)
            elif video_data is not None:
                result = await self._process_video_data(video_data, options)
            else:
                raise ValidationError("未提供任何视频数据")

            logger.info(f"视频处理完成: {result.get('duration')} 秒, {result.get('frame_count')} 帧")
            return result

        except Exception as e:
            logger.error(f"视频处理失败: {str(e)}")
            raise DataProcessingError(str(e), "video")

    async def _process_file(
        self,
        file_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理视频文件"""
        import cv2

        path = Path(file_path)

        if not path.exists():
            raise ValidationError(f"文件不存在: {file_path}")

        cap = cv2.VideoCapture(file_path)

        try:
            if not cap.isOpened():
                raise DataProcessingError(f"无法打开视频文件: {file_path}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            if duration > self.max_duration:
                raise ValidationError(f"视频时长过长: {duration} 秒 > {self.max_duration} 秒")

            return await self._process_video_capture(
                cap, fps, frame_count, width, height, duration, options
            )

        finally:
            cap.release()

    async def _process_video_data(
        self,
        video_data: Union[bytes, str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理视频数据"""
        import cv2

        if isinstance(video_data, str):
            if video_data.startswith("data:video"):
                video_data = video_data.split(",")[1]

            video_bytes = base64.b64decode(video_data)
        else:
            video_bytes = video_data

        cap = cv2.VideoCapture(io.BytesIO(video_bytes))

        try:
            if not cap.isOpened():
                raise DataProcessingError("无法打开视频数据")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            if duration > self.max_duration:
                raise ValidationError(f"视频时长过长: {duration} 秒 > {self.max_duration} 秒")

            return await self._process_video_capture(
                cap, fps, frame_count, width, height, duration, options
            )

        finally:
            cap.release()

    async def _process_video_capture(
        self,
        cap,
        fps: float,
        frame_count: int,
        width: int,
        height: int,
        duration: float,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理视频捕获对象"""
        import cv2

        basic_info = {
            "fps": round(fps, 2),
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration": round(duration, 2),
            "resolution": f"{width}x{height}",
            "aspect_ratio": round(width / height, 2) if height > 0 else 0,
        }

        if options.get("extract_thumbnails", True):
            thumbnails = await self._extract_thumbnails(cap, fps, frame_count)
        else:
            thumbnails = []

        if options.get("detect_scenes", True):
            scenes = await self._detect_scenes(cap, fps, frame_count)
        else:
            scenes = []

        if options.get("analyze_motion", True):
            motion = await self._analyze_motion(cap, fps, frame_count)
        else:
            motion = None

        if options.get("extract_keyframes", True):
            keyframes = await self._extract_keyframes(cap, fps, frame_count)
        else:
            keyframes = []

        if options.get("generate_summary", True):
            summary = await self._generate_summary(
                cap, fps, frame_count, thumbnails, scenes
            )
        else:
            summary = None

        result = {
            **basic_info,
            "thumbnails": thumbnails,
            "scenes": scenes,
            "motion": motion,
            "keyframes": keyframes,
            "summary": summary,
        }

        return result

    async def _extract_thumbnails(
        self,
        cap,
        fps: float,
        frame_count: int
    ) -> List[Dict[str, Any]]:
        """提取视频缩略图"""
        import cv2

        interval = max(1, int(self.thumbnail_interval * fps))
        num_thumbnails = min(frame_count // interval, 30)

        thumbnails = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        for i in range(num_thumbnails):
            frame_pos = i * interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)

            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_pos / fps

            thumbnail = self._resize_frame(frame, (160, 90))
            thumbnail_base64 = self._frame_to_base64(thumbnail)

            thumbnails.append({
                "timestamp": round(timestamp, 2),
                "frame_number": frame_pos,
                "image": thumbnail_base64,
            })

        return thumbnails

    async def _detect_scenes(
        self,
        cap,
        fps: float,
        frame_count: int
    ) -> List[Dict[str, Any]]:
        """检测场景变化"""
        import cv2

        if frame_count < 2:
            return []

        sample_interval = max(1, frame_count // 100)

        frames = []
        positions = []

        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        pos = 0

        while pos < frame_count:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(gray)
            positions.append(pos)
            pos += sample_interval

        scenes = []
        threshold = 30.0

        for i in range(1, len(frames)):
            diff = cv2.norm(frames[i], frames[i-1], cv2.NORM_L2)
            mean_diff = diff / frames[i].size

            if mean_diff > threshold:
                scenes.append({
                    "timestamp": round(positions[i] / fps, 2),
                    "frame_number": positions[i],
                    "intensity": round(mean_diff, 4),
                    "type": "cut",
                })

        return scenes[:50]

    async def _analyze_motion(
        self,
        cap,
        fps: float,
        frame_count: int
    ) -> Dict[str, Any]:
        """分析运动"""
        import cv2

        if frame_count < 2:
            return {}

        sample_interval = max(1, int(fps))

        prev_gray = None
        motion_values = []
        timestamps = []

        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_idx = 0

        while frame_idx < frame_count:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                motion = np.sum(diff) / diff.size
                motion_values.append(motion)
                timestamps.append(frame_idx / fps)

            prev_gray = gray
            frame_idx += sample_interval

            for _ in range(sample_interval - 1):
                cap.read()

        if not motion_values:
            return {}

        return {
            "mean_motion": round(float(np.mean(motion_values)), 4),
            "max_motion": round(float(np.max(motion_values)), 4),
            "min_motion": round(float(np.min(motion_values)), 4),
            "std_motion": round(float(np.std(motion_values)), 4),
            "motion_samples": len(motion_values),
            "timestamps": [round(t, 2) for t in timestamps[:100]],
            "motion_values": [round(v, 4) for v in motion_values[:100]],
        }

    async def _extract_keyframes(
        self,
        cap,
        fps: float,
        frame_count: int
    ) -> List[Dict[str, Any]]:
        """提取关键帧"""
        import cv2

        if frame_count < 3:
            return []

        num_keyframes = min(10, frame_count // 10)
        interval = frame_count // num_keyframes

        keyframes = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        for i in range(num_keyframes):
            frame_pos = i * interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)

            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_pos / fps

            resized = self._resize_frame(frame, (320, 180))
            keyframe_base64 = self._frame_to_base64(resized)

            keyframes.append({
                "timestamp": round(timestamp, 2),
                "frame_number": frame_pos,
                "image": keyframe_base64,
            })

        return keyframes

    async def _generate_summary(
        self,
        cap,
        fps: float,
        frame_count: int,
        thumbnails: List[Dict],
        scenes: List[Dict]
    ) -> Dict[str, Any]:
        """生成视频摘要"""
        duration = frame_count / fps if fps > 0 else 0

        summary = {
            "total_duration": round(duration, 2),
            "total_scenes": len(scenes),
            "scene_changes": [],
            "highlights": [],
        }

        if scenes:
            scene_durations = []
            for i, scene in enumerate(scenes):
                if i < len(scenes) - 1:
                    duration_scene = scenes[i + 1]["timestamp"] - scene["timestamp"]
                else:
                    duration_scene = duration - scene["timestamp"]
                scene_durations.append(duration_scene)

            avg_scene_duration = np.mean(scene_durations)
            summary["scene_changes"].append({
                "average_scene_duration": round(avg_scene_duration, 2),
                "scene_count": len(scenes),
            })

        if thumbnails:
            timestamps = [t["timestamp"] for t in thumbnails]
            summary["timeline"] = {
                "start": 0,
                "end": duration,
                "sample_points": timestamps[:20],
            }

        return summary

    def _resize_frame(self, frame: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        """调整帧大小"""
        import cv2
        return cv2.resize(frame, size, interpolation=cv2.INTER_AREA)

    def _frame_to_base64(self, frame: np.ndarray) -> str:
        """将帧转换为 Base64"""
        import cv2
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode()

    async def batch_process(
        self,
        file_paths: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量处理视频

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
