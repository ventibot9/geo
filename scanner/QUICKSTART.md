# 快速开始指南

## 5分钟上手GEO平台内容扫描器

---

### 步骤1：安装依赖

```bash
cd /root/.openclaw/workspace-open-lead/geo-platform/scanner
pip install -r requirements.txt
```

---

### 步骤2：测试基本功能

运行示例脚本：

```bash
python3 example.py
```

这将扫描 `example.com` 并生成两个报告文件：
- `example_report.json` - JSON格式报告
- `example_report.md` - Markdown格式报告

---

### 步骤3：使用CLI扫描单个URL

```bash
# 扫描并输出到终端
python3 -m geo_scanner.cli scan https://example.com

# 保存为JSON报告
python3 -m geo_scanner.cli scan https://example.com -o report.json -f json
```

---

### 步骤4：批量扫描

创建一个 `urls.txt` 文件：

```
https://example.com
https://github.com
https://stackoverflow.com
```

然后批量扫描：

```bash
python3 -m geo_scanner.cli from-file urls.txt -o batch_report.md -f markdown
```

---

### 步骤5：查看报告

打开生成的报告文件查看结果和建议。

---

## Python编程接口快速示例

```python
# quick_start.py
from geo_scanner.core.crawler import SimpleCrawler
from geo_scanner.scoring.evaluator import AIFriendlyEvaluator

# 1. 爬取页面
crawler = SimpleCrawler()
page_data = crawler.fetch("https://example.com")

# 2. 评估
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
```

运行：

```bash
python3 quick_start.py
```

---

## 常用命令速查

```bash
# 扫描单个URL
python3 -m geo_scanner.cli scan <URL>

# 批量扫描多个URL
python3 -m geo_scanner.cli batch <URL1> <URL2> <URL3>

# 从文件扫描
python3 -m geo_scanner.cli from-file urls.txt

# 保存为JSON
python3 -m geo_scanner.cli scan <URL> -o report.json -f json

# 保存为Markdown
python3 -m geo_scanner.cli scan <URL> -o report.md -f markdown
```

---

## 下一步

- 📖 阅读 [README.md](README.md) 了解完整功能
- 📊 查看 [SCORING_ALGORITHM.md](SCORING_ALGORITHM.md) 了解评分细节
- 🛠️ 参考 [CLI_GUIDE.md](CLI_GUIDE.md) 学习高级用法

---

## 需要帮助？

如果遇到问题，请检查：

1. Python版本是否为3.11+
2. 依赖是否全部安装成功
3. 目标URL是否可访问
4. 对于动态页面，是否需要使用 `--wait` 选项

```bash
# 查看帮助
python3 -m geo_scanner.cli --help
```
