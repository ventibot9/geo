"""
GEO平台内容扫描器 - 使用示例
"""

from geo_scanner.core.crawler import SimpleCrawler
from geo_scanner.scoring.evaluator import AIFriendlyEvaluator
from geo_scanner.report.generator import ReportGenerator


def main():
    """示例：扫描单个网站"""
    print("🔍 GEO平台AI友好度扫描器示例")
    print("=" * 60)

    # 测试URL列表
    test_urls = [
        "https://example.com",
    ]

    # 创建报告生成器
    report_gen = ReportGenerator()

    for url in test_urls:
        print(f"\n正在扫描: {url}")

        # 1. 爬取页面
        crawler = SimpleCrawler()
        page_data = crawler.fetch(url)

        if page_data.get('error'):
            print(f"❌ 扫描失败: {page_data['error']}")
            continue

        print(f"✓ 页面抓取成功")
        print(f"  标题: {page_data['title']}")

        # 2. 评估AI友好度
        evaluator = AIFriendlyEvaluator()
        result = evaluator.evaluate(page_data)

        # 3. 显示结果
        scores = result['scores']
        print(f"\n评分结果: {result['grade']}级 ({scores['total']}/100)")
        print(f"  标题结构:      {scores['heading_structure']:2d}/30")
        print(f"  表格使用:      {scores['table_usage']:2d}/20")
        print(f"  数据完整性:    {scores['data_completeness']:2d}/25")
        print(f"  内容清晰度:    {scores['content_clarity']:2d}/15")
        print(f"  格式兼容性:    {scores['format_compatibility']:2d}/10")

        if result['suggestions']:
            print(f"\n优化建议:")
            for suggestion in result['suggestions']:
                print(f"  • {suggestion}")
        else:
            print(f"\n✓ 内容结构良好，无优化建议")

        # 添加到报告
        report_gen.add_result(result)

    # 4. 生成并保存报告
    print("\n" + "=" * 60)
    print("生成报告...")

    # 保存为JSON
    report_gen.save_report("example_report.json", format="json")
    print("✓ JSON报告已保存: example_report.json")

    # 保存为Markdown
    report_gen.save_report("example_report.md", format="markdown")
    print("✓ Markdown报告已保存: example_report.md")

    # 显示文本报告
    print("\n文本报告预览:")
    print(report_gen.generate_text())


if __name__ == '__main__':
    main()
