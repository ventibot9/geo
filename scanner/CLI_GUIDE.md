# CLI工具使用方法

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 安装CLI（开发模式）
pip install -e .
```

安装后，可以在任何地方使用 `geo-scanner` 命令。

---

## 基本命令

### 1. 扫描单个URL

#### 语法
```bash
geo-scanner scan [OPTIONS] URL
```

#### 选项
- `--output`, `-o`: 输出文件路径
- `--format`, `-f`: 报告格式（text|json|markdown），默认：text
- `--headless/--no-headless`: 是否使用无头浏览器，默认：True
- `--wait`, `-w`: 等待的CSS选择器（用于动态页面）

#### 示例

**基本用法（输出到终端）**
```bash
geo-scanner scan https://example.com
```

**输出到JSON文件**
```bash
geo-scanner scan https://example.com -o report.json -f json
```

**输出到Markdown文件**
```bash
geo-scanner scan https://example.com -o report.md -f markdown
```

**使用Puppeteer扫描动态页面**
```bash
# 等待特定元素出现
geo-scanner scan https://example.com --wait .content-loaded

# 不使用无头模式（可以看到浏览器窗口）
geo-scanner scan https://example.com --no-headless
```

**完整示例**
```bash
geo-scanner scan https://example.com \
  -o my_report.json \
  -f json \
  --wait .main-content
```

---

### 2. 批量扫描多个URL

#### 语法
```bash
geo-scanner batch [OPTIONS] URLS...
```

#### 选项
- `--output`, `-o`: 输出文件路径
- `--format`, `-f`: 报告格式（text|json|markdown），默认：text
- `--headless/--no-headless`: 是否使用无头浏览器，默认：True

#### 示例

**批量扫描（输出到终端）**
```bash
geo-scanner batch https://site1.com https://site2.com https://site3.com
```

**批量扫描并保存为JSON**
```bash
geo-scanner batch \
  https://site1.com \
  https://site2.com \
  https://site3.com \
  -o batch_report.json \
  -f json
```

**批量扫描并保存为Markdown**
```bash
geo-scanner batch \
  https://api.example.com/docs \
  https://docs.example.com/guide \
  -o docs_report.md \
  -f markdown
```

---

### 3. 从文件读取URL列表

#### 语法
```bash
geo-scanner from-file [OPTIONS] FILEPATH
```

#### 选项
- `--output`, `-o`: 输出文件路径
- `--format`, `-f`: 报告格式（text|json|markdown），默认：text

#### 文件格式
创建一个文本文件（如`urls.txt`），每行一个URL：

```
https://example.com/page1
https://example.com/page2
https://example.com/page3
```

#### 示例

**从文件扫描**
```bash
geo-scanner from-file urls.txt
```

**从文件扫描并保存报告**
```bash
geo-scanner from-file urls.txt -o report.json -f json
```

**从文件扫描并生成Markdown报告**
```bash
geo-scanner from-file urls.txt -o report.md -f markdown
```

---

## 查看帮助

```bash
# 查看主帮助
geo-scanner --help

# 查看scan命令帮助
geo-scanner scan --help

# 查看batch命令帮助
geo-scanner batch --help

# 查看from-file命令帮助
geo-scanner from-file --help
```

---

## 输出格式

### 1. Text格式（默认）

适合在终端直接查看，格式简洁。

**示例输出**:
```
================================================================================
GEO平台AI友好度扫描报告
================================================================================
扫描时间: 2026-03-17 05:30:00
扫描页面数: 1

平均得分: 75.0/100
等级分布:
  B级: 1个

--------------------------------------------------------------------------------
[1] https://example.com
等级: B | 总分: 75

各项得分:
  标题结构:      25/30
  表格使用:      15/20
  数据完整性:    18/25
  内容清晰度:    12/15
  格式兼容性:     5/10

优化建议:
  • 页面有2个H1标题，建议只保留一个
  • 部分表格缺少表头(1个)，建议补充
  • 建议使用更多HTML5语义化标签

