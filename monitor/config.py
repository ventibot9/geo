"""
GEO监控服务配置文件
"""

import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_PATH = BASE_DIR / "data" / "monitor.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 企业关键词配置
COMPANY_KEYWORDS = {
    "企业名称": ["GEO", "GeoPlatform", "地理信息平台"],
    "产品名称": ["地图服务", "地理编码", "路径规划", "地理围栏"],
    "品牌词": ["GEO云", "GeoAPI", "GeoMap"]
}

# 搜索查询模板
SEARCH_QUERIES = [
    "{company} 是什么",
    "{company} 的优势",
    "{company} vs 竞品",
    "{product} 使用教程",
    "{brand} 官网"
]

# AI引擎配置
ENGINES = {
    "chatgpt": {
        "enabled": True,
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1"
    },
    "claude": {
        "enabled": True,
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "model": "claude-3-haiku-20240307",
        "base_url": "https://api.anthropic.com"
    },
    "ernie": {
        "enabled": True,
        "api_key": os.getenv("ERNIE_API_KEY", ""),
        "secret_key": os.getenv("ERNIE_SECRET_KEY", ""),
        "search_url": "https://www.baidu.com/s"
    }
}

# 调度任务配置
SCHEDULE_CONFIG = {
    "monitor_interval": {
        "hours": 6  # 每6小时执行一次监控
    },
    "report_interval": {
        "days": 1  # 每天生成一次报告
    },
    "timezone": "Asia/Shanghai"
}

# Selenium配置
SELENIUM_CONFIG = {
    "headless": True,
    "timeout": 30,
    "chrome_options": [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080"
    ]
}

# 报告配置
REPORT_CONFIG = {
    "output_dir": BASE_DIR / "reports",
    "date_format": "%Y-%m-%d",
    "charts_enabled": True
}
