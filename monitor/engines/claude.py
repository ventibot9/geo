"""
Claude引擎实现
"""

from typing import Dict
from .base import BaseEngine, QueryResult

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ClaudeEngine(BaseEngine):
    """Claude引擎"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.model = config.get("model", "claude-3-haiku-20240307")
        self.base_url = config.get("base_url", "https://api.anthropic.com")

        if ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None

    def query(self, prompt: str) -> QueryResult:
        """查询Claude"""
        if not self.enabled:
            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response="",
                success=False,
                error_message="Engine not enabled"
            )

        if not ANTHROPIC_AVAILABLE or not self.client:
            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response="",
                success=False,
                error_message="Anthropic library not available or client not initialized"
            )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = response.content[0].text

            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response=response_text,
                success=True,
                metadata={
                    "model": self.model,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                    }
                }
            )

        except Exception as e:
            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response="",
                success=False,
                error_message=str(e)
            )

    def is_available(self) -> bool:
        """检查是否可用"""
        return (
            ANTHROPIC_AVAILABLE
            and self.enabled
            and bool(self.api_key)
            and self.client is not None
        )
