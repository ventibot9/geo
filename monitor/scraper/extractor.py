"""
引用数据提取器
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

from config import COMPANY_KEYWORDS
from database.models import CitationRecord


@dataclass
class CitationData:
    """引用数据"""
    engine_name: str
    query_text: str
    response_text: str
    keyword_found: str
    keyword_category: str
    citation_count: int
    confidence_score: float
    timestamp: datetime
    raw_response: str = None


class CitationExtractor:
    """引用提取器"""

    def __init__(self, keywords: Dict[str, List[str]] = None):
        self.keywords = keywords or COMPANY_KEYWORDS

    def extract_from_response(
        self,
        engine_name: str,
        query_text: str,
        response_text: str,
        confidence_score: float = 0.0
    ) -> List[CitationData]:
        """
        从AI响应中提取引用数据

        Args:
            engine_name: 引擎名称
            query_text: 查询文本
            response_text: 响应文本
            confidence_score: 置信度分数

        Returns:
            List[CitationData]: 引用数据列表
        """
        citations = []

        for category, kw_list in self.keywords.items():
            for keyword in kw_list:
                if keyword.lower() in response_text.lower():
                    count = response_text.lower().count(keyword.lower())

                    citation = CitationData(
                        engine_name=engine_name,
                        query_text=query_text,
                        response_text=response_text,
                        keyword_found=keyword,
                        keyword_category=category,
                        citation_count=count,
                        confidence_score=confidence_score,
                        timestamp=datetime.now()
                    )

                    citations.append(citation)

        return citations

    def to_db_record(self, citation: CitationData) -> CitationRecord:
        """
        转换为数据库记录

        Args:
            citation: 引用数据

        Returns:
            CitationRecord: 数据库记录
        """
        return CitationRecord(
            engine_name=citation.engine_name,
            query_text=citation.query_text,
            response_text=citation.response_text,
            keyword_found=citation.keyword_found,
            keyword_category=citation.keyword_category,
            citation_count=citation.citation_count,
            confidence_score=citation.confidence_score,
            timestamp=citation.timestamp,
            raw_response=citation.raw_response
        )

    def calculate_exposure(
        self,
        citations: List[CitationData]
    ) -> Dict[str, int]:
        """
        计算曝光量

        Args:
            citations: 引用数据列表

        Returns:
            Dict[str, int]: 曝光量统计 {keyword: exposure}
        """
        exposure = {}

        for citation in citations:
            keyword = citation.keyword_found
            # 曝光量 = 查询数（这里简化为1次查询）
            if keyword not in exposure:
                exposure[keyword] = 0
            exposure[keyword] += 1

        return exposure

    def analyze_trends(
        self,
        all_citations: List[CitationData]
    ) -> Dict[str, Dict]:
        """
        分析引用趋势

        Args:
            all_citations: 所有引用数据

        Returns:
            Dict[str, Dict]: 趋势分析
                {
                    "keyword1": {
                        "total": 10,
                        "avg_confidence": 0.85,
                        "categories": ["企业名称", "产品名称"]
                    },
                    ...
                }
        """
        trends = {}

        for citation in all_citations:
            keyword = citation.keyword_found

            if keyword not in trends:
                trends[keyword] = {
                    "total": 0,
                    "total_confidence": 0.0,
                    "categories": set()
                }

            trends[keyword]["total"] += citation.citation_count
            trends[keyword]["total_confidence"] += citation.confidence_score
            trends[keyword]["categories"].add(citation.keyword_category)

        # 计算平均值
        for keyword in trends:
            trends[keyword]["avg_confidence"] = (
                trends[keyword]["total_confidence"] / len(trends[keyword]["categories"])
                if trends[keyword]["categories"]
                else 0.0
            )
            trends[keyword]["categories"] = list(trends[keyword]["categories"])

        return trends
