from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseLLMAdapter(ABC):
    """大模型适配器基类"""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.extra_config = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """生成文本"""
        pass

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """流式生成文本"""
        pass

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.model

    def get_provider(self) -> str:
        """获取提供商名称"""
        return self.__class__.__name__.replace("Adapter", "")
