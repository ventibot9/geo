# GEO平台内容扫描器 - 交付文档

## 📋 项目完成情况

✅ **所有需求已完成**

---

## 🎯 核心功能

### 1. 网站爬虫
- ✅ SimpleCrawler: 静态页面快速爬取
- ✅ WebCrawler: 基于Puppeteer的动态页面爬取（支持JS渲染）
- ✅ 自定义User-Agent和视口设置
- ✅ 支持等待特定元素（用于SPA应用）

### 2. AI友好度评分算法（100分制）

| 维度 | 满分 | 说明 |
|------|------|------|
| 标题结构 | 30 | H1/H2/H3层级完整性、无跳级 |
| 表格使用 | 20 | 表格存在、表头、数据完整 |
| 数据完整性 | 25 | meta信息、data属性、链接、图片alt |
| 内容清晰度 | 15 | 段落、列表、代码块结构 |
| 格式兼容性 | 10 | 语义化标签、Markdown/API友好 |

**等级划分**: A(90-100), B(80-89), C(70-79), D(60-69), E(0-59)

### 3. 扫描报告
- ✅ Text格式（终端输出）
- ✅ JSON格式（程序处理）
- ✅ Markdown格式（文档展示）

### 4. CLI工具
- ✅ 单URL扫描
- ✅ 批量扫描
- ✅ 从文件读取URL列表
- ✅ 美化终端输出

### 5. 任务调度
- ✅ 并发任务调度器
- ✅ 周期性任务调度

---

## 📖 评分算法详细说明

### 1. 标题结构（30分）

| 子项 | 满分 | 评分标准 |
|------|------|----------|
| H1唯一性 | 10 | 10分: 有且仅有1个H1；5分: 多个H1；0分: 无H1 |
| H2存在性 | 10 | 10分: ≥3个H2；5分: 1-2个H2；0分: 无H2 |
| H3存在性 | 5 | 5分: ≥3个H3；2分: 1-2个H3；0分: 无H3 |
| 层级连续性 | 5 | 5分: 无跳级；0分: 有跳级 |

### 2. 表格使用（20分）

| 子项 | 满分 | 评分标准 |
|------|------|----------|
| 表格存在 | 5 | 5分: 有表格；0分: 无表格 |
| 表头完整 | 5 | 5分: 全部有表头；2分: 部分有表头；0分: 无表头 |
| 结构良好 | 5 | 5分: 所有表格≥2行；0分: 否 |
| 数据完整 | 5 | 5分: 空单元格<10%；2分: 10-50%；0分: >50% |

### 3. 数据完整性（25分）

| 子项 | 满分 | 评分标准 |
|------|------|----------|
| data-*属性 | 10 | 10分: ≥5个；5分: 1-4个；0分: 0个 |
| meta信息 | 8 | 8分: ≥5个；4分: 3-4个；0分: <3个 |
| 链接完整 | 4 | 4分: 全部有效；2分: 部分无效；0分: 大量空链接 |
| 图片alt | 3 | 3分: ≥90%；1分: 50-90%；0分: <50% |

### 4. 内容清晰度（15分）

| 子项 | 满分 | 评分标准 |
|------|------|----------|
| 段落结构 | 5 | 5分: ≥5个段落；3分: 2-4个；0分: <2个 |
| 列表使用 | 5 | 5分: ≥2个列表；3分: 1个；0分: 无 |
| 代码块 | 5 | 5分: ≥2个；2分: 1个；0分: 无 |

### 5. 格式兼容性（10分）

| 子项 | 满分 | 评分标准 |
|------|------|----------|
| 语义化标签 | 5 | 5分: ≥3种；3分: 1-2种；0分: 0种 |
| Markdown友好 | 5 | 5分: 有代码块或(列表+标题)；2分: 结构不完整；0分: 不适合 |

---

## 🚀 CLI使用方法

### 安装依赖

```bash
cd /root/.openclaw/workspace-open-lead/geo-platform/scanner
pip install -r requirements.txt
```

### 基本命令

#### 1. 扫描单个URL

```bash
# 基本用法（输出到终端）
python3 -m geo_scanner.cli scan https://example.com

# 保存为JSON报告
python3 -m geo_scanner.cli scan https://example.com -o report.json -f json

# 保存为Markdown报告
python3 -m geo_scanner.cli scan https://example.com -o report.md -f markdown

# 使用Puppeteer（动态页面）
python3 -m geo_scanner.cli scan https://example.com --wait .content-loaded

# 不使用无头模式（调试）
python3 -m geo_scanner.cli scan https://example.com --no-headless
```

#### 2. 批量扫描多个URL

```bash
# 批量扫描
python3 -m geo_scanner.cli batch https://site1.com https://site2.com https://site3.com

# 保存报告
python3 -m geo_scanner.cli batch \
  https://site1.com \
  https://site2.com \
  -o batch_report.json \
  -f json
```

