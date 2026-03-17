#!/bin/bash

echo "Starting GEO Platform AI Rewrite Service..."

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env file and add your API keys before starting."
    exit 1
fi

# 创建数据目录
mkdir -p data

# 启动服务
echo "Starting service on port 8000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
