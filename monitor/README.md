# GEO平台引用监控服务

监控各大AI引擎对企业关键词的引用情况，统计曝光量，分析趋势，生成报告。

## 技术栈
- Python 3.11
- Selenium (网页自动化)
- BeautifulSoup (HTML解析)
- APScheduler (定时任务)
- SQLite (数据存储)

## 功能模块
1. **AI引擎查询接口** - 支持ChatGPT、Claude、文心一言等
2. **引用数据抓取** - 提取AI回答中的企业关键词
3. **数据存储** - SQLite数据库记录引用数据
4. **定期监控** - APScheduler定时任务
5. **报告生成** - 生成监控统计报告

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行
```bash
python main.py
```

## 配置
修改 `config.py` 设置：
- 企业关键词列表
- 监控引擎配置
- 调度任务时间
