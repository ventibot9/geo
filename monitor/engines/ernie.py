"""
文心一言引擎实现（通过搜索API）
"""

from typing import Dict
from .base import BaseEngine, QueryResult

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class ErnieEngine(BaseEngine):
    """文心一言引擎（通过搜索）"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.secret_key = config.get("secret_key", "")
        self.search_url = config.get("search_url", "https://www.baidu.com/s")

        # 如果有API密钥，使用百度API，否则使用网页搜索
        self.use_api = bool(self.api_key and self.secret_key)

    def query(self, prompt: str) -> QueryResult:
        """查询文心一言"""
        if not self.enabled:
            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response="",
                success=False,
                error_message="Engine not enabled"
            )

        if not REQUESTS_AVAILABLE:
            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response="",
                success=False,
                error_message="Requests library not available"
            )

        try:
            if self.use_api:
                return self._query_via_api(prompt)
            else:
                return self._query_via_web(prompt)

        except Exception as e:
            return QueryResult(
                engine_name=self.get_name(),
                query=prompt,
                response="",
                success=False,
                error_message=str(e)
            )

    def _query_via_api(self, prompt: str) -> QueryResult:
        """通过API查询（需要百度AI平台API密钥）"""
        # 这里需要实现百度文心一言API调用
        # 由于需要access_token，这里简化实现
        return QueryResult(
            engine_name=self.get_name(),
            query=prompt,
            response="API mode requires Baidu AI platform credentials",
            success=False,
            error_message="API credentials not properly configured"
        )

    def _query_via_web(self, prompt: str) -> QueryResult:
        """通过网页搜索获取内容"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        params = {
            "wd": prompt,
            "rn": 10  # 返回结果数量
        }

        response = requests.get(
            self.search_url,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 提取搜索结果
        results = []
        result_divs = soup.find_all("div", class_="result")

        for div in result_divs[:5]:  # 只取前5个结果
            title = div.find("h3")
            snippet = div.find("div", class_="c-abstract")

            if title and snippet:
                results.append({
                    "title": title.get_text(strip=True),
                    "snippet": snippet.get_text(strip=True)
                })

        # 构造响应文本
        response_text = "\n\n".join([
            f"{r['title']}\n{r['snippet']}" for r in results
        ])

        if not response_text:
            response_text = "No search results found"

        return QueryResult(
            engine_name=self.get_name(),
            query=prompt,
            response=response_text,
            success=True,
            metadata={
                "method": "web_search",
                "results_count": len(results)
            }
        )

    def is_available(self) -> bool:
        """检查是否可用"""
        return (
            REQUESTS_AVAILABLE
            and self.enabled
        )
