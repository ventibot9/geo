# 项目结构说明

```
monitor/
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖列表
├── config.py                 # 配置文件
├── main.py                   # 主程序入口
├── start.sh                  # 启动脚本
├── .env.example              # 环境变量示例
├── MONITORING_METHOD.md      # 监控方法说明
├── DATA_MODEL.md             # 数据模型设计
│
├── database/                 # 数据库模块
│   ├── __init__.py          # 模块导出
│   ├── models.py            # 数据库模型定义
│   └── db.py                # 数据库连接管理
│
├── engines/                  # AI引擎模块
│   ├── __init__.py          # 模块导出
│   ├── base.py              # 引擎基类
│   ├── chatgpt.py           # ChatGPT引擎
│   ├── claude.py            # Claude引擎
│   └── ernie.py             # 文心一言引擎
│
├── scraper/                  # 数据抓取模块
│   ├── __init__.py          # 模块导出
│   └── extractor.py         # 引用数据提取器
│
├── scheduler/                # 调度任务模块
│   ├── __init__.py          # 模块导出
│   └── tasks.py             # 定时任务定义
│
├── reporter/                 # 报告生成模块
│   ├── __init__.py          # 模块导出
│   └── generator.py         # 报告生成器
│
├── utils/                    # 工具模块
│   ├── __init__.py          # 模块导出
│   └── keywords.py          # 关键词管理工具
│
├── data/                     # 数据目录（运行时创建）
│   └── monitor.db           # SQLite数据库
│
└── reports/                  # 报告目录（运行时创建）
    ├── report_2026-03-17.json
    └── report_2026-03-17.txt
```

## 模块说明

### database/
**数据库模块** - 负责数据持久化

- `models.py`: 定义4张表（CitationRecord, EngineConfig, KeywordStats, MonitorTask）
- `db.py`: 数据库连接管理和会话工厂

### engines/
**AI引擎模块** - 封装不同AI引擎的查询接口

- `base.py`: 抽象基类，定义引擎接口规范
- `chatgpt.py`: OpenAI ChatGPT实现
- `claude.py`: Anthropic Claude实现
- `ernie.py`: 百度文心一言（通过搜索）实现

### scraper/
**数据抓取模块** - 从AI响应中提取引用信息

- `extractor.py`: 关键词匹配、置信度计算、趋势分析

### scheduler/
**调度任务模块** - 定时执行监控和报告生成

- `tasks.py`: 使用APScheduler实现定时任务
  - 监控任务：每6小时执行
  - 报告任务：每天执行

### reporter/
**报告生成模块** - 生成监控统计报告

- `generator.py`: 生成JSON和文本格式的报告
  - 日报生成
  - 趋势分析
  - 热门关键词排行

### utils/
**工具模块** - 通用工具函数

- `keywords.py`: 关键词管理
  - 添加/删除关键词
  - 生成查询变体
  - 导出摘要

## 核心流程

```
main.py (启动)
  ↓
MonitorScheduler (初始化)
  ↓
run_monitor_task (定时执行)
  ↓
  ├─ ChatGPTEngine.query()
  ├─ ClaudeEngine.query()
  └─ ErnieEngine.query()
  ↓
CitationExtractor.extract_from_response()
  ↓
保存到 database.CitationRecord
  ↓
run_report_task (定时执行)
  ↓
ReportGenerator.generate_daily_report()
  ↓
保存到 reports/ 目录
```

## 依赖关系

```
main.py
  ├─ scheduler/tasks.py
  │   ├─ engines/* (AI引擎)
  │   ├─ scraper/extractor.py
  │   └─ database/
  │
  └─ reporter/generator.py
      └─ database/

所有模块都依赖 config.py
```

## 数据流

```
查询生成 → AI引擎 → 响应提取 → 数据存储 → 统计分析 → 报告生成
```

## 扩展点

1. **添加新AI引擎**
   - 在 `engines/` 下创建新文件
   - 继承 `BaseEngine`
   - 实现 `query()` 和 `is_available()` 方法

2. **自定义报告格式**
   - 在 `reporter/generator.py` 中添加新方法
   - 支持Markdown、CSV、PDF等格式

3. **增强关键词管理**
   - 扩展 `utils/keywords.py`
   - 支持从文件导入导出
   - 支持关键词权重配置

4. **添加告警功能**
   - 监控引用数量变化
   - 邮件/消息通知
