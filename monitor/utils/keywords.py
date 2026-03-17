"""
关键词管理工具
"""

from typing import Dict, List
import json
from pathlib import Path


class KeywordManager:
    """关键词管理器"""

    def __init__(self, keywords: Dict[str, List[str]] = None, config_file: str = None):
        self.keywords = keywords or {}
        self.config_file = config_file

        if self.config_file:
            self.load_from_file(self.config_file)

    def add_keyword(self, category: str, keyword: str):
        """
        添加关键词

        Args:
            category: 分类
            keyword: 关键词
        """
        if category not in self.keywords:
            self.keywords[category] = []
        if keyword not in self.keywords[category]:
            self.keywords[category].append(keyword)

    def add_keywords(self, category: str, keywords: List[str]):
        """
        批量添加关键词

        Args:
            category: 分类
            keywords: 关键词列表
        """
        if category not in self.keywords:
            self.keywords[category] = []
        for keyword in keywords:
            if keyword not in self.keywords[category]:
                self.keywords[category].append(keyword)

    def remove_keyword(self, category: str, keyword: str):
        """
        删除关键词

        Args:
            category: 分类
            keyword: 关键词
        """
        if category in self.keywords and keyword in self.keywords[category]:
            self.keywords[category].remove(keyword)

    def get_keywords(self, category: str = None) -> List[str]:
        """
        获取关键词列表

        Args:
            category: 分类，如果为None则返回所有关键词

        Returns:
            List[str]: 关键词列表
        """
        if category:
            return self.keywords.get(category, [])

        # 返回所有关键词
        all_keywords = []
        for kw_list in self.keywords.values():
            all_keywords.extend(kw_list)
        return all_keywords

    def get_categories(self) -> List[str]:
        """
        获取所有分类

        Returns:
            List[str]: 分类列表
        """
        return list(self.keywords.keys())

    def save_to_file(self, filepath: str):
        """
        保存到文件

        Args:
            filepath: 文件路径
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.keywords, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath: str):
        """
        从文件加载

        Args:
            filepath: 文件路径
        """
        path = Path(filepath)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.keywords = json.load(f)

    def generate_query_variants(self, base_query: str) -> List[str]:
        """
        生成查询变体

        Args:
            base_query: 基础查询

        Returns:
            List[str]: 查询变体列表
        """
        variants = [base_query]

        # 添加不同后缀
        suffixes = ["是什么", "怎么样", "推荐吗", "官网", "价格", "功能"]
        for suffix in suffixes:
            variants.append(f"{base_query}{suffix}")

        # 添加比较类查询
        for category in self.get_categories():
            keywords = self.get_keywords(category)
            for keyword in keywords[:2]:  # 每个分类只用2个关键词
                if keyword != base_query:
                    variants.append(f"{base_query} vs {keyword}")

        return variants[:10]  # 限制返回数量

    def get_all_queries(self) -> List[str]:
        """
        获取所有可能的查询

        Returns:
            List[str]: 查询列表
        """
        queries = []

        for category in self.get_categories():
            for keyword in self.get_keywords(category):
                queries.extend(self.generate_query_variants(keyword))

        return list(set(queries))  # 去重

    def export_summary(self) -> str:
        """
        导出关键词摘要

        Returns:
            str: 摘要文本
        """
        lines = ["关键词摘要", "=" * 40]
        for category, keywords in self.keywords.items():
            lines.append(f"\n{category} ({len(keywords)}):")
            lines.append(", ".join(keywords))
        return "\n".join(lines)
