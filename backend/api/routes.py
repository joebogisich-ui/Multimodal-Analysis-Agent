"""
API 路由模块

提供系统的 RESTful API 接口，支持任务管理、数据上传、分析执行等功能。
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.core.logging import get_logger
from backend.core.exceptions import BaseAgentException
from backend.agents.orchestrator import orchestrator, TaskType, TaskStatus
from backend.agents.analyzer import DataAnalyzer
from backend.agents.visualizer import ChartVisualizer, DashboardGenerator
from backend.agents.planner import TaskPlanner
from backend.processors import TextProcessor, ImageProcessor, AudioProcessor, VideoProcessor

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1")

analyzer = DataAnalyzer()
visualizer = ChartVisualizer()
dashboard_generator = DashboardGenerator(visualizer)
planner = TaskPlanner()

text_processor = TextProcessor()
image_processor = ImageProcessor()
audio_processor = AudioProcessor()
video_processor = VideoProcessor()


class TaskCreateRequest(BaseModel):
    """任务创建请求"""
    task_type: str = Field(..., description="任务类型")
    input_data: Optional[Any] = Field(None, description="输入数据")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="任务参数")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class AnalysisRequest(BaseModel):
    """分析请求"""
    data: Optional[Dict[str, Any]] = Field(None, description="数据")
    analysis_type: str = Field(..., description="分析类型")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="分析参数")


class VisualizationRequest(BaseModel):
    """可视化请求"""
    data: Dict[str, Any] = Field(..., description="数据")
    chart_type: str = Field(..., description="图表类型")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="图表参数")


class PlanGenerationRequest(BaseModel):
    """计划生成请求"""
    user_intent: str = Field(..., description="用户意图")
    data_info: Dict[str, Any] = Field(..., description="数据信息")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


@router.get("/")
async def root():
    """根路径"""
    return {
        "name": "Multimodal Analysis Agent API",
        "version": "1.0.0",
        "status": "running",
    }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.post("/tasks")
async def create_task(request: TaskCreateRequest):
    """创建任务"""
    try:
        task_type = TaskType(request.task_type)
        task = await orchestrator.create_task(
            task_type=task_type,
            input_data=request.input_data,
            parameters=request.parameters,
            metadata=request.metadata,
        )
        return {"task_id": task.id, "status": task.status.value}
    except Exception as e:
        logger.error(f"创建任务失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取任务信息"""
    task = await orchestrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return task.to_dict()


@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    """执行任务"""
    try:
        result = await orchestrator.execute_task(task_id)
        return {"task_id": task_id, "status": "completed", "result": result}
    except Exception as e:
        logger.error(f"任务执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def list_tasks(
    status: Optional[str] = Query(None, description="状态过滤"),
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
):
    """列出任务"""
    task_status = TaskStatus(status) if status else None
    tasks = await orchestrator.list_tasks(status=task_status, limit=limit)
    return {"tasks": tasks, "count": len(tasks)}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    success = await orchestrator.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return {"message": "任务已删除"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="上传的文件"),
):
    """上传文件"""
    import os
    from pathlib import Path

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / file.filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    file_size = len(content)
    suffix = Path(file.filename).suffix.lower()

    detected_type = "unknown"
    if suffix in [".csv", ".xlsx", ".xls", ".json"]:
        detected_type = "tabular"
    elif suffix in [".txt", ".md"]:
        detected_type = "text"
    elif suffix in [".jpg", ".jpeg", ".png", ".gif"]:
        detected_type = "image"
    elif suffix in [".mp3", ".wav"]:
        detected_type = "audio"
    elif suffix in [".mp4", ".avi", ".mov"]:
        detected_type = "video"

    return {
        "file_id": str(file_path),
        "filename": file.filename,
        "size": file_size,
        "type": detected_type,
    }


@router.post("/process/text")
async def process_text(
    file_path: Optional[str] = Body(None),
    text: Optional[str] = Body(None),
    data: Optional[Dict[str, Any]] = Body(None),
    options: Optional[Dict[str, Any]] = Body(None),
):
    """处理文本"""
    try:
        result = await text_processor.process(
            file_path=file_path,
            text=text,
            data=data,
            options=options,
        )
        return result
    except Exception as e:
        logger.error(f"文本处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/image")
