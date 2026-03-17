#!/bin/bash
# GEO监控服务启动脚本

# 设置工作目录
cd "$(dirname "$0")"

# 激活虚拟环境（如果使用）
# source venv/bin/activate

# 检查依赖
echo "Checking dependencies..."
if ! python -c "import selenium" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# 创建必要的目录
mkdir -p data reports

# 启动服务
echo "Starting GEO Monitor Service..."
python main.py "$@"
