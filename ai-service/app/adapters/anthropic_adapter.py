from typing import Optional, AsyncGenerator
import anthropic
from .base import BaseLLMAdapter


class AnthropicAdapter(BaseLLMAdapter):
    """Anthropic Claude API 适配器"""

    def __init__(self, api_key: str, model: str, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """生成文本"""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 4096,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )

        return response.content[0].text

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """流式生成文本"""
        stream = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 4096,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            stream=True,
        )

        async for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                yield event.delta.text
