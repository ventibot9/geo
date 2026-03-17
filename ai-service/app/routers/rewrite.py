from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.schemas import (
    RewriteRequest,
    RewriteResponse,
    BatchRewriteRequest,
    QualityEvaluationRequest,
    QualityEvaluation,
    ModelInfo,
)
from ..services.rewrite_service import RewriteService
from ..services.model_factory import ModelFactory
from ..database import get_session
from typing import List
import json

router = APIRouter(prefix="/api/v1/rewrite", tags=["改写"])
service = RewriteService()


@router.post("", response_model=RewriteResponse, summary="单条改写")
async def rewrite(
    request: RewriteRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    对单条内容进行AI改写优化

    - **content**: 原始内容（必填）
    - **model_provider**: 模型提供商（默认：anthropic）
    - **model**: 指定模型名称（可选）
    - **temperature**: 温度参数 0-1（默认：0.7）
    - **optimize_structure**: 是否优化结构（默认：true）
    - **extract_tables**: 是否提取表格（默认：true）
    """
    try:
        return await service.rewrite(request, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=List[RewriteResponse], summary="批量改写")
async def batch_rewrite(
    request: BatchRewriteRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    批量改写多条内容

    - **contents**: 内容列表（1-50条）
    - 其他参数同单条改写
    """
    try:
        return await service.batch_rewrite(request, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate", response_model=QualityEvaluation, summary="质量评估")
async def evaluate_quality(request: QualityEvaluationRequest):
    """
    评估改写质量

    - **original**: 原始内容
    - **rewritten**: 改写后内容
    - **model_provider**: 评估用的模型（默认：anthropic）
    """
    try:
        return await service.evaluate_quality(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="获取改写历史")
async def get_history(
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    """
    获取最近的改写历史记录

    - **limit**: 返回记录数量（默认：50）
    """
    try:
        return await service.get_history(session, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/record/{record_id}", summary="获取单条记录")
async def get_record(
    record_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    获取指定ID的改写记录详情
    """
    try:
        record = await service.get_record(record_id, session)
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", summary="获取可用模型")
async def get_models():
    """
    获取当前配置的可用模型列表
    """
    models = ModelFactory.get_available_models()
    return [
        {
            "provider": m["provider"].value,
            "model": m["model"],
            "available": m["available"],
        }
        for m in models
    ]


@router.get("/health", summary="健康检查")
async def health_check():
    """服务健康检查"""
    return {
        "status": "ok",
        "models": len(ModelFactory.get_available_models()),
    }
