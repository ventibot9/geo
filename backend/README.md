# GEO Platform Backend API

GEO平台后端API服务，基于Node.js + Express + TypeScript + Prisma + PostgreSQL。

## 功能特性

- ✅ RESTful API基础框架
- ✅ JWT用户认证系统
- ✅ 企业多租户管理
- ✅ 基于Prisma的数据建模
- ✅ Bull + Redis任务队列
- ✅ 扫描任务管理
- ✅ Docker容器化部署

## 技术栈

- **运行时**: Node.js 20
- **框架**: Express.js
- **语言**: TypeScript
- **数据库**: PostgreSQL 15
- **ORM**: Prisma
- **缓存/队列**: Redis 7 + Bull
- **认证**: JWT

## 项目结构

```
backend/
├── prisma/
│   ├── schema.prisma        # 数据库Schema
│   └── seed.ts              # 数据库种子
├── src/
│   ├── config/              # 配置文件
│   │   ├── database.ts      # Prisma客户端
│   │   ├── redis.ts         # Redis配置
│   │   └── index.ts         # 应用配置
│   ├── controllers/         # 控制器
│   │   ├── authController.ts
│   │   ├── scanController.ts
│   │   └── healthController.ts
│   ├── middleware/          # 中间件
│   │   ├── auth.ts          # 认证中间件
│   │   ├── error.ts         # 错误处理
│   │   └── validation.ts    # 验证中间件
│   ├── routes/              # 路由
│   │   ├── authRoutes.ts
│   │   ├── scanRoutes.ts
│   │   ├── healthRoutes.ts
│   │   └── index.ts
│   ├── services/            # 业务逻辑
│   │   ├── authService.ts
│   │   ├── scanService.ts
│   │   └── queueService.ts
│   ├── app.ts               # Express应用
│   └── index.ts             # 入口文件
├── .env                     # 环境变量
├── .env.example             # 环境变量示例
├── docker-compose.yml       # Docker编排
├── Dockerfile               # Docker镜像
├── tsconfig.json            # TypeScript配置
├── package.json
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，配置数据库和Redis连接
```

### 3. 启动数据库和Redis

使用Docker Compose：
```bash
docker-compose up -d postgres redis
```

或使用独立服务：
```bash
# PostgreSQL
docker run -d --name postgres \\
  -e POSTGRES_USER=postgres \\
  -e POSTGRES_PASSWORD=postgres \\
  -e POSTGRES_DB=geo_platform \\
  -p 5432:5432 \\
  postgres:15-alpine

# Redis
docker run -d --name redis \\
  -p 6379:6379 \\
  redis:7-alpine
```

### 4. 数据库迁移

```bash
# 生成Prisma客户端
npm run prisma:generate

# 运行迁移
npm run prisma:migrate

# （可选）填充种子数据
npx ts-node prisma/seed.ts
```

### 5. 启动开发服务器

```bash
npm run dev
```

服务器将在 http://localhost:3001 启动。

## API文档

### 健康检查
```
GET /api/health
```

### 认证
```
POST /api/auth/register    # 注册
POST /api/auth/login       # 登录
GET  /api/auth/profile     # 获取用户信息（需认证）
```

### 扫描任务
```
POST /api/scans/create     # 创建扫描任务（需认证）
GET  /api/scans/list       # 列出扫描任务（需认证）
GET  /api/scans/:id        # 获取任务详情（需认证）
DELETE /api/scans/:id      # 删除任务（需管理员权限）
```

### 认证方式

在请求头中包含JWT token：
```
Authorization: Bearer <your-jwt-token>
```

## 数据模型

### Enterprise（企业）
- `id`: UUID
- `name`: 企业名称
- `domain`: 企业域名（唯一）
- `plan`: 套餐类型（free/pro/enterprise）
- `status`: 状态（active/suspended/cancelled）

### User（用户）
- `id`: UUID
- `email`: 邮箱（唯一）
- `password`: 密码（哈希）
- `name`: 用户名
- `role`: 角色（admin/user）
- `enterpriseId`: 所属企业ID

### SiteConfig（网站配置）
- `id`: UUID
- `url`: 网站URL
- `scanSchedule`: 扫描计划（daily/weekly/monthly）
- `active`: 是否激活

### ScanTask（扫描任务）
- `id`: UUID
- `status`: 状态（pending/running/completed/failed）
- `totalPages`: 总页面数
- `processedPages`: 已处理页面数
- `avgAiScore`: 平均AI评分

### ContentPage（内容页面）
- `id`: UUID
- `url`: 页面URL
- `title`: 页面标题
- `content`: 页面内容
- `aiScore`: AI友好度评分
- `optimizationTips`: 优化建议（JSON）

## Docker部署

### 构建镜像
```bash
docker build -t geo-backend .
```

### 运行所有服务
```bash
docker-compose up -d
```

### 查看日志
```bash
docker-compose logs -f backend
```

### 停止服务
```bash
docker-compose down
```

## 开发命令

```bash
npm run dev          # 开发模式（nodemon）
npm run build        # 构建TypeScript
npm start            # 生产模式
npm run lint         # ESLint检查
npm run prisma:generate   # 生成Prisma客户端
npm run prisma:migrate    # 运行数据库迁移
npm run prisma:studio     # 打开Prisma Studio
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| PORT | 服务端口 | 3001 |
| NODE_ENV | 运行环境 | development |
| DATABASE_URL | PostgreSQL连接字符串 | - |
| REDIS_HOST | Redis主机 | localhost |
| REDIS_PORT | Redis端口 | 6379 |
| JWT_SECRET | JWT密钥 | - |
| JWT_EXPIRES_IN | JWT过期时间 | 7d |
| BCRYPT_ROUNDS | 密码哈希轮数 | 10 |
| CORS_ORIGIN | CORS允许的源 | http://localhost:3000 |

## 生产环境建议

1. 修改JWT_SECRET为强密码
2. 使用环境变量管理工具（如AWS Secrets Manager）
3. 启用HTTPS
4. 配置日志聚合
5. 设置监控和告警
6. 定期备份数据库
7. 使用进程管理器（PM2）
8. 配置Nginx反向代理

## 许可证

MIT
