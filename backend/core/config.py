"""
配置管理模块

提供系统配置的加载、验证和管理功能，支持 YAML 配置文件和环境变量。
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ServerConfig(BaseModel):
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    log_level: str = "info"
    cors_origins: List[str] = ["http://localhost:3000"]


class RedisConfig(BaseModel):
    """Redis 配置"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 50


class StorageConfig(BaseModel):
    """文件存储配置"""
    upload_dir: str = "./uploads"
    temp_dir: str = "./temp"
    max_file_size: int = 104857600  # 100MB
    allowed_extensions: List[str] = [
        ".csv", ".json", ".xlsx", ".xls", ".txt",
        ".jpg", ".jpeg", ".png", ".gif",
        ".mp3", ".wav", ".mp4", ".avi", ".mov"
    ]


class OpenAIConfig(BaseModel):
    """OpenAI 配置"""
    api_key: str = ""
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4096


class AnthropicConfig(BaseModel):
    """Anthropic 配置"""
    api_key: str = ""
    model: str = "claude-3-opus-20240229"
    temperature: float = 0.7
    max_tokens: int = 4096


class AIConfig(BaseModel):
    """AI 模型配置"""
    provider: str = "openai"
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)


class AgentConfig(BaseModel):
    """Agent 配置"""
    timeout: int = 300
    max_retries: int = 3
    retry_delay: int = 5
    cache_enabled: bool = True
    cache_ttl: int = 3600
    parallel_tasks: int = 5


class ProcessingConfig(BaseModel):
    """数据处理配置"""
    text: Dict[str, Any] = Field(default_factory=lambda: {
        "max_length": 50000,
        "languages": ["zh", "en"],
        "embedding_model": "text-embedding-ada-002"
    })
    image: Dict[str, Any] = Field(default_factory=lambda: {
        "max_size": 10485760,
        "supported_formats": ["jpg", "jpeg", "png", "gif", "webp"],
        "thumbnail_size": [256, 256]
    })
    audio: Dict[str, Any] = Field(default_factory=lambda: {
        "max_duration": 3600,
        "sample_rate": 16000,
        "supported_formats": ["mp3", "wav", "aac", "flac"]
    })
    video: Dict[str, Any] = Field(default_factory=lambda: {
        "max_duration": 7200,
        "max_frames": 1000,
        "thumbnail_interval": 10
    })


class AnalysisConfig(BaseModel):
    """分析引擎配置"""
    statistics: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "confidence_level": 0.95
    })
    trend: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "forecast_periods": 12,
        "seasonality_detection": True
    })
    clustering: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "max_clusters": 20,
        "algorithm": "kmeans"
    })
    correlation: Dict[str, Any] = Field(default_factory=lambda: {
        "enabled": True,
        "method": "pearson"
    })


class VisualizationConfig(BaseModel):
    """可视化配置"""
    default_theme: str = "light"
    color_schemes: Dict[str, str] = Field(default_factory=lambda: {
        "categorical": "category10",
        "sequential": "blues",
        "diverging": "RdBu"
    })
    export_formats: List[str] = ["png", "svg", "pdf", "html"]
    chart_width: int = 800
    chart_height: int = 600


class SecurityConfig(BaseModel):
    """安全配置"""
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7


class Settings(BaseModel):
    """系统配置"""
    server: ServerConfig = Field(default_factory=ServerConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    @classmethod
    def load_from_yaml(cls, config_path: str = "config/settings.yaml") -> "Settings":
        """从 YAML 文件加载配置"""
        config_file = Path(config_path)
        if not config_file.exists():
            return cls()

        with open(config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    @classmethod
    def load_from_env(cls) -> "Settings":
        """从环境变量加载配置"""
        return cls(
            ai=AIConfig(
                openai=OpenAIConfig(
                    api_key=os.getenv("OPENAI_API_KEY", ""),
                    model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
                ),
                anthropic=AnthropicConfig(
                    api_key=os.getenv("CLAUDE_API_KEY", ""),
                    model=os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
                )
            ),
            security=SecurityConfig(
                secret_key=os.getenv("SECRET_KEY", "your-secret-key-here")
            )
        )


# 全局配置实例
settings = Settings.load_from_yaml()
