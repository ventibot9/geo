from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.schemas import (
    RewriteRequest,
    RewriteResponse,
    BatchRewriteRequest,
    QualityEvaluationRequest,
    QualityEvaluation,
    ModelProvider,
)
from ..models.database import RewriteRecordDB
from ..prompts import build_rewrite_prompt, SYSTEM_PROMPT, QUALITY_EVALUATION_PROMPT
from .model_factory import ModelFactory
import json
import re


class RewriteService:
    """改写服务"""

    def __init__(self):
        pass

    async def rewrite(
        self,
        request: RewriteRequest,
        session: AsyncSession,
    ) -> RewriteResponse:
        """单条改写"""
        # 获取模型适配器
        provider = request.model_provider or ModelFactory.get_default_provider()
        adapter = ModelFactory.get_adapter(provider, request.model)

        # 构建 Prompt
        system_prompt = request.system_prompt or SYSTEM_PROMPT
        user_prompt = build_rewrite_prompt(
            request.content,
            optimize_structure=request.optimize_structure,
            extract_tables=request.extract_tables,
        )

        # 调用模型
        rewritten = await adapter.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=request.temperature,
            max_tokens=4096,
        )

        # 保存记录
        record = RewriteRecordDB(
            original=request.content,
            rewritten=rewritten,
            model_provider=provider.value,
            model=adapter.get_model_name(),
        )
        session.add(record)
        await session.flush()
        await session.refresh(record)

        return RewriteResponse(
            id=record.id,
            original=record.original,
            rewritten=record.rewritten,
            model_provider=ModelProvider(record.model_provider),
            model=record.model,
            created_at=record.created_at,
        )

    async def batch_rewrite(
        self,
        request: BatchRewriteRequest,
        session: AsyncSession,
    ) -> List[RewriteResponse]:
        """批量改写"""
        results = []

        for content in request.contents:
            single_request = RewriteRequest(
                content=content,
                model_provider=request.model_provider,
                model=request.model,
                temperature=request.temperature,
                optimize_structure=request.optimize_structure,
                extract_tables=request.extract_tables,
            )
            result = await self.rewrite(single_request, session)
            results.append(result)

        return results

    async def evaluate_quality(
        self,
        request: QualityEvaluationRequest,
    ) -> QualityEvaluation:
        """评估改写质量"""
        provider = request.model_provider or ModelFactory.get_default_provider()
        adapter = ModelFactory.get_adapter(provider)

        prompt = QUALITY_EVALUATION_PROMPT.format(
            original=request.original,
            rewritten=request.rewritten,
        )

        response = await adapter.generate(
            prompt=prompt,
            temperature=0.3,  # 评估时使用较低温度
            max_tokens=1024,
        )

        # 解析 JSON 响应
        try:
            # 尝试提取 JSON 部分
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            evaluation = QualityEvaluation(**data)

            # 更新数据库记录
            # 这里简化处理，实际需要根据记录ID查询更新

            return evaluation

        except (json.JSONDecodeError, ValueError) as e:
            # 解析失败返回默认评分
            return QualityEvaluation(
                overall_score=0.5,
                completeness=0.5,
                clarity=0.5,
                structure=0.5,
                suggestions=["无法解析评估结果，请检查模型输出格式"],
            )

    async def get_history(
        self,
        session: AsyncSession,
        limit: int = 50,
    ) -> List[dict]:
        """获取改写历史"""
        query = select(RewriteRecordDB).order_by(
            RewriteRecordDB.created_at.desc()
        ).limit(limit)

        result = await session.execute(query)
        records = result.scalars().all()

        return [
            {
                "id": r.id,
                "original": r.original[:200] + "..." if len(r.original) > 200 else r.original,
                "rewritten": r.rewritten[:200] + "..." if len(r.rewritten) > 200 else r.rewritten,
                "model_provider": r.model_provider,
                "model": r.model,
                "created_at": r.created_at.isoformat(),
                "quality_score": r.quality_score,
            }
            for r in records
        ]

    async def get_record(
        self,
        record_id: str,
        session: AsyncSession,
    ) -> Optional[dict]:
        """获取单条记录"""
        query = select(RewriteRecordDB).where(RewriteRecordDB.id == record_id)
        result = await session.execute(query)
        record = result.scalar_one_or_none()

        if not record:
            return None

        return {
            "id": record.id,
            "original": record.original,
            "rewritten": record.rewritten,
            "model_provider": record.model_provider,
            "model": record.model,
            "created_at": record.created_at.isoformat(),
            "quality_score": record.quality_score,
            "quality_details": record.quality_details,
        }