================================================================================
报告结束
================================================================================
```

### 2. JSON格式

适合程序处理，包含完整的结构化数据。

**示例输出**:
```json
{
  "scan_time": "2026-03-17T05:30:00",
  "total_pages": 1,
  "results": [
    {
      "url": "https://example.com",
      "scores": {
        "heading_structure": 25,
        "table_usage": 15,
        "data_completeness": 18,
        "content_clarity": 12,
        "format_compatibility": 5,
        "total": 75
      },
      "suggestions": [
        "页面有2个H1标题，建议只保留一个",
        "部分表格缺少表头(1个)，建议补充"
      ],
      "grade": "B"
    }
  ],
  "summary": {
    "average_score": 75.0,
    "average_scores": {
      "heading_structure": 25.0,
      "table_usage": 15.0,
      "data_completeness": 18.0,
      "content_clarity": 12.0,
      "format_compatibility": 5.0
    },
    "grade_distribution": {
      "B": 1
    },
    "common_suggestions": [
      ["页面有2个H1标题，建议只保留一个", 1],
      ["部分表格缺少表头(1个)，建议补充", 1]
    ]
  }
}
```

### 3. Markdown格式

适合生成文档或在GitHub等平台展示。

**示例输出**:
```markdown
# GEO平台AI友好度扫描报告

**扫描时间**: 2026-03-17 05:30:00
**扫描页面数**: 1

**平均得分**: 75.0/100

## 等级分布

- B级: 1个

## 详细扫描结果

### [1] https://example.com

**等级**: B | **总分**: 75

| 评估项 | 得分 | 满分 |
|--------|------|------|
| 标题结构 | 25 | 30 |
| 表格使用 | 15 | 20 |
| 数据完整性 | 18 | 25 |
| 内容清晰度 | 12 | 15 |
| 格式兼容性 | 5 | 10 |

**优化建议**:

- 页面有2个H1标题，建议只保留一个
- 部分表格缺少表头(1个)，建议补充
```

---

## 实际使用场景

### 场景1：定期检查网站质量

```bash
# 创建定时任务，每天执行一次
# crontab -e
0 9 * * * /usr/local/bin/geo-scanner batch https://example.com -o /var/reports/$(date +\%Y\%m\%d).json -f json
```

### 场景2：API文档优化

```bash
# 扫描API文档页面
geo-scanner scan https://api.example.com/docs \
  -o api_scan.md \
  -f markdown

# 根据建议优化文档结构
```

### 场景3：竞品分析

```bash
# 创建竞品URL列表文件
echo "https://competitor1.com" > competitors.txt
echo "https://competitor2.com" >> competitors.txt
echo "https://competitor3.com" >> competitors.txt

# 批量扫描对比
geo-scanner from-file competitors.txt -o competitors_report.json -f json
```

### 场景4：内容迁移前评估

```bash
# 迁移前评估旧站点的AI友好度
geo-scanner from-file old_site_urls.txt \
  -o migration_assessment.md \
  -f markdown
```

---

## 常见问题

### Q1: 扫描失败怎么办？

检查以下几点：
1. URL是否正确且可访问
2. 网络连接是否正常
3. 是否需要使用`--wait`选项等待动态加载

```bash
# 尝试增加等待时间
geo-scanner scan https://example.com --wait .main-content
```

### Q2: 动态页面扫描不准确？

使用Puppeteer模式：

```bash
# 等待特定元素出现
geo-scanner scan https://example.com --wait .content-loaded

# 或者使用非无头模式调试
geo-scanner scan https://example.com --no-headless
```

### Q3: 批量扫描太慢？

减少并发数或者分批处理。CLI目前是顺序扫描，如果需要并发，可以使用编程接口：

```python
from geo_scanner.core.scheduler import TaskScheduler
# ...
```

### Q4: 如何自定义评分规则？

需要修改源代码中的`AIFriendlyEvaluator`类，或者创建继承该类的自定义评估器。

---

## 进阶用法

### 编程接口集成

虽然CLI工具方便，但对于复杂的场景，建议直接使用编程接口：

```python
from geo_scanner.core.crawler import SimpleCrawler
from geo_scanner.scoring.evaluator import AIFriendlyEvaluator
from geo_scanner.report.generator import ReportGenerator

# 自定义扫描逻辑
urls = [...]
report_gen = ReportGenerator()

for url in urls:
    crawler = SimpleCrawler()
    page_data = crawler.fetch(url)

    evaluator = AIFriendlyEvaluator()
    result = evaluator.evaluate(page_data)

    report_gen.add_result(result)

    # 自定义处理
    if result['scores']['total'] < 60:
        print(f"警告: {url} 得分过低！")

report_gen.save_report("custom_report.json")
```

---

## 更新日志

- v1.0.0: 初始版本
  - 支持单URL扫描
  - 支持批量扫描
  - 支持从文件读取URL
  - 支持多种输出格式
