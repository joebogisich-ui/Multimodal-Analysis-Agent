"""
文本处理器模块

提供文本数据的读取、清洗、分词、特征提取等功能。
"""

import json
import re
import csv
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import pandas as pd

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import DataProcessingError, ValidationError

logger = get_logger(__name__)


class TextProcessor:
    """
    文本处理器

    支持多种文本格式的处理，包括纯文本、JSON、CSV、Markdown 等。
    提供文本清洗、分词、实体识别和语义向量化功能。
    """

    def __init__(self):
        """初始化文本处理器"""
        self.max_length = settings.processing.text.get("max_length", 50000)
        self.languages = settings.processing.text.get("languages", ["zh", "en"])
        logger.info("文本处理器初始化完成")

    async def process(
        self,
        file_path: Optional[str] = None,
        text: Optional[str] = None,
        data: Optional[Union[Dict, List, pd.DataFrame]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理文本数据

        Args:
            file_path: 文件路径
            text: 文本内容
            data: 结构化数据
            options: 处理选项

        Returns:
            处理结果
        """
        options = options or {}

        try:
            if file_path:
                result = await self._process_file(file_path, options)
            elif text:
                result = await self._process_text(text, options)
            elif data is not None:
                result = await self._process_data(data, options)
            else:
                raise ValidationError("未提供任何输入数据")

            logger.info(f"文本处理完成，结果包含 {len(result.get('chunks', []))} 个文本块")
            return result

        except Exception as e:
            logger.error(f"文本处理失败: {str(e)}")
            raise DataProcessingError(str(e), "text")

    async def _process_file(
        self,
        file_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理文本文件"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".txt":
            return await self._process_txt(file_path, options)
        elif suffix == ".json":
            return await self._process_json(file_path, options)
        elif suffix in [".csv", ".xlsx", ".xls"]:
            return await self._process_table(file_path, options)
        elif suffix == ".md":
            return await self._process_markdown(file_path, options)
        else:
            raise ValidationError(f"不支持的文本格式: {suffix}")

    async def _process_txt(
        self,
        file_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理纯文本文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        return await self._process_text(text, options)

    async def _process_json(
        self,
        file_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理 JSON 文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, str):
            return await self._process_text(data, options)
        elif isinstance(data, list):
            texts = [str(item) for item in data]
            combined_text = " ".join(texts)
            return await self._process_text(combined_text, options)
        elif isinstance(data, dict):
            texts = self._flatten_dict(data)
            combined_text = " ".join(texts)
            return await self._process_text(combined_text, options)
        else:
            raise ValidationError("无法处理的 JSON 结构")

    async def _process_table(
        self,
        file_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理表格文件"""
        suffix = Path(file_path).suffix.lower()

        if suffix == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        text_column = options.get("text_column")
        if text_column and text_column in df.columns:
            texts = df[text_column].astype(str).tolist()
        else:
            texts = []
            for col in df.columns:
                if df[col].dtype == "object":
                    texts.extend(df[col].astype(str).tolist())

        combined_text = " ".join(texts)
        return await self._process_text(combined_text, options)

    async def _process_markdown(
        self,
        file_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理 Markdown 文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        text = self._clean_markdown(text)
        return await self._process_text(text, options)

    async def _process_text(
        self,
        text: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理文本内容"""
        original_length = len(text)
        text = text[:self.max_length]

        cleaned_text = self._clean_text(text)

        language = self._detect_language(cleaned_text)

        tokens = self._tokenize(cleaned_text, language)

        sentences = self._split_sentences(cleaned_text, language)

        chunks = self._create_chunks(
            sentences,
            chunk_size=options.get("chunk_size", 500),
            overlap=options.get("overlap", 50)
        )

        word_freq = self._calculate_word_frequency(tokens, language)

        result = {
            "original_text": text[:1000] + "..." if len(text) > 1000 else text,
            "original_length": original_length,
            "processed_length": len(text),
            "language": language,
            "cleaned_text": cleaned_text,
            "tokens": tokens[:100],
            "token_count": len(tokens),
            "sentence_count": len(sentences),
            "chunks": chunks,
            "word_frequency": dict(list(word_freq.items())[:50]),
            "statistics": {
                "chars": len(cleaned_text),
                "words": len(tokens),
                "sentences": len(sentences),
                "avg_word_length": sum(len(w) for w in tokens) / len(tokens) if tokens else 0,
                "avg_sentence_length": len(tokens) / len(sentences) if sentences else 0,
            }
        }

        return result

    async def _process_data(
        self,
        data: Union[Dict, List, pd.DataFrame],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理结构化数据"""
        if isinstance(data, pd.DataFrame):
            return await self._process_dataframe(data, options)
        elif isinstance(data, list):
            return await self._process_list(data, options)
        elif isinstance(data, dict):
            return await self._process_dict(data, options)
        else:
            raise ValidationError(f"不支持的数据类型: {type(data)}")

    async def _process_dataframe(
        self,
        df: pd.DataFrame,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理 DataFrame"""
        texts = []
        for col in df.columns:
            if df[col].dtype == "object":
                texts.extend(df[col].astype(str).tolist())

        combined_text = " ".join(texts)
        result = await self._process_text(combined_text, options)

        result["data_info"] = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }

        return result

    async def _process_list(
        self,
        data: List,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理列表数据"""
        texts = [str(item) for item in data]
        combined_text = " ".join(texts)
        return await self._process_text(combined_text, options)

    async def _process_dict(
        self,
        data: Dict,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理字典数据"""
        texts = self._flatten_dict(data)
        combined_text = " ".join(texts)
        return await self._process_text(combined_text, options)

    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u4e00-\u9fff,.!?;:()（）【】《》""''""、。！？；：]', '', text)
        text = text.strip()
        return text

    def _clean_markdown(self, text: str) -> str:
        """清洗 Markdown"""
        text = re.sub(r'#{1,6}\s+', '', text)
        text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def _flatten_dict(
        self,
        data: Dict,
        parent_key: str = '',
        sep: str = ' '
    ) -> List[str]:
        """扁平化字典"""
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep))
            elif isinstance(v, list):
                items.extend([str(item) for item in v])
            else:
                items.append(str(v))
        return items

    def _detect_language(self, text: str) -> str:
        """检测语言"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(re.findall(r'[\w]', text))

        if total_chars == 0:
            return "unknown"

        chinese_ratio = chinese_chars / total_chars

        if chinese_ratio > 0.3:
            return "zh"
        else:
            return "en"

    def _tokenize(self, text: str, language: str) -> List[str]:
        """分词"""
        if language == "zh":
            try:
                import jieba
                tokens = list(jieba.cut(text))
            except ImportError:
                tokens = list(text)
        else:
            tokens = re.findall(r'\b\w+\b', text.lower())

        tokens = [t for t in tokens if len(t) > 0]
        return tokens

    def _split_sentences(self, text: str, language: str) -> List[str]:
        """分割句子"""
        if language == "zh":
            sentences = re.split(r'[。！？；\n]+', text)
        else:
            sentences = re.split(r'[.!?;:\n]+', text)

        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _create_chunks(
        self,
        sentences: List[str],
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """创建文本块"""
        chunks = []
        current_tokens = []
        current_chunk = []
        chunk_id = 0

        for sentence in sentences:
            sentence_tokens = sentence.split()

            if sum(len(t) for t in current_tokens) + len(sentence_tokens) > chunk_size:
                if current_chunk:
                    chunks.append({
                        "id": chunk_id,
                        "text": " ".join(current_chunk),
                        "token_count": sum(len(t) for t in current_tokens),
                    })
                    chunk_id += 1

                overlap_tokens = []
                if overlap > 0 and current_tokens:
                    for t in reversed(current_tokens):
                        overlap_tokens.insert(0, t)
                        if sum(len(token) for token in overlap_tokens) >= overlap:
                            break

                current_tokens = overlap_tokens
                current_chunk = [" ".join(current_tokens)] if current_tokens else []

            current_tokens.extend(sentence_tokens)
            current_chunk.append(sentence)

        if current_chunk:
            chunks.append({
                "id": chunk_id,
                "text": " ".join(current_chunk),
                "token_count": sum(len(t) for t in current_tokens),
            })

        return chunks

    def _calculate_word_frequency(
        self,
        tokens: List[str],
        language: str,
        top_n: int = 50
    ) -> Dict[str, int]:
        """计算词频"""
        stopwords = self._get_stopwords(language)

        filtered_tokens = [
            t for t in tokens
            if t.lower() not in stopwords and len(t) > 1
        ]

        freq = {}
        for token in filtered_tokens:
            token_lower = token.lower()
            freq[token_lower] = freq.get(token_lower, 0) + 1

        sorted_freq = dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))
        return dict(list(sorted_freq.items())[:top_n])

    def _get_stopwords(self, language: str) -> set:
        """获取停用词"""
        if language == "zh":
            return {
                "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
                "都", "一", "一个", "上", "也", "很", "到", "说", "要",
                "去", "你", "会", "着", "没有", "看", "好", "自己", "这"
            }
        else:
            return {
                "the", "a", "an", "and", "or", "but", "in", "on", "at",
                "to", "for", "of", "with", "by", "from", "is", "are",
                "was", "were", "be", "been", "being", "have", "has",
                "had", "do", "does", "did", "will", "would", "could"
            }
