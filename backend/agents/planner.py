"""
任务规划器模块

提供智能任务规划和分解功能，根据用户意图自动生成任务执行计划。
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import ValidationError
from backend.agents.orchestrator import TaskType

logger = get_logger(__name__)


class DataType(str, Enum):
    """数据类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TABULAR = "tabular"
    MIXED = "mixed"


class AnalysisType(str, Enum):
    """分析类型枚举"""
    DESCRIPTIVE = "descriptive"      # 描述性分析
    DIAGNOSTIC = "diagnostic"        # 诊断性分析
    PREDICTIVE = "predictive"        # 预测性分析
    PRESCRIPTIVE = "prescriptive"   # 规范性分析


class TaskPlanner:
    """
    任务规划器

    负责解析用户意图、确定数据类型、规划分析流程并生成任务序列。
    """

    def __init__(self):
        """初始化任务规划器"""
        self.data_type_patterns = {
            "csv": DataType.TABULAR,
            "xlsx": DataType.TABULAR,
            "xls": DataType.TABULAR,
            "json": DataType.TABULAR,
            "txt": DataType.TEXT,
            "md": DataType.TEXT,
            "pdf": DataType.MIXED,
            "jpg": DataType.IMAGE,
            "jpeg": DataType.IMAGE,
            "png": DataType.IMAGE,
            "gif": DataType.IMAGE,
            "mp3": DataType.AUDIO,
            "wav": DataType.AUDIO,
            "mp4": DataType.VIDEO,
            "avi": DataType.VIDEO,
            "mov": DataType.VIDEO,
        }

        self.analysis_workflows = {
            DataType.TABULAR: {
                AnalysisType.DESCRIPTIVE: [
                    TaskType.DATA_ANALYSIS,
                    TaskType.VISUALIZATION,
                ],
                AnalysisType.DIAGNOSTIC: [
                    TaskType.DATA_ANALYSIS,
                    TaskType.CORRELATION_ANALYSIS,
                    TaskType.VISUALIZATION,
                ],
                AnalysisType.PREDICTIVE: [
                    TaskType.DATA_ANALYSIS,
                    TaskType.TREND_ANALYSIS,
                    TaskType.VISUALIZATION,
                ],
            },
            DataType.IMAGE: {
                AnalysisType.DESCRIPTIVE: [
                    TaskType.IMAGE_ANALYSIS,
                ],
            },
            DataType.AUDIO: {
                AnalysisType.DESCRIPTIVE: [
                    TaskType.AUDIO_ANALYSIS,
                ],
            },
            DataType.VIDEO: {
                AnalysisType.DESCRIPTIVE: [
                    TaskType.VIDEO_ANALYSIS,
                ],
            },
            DataType.TEXT: {
                AnalysisType.DESCRIPTIVE: [
                    TaskType.TEXT_ANALYSIS,
                ],
            },
        }

        logger.info("任务规划器初始化完成")

    def detect_data_type(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> DataType:
        """
        检测数据类型

        Args:
            file_path: 文件路径
            metadata: 文件元数据

        Returns:
            检测到的数据类型
        """
        import os
        ext = os.path.splitext(file_path)[1].lower().lstrip(".")

        detected_type = self.data_type_patterns.get(ext, DataType.MIXED)

        if metadata:
            mime_type = metadata.get("mime_type", "")
            if "image" in mime_type:
                detected_type = DataType.IMAGE
            elif "audio" in mime_type:
                detected_type = DataType.AUDIO
            elif "video" in mime_type:
                detected_type = DataType.VIDEO
            elif "text" in mime_type:
                detected_type = DataType.TEXT

        logger.info(f"检测到数据类型: {detected_type.value}, 文件: {file_path}")
        return detected_type

    def determine_analysis_type(
        self,
        user_intent: str,
        data_characteristics: Dict[str, Any]
    ) -> AnalysisType:
        """
        确定分析类型

        Args:
            user_intent: 用户意图描述
            data_characteristics: 数据特征

        Returns:
            分析类型
        """
        intent_lower = user_intent.lower()

        if any(keyword in intent_lower for keyword in ["预测", "forecast", "predict", "趋势", "trend"]):
            return AnalysisType.PREDICTIVE
        elif any(keyword in intent_lower for keyword in ["原因", "why", "diagnose", "诊断", "分析"]):
            return AnalysisType.DIAGNOSTIC
        elif any(keyword in intent_lower for keyword in ["建议", "recommend", "优化", "optimize"]):
            return AnalysisType.PRESCRIPTIVE
        else:
            return AnalysisType.DESCRIPTIVE

    def generate_task_plan(
        self,
        user_intent: str,
        data_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成任务执行计划

        Args:
            user_intent: 用户意图描述
            data_info: 数据信息
            metadata: 额外的元数据

        Returns:
            任务计划
        """
        file_path = data_info.get("file_path", "")
        data_type = self.detect_data_type(file_path, metadata)

        characteristics = self._analyze_data_characteristics(data_info)
        analysis_type = self.determine_analysis_type(user_intent, characteristics)

        workflow = self.analysis_workflows.get(data_type, {}).get(
            analysis_type,
            [TaskType.DATA_ANALYSIS]
        )

        plan = {
            "data_type": data_type.value,
            "analysis_type": analysis_type.value,
            "tasks": [],
            "parameters": {},
            "estimated_duration": len(workflow) * 30,
        }

        for i, task_type in enumerate(workflow):
            task_config = {
                "id": f"task_{i + 1}",
                "type": task_type.value,
                "dependencies": [f"task_{i}"] if i > 0 else [],
                "parameters": self._get_task_parameters(task_type, data_info),
            }
            plan["tasks"].append(task_config)

        logger.info(f"生成了包含 {len(plan['tasks'])} 个任务的分析计划")
        return plan

    def _analyze_data_characteristics(self, data_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析数据特征

        Args:
            data_info: 数据信息

        Returns:
            数据特征
        """
        characteristics = {
            "has_time_series": False,
            "has_categorical": False,
            "has_numeric": False,
            "has_text": False,
            "volume": data_info.get("size", 0),
            "dimensions": data_info.get("dimensions", 0),
        }

        if "columns" in data_info:
            for col in data_info["columns"]:
                col_type = col.get("type", "unknown")
                if col_type in ["int64", "float64"]:
                    characteristics["has_numeric"] = True
                elif col_type in ["object", "string"]:
                    characteristics["has_text"] = True
                    characteristics["has_categorical"] = True

        if "time_column" in data_info:
            characteristics["has_time_series"] = True

        return characteristics

    def _get_task_parameters(
        self,
        task_type: TaskType,
        data_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        获取任务参数

        Args:
            task_type: 任务类型
            data_info: 数据信息

        Returns:
            任务参数
        """
        params = {}

        if task_type == TaskType.DATA_ANALYSIS:
            params = {
                "analysis_methods": ["statistics", "distribution"],
            }
        elif task_type == TaskType.TREND_ANALYSIS:
            params = {
                "date_column": data_info.get("time_column"),
                "value_column": data_info.get("value_column"),
                "forecast_periods": 12,
            }
        elif task_type == TaskType.CLUSTER_ANALYSIS:
            params = {
                "algorithm": "kmeans",
                "n_clusters": 4,
            }
        elif task_type == TaskType.CORRELATION_ANALYSIS:
            params = {
                "method": "pearson",
            }
        elif task_type == TaskType.VISUALIZATION:
            params = {
                "chart_types": ["line", "bar", "heatmap"],
            }

        return params

    async def optimize_plan(
        self,
        plan: Dict[str, Any],
        available_resources: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        优化任务计划

        Args:
            plan: 原始任务计划
            available_resources: 可用资源

        Returns:
            优化后的任务计划
        """
        max_parallel = settings.agent.parallel_tasks

        parallelizable_groups = []
        current_group = []

        for task in plan["tasks"]:
            if task["dependencies"]:
                if current_group:
                    parallelizable_groups.append(current_group)
                    current_group = []
                parallelizable_groups.append([task])
            else:
                current_group.append(task)
                if len(current_group) >= max_parallel:
                    parallelizable_groups.append(current_group)
                    current_group = []

        if current_group:
            parallelizable_groups.append(current_group)

        optimized_tasks = []
        task_id_offset = 0

        for group in parallelizable_groups:
            for task in group:
                new_task = task.copy()
                new_task["id"] = f"task_{task_id_offset + 1}"
                new_task["parallel_group"] = len(parallelized_groups := [
                    i for i, g in enumerate(parallelizable_groups)
                    if task in g
                ])
                optimized_tasks.append(new_task)
                task_id_offset += 1

        return {
            **plan,
            "tasks": optimized_tasks,
            "estimated_duration": len(parallelizable_groups) * 30,
            "parallel_groups": len(parallelizable_groups),
        }

    def validate_plan(self, plan: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证任务计划

        Args:
            plan: 任务计划

        Returns:
            (是否有效, 错误信息)
        """
        if not plan.get("tasks"):
            return False, "计划中没有任务"

        task_ids = set()
        for task in plan["tasks"]:
            task_id = task.get("id")
            if not task_id:
                return False, "任务缺少ID"

            if task_id in task_ids:
                return False, f"任务ID重复: {task_id}"

            task_ids.add(task_id)

            for dep_id in task.get("dependencies", []):
                if dep_id not in task_ids:
                    pass

        if not plan.get("data_type"):
            return False, "计划缺少数据类型"

        return True, None

    def merge_plans(
        self,
        plans: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        合并多个任务计划

        Args:
            plans: 任务计划列表

        Returns:
            合并后的计划
        """
        merged = {
            "data_type": DataType.MIXED.value,
            "analysis_type": "comprehensive",
            "tasks": [],
            "parameters": {},
            "estimated_duration": 0,
        }

        task_id_offset = 0

        for plan in plans:
            for task in plan.get("tasks", []):
                new_task = task.copy()
                new_task["id"] = f"task_{task_id_offset + 1}"
                new_task["source_plan"] = plans.index(plan)
                merged["tasks"].append(new_task)
                task_id_offset += 1

            merged["parameters"].update(plan.get("parameters", {}))
            merged["estimated_duration"] += plan.get("estimated_duration", 0)

        return merged
