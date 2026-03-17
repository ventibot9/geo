"""
AI友好度评分算法
评估网站内容结构对AI的友好程度
"""

from typing import Dict, Any, List, Tuple
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)


class AIFriendlyEvaluator:
    """AI友好度评估器"""

    def __init__(self):
        """初始化评估器"""
        self.scores = {
            'heading_structure': 0,  # 标题结构: 30分
            'table_usage': 0,         # 表格使用: 20分
            'data_completeness': 0,  # 数据完整性: 25分
            'content_clarity': 0,    # 内容清晰度: 15分
            'format_compatibility': 0,  # 格式兼容性: 10分
            'total': 0,
        }
        self.suggestions = []

    def evaluate(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估页面AI友好度

        Args:
            page_data: 页面数据字典

        Returns:
            评分结果和建议
        """
        soup = page_data.get('soup', BeautifulSoup('', 'lxml'))
        html = page_data.get('html', '')
        url = page_data.get('url', '')

        logger.info(f"开始评估: {url}")

        # 重置评分
        self._reset_scores()

        # 评估各项指标
        self._evaluate_heading_structure(soup)
        self._evaluate_table_usage(soup)
        self._evaluate_data_completeness(soup, html)
        self._evaluate_content_clarity(soup, html)
        self._evaluate_format_compatibility(soup, html)

        # 计算总分
        self.scores['total'] = sum(self.scores[k] for k in self.scores if k != 'total')

        result = {
            'url': url,
            'scores': self.scores.copy(),
            'suggestions': self.suggestions.copy(),
            'grade': self._get_grade(self.scores['total']),
        }

        logger.info(f"评估完成: {url}, 得分: {self.scores['total']}")
        return result

    def _reset_scores(self):
        """重置评分"""
        self.scores = {
            'heading_structure': 0,
            'table_usage': 0,
            'data_completeness': 0,
            'content_clarity': 0,
            'format_compatibility': 0,
            'total': 0,
        }
        self.suggestions = []

    def _evaluate_heading_structure(self, soup: BeautifulSoup):
        """
        评估标题层级结构（30分）

        评分规则:
        - H1存在且唯一: 10分
        - H2存在且有层次: 10分
        - H3存在且结构合理: 5分
        - 层级无跳级: 5分
        """
        score = 0

        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')

        # H1存在且唯一
        if len(h1_tags) == 1:
            score += 10
        elif len(h1_tags) == 0:
            self.suggestions.append("缺少H1标题，建议添加唯一的H1标题")
        else:
            score += 5
            self.suggestions.append(f"页面有{len(h1_tags)}个H1标题，建议只保留一个")

        # H2存在且有层次
        if len(h2_tags) >= 3:
            score += 10
        elif len(h2_tags) > 0:
            score += 5
            self.suggestions.append(f"页面只有{len(h2_tags)}个H2标题，建议增加小标题层级")
        else:
            self.suggestions.append("缺少H2标题，建议增加内容层级结构")

        # H3存在
        if len(h3_tags) >= 3:
            score += 5
        elif len(h3_tags) > 0:
            score += 2

        # 检查层级是否跳级（例如H1后直接H3）
        headings = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append(int(tag.name[1]))

        for i in range(1, len(headings)):
            if headings[i] > headings[i-1] + 1:
                score += 0  # 跳级扣分
                if not any("标题层级" in s for s in self.suggestions):
                    self.suggestions.append("检测到标题层级跳级，建议保持连续的层级结构")
                break
        else:
            score += 5

        self.scores['heading_structure'] = min(30, score)

    def _evaluate_table_usage(self, soup: BeautifulSoup):
        """
        评估表格使用情况（20分）

        评分规则:
        - 表格存在: 5分
        - 表格有表头: 5分
        - 表格结构化好: 5分
        - 表格数据完整: 5分
        """
        score = 0

        tables = soup.find_all('table')

        if tables:
            score += 5
        else:
            self.suggestions.append("页面缺少表格，适合数据展示的内容建议使用表格")

            # 即使没有表格也给一些基础分
            self.scores['table_usage'] = 0
            return

        # 检查表头
        tables_with_headers = 0
        for table in tables:
            thead = table.find('thead')
            if thead:
                tables_with_headers += 1
            else:
                # 检查第一行是否是th
                first_row = table.find('tr')
                if first_row and first_row.find_all('th'):
                    tables_with_headers += 1

        if tables_with_headers == len(tables) and len(tables) > 0:
            score += 5
        elif tables_with_headers > 0:
            score += 2
            self.suggestions.append(f"部分表格缺少表头({len(tables)-tables_with_headers}个)，建议补充")

        # 检查表格结构
        well_structured = 0
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) >= 2:
                well_structured += 1

        if well_structured == len(tables):
            score += 5

        # 检查表格数据完整性（空单元格）
        total_cells = 0
        empty_cells = 0
        for table in tables:
            cells = table.find_all(['td', 'th'])
            total_cells += len(cells)
            empty_cells += sum(1 for cell in cells if not cell.get_text(strip=True))

        if total_cells > 0 and (empty_cells / total_cells) < 0.1:
            score += 5
        elif empty_cells > 0:
            score += 2
            self.suggestions.append(f"表格中有{empty_cells}个空单元格，建议补充数据")

        self.scores['table_usage'] = min(20, score)

    def _evaluate_data_completeness(self, soup: BeautifulSoup, html: str):
        """
        评估数据完整性（25分）

        评分规则:
        - 关键参数标签: 10分
        - 元数据完整: 8分
        - 链接可访问: 4分
        - 图片有alt: 3分
        """
        score = 0

        # 检查关键参数标签（data属性）
        data_tags = soup.find_all(attrs=lambda x: x and x.startswith('data-'))
        if len(data_tags) > 5:
            score += 10
        elif len(data_tags) > 0:
            score += 5
            self.suggestions.append("data-* 属性较少，考虑为关键数据添加data属性")

        # 检查meta信息
        meta_tags = soup.find_all('meta')
        if len(meta_tags) >= 5:
            score += 8
        elif len(meta_tags) >= 3:
            score += 4
            self.suggestions.append("meta信息不完整，建议补充description、keywords等")

        # 检查链接
        links = soup.find_all('a', href=True)
        broken_links = sum(1 for a in links if not a['href'].strip())

        if len(links) > 0 and broken_links == 0:
            score += 4
        elif broken_links > 0:
            score += 2
            self.suggestions.append(f"发现{broken_links}个空链接，请检查")

        # 检查图片alt属性
        images = soup.find_all('img')
        images_with_alt = sum(1 for img in images if img.get('alt'))

        if len(images) > 0:
            alt_ratio = images_with_alt / len(images)
            if alt_ratio >= 0.9:
                score += 3
            elif alt_ratio >= 0.5:
                score += 1
                self.suggestions.append(f"{len(images)-images_with_alt}张图片缺少alt属性")
        else:
            score += 3  # 没有图片也算完整

        self.scores['data_completeness'] = min(25, score)

    def _evaluate_content_clarity(self, soup: BeautifulSoup, html: str):
        """
        评估内容清晰度（15分）

        评分规则:
        - 段落结构清晰: 5分
        - 列表使用合理: 5分
        - 代码块格式化: 5分
        """
        score = 0

        # 检查段落
        paragraphs = soup.find_all('p')
        if len(paragraphs) >= 5:
            score += 5
        elif len(paragraphs) >= 2:
            score += 3

        # 检查列表
        lists = soup.find_all(['ul', 'ol'])
        if len(lists) >= 2:
            score += 5
        elif len(lists) >= 1:
            score += 3

        # 检查代码块
        code_blocks = soup.find_all(['pre', 'code'])
        if len(code_blocks) >= 2:
            score += 5
        elif len(code_blocks) >= 1:
            score += 2

        self.scores['content_clarity'] = min(15, score)

    def _evaluate_format_compatibility(self, soup: BeautifulSoup, html: str):
        """
        评估格式兼容性（10分）

        评分规则:
        - 语义化标签: 5分
        - Markdown友好: 5分
        """
        score = 0

        # 检查语义化标签
        semantic_tags = ['article', 'section', 'aside', 'nav', 'header', 'footer', 'main']
        semantic_count = sum(len(soup.find_all(tag)) for tag in semantic_tags)

        if semantic_count >= 3:
            score += 5
        elif semantic_count >= 1:
            score += 3
            self.suggestions.append("建议使用更多HTML5语义化标签")

        # 检查是否类似Markdown/API文档格式
        # 检查是否有代码块、列表、标题等结构
        has_code = bool(soup.find_all(['pre', 'code']))
        has_lists = bool(soup.find_all(['ul', 'ol']))
        has_headings = bool(soup.find_all(['h1', 'h2', 'h3']))

        if has_code or (has_lists and has_headings):
            score += 5
        else:
            score += 2
            self.suggestions.append("内容结构不够清晰，AI解析困难")

        self.scores['format_compatibility'] = min(10, score)

    def _get_grade(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'E'