async def process_image(
    file_path: Optional[str] = Body(None),
    image_data: Optional[str] = Body(None),
    options: Optional[Dict[str, Any]] = Body(None),
):
    """处理图像"""
    try:
        result = await image_processor.process(
            file_path=file_path,
            image_data=image_data,
            options=options,
        )
        return result
    except Exception as e:
        logger.error(f"图像处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/audio")
async def process_audio(
    file_path: Optional[str] = Body(None),
    audio_data: Optional[str] = Body(None),
    options: Optional[Dict[str, Any]] = Body(None),
):
    """处理音频"""
    try:
        result = await audio_processor.process(
            file_path=file_path,
            audio_data=audio_data,
            options=options,
        )
        return result
    except Exception as e:
        logger.error(f"音频处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/video")
async def process_video(
    file_path: Optional[str] = Body(None),
    video_data: Optional[str] = Body(None),
    options: Optional[Dict[str, Any]] = Body(None),
):
    """处理视频"""
    try:
        result = await video_processor.process(
            file_path=file_path,
            video_data=video_data,
            options=options,
        )
        return result
    except Exception as e:
        logger.error(f"视频处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_data(request: AnalysisRequest):
    """数据分析"""
    try:
        result = await analyzer.analyze(
            data=request.data,
            analysis_type=request.analysis_type,
            parameters=request.parameters,
        )
        return result
    except Exception as e:
        logger.error(f"分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/visualize")
async def create_visualization(request: VisualizationRequest):
    """创建可视化"""
    try:
        result = await visualizer.generate_chart(
            data=request.data,
            chart_type=request.chart_type,
            parameters=request.parameters,
        )
        return result
    except Exception as e:
        logger.error(f"可视化生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard")
async def create_dashboard(chart_configs: List[Dict[str, Any]]):
    """创建仪表盘"""
    try:
        result = await dashboard_generator.generate_dashboard(chart_configs)
        return result
    except Exception as e:
        logger.error(f"仪表盘生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plan")
async def generate_plan(request: PlanGenerationRequest):
    """生成任务计划"""
    try:
        plan = planner.generate_task_plan(
            user_intent=request.user_intent,
            data_info=request.data_info,
            metadata=request.metadata,
        )

        is_valid, error_msg = planner.validate_plan(plan)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        optimized_plan = await planner.optimize_plan(plan)

        return optimized_plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"计划生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/types")
async def get_analysis_types():
    """获取分析类型"""
    return {
        "types": [
            {"id": "statistics", "name": "统计分析", "description": "描述性统计和分布分析"},
            {"id": "trend", "name": "趋势分析", "description": "时间序列趋势和预测"},
            {"id": "clustering", "name": "聚类分析", "description": "数据聚类和模式发现"},
            {"id": "correlation", "name": "相关性分析", "description": "变量间关联分析"},
            {"id": "regression", "name": "回归分析", "description": "回归建模和预测"},
            {"id": "distribution", "name": "分布分析", "description": "数据分布特征分析"},
        ]
    }


@router.get("/chart/types")
async def get_chart_types():
    """获取图表类型"""
    return {
        "types": [
            {"id": "line", "name": "折线图", "category": "趋势"},
            {"id": "bar", "name": "柱状图", "category": "比较"},
            {"id": "scatter", "name": "散点图", "category": "关联"},
            {"id": "pie", "name": "饼图", "category": "构成"},
            {"id": "histogram", "name": "直方图", "category": "分布"},
            {"id": "box", "name": "箱线图", "category": "分布"},
            {"id": "heatmap", "name": "热力图", "category": "关联"},
            {"id": "radar", "name": "雷达图", "category": "比较"},
            {"id": "treemap", "name": "树形图", "category": "构成"},
            {"id": "wordcloud", "name": "词云图", "category": "文本"},
        ]
    }
