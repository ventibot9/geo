#!/bin/bash

echo "🚀 GEO平台后端API - 开发环境启动脚本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js 20+"
    exit 1
fi

echo "✅ 环境检查通过"

# 创建.env文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建.env文件..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件配置环境变量"
fi

# 启动PostgreSQL和Redis
echo "🐘 启动PostgreSQL和Redis..."
docker-compose up -d postgres redis

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 5

# 检查数据库连接
echo "🔍 检查数据库连接..."
until docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; do
    echo "⏳ 等待PostgreSQL启动..."
    sleep 2
done
echo "✅ PostgreSQL已就绪"

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 生成Prisma客户端
echo "🔧 生成Prisma客户端..."
npm run prisma:generate

# 运行数据库迁移
echo "🗄️  运行数据库迁移..."
npm run prisma:migrate || echo "⚠️  迁移已存在或失败"

# 询问是否填充种子数据
echo ""
read -p "是否填充种子数据？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 填充种子数据..."
    npx ts-node prisma/seed.ts
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 所有服务已启动！"
echo ""
echo "📚 API文档: http://localhost:3001"
echo "🏥 健康检查: http://localhost:3001/api/health"
echo "🔧 Prisma Studio: npm run prisma:studio"
echo ""
echo "🚀 启动开发服务器: npm run dev"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
