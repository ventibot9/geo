"""
ChatGPT引擎实现
"""

from typing import Dict
from .base import BaseEngine, QueryResult

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ChatGPTEngine(BaseEngine):
    """ChatGPT引擎"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.model = config.get("model", "gpt-3.5-turbo")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")

        if OPENAI_AVAILABLE:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None

    def query(self, prompt: str) -> QueryResult:
        """查询ChatGPT"""
        if not self.enabled:
            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response="",
                success=False,
                error_message="Engine not enabled"
            )

        if not OPENAI_AVAILABLE or not self.client:
            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response="",
                success=False,
                error_message="OpenAI library not available or client not initialized"
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            response_text = response.choices[0].message.content

            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response=response_text,
                success=True,
                metadata={
                    "model": self.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
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
            OPENAI_AVAILABLE
            and self.enabled
            and bool(self.api_key)
            and self.client is not None
        )
