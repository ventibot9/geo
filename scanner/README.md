# GEO平台内容AI友好度扫描器

一个用于评估网站内容对AI友好程度的扫描工具，帮助优化网站结构以便更好地被AI理解和索引。

## 功能特性

- ✅ 基于Puppeteer的动态页面爬虫（支持JS渲染）
- ✅ 静态页面快速爬取
- ✅ AI友好度多维评分算法
- ✅ 结构化扫描报告（Text/JSON/Markdown）
- ✅ 批量扫描和任务调度
- ✅ 命令行CLI工具

## 安装

### 环境要求

- Python 3.11+
- Node.js 18+ (用于Puppeteer)

### 安装依赖

```bash
pip install -r requirements.txt
```

## 评分标准

### 总分：100分

| 评估项 | 满分 | 说明 |
|--------|------|------|
| 标题结构 | 30 | H1/H2/H3层级完整性、无跳级 |
| 表格使用 | 20 | 表格存在性、表头、数据完整 |
| 数据完整性 | 25 | meta信息、data属性、链接、图片alt |
| 内容清晰度 | 15 | 段落、列表、代码块结构 |
| 格式兼容性 | 10 | 语义化标签、Markdown/API友好 |

### 等级划分

- **A级**: 90-100分 - 结构优秀
- **B级**: 80-89分 - 结构良好
- **C级**: 70-79分 - 结构一般
- **D级**: 60-69分 - 需要改进
- **E级**: 0-59分 - 需要重构

## CLI使用方法

### 扫描单个URL

```bash
# 基本用法
geo-scanner scan https://example.com

# 输出到JSON文件
geo-scanner scan https://example.com -o report.json -f json

# 输出到Markdown文件
geo-scanner scan https://example.com -o report.md -f markdown

# 使用Puppeteer（需要JS渲染的页面）
geo-scanner scan https://example.com --no-headless -w .content-loaded
```

### 批量扫描多个URL

```bash
# 扫描多个URL
geo-scanner batch https://site1.com https://site2.com https://site3.com -o batch-report.json -f json

# 从文件读取URL列表
# urls.txt 文件内容（每行一个URL）:
# https://site1.com
# https://site2.com
# https://site3.com

geo-scanner from-file urls.txt -o report.md -f markdown
```

### 查看帮助

```bash
geo-scanner --help
geo-scanner scan --help
geo-scanner batch --help
geo-scanner from-file --help
```

## 编程接口使用

### 基本使用

```python
from geo_scanner.core.crawler import SimpleCrawler
from geo_scanner.scoring.evaluator import AIFriendlyEvaluator
from geo_scanner.report.generator import ReportGenerator

# 1. 爬取页面
crawler = SimpleCrawler()
page_data = crawler.fetch("https://example.com")

# 2. 评估AI友好度
evaluator = AIFriendlyEvaluator()
result = evaluator.evaluate(page_data)

print(f"得分: {result['scores']['total']}/100")
print(f"等级: {result['grade']}")
print(f"建议: {result['suggestions']}")

# 3. 生成报告
report_gen = ReportGenerator()
report_gen.add_result(result)
report_gen.save_report("report.json", format="json")
```

### 使用Puppeteer（动态页面）

```python
import asyncio
from geo_scanner.core.crawler import WebCrawler
from geo_scanner.scoring.evaluator import AIFriendlyEvaluator

async def scan_dynamic():
    async with WebCrawler(headless=True) as crawler:
        page_data = await crawler.fetch_page(
            "https://example.com",
            wait_for=".content-loaded"  # 等待特定元素出现
        )

    evaluator = AIFriendlyEvaluator()
    result = evaluator.evaluate(page_data)

    return result

# 运行
result = asyncio.run(scan_dynamic())
print(f"得分: {result['scores']['total']}/100")
```

### 批量扫描

```python
import asyncio
from geo_scanner.core.crawler import SimpleCrawler
from geo_scanner.core.scheduler import TaskScheduler, ScanTask
from geo_scanner.scoring.evaluator import AIFriendlyEvaluator

urls = [
    "https://site1.com",
    "https://site2.com",
    "https://site3.com",
]

# 创建调度器
scheduler = TaskScheduler(max_concurrent=3)

# 添加任务
def scan_url(url: str) -> dict:
    crawler = SimpleCrawler()
    page_data = crawler.fetch(url)
    evaluator = AIFriendlyEvaluator()
    return evaluator.evaluate(page_data)

for url in urls:
    scheduler.add_task(ScanTask(url))

# 运行所有任务
asyncio.run(scheduler.run_all(scan_url))

# 查看状态
print(scheduler.get_status())
```

### 定期扫描

```python
import asyncio
from geo_scanner.core.crawler import SimpleCrawler
from geo_scanner.core.scheduler import PeriodicScheduler
from geo_scanner.scoring.evaluator import AIFriendlyEvaluator

# 创建周期调度器（每60分钟执行一次）
periodic_scheduler = PeriodicScheduler(interval_minutes=60)

# 添加要定期扫描的URL
periodic_scheduler.add_url("https://site1.com")
periodic_scheduler.add_url("https://site2.com")

def scan_url(url: str) -> dict:
    crawler = SimpleCrawler()
    page_data = crawler.fetch(url)
    evaluator = AIFriendlyEvaluator()
    return evaluator.evaluate(page_data)

# 检查并执行（可以放在定时任务中）
async def check_and_run():
    if periodic_scheduler.should_run():
        await periodic_scheduler.run_if_due(scan_url)

# 模拟定时检查
asyncio.run(check_and_run())
```

## 项目结构

```
geo-platform/scanner/
├── geo_scanner/
│   ├── __init__.py
│   ├── cli.py              # CLI工具入口
│   ├── core/
│   │   ├── crawler.py      # 爬虫模块
│   │   └── scheduler.py    # 任务调度器
│   ├── scoring/
│   │   └── evaluator.py   # AI友好度评估算法
│   └── report/
│       └── generator.py    # 报告生成器
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 开发

### 运行测试

```bash
python -m pytest tests/
```

### 代码风格

遵循PEP 8规范，使用black格式化代码。

## License

MIT
