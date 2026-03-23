"""
系统入口模块

提供 FastAPI 应用的创建和配置功能。
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.core.logging import setup_logging, get_logger
from backend.core.exceptions import BaseAgentException
from backend.api.routes import router

logger = setup_logging("backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("系统启动...")
    yield
    logger.info("系统关闭...")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="Multimodal Analysis Agent",
        description="基于多模态内容理解的全自动化数据分析可视化 Agent 系统",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(BaseAgentException)
    async def agent_exception_handler(request: Request, exc: BaseAgentException):
        """处理自定义异常"""
        return JSONResponse(
            status_code=400,
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理通用异常"""
        logger.error(f"未处理的异常: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "details": str(exc) if settings.server.log_level == "debug" else None,
            },
        )

    app.include_router(router)

    return app


app = create_app()


def main():
    """主函数"""
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        log_level=settings.server.log_level,
    )


if __name__ == "__main__":
    main()
