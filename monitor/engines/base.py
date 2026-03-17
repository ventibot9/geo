"""
AI引擎基类
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class QueryResult:
    """查询结果"""
    engine_name: str
    query: str
    response: str
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None


class BaseEngine(ABC):
    """AI引擎抽象基类"""

    def __init__(self, config: Dict):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.api_key = config.get("api_key", "")

    @abstractmethod
    def query(self, prompt: str) -> QueryResult:
        """
        执行查询

        Args:
            prompt: 查询提示词

        Returns:
            QueryResult: 查询结果
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查引擎是否可用

        Returns:
            bool: 是否可用
        """
        pass

    def get_name(self) -> str:
        """获取引擎名称"""
        return self.__class__.__name__.replace("Engine", "").lower()

    def check_keywords_in_response(
        self,
        response: str,
        keywords: Dict[str, List[str]]
    ) -> List[Dict]:
        """
        检查响应中是否包含关键词

        Args:
            response: AI响应文本
            keywords: 关键词字典 {category: [keywords]}

        Returns:
            List[Dict]: 匹配到的关键词列表
                [{keyword, category, count}]
        """
        found_keywords = []

        for category, kw_list in keywords.items():
            for keyword in kw_list:
                if keyword.lower() in response.lower():
                    count = response.lower().count(keyword.lower())
                    found_keywords.append({
                        "keyword": keyword,
                        "category": category,
                        "count": count
                    })

        return found_keywords

    def calculate_confidence(self, found_keywords: List[Dict]) -> float:
        """
        计算置信度分数

        Args:
            found_keywords: 匹配到的关键词列表

        Returns:
            float: 置信度分数 (0-1)
        """
        if not found_keywords:
            return 0.0

        # 基础分：至少匹配到一个关键词
        score = 0.5

        # 关键词数量加成
        keyword_count = sum(kw["count"] for kw in found_keywords)
        score += min(keyword_count * 0.1, 0.3)

        # 多类别加成
        categories = set(kw["category"] for kw in found_keywords)
        if len(categories) > 1:
            score += 0.2

        return min(score, 1.0)
