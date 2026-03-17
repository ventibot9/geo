"""
监控报告生成器
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import json

from config import REPORT_CONFIG
from database import get_db
from database.models import CitationRecord, KeywordStats, MonitorTask


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.db = get_db()
        self.output_dir = Path(REPORT_CONFIG["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_report(self, date: datetime = None) -> Dict:
        """
        生成日报

        Args:
            date: 报告日期，默认为今天

        Returns:
            Dict: 报告数据
        """
        if date is None:
            date = datetime.now()

        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        report = {
            "date": date.strftime(REPORT_CONFIG["date_format"]),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {},
            "by_engine": {},
            "by_keyword": {},
            "by_category": {},
            "trends": {}
        }

        with self.db.session() as session:
            # 总体统计
            all_records = session.query(CitationRecord).filter(
                CitationRecord.timestamp >= start_date,
                CitationRecord.timestamp < end_date
            ).all()

            report["summary"] = {
                "total_queries": len(set(r.query_text for r in all_records)),
                "total_citations": len(all_records),
                "unique_keywords": len(set(r.keyword_found for r in all_records)),
                "avg_confidence": sum(r.confidence_score for r in all_records) / len(all_records) if all_records else 0
            }

            # 按引擎统计
            for record in all_records:
                engine = record.engine_name
                if engine not in report["by_engine"]:
                    report["by_engine"][engine] = {
                        "citations": 0,
                        "keywords": set(),
                        "avg_confidence": []
                    }
                report["by_engine"][engine]["citations"] += 1
                report["by_engine"][engine]["keywords"].add(record.keyword_found)
                report["by_engine"][engine]["avg_confidence"].append(record.confidence_score)

            # 转换set为list并计算平均置信度
            for engine in report["by_engine"]:
                report["by_engine"][engine]["keywords"] = list(report["by_engine"][engine]["keywords"])
                confs = report["by_engine"][engine]["avg_confidence"]
                report["by_engine"][engine]["avg_confidence"] = sum(confs) / len(confs) if confs else 0

            # 按关键词统计
            for record in all_records:
                keyword = record.keyword_found
                if keyword not in report["by_keyword"]:
                    report["by_keyword"][keyword] = {
                        "total_citations": 0,
                        "engines": set(),
                        "categories": set(),
                        "avg_confidence": []
                    }
                report["by_keyword"][keyword]["total_citations"] += record.citation_count
                report["by_keyword"][keyword]["engines"].add(record.engine_name)
                report["by_keyword"][keyword]["categories"].add(record.keyword_category)
                report["by_keyword"][keyword]["avg_confidence"].append(record.confidence_score)

            for keyword in report["by_keyword"]:
                report["by_keyword"][keyword]["engines"] = list(report["by_keyword"][keyword]["engines"])
                report["by_keyword"][keyword]["categories"] = list(report["by_keyword"][keyword]["categories"])
                confs = report["by_keyword"][keyword]["avg_confidence"]
                report["by_keyword"][keyword]["avg_confidence"] = sum(confs) / len(confs) if confs else 0

            # 按分类统计
            for record in all_records:
                category = record.keyword_category
                if category not in report["by_category"]:
                    report["by_category"][category] = {
                        "total_citations": 0,
                        "unique_keywords": set()
                    }
                report["by_category"][category]["total_citations"] += record.citation_count
                report["by_category"][category]["unique_keywords"].add(record.keyword_found)

            for category in report["by_category"]:
                report["by_category"][category]["unique_keywords"] = len(report["by_category"][category]["unique_keywords"])

            # 趋势分析（最近7天）
            report["trends"] = self._calculate_trends(session, start_date, end_date)

        return report

    def _calculate_trends(
        self,
        session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        计算趋势

        Args:
            session: 数据库会话
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict: 趋势数据
        """
        trends = {
            "daily_trends": [],
            "top_keywords": []
        }

        # 最近7天的每日趋势
        for i in range(7):
            day_start = end_date - timedelta(days=i+1)
            day_end = day_start + timedelta(days=1)

            records = session.query(CitationRecord).filter(
                CitationRecord.timestamp >= day_start,
                CitationRecord.timestamp < day_end
            ).all()

            if records:
                trends["daily_trends"].append({
                    "date": day_start.strftime(REPORT_CONFIG["date_format"]),
                    "citations": len(records),
                    "unique_keywords": len(set(r.keyword_found for r in records))
                })

        # 热门关键词（按引用次数）
        stats = session.query(KeywordStats).filter(
            KeywordStats.date >= start_date - timedelta(days=7)
        ).all()

        # 排序并取前10
        sorted_stats = sorted(
            stats,
            key=lambda x: x.total_citations,
            reverse=True
        )[:10]

        trends["top_keywords"] = [
            {
                "keyword": stat.keyword,
                "citations": stat.total_citations,
                "engine": stat.engine_name,
                "avg_confidence": stat.avg_confidence
            }
            for stat in sorted_stats
        ]

        return trends

    def save_report(self, report: Dict, filename: str = None) -> Path:
        """
        保存报告到文件

        Args:
            report: 报告数据
            filename: 文件名，默认自动生成

        Returns:
            Path: 报告文件路径
        """
        if filename is None:
            filename = f"report_{report['date']}.json"

        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return filepath

    def generate_text_report(self, report: Dict) -> str:
        """
        生成文本格式报告

        Args:
            report: 报告数据

        Returns:
            str: 文本报告
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"GEO平台AI引用监控报告 - {report['date']}")
        lines.append("=" * 60)
        lines.append("")

        # 总体统计
        lines.append("【总体统计】")
        lines.append(f"查询次数: {report['summary']['total_queries']}")
        lines.append(f"引用次数: {report['summary']['total_citations']}")
        lines.append(f"涉及关键词: {report['summary']['unique_keywords']}")
        lines.append(f"平均置信度: {report['summary']['avg_confidence']:.2f}")
        lines.append("")

        # 按引擎
        lines.append("【按引擎统计】")
        for engine, data in report["by_engine"].items():
            lines.append(f"  {engine}:")
            lines.append(f"    引用数: {data['citations']}")
            lines.append(f"    关键词: {', '.join(data['keywords'][:5])}")
            lines.append(f"    置信度: {data['avg_confidence']:.2f}")
        lines.append("")

        # 热门关键词
        lines.append("【热门关键词】")
        for kw_data in report["trends"]["top_keywords"][:5]:
            lines.append(f"  {kw_data['keyword']}: {kw_data['citations']}次引用")
        lines.append("")

        # 趋势
        lines.append("【7天趋势】")
        for trend in report["trends"]["daily_trends"]:
            lines.append(f"  {trend['date']}: {trend['citations']}引用, {trend['unique_keywords']}关键词")

        return "\n".join(lines)

    def generate_full_report(self, date: datetime = None) -> tuple:
        """
        生成完整报告（JSON + 文本）

        Args:
            date: 报告日期

        Returns:
            tuple: (json_file_path, text_file_path)
        """
        report = self.generate_daily_report(date)

        # 保存JSON
        json_file = self.save_report(report)

        # 生成并保存文本
        text_content = self.generate_text_report(report)
        text_file = self.output_dir / f"report_{report['date']}.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text_content)

        return json_file, text_file
