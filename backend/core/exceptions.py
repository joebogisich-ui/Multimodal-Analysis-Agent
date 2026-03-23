"""
异常定义模块

定义系统专用的异常类型，用于错误处理和异常传播。
"""

from typing import Any, Dict, Optional


class BaseAgentException(Exception):
    """系统异常基类"""

    def __init__(
        self,
        message: str,
        code: str = "AGENT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常

        Args:
            message: 错误消息
            code: 错误代码
            details: 额外的错误详情
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }


class ValidationError(BaseAgentException):
    """数据验证异常"""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field} if field else {}
        )


class DataProcessingError(BaseAgentException):
    """数据处理异常"""

    def __init__(self, message: str, data_type: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATA_PROCESSING_ERROR",
            details={"data_type": data_type} if data_type else {}
        )


class AnalysisError(BaseAgentException):
    """数据分析异常"""

    def __init__(self, message: str, analysis_type: Optional[str] = None):
        super().__init__(
            message=message,
            code="ANALYSIS_ERROR",
            details={"analysis_type": analysis_type} if analysis_type else {}
        )


class VisualizationError(BaseAgentException):
    """可视化生成异常"""

    def __init__(self, message: str, chart_type: Optional[str] = None):
        super().__init__(
            message=message,
            code="VISUALIZATION_ERROR",
            details={"chart_type": chart_type} if chart_type else {}
        )


class TaskTimeoutError(BaseAgentException):
    """任务超时异常"""

    def __init__(self, task_id: str, timeout: int):
        super().__init__(
            message=f"任务 {task_id} 执行超时，超时时间为 {timeout} 秒",
            code="TASK_TIMEOUT",
            details={"task_id": task_id, "timeout": timeout}
        )


class TaskNotFoundError(BaseAgentException):
    """任务未找到异常"""

    def __init__(self, task_id: str):
        super().__init__(
            message=f"任务 {task_id} 不存在",
            code="TASK_NOT_FOUND",
            details={"task_id": task_id}
        )


class FileProcessingError(BaseAgentException):
    """文件处理异常"""

    def __init__(
        self,
        message: str,
        filename: Optional[str] = None,
        file_type: Optional[str] = None
    ):
        super().__init__(
            message=message,
            code="FILE_PROCESSING_ERROR",
            details={
                "filename": filename,
                "file_type": file_type
            }
        )


class UnsupportedFormatError(BaseAgentException):
    """不支持的格式异常"""

    def __init__(self, format_type: str, supported_types: list):
        super().__init__(
            message=f"不支持的格式类型: {format_type}",
            code="UNSUPPORTED_FORMAT",
            details={
                "format_type": format_type,
                "supported_types": supported_types
            }
        )


class ModelAPIError(BaseAgentException):
    """模型 API 调用异常"""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        super().__init__(
            message=message,
            code="MODEL_API_ERROR",
            details={
                "provider": provider,
                "status_code": status_code
            }
        )


class AuthenticationError(BaseAgentException):
    """认证异常"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(BaseAgentException):
    """授权异常"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR"
        )


class RateLimitError(BaseAgentException):
    """请求频率限制异常"""

    def __init__(self, retry_after: Optional[int] = None):
        super().__init__(
            message="请求频率超限，请稍后重试",
            code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after} if retry_after else {}
        )
