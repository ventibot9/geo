"""
GEO平台内容扫描器CLI工具
"""

import asyncio
import click
import sys
import logging
from pathlib import Path
from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.crawler import WebCrawler, SimpleCrawler
from .scoring.evaluator import AIFriendlyEvaluator
from .report.generator import ReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """GEO平台AI友好度扫描器"""
    pass


@cli.command()
@click.argument('url')
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'markdown']),
              default='text', help='报告格式')
@click.option('--headless/--no-headless', default=True, help='是否使用无头浏览器')
@click.option('--wait', '-w', help='等待的CSS选择器')
def scan(url, output, format, headless, wait):
    """
    扫描单个URL的AI友好度

    示例:
      geo-scanner scan https://example.com --output report.json --format json
    """
    console.print(f"[cyan]🔍 开始扫描: {url}[/cyan]")

    # 选择爬虫方式
    if wait:
        # 需要等待元素，使用Puppeteer
        result = asyncio.run(scan_with_puppeteer(url, headless, wait))
    else:
        # 使用简单爬虫
        result = scan_simple(url)

    if result.get('error'):
        console.print(f"[red]❌ 扫描失败: {result['error']}[/red]")
        sys.exit(1)

    # 生成报告
    report_gen = ReportGenerator()
    report_gen.add_result(result)

    # 显示结果
    display_result(result)

    # 保存报告
    if output:
        report_gen.save_report(output, format)
        console.print(f"[green]✓ 报告已保存: {output}[/green]")
    else:
        console.print("\n" + report_gen.generate_text())


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'markdown']),
              default='text', help='报告格式')
@click.option('--headless/--no-headless', default=True, help='是否使用无头浏览器')
def batch(urls, output, format, headless):
    """
    批量扫描多个URL

    示例:
      geo-scanner batch https://site1.com https://site2.com -o report.json -f json
    """
    console.print(f"[cyan]🔍 开始批量扫描 {len(urls)} 个URL[/cyan]")

    report_gen = ReportGenerator()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("扫描中...", total=len(urls))

        for url in urls:
            progress.update(task, description=f"扫描: {url}")

            result = scan_simple(url)

            if not result.get('error'):
                report_gen.add_result(result)
            else:
                console.print(f"[red]✗ {url}: {result['error']}[/red]")

            progress.update(task, advance=1)

    # 显示汇总
    display_summary(report_gen)

    # 保存报告
    if output:
        report_gen.save_report(output, format)
        console.print(f"\n[green]✓ 报告已保存: {output}[/green]")
    else:
        console.print("\n" + report_gen.generate_text())


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'markdown']),
              default='text', help='报告格式')
def from_file(filepath, output, format):
    """
    从文件读取URL列表并批量扫描

    示例:
      geo-scanner from-file urls.txt -o report.json -f json
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    console.print(f"[cyan]🔍 从文件读取到 {len(urls)} 个URL[/cyan]")

    report_gen = ReportGenerator()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("扫描中...", total=len(urls))

        for url in urls:
            progress.update(task, description=f"扫描: {url}")

            result = scan_simple(url)

            if not result.get('error'):
                report_gen.add_result(result)
            else:
                console.print(f"[red]✗ {url}: {result['error']}[/red]")

            progress.update(task, advance=1)

    # 显示汇总
    display_summary(report_gen)

    # 保存报告
    if output:
        report_gen.save_report(output, format)
        console.print(f"\n[green]✓ 报告已保存: {output}[/green]")
    else:
        console.print("\n" + report_gen.generate_text())


def scan_simple(url: str) -> dict:
    """使用简单爬虫扫描"""
    crawler = SimpleCrawler()
    page_data = crawler.fetch(url)

    if page_data.get('error'):
        return page_data

    # 评估
    evaluator = AIFriendlyEvaluator()
    result = evaluator.evaluate(page_data)

    return result


async def scan_with_puppeteer(url: str, headless: bool, wait_selector: str) -> dict:
    """使用Puppeteer爬虫扫描"""
    async with WebCrawler(headless=headless) as crawler:
        page_data = await crawler.fetch_page(url, wait_for=wait_selector)

    if page_data.get('error'):
        return page_data

    # 评估
    evaluator = AIFriendlyEvaluator()
    result = evaluator.evaluate(page_data)

    return result


def display_result(result: dict):
    """显示单个扫描结果"""
    scores = result['scores']
    total = scores['total']
    grade = result['grade']

    # 等级颜色
    grade_colors = {'A': 'green', 'B': 'blue', 'C': 'yellow', 'D': 'orange', 'E': 'red'}
    grade_color = grade_colors.get(grade, 'white')

    console.print(f"\n[bold]评分结果: [{grade_color}]{grade}级[/] ({total}/100)[/bold]")

    # 得分表格
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("评估项", style="dim")
    table.add_column("得分", justify="right")
    table.add_column("满分", justify="right")

    items = [
        ("标题结构", scores['heading_structure'], 30),
        ("表格使用", scores['table_usage'], 20),
        ("数据完整性", scores['data_completeness'], 25),
        ("内容清晰度", scores['content_clarity'], 15),
        ("格式兼容性", scores['format_compatibility'], 10),
    ]

    for label, score, max_score in items:
        color = "green" if score >= max_score * 0.8 else "yellow" if score >= max_score * 0.5 else "red"
        table.add_row(label, f"[{color}]{score}[/]", str(max_score))

    console.print(table)

    # 建议面板
    if result['suggestions']:
        suggestions = "\n".join(f"• {s}" for s in result['suggestions'])
        console.print(Panel(suggestions, title="优化建议", border_style="yellow"))
    else:
        console.print(Panel("✓ 内容结构良好，无优化建议", title="优化建议", border_style="green"))


def display_summary(report_gen: ReportGenerator):
    """显示批量扫描汇总"""
    results = report_gen.results

    if not results:
        console.print("[red]没有有效的扫描结果[/red]")
        return

    # 统计
    avg_score = sum(r['scores']['total'] for r in results) / len(results)

    console.print(f"\n[bold]扫描汇总 ({len(results)} 个页面)[/bold]")
    console.print(f"平均得分: {avg_score:.1f}/100")

    # 得分表格
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("URL", max_width=40)
    table.add_column("等级", justify="center")
    table.add_column("总分", justify="right")

    for r in results:
        grade_color = {'A': 'green', 'B': 'blue', 'C': 'yellow', 'D': 'orange', 'E': 'red'}
        color = grade_color.get(r['grade'], 'white')
        table.add_row(r['url'], f"[{color}]{r['grade']}[/]", str(r['scores']['total']))

    console.print(table)


def main():
    """主入口"""
    cli()


if __name__ == '__main__':
    main()
