from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ModelProvider(str, Enum):
    """模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LLAMA = "llama"


class RewriteRequest(BaseModel):
    """改写请求"""
    content: str = Field(..., description="原始内容")
    model_provider: Optional[ModelProvider] = Field(
        default=ModelProvider.ANTHROPIC,
        description="模型提供商"
    )
    model: Optional[str] = Field(default=None, description="指定模型名称（可选）")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="温度参数")
    optimize_structure: bool = Field(default=True, description="是否优化结构")
    extract_tables: bool = Field(default=True, description="是否提取表格")
    system_prompt: Optional[str] = Field(default=None, description="自定义系统提示")


class BatchRewriteRequest(BaseModel):
    """批量改写请求"""
    contents: List[str] = Field(..., min_items=1, max_items=50, description="内容列表")
    model_provider: Optional[ModelProvider] = Field(
        default=ModelProvider.ANTHROPIC,
        description="模型提供商"
    )
    model: Optional[str] = Field(default=None, description="指定模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    optimize_structure: bool = Field(default=True)
    extract_tables: bool = Field(default=True)


class QualityEvaluationRequest(BaseModel):
    """质量评估请求"""
    original: str = Field(..., description="原始内容")
    rewritten: str = Field(..., description="改写后内容")
    model_provider: Optional[ModelProvider] = Field(default=ModelProvider.ANTHROPIC)


class QualityEvaluation(BaseModel):
    """质量评估结果"""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="总体评分")
    completeness: float = Field(..., ge=0.0, le=1.0, description="完整性")
    clarity: float = Field(..., ge=0.0, le=1.0, description="清晰度")
    structure: float = Field(..., ge=0.0, le=1.0, description="结构化程度")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")


class RewriteResponse(BaseModel):
    """改写响应"""
    id: str = Field(..., description="记录ID")
    original: str = Field(..., description="原始内容")
    rewritten: str = Field(..., description="改写后内容")
    model_provider: ModelProvider = Field(..., description="使用的模型")
    model: str = Field(..., description="具体模型名称")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    quality: Optional[QualityEvaluation] = Field(default=None, description="质量评估")


class RewriteRecord(BaseModel):
    """改写记录"""
    id: str
    original: str
    rewritten: str
    model_provider: ModelProvider
    model: str
    created_at: datetime
    quality: Optional[QualityEvaluation] = None


class ModelInfo(BaseModel):
    """模型信息"""
    provider: ModelProvider
    model: str
    available: bool
