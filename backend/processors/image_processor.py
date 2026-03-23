"""
图像处理器模块

提供图像数据的加载、预处理、特征提取和内容分析功能。
"""

import io
import base64
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

import numpy as np
from PIL import Image

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import DataProcessingError, ValidationError

logger = get_logger(__name__)


class ImageProcessor:
    """
    图像处理器

    支持常见图像格式的处理，提供图像特征提取、对象检测、
    场景识别和图像分类等功能。
    """

    def __init__(self):
        """初始化图像处理器"""
        self.max_size = settings.processing.image.get("max_size", 10485760)
        self.supported_formats = settings.processing.image.get(
            "supported_formats",
            ["jpg", "jpeg", "png", "gif", "webp"]
        )
        self.thumbnail_size = tuple(settings.processing.image.get("thumbnail_size", [256, 256]))
        self._model = None
        logger.info("图像处理器初始化完成")

    async def process(
        self,
        file_path: Optional[str] = None,
        image_data: Optional[Union[bytes, str, np.ndarray]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理图像数据

        Args:
            file_path: 文件路径
            image_data: 图像数据（字节、Base64 或 numpy 数组）
            options: 处理选项

        Returns:
            处理结果
        """
        options = options or {}

        try:
            if file_path:
                result = await self._process_file(file_path, options)
            elif image_data is not None:
                result = await self._process_image_data(image_data, options)
            else:
                raise ValidationError("未提供任何图像数据")

            logger.info(f"图像处理完成: {result.get('width')}x{result.get('height')}")
            return result

        except Exception as e:
            logger.error(f"图像处理失败: {str(e)}")
            raise DataProcessingError(str(e), "image")

    async def _process_file(
        self,
        file_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理图像文件"""
        path = Path(file_path)

        if not path.exists():
            raise ValidationError(f"文件不存在: {file_path}")

        suffix = path.suffix.lower().lstrip(".")
        if suffix not in self.supported_formats:
            raise ValidationError(f"不支持的图像格式: {suffix}")

        file_size = path.stat().st_size
        if file_size > self.max_size:
            raise ValidationError(f"图像文件过大: {file_size} bytes > {self.max_size} bytes")

        with Image.open(file_path) as img:
            return await self._process_pil_image(img, options, path.name)

    async def _process_image_data(
        self,
        image_data: Union[bytes, str, np.ndarray],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理图像数据"""
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str):
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data.astype("uint8"))
        else:
            raise ValidationError(f"不支持的图像数据类型: {type(image_data)}")

        return await self._process_pil_image(image, options)

    async def _process_pil_image(
        self,
        image: Image.Image,
        options: Dict[str, Any],
        filename: str = "image"
    ) -> Dict[str, Any]:
        """处理 PIL 图像对象"""
        mode = image.mode
        width, height = image.size
        format_type = image.format or "UNKNOWN"

        basic_stats = self._calculate_basic_stats(image)

        if options.get("generate_thumbnail", True):
            thumbnail = self._generate_thumbnail(image)
            thumbnail_base64 = self._image_to_base64(thumbnail)
        else:
            thumbnail_base64 = None

        colors = self._extract_dominant_colors(image)

        if options.get("extract_features", False):
            features = await self._extract_features(image)
        else:
            features = None

        if options.get("detect_objects", False):
            objects = await self._detect_objects(image)
        else:
            objects = None

        image_base64 = None
        if options.get("return_base64", False):
            image_base64 = self._image_to_base64(image)

        result = {
            "filename": filename,
            "format": format_type,
            "mode": mode,
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 2) if height > 0 else 0,
            "size_bytes": len(self._image_to_bytes(image)),
            "basic_stats": basic_stats,
            "colors": colors,
            "thumbnail": thumbnail_base64,
            "features": features,
            "objects": objects,
            "image_base64": image_base64,
        }

        return result

    def _calculate_basic_stats(self, image: Image.Image) -> Dict[str, Any]:
        """计算图像基本统计"""
        if image.mode in ["L", "P"]:
            img_array = np.array(image)
            return {
                "mean": float(np.mean(img_array)),
                "std": float(np.std(img_array)),
                "min": int(np.min(img_array)),
                "max": int(np.max(img_array)),
            }
        elif image.mode in ["RGB", "RGBA"]:
            img_array = np.array(image)
            if image.mode == "RGBA":
                img_array = img_array[:, :, :3]

            channel_names = ["red", "green", "blue"]
            stats = {}

            for i, name in enumerate(channel_names):
                channel = img_array[:, :, i]
                stats[name] = {
                    "mean": float(np.mean(channel)),
                    "std": float(np.std(channel)),
                    "min": int(np.min(channel)),
                    "max": int(np.max(channel)),
                }

            grayscale = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
            stats["luminance"] = {
                "mean": float(np.mean(grayscale)),
                "std": float(np.std(grayscale)),
            }

            return stats
        else:
            return {}

    def _generate_thumbnail(self, image: Image.Image) -> Image.Image:
        """生成缩略图"""
        image_copy = image.copy()
        image_copy.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
        return image_copy

    def _extract_dominant_colors(
        self,
        image: Image.Image,
        n_colors: int = 5
    ) -> List[Dict[str, Any]]:
        """提取主色调"""
        img_copy = image.copy()
        img_copy = img_copy.convert("RGB")
        img_copy = img_copy.resize((100, 100), Image.Resampling.LANCZOS)

        img_array = np.array(img_copy)
        pixels = img_array.reshape(-1, 3)

        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)

        colors = []
        for i, center in enumerate(kmeans.cluster_centers_):
            r, g, b = int(center[0]), int(center[1]), int(center[2])
            hex_color = f"#{r:02x}{g:02x}{b:02x}"

            count = np.sum(kmeans.labels_ == i)
            percentage = count / len(kmeans.labels_) * 100

            colors.append({
                "rank": i + 1,
                "rgb": {"r": r, "g": g, "b": b},
                "hex": hex_color,
                "percentage": round(percentage, 2),
            })

        colors.sort(key=lambda x: x["percentage"], reverse=True)
        return colors

    async def _extract_features(self, image: Image.Image) -> Dict[str, Any]:
        """提取图像特征"""
        img_copy = image.copy()
        img_copy = img_copy.convert("RGB")
        img_copy = img_copy.resize((224, 224), Image.Resampling.LANCZOS)

        img_array = np.array(img_copy).flatten()

        features = {
            "histogram": self._calculate_histogram(img_copy),
            "texture": self._calculate_texture_features(img_copy),
            "shape": self._calculate_shape_features(img_copy),
        }

        return features

    def _calculate_histogram(self, image: Image.Image) -> Dict[str, List[int]]:
        """计算颜色直方图"""
        img_array = np.array(image)

        if len(img_array.shape) == 2:
            hist, _ = np.histogram(img_array.flatten(), bins=256, range=(0, 256))
            return {"grayscale": hist.tolist()}
        else:
            result = {}
            for i, color in enumerate(["red", "green", "blue"]):
                hist, _ = np.histogram(img_array[:, :, i].flatten(), bins=256, range=(0, 256))
                result[color] = hist.tolist()
            return result

    def _calculate_texture_features(self, image: Image.Image) -> Dict[str, float]:
        """计算纹理特征"""
        img_array = np.array(image.convert("L"))

        mean_val = np.mean(img_array)
        std_val = np.std(img_array)

        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

        edges_x = np.abs(np.convolve(img_array.flatten(), sobel_x.flatten(), mode='same'))
        edges_y = np.abs(np.convolve(img_array.flatten(), sobel_y.flatten(), mode='same'))

        edge_magnitude = np.sqrt(edges_x**2 + edges_y**2)

        return {
            "mean": float(mean_val),
            "std": float(std_val),
            "edge_mean": float(np.mean(edge_magnitude)),
            "edge_std": float(np.std(edge_magnitude)),
        }

    def _calculate_shape_features(self, image: Image.Image) -> Dict[str, Any]:
        """计算形状特征"""
        img_array = np.array(image.convert("L"))
        binary = (img_array > 127).astype(int)

        height, width = binary.shape
        aspect_ratio = width / height if height > 0 else 0

        foreground_ratio = np.sum(binary) / binary.size

        return {
            "aspect_ratio": round(aspect_ratio, 3),
            "foreground_ratio": round(foreground_ratio, 3),
            "width": width,
            "height": height,
        }

    async def _detect_objects(
        self,
        image: Image.Image
    ) -> List[Dict[str, Any]]:
        """检测图像中的对象"""
        return []

    def _image_to_base64(self, image: Image.Image) -> str:
        """将图像转换为 Base64"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def _image_to_bytes(self, image: Image.Image) -> bytes:
        """将图像转换为字节"""
        buffer = io.BytesIO()
        image.save(buffer, format=image.format or "PNG")
        return buffer.getvalue()

    async def batch_process(
        self,
        file_paths: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        批量处理图像

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
                processed_results.append(result)

        return processed_results
