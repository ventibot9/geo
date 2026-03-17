from typing import Optional
from ..adapters import (
    OpenAIAdapter,
    AnthropicAdapter,
    LlamaAdapter,
    BaseLLMAdapter,
)
from ..models.schemas import ModelProvider
import os


class ModelFactory:
    """模型工厂类"""

    _instances: dict[str, BaseLLMAdapter] = {}

    @classmethod
    def get_adapter(
        cls,
        provider: ModelProvider,
        model: Optional[str] = None,
    ) -> BaseLLMAdapter:
        """获取模型适配器实例"""
        key = f"{provider.value}:{model or 'default'}"

        if key not in cls._instances:
            cls._instances[key] = cls._create_adapter(provider, model)

        return cls._instances[key]

    @classmethod
    def _create_adapter(
        cls,
        provider: ModelProvider,
        model: Optional[str] = None,
    ) -> BaseLLMAdapter:
        """创建适配器实例"""
        if provider == ModelProvider.OPENAI:
            return OpenAIAdapter(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )

        elif provider == ModelProvider.ANTHROPIC:
            return AnthropicAdapter(
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                model=model or os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            )

        elif provider == ModelProvider.LLAMA:
            return LlamaAdapter(
                api_key="dummy",  # 本地模型不需要真实 key
                model=model or os.getenv("LLAMA_MODEL", "llama2"),
                base_url=os.getenv("LLAMA_API_BASE", "http://localhost:11434/v1"),
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @classmethod
    def get_default_provider(cls) -> ModelProvider:
        """获取默认提供商"""
        default = os.getenv("DEFAULT_MODEL", "anthropic")
        try:
            return ModelProvider(default)
        except ValueError:
            return ModelProvider.ANTHROPIC

    @classmethod
    def get_available_models(cls) -> list:
        """获取可用模型列表"""
        models = []

        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            models.append({
                "provider": ModelProvider.OPENAI,
                "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                "available": True,
            })

        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            models.append({
                "provider": ModelProvider.ANTHROPIC,
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
                "available": True,
            })

        # Llama
        if os.getenv("LLAMA_API_BASE"):
            models.append({
                "provider": ModelProvider.LLAMA,
                "model": os.getenv("LLAMA_MODEL", "llama2"),
                "available": True,
            })

        return models
