"""
任务编排器模块

作为系统的核心控制单元，负责接收用户请求、解析任务意图、
分解复杂任务、协调各处理模块以及整合最终结果。
"""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import (
    TaskNotFoundError,
    TaskTimeoutError,
    ValidationError,
)

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """任务类型枚举"""
    TEXT_ANALYSIS = "text_analysis"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_ANALYSIS = "audio_analysis"
    VIDEO_ANALYSIS = "video_analysis"
    DATA_ANALYSIS = "data_analysis"
    TREND_ANALYSIS = "trend_analysis"
    CLUSTER_ANALYSIS = "cluster_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    VISUALIZATION = "visualization"
    REPORT_GENERATION = "report_generation"


class Task:
    """任务数据模型"""

    def __init__(
        self,
        task_type: TaskType,
        input_data: Any,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化任务

        Args:
            task_type: 任务类型
            input_data: 输入数据
            parameters: 任务参数
            metadata: 任务元数据
        """
        self.id = str(uuid.uuid4())
        self.task_type = task_type
        self.input_data = input_data
        self.parameters = parameters or {}
        self.metadata = metadata or {}
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.progress = 0
        self.subtasks: List["Task"] = []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "progress": self.progress,
            "result": self.result,
            "error": self.error.to_dict() if self.error else None,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


class AgentOrchestrator:
    """
    Agent 协调器

    核心控制单元，负责管理整个分析流程的协调执行。
    支持任务分解、并行处理、状态监控和错误恢复。
    """

    def __init__(self):
        """初始化协调器"""
        self.tasks: Dict[str, Task] = {}
        self.handlers: Dict[TaskType, callable] = {}
        self._lock = asyncio.Lock()
        logger.info("Agent 协调器初始化完成")

    def register_handler(self, task_type: TaskType, handler: callable):
        """
        注册任务处理器

        Args:
            task_type: 任务类型
            handler: 处理函数
        """
        self.handlers[task_type] = handler
        logger.info(f"已注册任务处理器: {task_type.value}")

    async def create_task(
        self,
        task_type: TaskType,
        input_data: Any,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        创建新任务

        Args:
            task_type: 任务类型
            input_data: 输入数据
            parameters: 任务参数
            metadata: 任务元数据

        Returns:
            创建的任务对象
        """
        if task_type not in self.handlers:
            raise ValidationError(f"不支持的任务类型: {task_type.value}")

        task = Task(task_type, input_data, parameters, metadata)

        async with self._lock:
            self.tasks[task.id] = task

        logger.info(f"创建新任务: {task.id}, 类型: {task_type.value}")
        return task

    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        执行指定任务

        Args:
            task_id: 任务ID

        Returns:
            任务执行结果

        Raises:
            TaskNotFoundError: 任务不存在
            TaskTimeoutError: 任务执行超时
        """
        task = await self.get_task(task_id)
        if not task:
            raise TaskNotFoundError(task_id)

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        logger.info(f"开始执行任务: {task_id}")

        try:
            handler = self.handlers.get(task.task_type)
            if not handler:
                raise ValidationError(f"未找到任务处理器: {task.task_type.value}")

            if asyncio.iscoroutinefunction(handler):
                result = await asyncio.wait_for(
                    handler(task),
                    timeout=settings.agent.timeout
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(handler, task),
                    timeout=settings.agent.timeout
                )

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.progress = 100
            task.completed_at = datetime.now()
            logger.info(f"任务执行完成: {task_id}")

            return result

        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = TaskTimeoutError(task_id, settings.agent.timeout)
            logger.error(f"任务执行超时: {task_id}")
            raise task.error

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = e
            task.completed_at = datetime.now()
            logger.error(f"任务执行失败: {task_id}, 错误: {str(e)}")
            raise

    async def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务信息

        Args:
            task_id: 任务ID

        Returns:
            任务对象，不存在则返回 None
        """
        async with self._lock:
            return self.tasks.get(task_id)

    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        列出任务

        Args:
            status: 任务状态过滤
            limit: 返回数量限制

        Returns:
            任务列表
        """
        async with self._lock:
            tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return [t.to_dict() for t in tasks[:limit]]

    async def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        task = await self.get_task(task_id)
        if not task:
            return False

        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        logger.info(f"任务已取消: {task_id}")
        return True

    async def delete_task(self, task_id: str) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功删除
        """
        async with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                logger.info(f"任务已删除: {task_id}")
                return True
        return False

    async def create_subtasks(
        self,
        parent_task: Task,
        subtask_specs: List[Dict[str, Any]]
    ) -> List[Task]:
        """
        创建子任务

        Args:
            parent_task: 父任务
            subtask_specs: 子任务规格列表

        Returns:
            创建的子任务列表
        """
        subtasks = []
        for spec in subtask_specs:
            task_type = TaskType(spec["task_type"])
            subtask = await self.create_task(
                task_type=task_type,
                input_data=spec.get("input_data"),
                parameters=spec.get("parameters"),
                metadata={"parent_task_id": parent_task.id}
            )
            parent_task.subtasks.append(subtask)
            subtasks.append(subtask)

        logger.info(f"为任务 {parent_task.id} 创建了 {len(subtasks)} 个子任务")
        return subtasks

    async def execute_parallel(self, task_ids: List[str]) -> List[Dict[str, Any]]:
        """
        并行执行多个任务

        Args:
            task_ids: 任务ID列表

        Returns:
            任务结果列表
        """
        logger.info(f"开始并行执行 {len(task_ids)} 个任务")
        tasks = [self.execute_task(tid) for tid in task_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "task_id": task_ids[i],
                    "status": "failed",
                    "error": str(result)
                })
            else:
                processed_results.append({
                    "task_id": task_ids[i],
                    "status": "completed",
                    "result": result
                })

        return processed_results


# 全局协调器实例
orchestrator = AgentOrchestrator()