#### 3. 从文件读取URL列表

创建 `urls.txt` 文件（每行一个URL）：

```
https://example.com/page1
https://example.com/page2
https://example.com/page3
```

然后执行：

```bash
python3 -m geo_scanner.cli from-file urls.txt

# 保存报告
python3 -m geo_scanner.cli from-file urls.txt -o report.json -f json
```

### 命令参数说明

#### scan命令参数

- `URL`: 必需，要扫描的URL
- `-o, --output PATH`: 输出文件路径
- `-f, --format [text|json|markdown]`: 报告格式，默认text
- `--headless/--no-headless`: 是否使用无头浏览器，默认True
- `-w, --wait TEXT`: 等待的CSS选择器（用于动态页面）

#### batch命令参数

- `URLS...`: 必需，多个URL（空格分隔）
- `-o, --output PATH`: 输出文件路径
- `-f, --format [text|json|markdown]`: 报告格式，默认text
- `--headless/--no-headless`: 是否使用无头浏览器

#### from-file命令参数

- `FILEPATH`: 必需，包含URL列表的文件路径
- `-o, --output PATH`: 输出文件路径
- `-f, --format [text|json|markdown]`: 报告格式，默认text

### 查看帮助

```bash
# 主帮助
python3 -m geo_scanner.cli --help

# scan命令帮助
python3 -m geo_scanner.cli scan --help

# batch命令帮助
python3 -m geo_scanner.cli batch --help

# from-file命令帮助
python3 -m geo_scanner.cli from-file --help
```

---

## 💻 编程接口使用

### 基本示例

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

# 3. 查看结果
print(f"URL: {result['url']}")
print(f"总分: {result['scores']['total']}/100")
print(f"等级: {result['grade']}")

print("\n各项得分:")
print(f"  标题结构: {result['scores']['heading_structure']}/30")
print(f"  表格使用: {result['scores']['table_usage']}/20")
print(f"  数据完整性: {result['scores']['data_completeness']}/25")
print(f"  内容清晰度: {result['scores']['content_clarity']}/15")
print(f"  格式兼容性: {result['scores']['format_compatibility']}/10")

print("\n优化建议:")
for suggestion in result['suggestions']:
    print(f"  • {suggestion}")

# 4. 生成报告
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
            wait_for=".content-loaded"  # 等待特定元素
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

---

## 📁 项目结构

```
geo-platform/scanner/
├── geo_scanner/
│   ├── cli.py              # CLI工具入口
│   ├── core/
│   │   ├── crawler.py      # 爬虫模块
│   │   └── scheduler.py    # 任务调度器
│   ├── scoring/
│   │   └── evaluator.py   # AI友好度评估器
│   └── report/
│       └── generator.py    # 报告生成器
├── example.py             # 使用示例
├── requirements.txt       # Python依赖
├── pyproject.toml        # 项目配置
├── README.md             # 项目文档
├── QUICKSTART.md         # 快速开始指南
├── CLI_GUIDE.md          # CLI使用详细指南
├── SCORING_ALGORITHM.md  # 评分算法详解
├── PROJECT_SUMMARY.md    # 项目总结
└── DELIVERY.md           # 本文件
```

---

## ✅ 测试验证

已成功测试以下功能：

1. ✅ 基础爬虫功能
2. ✅ AI友好度评分算法
3. ✅ 报告生成（JSON/Markdown/Text）
4. ✅ CLI工具所有命令
5. ✅ 美化终端输出

测试输出示例：

```
评分结果: E级 (27/100)
┏━━━━━━━━━━━━┳━━━━━━┳━━━━━━┓
┃ 评估项     ┃ 得分 ┃ 满分 ┃
┡━━━━━━━━━━━━╇━━━━━━╇━━━━━━┩
│ 标题结构   │   15 │   30 │
│ 表格使用   │    0 │   20 │
│ 数据完整性 │    7 │   25 │
│ 内容清晰度 │    3 │   15 │
│ 格式兼容性 │    2 │   10 │
└────────────┴──────┴──────┘
╭────────────────────────────────── 优化建议 ──────────────────────────────────╮
│ • 缺少H2标题，建议增加内容层级结构                                           │
│ • 页面缺少表格，适合数据展示的内容建议使用表格                               │
│ • 内容结构不够清晰，AI解析困难                                               │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 📚 更多文档

- **README.md**: 项目介绍和完整功能说明
- **QUICKSTART.md**: 5分钟快速开始指南
- **CLI_GUIDE.md**: CLI工具详细使用方法和示例
- **SCORING_ALGORITHM.md**: 评分算法完整说明和优化建议
- **PROJECT_SUMMARY.md**: 项目完成情况和技术细节

---

## 🎉 项目状态

✅ **开发完成，可直接使用**

所有功能已实现并测试通过，文档完善。
