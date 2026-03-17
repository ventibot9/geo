"""
示例：如何使用GEO监控服务
"""

from database import get_db
from scheduler.tasks import MonitorScheduler
from reporter.generator import ReportGenerator
from utils.keywords import KeywordManager
from config import COMPANY_KEYWORDS


def example_1_basic_monitoring():
    """示例1：基本监控流程"""
    print("=" * 60)
    print("示例1：基本监控流程")
    print("=" * 60)

    # 1. 初始化数据库
    db = get_db()
    print("✓ 数据库已初始化")

    # 2. 创建关键词管理器
    km = KeywordManager(COMPANY_KEYWORDS)
    print(f"✓ 关键词已加载：{len(km.get_categories())}个分类，{len(km.get_keywords())}个关键词")

    # 3. 初始化调度器
    scheduler = MonitorScheduler()
    print(f"✓ 调度器已初始化，{len(scheduler.engines)}个AI引擎")

    # 4. 运行一次监控
    print("\n开始执行监控...")
    scheduler.trigger_now()
    print("✓ 监控完成")

    # 5. 生成报告
    print("\n生成报告...")
    generator = ReportGenerator()
    json_file, text_file = generator.generate_full_report()
    print(f"✓ 报告已生成：")
    print(f"  - JSON: {json_file}")
    print(f"  - Text: {text_file}")


def example_2_keyword_management():
    """示例2：关键词管理"""
    print("\n" + "=" * 60)
    print("示例2：关键词管理")
    print("=" * 60)

    # 创建关键词管理器
    km = KeywordManager()

    # 添加关键词
    km.add_keyword("产品名称", "新的产品A")
    km.add_keywords("产品名称", ["新的产品B", "新的产品C"])
    km.add_keyword("品牌词", "GEO Pro")

    print("✓ 关键词已添加")

    # 查看所有分类
    print(f"\n分类列表：{km.get_categories()}")

    # 查看某个分类的关键词
    product_keywords = km.get_keywords("产品名称")
    print(f"\n产品名称分类：{product_keywords}")

    # 生成查询变体
    queries = km.generate_query_variants("GEO")
    print(f"\nGEO的查询变体（前5个）：{queries[:5]}")

    # 导出摘要
    print("\n关键词摘要：")
    print(km.export_summary())


def example_3_database_queries():
    """示例3：数据库查询"""
    print("\n" + "=" * 60)
    print("示例3：数据库查询")
    print("=" * 60)

    db = get_db()

    with db.session() as session:
        from database.models import CitationRecord
        from datetime import datetime, timedelta

        # 查询最近的引用记录
        recent = session.query(CitationRecord).order_by(
            CitationRecord.timestamp.desc()
        ).limit(5).all()

        print("最近的5条引用记录：")
        for record in recent:
            print(f"  - {record.engine_name}: {record.keyword_found} ({record.timestamp})")

        # 按引擎统计
        print("\n按引擎统计：")
        from sqlalchemy import func
        stats = session.query(
            CitationRecord.engine_name,
            func.count(CitationRecord.id).label('count')
        ).group_by(CitationRecord.engine_name).all()

        for engine_name, count in stats:
            print(f"  - {engine_name}: {count}条记录")

        # 按关键词统计
        print("\n热门关键词（Top 5）：")
        keyword_stats = session.query(
            CitationRecord.keyword_found,
            func.sum(CitationRecord.citation_count).label('total')
        ).group_by(CitationRecord.keyword_found).order_by(
            func.sum(CitationRecord.citation_count).desc()
        ).limit(5).all()

        for keyword, total in keyword_stats:
            print(f"  - {keyword}: {total}次引用")


def example_4_report_generation():
    """示例4：报告生成"""
    print("\n" + "=" * 60)
    print("示例4：报告生成")
    print("=" * 60)

    generator = ReportGenerator()

    # 生成日报
    report = generator.generate_daily_report()

    # 查看摘要
    print("报告摘要：")
    print(f"  - 日期: {report['date']}")
    print(f"  - 总查询: {report['summary']['total_queries']}")
    print(f"  - 总引用: {report['summary']['total_citations']}")
    print(f"  - 平均置信度: {report['summary']['avg_confidence']:.2f}")

    # 查看按引擎统计
    print("\n按引擎统计：")
    for engine, data in report['by_engine'].items():
        print(f"  - {engine}: {data['citations']}引用")

    # 生成文本报告
    text_report = generator.generate_text_report(report)
    print("\n文本报告预览（前500字符）：")
    print(text_report[:500] + "...")

    # 保存报告
    json_file, text_file = generator.generate_full_report()
    print(f"\n✓ 报告已保存到：{json_file}")


def main():
    """运行所有示例"""
    try:
        # 选择要运行的示例
        print("\n请选择要运行的示例：")
        print("1. 基本监控流程")
        print("2. 关键词管理")
        print("3. 数据库查询")
        print("4. 报告生成")
        print("5. 全部运行")

        choice = input("\n输入选项 (1-5): ").strip()

        if choice == "1":
            example_1_basic_monitoring()
        elif choice == "2":
            example_2_keyword_management()
        elif choice == "3":
            example_3_database_queries()
        elif choice == "4":
            example_4_report_generation()
        elif choice == "5":
            example_1_basic_monitoring()
            example_2_keyword_management()
            example_3_database_queries()
            example_4_report_generation()
        else:
            print("无效选项")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
