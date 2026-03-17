# 快速开始指南

## 1. 安装依赖

```bash
cd /root/.openclaw/workspace-open-lead/geo-platform/monitor
pip install -r requirements.txt
```

## 2. 配置API密钥

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```env
# OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 百度AI API Keys（可选）
ERNIE_API_KEY=your-key
ERNIE_SECRET_KEY=your-secret
```

## 3. 运行示例

```bash
python example.py
```

选择选项查看示例代码的使用。

## 4. 运行一次监控

```bash
python main.py --once
```

这将执行一次完整的监控流程，包括：
- 查询各AI引擎
- 提取引用数据
- 生成监控报告

## 5. 生成报告

```bash
python main.py --report
```

生成当天的监控报告，保存在 `reports/` 目录。

## 6. 启动服务

```bash
python main.py
```

或使用启动脚本：

```bash
./start.sh
```

服务将：
- 每6小时执行一次监控
- 每天生成一次报告
- 持续运行直到手动停止（Ctrl+C）

## 7. 查看报告

报告文件位于 `reports/` 目录：

- `report_YYYY-MM-DD.json` - JSON格式报告
- `report_YYYY-MM-DD.txt` - 文本格式报告

## 8. 自定义配置

编辑 `config.py` 文件：

### 修改关键词

```python
COMPANY_KEYWORDS = {
    "企业名称": ["你的公司名", "品牌名"],
    "产品名称": ["产品A", "产品B"],
    "品牌词": ["品牌词1", "品牌词2"]
}
```

### 修改查询模板

```python
SEARCH_QUERIES = [
    "{company} 是什么",
    "{company} 怎么样",
    "{product} 教程",
    "{brand} 官网"
]
```

### 修改调度时间

```python
SCHEDULE_CONFIG = {
    "monitor_interval": {"hours": 6},  # 每6小时
    "report_interval": {"days": 1},    # 每天一次
    "timezone": "Asia/Shanghai"
}
```

### 启用/禁用引擎

```python
ENGINES = {
    "chatgpt": {"enabled": True, ...},
    "claude": {"enabled": True, ...},
    "ernie": {"enabled": False, ...}  # 禁用
}
```

## 9. 查看数据库

数据库文件位于 `data/monitor.db`

使用SQLite命令行工具查看：

```bash
sqlite3 data/monitor.db
```

常用SQL查询：

```sql
-- 查看所有表
.tables

-- 查看最近的引用记录
SELECT * FROM citation_records ORDER BY timestamp DESC LIMIT 10;

-- 按引擎统计
SELECT engine_name, COUNT(*) FROM citation_records GROUP BY engine_name;

-- 查看热门关键词
SELECT keyword, SUM(citation_count) as total
FROM citation_records
GROUP BY keyword
ORDER BY total DESC
LIMIT 10;
```

## 10. 故障排查

### 问题：没有API密钥

**解决**：
- 至少配置一个AI引擎的API密钥
- 如果没有，可以禁用该引擎：`enabled: False`

### 问题：查询失败

**解决**：
- 检查API密钥是否正确
- 检查网络连接
- 查看日志输出的错误信息

### 问题：没有检测到引用

**解决**：
- 检查关键词配置是否正确
- 尝试手动运行示例查看具体响应
- 调整关键词使其更匹配AI响应

### 问题：数据库文件损坏

**解决**：
```bash
rm data/monitor.db
python main.py --once
```

数据库会自动重新创建。

## 11. 性能优化

### 减少API调用成本

1. 减少查询频率
   ```python
   SCHEDULE_CONFIG = {
       "monitor_interval": {"hours": 12}  # 改为12小时
   }
   ```

2. 减少查询数量
   ```python
   SEARCH_QUERIES = ["{company} 是什么"]  # 只保留一个模板
   ```

3. 禁用不需要的引擎
   ```python
   ENGINES = {
       "chatgpt": {"enabled": True},
       "claude": {"enabled": False},
       "ernie": {"enabled": False}
   }
   ```

### 减少数据库大小

定期清理旧数据：

```bash
sqlite3 data/monitor.db "DELETE FROM citation_records WHERE timestamp < datetime('now', '-30 days');"
```

## 12. 下一步

- 阅读完整文档：
  - `MONITORING_METHOD.md` - 监控方法详解
  - `DATA_MODEL.md` - 数据模型设计
  - `PROJECT_STRUCTURE.md` - 项目结构说明

- 查看示例代码：
  - `example.py` - 完整的使用示例

- 根据需求自定义：
  - 修改 `config.py` 配置
  - 在 `engines/` 下添加新的AI引擎
  - 在 `reporter/` 下自定义报告格式
