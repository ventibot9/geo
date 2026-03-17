#!/bin/bash
# GEO平台一键启动脚本

set -e

echo "🌚 GEO平台启动脚本"
echo "================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，从.env.example复制..."
    cp .env.example .env
    echo "✅ .env文件已创建，请根据实际情况修改配置"
    echo "⚠️  特别注意修改以下配置："
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - JWT_SECRET"
    echo ""
    read -p "是否继续启动？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        exit 0
    fi
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis

# 启动服务
echo "🚀 启动Docker服务..."
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
if docker compose version &> /dev/null; then
    docker compose ps
else
    docker-compose ps
fi

# 等待数据库就绪
echo ""
echo "⏳ 等待数据库就绪..."
for i in {1..30}; do
    if docker exec geo-postgres pg_isready -U geo_user &> /dev/null; then
        echo "✅ 数据库已就绪"
        break
    fi
    echo "等待中... ($i/30)"
    sleep 2
done

# 初始化数据库（如果需要）
echo ""
echo "📦 初始化数据库..."
cd backend
if [ -f prisma/schema.prisma ]; then
    npx prisma generate
    npx prisma db push
    echo "✅ 数据库初始化完成"
fi
cd ..

# 显示访问信息
echo ""
echo "================================"
echo "✅ GEO平台启动成功！"
echo ""
echo "📱 访问地址："
echo "   前端: http://localhost:3000"
echo "   后端API: http://localhost:3001"
echo "   AI服务: http://localhost:8000"
echo ""
echo "📊 查看日志："
echo "   所有服务: docker-compose logs -f"
echo "   单个服务: docker-compose logs -f <service-name>"
echo ""
echo "🛑 停止服务："
echo "   docker-compose down"
echo ""
echo "📚 查看帮助："
echo "   ./start.sh --help"
echo "================================"
echo "🌚 祝使用愉快！"
