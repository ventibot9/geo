"""
扫描报告生成器
支持多种格式输出
"""

import json
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        self.results = []

    def add_result(self, result: Dict[str, Any]):
        """
        添加扫描结果

        Args:
            result: 评估结果字典
        """
        self.results.append(result)

    def generate_text(self) -> str:
        """
        生成文本格式报告

        Returns:
            文本报告
        """
        lines = []
        lines.append("=" * 80)
        lines.append("GEO平台AI友好度扫描报告")
        lines.append("=" * 80)
        lines.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"扫描页面数: {len(self.results)}")
        lines.append("")

        # 总体统计
        if self.results:
            avg_score = sum(r['scores']['total'] for r in self.results) / len(self.results)
            lines.append(f"平均得分: {avg_score:.1f}/100")

            # 等级分布
            grade_dist = {}
            for r in self.results:
                grade = r['grade']
                grade_dist[grade] = grade_dist.get(grade, 0) + 1

            lines.append("等级分布:")
            for grade in sorted(grade_dist.keys()):
                lines.append(f"  {grade}级: {grade_dist[grade]}个")
            lines.append("")

        # 详细结果
        for i, result in enumerate(self.results, 1):
            lines.append("-" * 80)
            lines.append(f"[{i}] {result['url']}")
            lines.append(f"等级: {result['grade']} | 总分: {result['scores']['total']}")
            lines.append("")

            # 各项得分
            lines.append("各项得分:")
            lines.append(f"  标题结构:      {result['scores']['heading_structure']:2d}/30")
            lines.append(f"  表格使用:      {result['scores']['table_usage']:2d}/20")
            lines.append(f"  数据完整性:    {result['scores']['data_completeness']:2d}/25")
            lines.append(f"  内容清晰度:    {result['scores']['content_clarity']:2d}/15")
            lines.append(f"  格式兼容性:    {result['scores']['format_compatibility']:2d}/10")
            lines.append("")

            # 优化建议
            if result['suggestions']:
                lines.append("优化建议:")
                for suggestion in result['suggestions']:
                    lines.append(f"  • {suggestion}")
            else:
                lines.append("优化建议: 无")
            lines.append("")

        lines.append("=" * 80)
        lines.append("报告结束")
        lines.append("=" * 80)

        return '\n'.join(lines)

    def generate_json(self) -> str:
        """
        生成JSON格式报告

        Returns:
            JSON报告字符串
        """
        report = {
            'scan_time': datetime.now().isoformat(),
            'total_pages': len(self.results),
            'results': self.results,
            'summary': self._generate_summary() if self.results else {}
        }

        return json.dumps(report, ensure_ascii=False, indent=2)

    def _generate_summary(self) -> Dict[str, Any]:
        """生成统计摘要"""
        total_score = sum(r['scores']['total'] for r in self.results)
        avg_score = total_score / len(self.results)

        # 各项平均分
        avg_scores = {
            'heading_structure': sum(r['scores']['heading_structure'] for r in self.results) / len(self.results),
            'table_usage': sum(r['scores']['table_usage'] for r in self.results) / len(self.results),
            'data_completeness': sum(r['scores']['data_completeness'] for r in self.results) / len(self.results),
            'content_clarity': sum(r['scores']['content_clarity'] for r in self.results) / len(self.results),
            'format_compatibility': sum(r['scores']['format_compatibility'] for r in self.results) / len(self.results),
        }

        # 等级分布
        grade_dist = {}
        for r in self.results:
            grade = r['grade']
            grade_dist[grade] = grade_dist.get(grade, 0) + 1

        # 汇总所有建议
        all_suggestions = {}
        for r in self.results:
            for suggestion in r['suggestions']:
                all_suggestions[suggestion] = all_suggestions.get(suggestion, 0) + 1

        return {
            'average_score': round(avg_score, 2),
            'average_scores': {k: round(v, 2) for k, v in avg_scores.items()},
            'grade_distribution': grade_dist,
            'common_suggestions': sorted(
                all_suggestions.items(),
                key=lambda x: x[1],
                reverse=True
            )
        }

    def generate_markdown(self) -> str:
        """
        生成Markdown格式报告

        Returns:
            Markdown报告字符串
        """
        lines = []
        lines.append("# GEO平台AI友好度扫描报告\n")
        lines.append(f"**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"**扫描页面数**: {len(self.results)}\n")

        # 总体统计
        if self.results:
            avg_score = sum(r['scores']['total'] for r in self.results) / len(self.results)
            lines.append(f"**平均得分**: {avg_score:.1f}/100\n")

            # 等级分布
            grade_dist = {}
            for r in self.results:
                grade = r['grade']
                grade_dist[grade] = grade_dist.get(grade, 0) + 1

            lines.append("## 等级分布\n")
            for grade in ['A', 'B', 'C', 'D', 'E']:
                count = grade_dist.get(grade, 0)
                if count > 0:
                    lines.append(f"- {grade}级: {count}个\n")

        # 详细结果
        lines.append("\n## 详细扫描结果\n")

        for i, result in enumerate(self.results, 1):
            lines.append(f"### [{i}] {result['url']}\n")
            lines.append(f"**等级**: {result['grade']} | **总分**: {result['scores']['total']}\n")

            # 各项得分表格
            lines.append("| 评估项 | 得分 | 满分 |")
            lines.append("|--------|------|------|")
            lines.append(f"| 标题结构 | {result['scores']['heading_structure']} | 30 |")
            lines.append(f"| 表格使用 | {result['scores']['table_usage']} | 20 |")
            lines.append(f"| 数据完整性 | {result['scores']['data_completeness']} | 25 |")
            lines.append(f"| 内容清晰度 | {result['scores']['content_clarity']} | 15 |")
            lines.append(f"| 格式兼容性 | {result['scores']['format_compatibility']} | 10 |\n")

            # 优化建议
            if result['suggestions']:
                lines.append("**优化建议**:\n")
                for suggestion in result['suggestions']:
                    lines.append(f"- {suggestion}\n")
            else:
                lines.append("**优化建议**: 无\n")

        return ''.join(lines)

    def save_report(self, filepath: str, format: str = 'text'):
        """
        保存报告到文件

        Args:
            filepath: 文件路径
            format: 报告格式 (text|json|markdown)
        """
        content = ''
        if format == 'json':
            content = self.generate_json()
        elif format == 'markdown':
            content = self.generate_markdown()
        else:
            content = self.generate_text()

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"报告已保存到: {filepath}")
