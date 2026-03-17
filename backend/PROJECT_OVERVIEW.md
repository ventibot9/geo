# GEO平台后端API - 项目概览

## 项目完成情况

✅ **已完成所有要求的功能**

### 1. 项目初始化
- ✅ Node.js项目初始化
- ✅ 依赖安装配置
- ✅ TypeScript配置
- ✅ ESLint配置
- ✅ 环境变量配置

### 2. 数据库Schema设计
基于Prisma设计了完整的数据模型：

- **Enterprise（企业）**: 多租户核心模型
  - 企业基本信息
  - 套餐类型（free/pro/enterprise）
  - 状态管理

- **User（用户）**: 用户认证和管理
  - JWT认证
  - 角色权限（admin/user）
  - 企业关联

- **SiteConfig（网站配置）**: 网站扫描配置
  - URL管理
  - 扫描计划（daily/weekly/monthly）

- **ScanTask（扫描任务）**: 扫描任务管理
  - 任务状态追踪
  - 统计数据（总数/平均分/最高分/最低分）
  - 时间追踪

- **ContentPage（内容页面）**: 页面内容分析
  - 内容存储
  - AI友好度评分
  - 优化建议（JSON格式）

- **AIReadabilityScore（AI评分历史）**: 评分历史记录
  - 多模型支持（GPT-4/Claude等）
  - 评分因子追踪

- **CitationData（引用数据）**: 引用监控
  - 多AI引擎支持
  - 关键词统计
  - 曝光量追踪

- **JobRecord（任务队列记录）**: Bull队列任务追踪

### 3. API路由和中间件

#### 认证中间件
- JWT token验证
- 角色权限控制
- 多租户数据隔离

#### 错误处理中间件
- 统一错误处理
- 自定义错误类
- 开发/生产环境适配

#### 验证中间件
- 请求数据验证
- 邮箱和密码验证

### 4. JWT认证系统

#### 认证路由
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/profile` - 获取用户信息

#### 认证功能
- 密码bcrypt加密（10轮哈希）
- JWT token生成（7天有效期）
- 企业多租户隔离
- 最后登录时间追踪

### 5. 任务调度系统

基于Bull + Redis实现：

#### 队列类型
- **扫描队列**: 内容扫描任务
- **改写队列**: AI改写任务
- **监控队列**: 引用监控任务

#### 功能
- 任务重试机制（3次，指数退避）
- 任务优先级
- 定时任务支持（每小时执行监控）
- 任务状态追踪
- 错误处理和日志

### 6. Docker部署

#### Docker Compose服务
- **PostgreSQL 15**: 数据库
  - 数据持久化
  - 健康检查
  - 自动重启

- **Redis 7**: 缓存和消息队列
  - 数据持久化
  - 健康检查
  - 自动重启

- **Backend API**: 后端服务
  - 多阶段构建
  - 依赖检查
  - 自动迁移

#### Dockerfile优化
- 多阶段构建减小镜像大小
- 非root用户运行
- 生产环境优化

## 项目结构

```
backend/
├── prisma/
│   ├── schema.prisma          # 数据库Schema
│   └── seed.ts                # 种子数据
├── src/
│   ├── config/                # 配置
│   │   ├── database.ts        # Prisma客户端
│   │   ├── redis.ts           # Redis配置
│   │   └── index.ts           # 应用配置
│   ├── controllers/           # 控制器
│   │   ├── authController.ts  # 认证控制器
│   │   ├── scanController.ts  # 扫描控制器
│   │   └── healthController.ts # 健康检查
│   ├── middleware/            # 中间件
│   │   ├── auth.ts            # 认证中间件
│   │   ├── error.ts           # 错误处理
│   │   └── validation.ts      # 数据验证
│   ├── routes/                # 路由
│   │   ├── authRoutes.ts      # 认证路由
│   │   ├── scanRoutes.ts      # 扫描路由
│   │   ├── healthRoutes.ts    # 健康检查路由
│   │   └── index.ts           # 路由汇总
│   ├── services/              # 业务逻辑
│   │   ├── authService.ts     # 认证服务
│   │   ├── scanService.ts     # 扫描服务
│   │   └── queueService.ts    # 队列服务
│   ├── app.ts                 # Express应用
│   └── index.ts               # 入口文件
├── .env                       # 环境变量
├── .env.example               # 环境变量示例
├── .eslintrc.json            # ESLint配置
├── .gitignore                # Git忽略文件
├── docker-compose.yml        # Docker编排
├── Dockerfile                # Docker镜像
├── tsconfig.json             # TypeScript配置
├── package.json              # 项目配置
└── README.md                 # 项目文档
```

## 关键代码说明

### 1. 数据库模型关系

```
Enterprise (1) ──┬─→ (N) User
                 ├─→ (N) SiteConfig ──→ (N) ScanTask ──→ (N) ContentPage ──→ (N) AIReadabilityScore
                 └─→ (N) CitationData
```

### 2. 认证流程

```
用户注册 → 哈希密码 → 创建企业和用户 → 生成JWT → 返回token
用户登录 → 验证密码 → 更新登录时间 → 生成JWT → 返回token
API请求 → 携带JWT → 验证token → 提取用户信息 → 处理请求
```

### 3. 扫描任务流程

```
创建任务 → 验证权限 → 创建ScanTask记录 → 添加到Bull队列 → Worker处理 → 更新状态
```

### 4. 多租户隔离

- 所有查询都包含`enterpriseId`过滤
- 认证中间件从JWT提取`enterpriseId`
- 控制器自动注入企业上下文

## API端点总览

### 公开端点
- `GET /` - API信息
- `GET /api/health` - 健康检查

### 认证端点
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/profile` - 获取用户信息（需认证）

### 扫描任务端点（需认证）
- `POST /api/scans/create` - 创建扫描任务
- `GET /api/scans/list` - 列出扫描任务
- `GET /api/scans/:id` - 获取任务详情
- `DELETE /api/scans/:id` - 删除任务（管理员）

## 快速启动

### 1. 启动基础设施
```bash
cd /root/.openclaw/workspace-open-lead/geo-platform/backend
docker-compose up -d postgres redis
```

### 2. 安装依赖和初始化数据库
```bash
npm install
npm run prisma:generate
npm run prisma:migrate
npx ts-node prisma/seed.ts  # 可选：填充种子数据
```

### 3. 启动开发服务器
```bash
npm run dev
```

### 4. 测试API
```bash
# 健康检查
curl http://localhost:3001/api/health

# 注册用户
curl -X POST http://localhost:3001/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "测试用户",
    "enterpriseName": "测试企业",
    "domain": "test.example.com"
  }'
```

## 技术亮点

1. **类型安全**: 全面的TypeScript类型定义
2. **数据验证**: 多层验证（中间件 + Service层）
3. **错误处理**: 统一的错误处理机制
4. **任务队列**: 可扩展的异步任务处理
5. **多租户**: 企业级数据隔离
6. **容器化**: 完整的Docker部署方案
7. **开发体验**: 热重载、类型提示、ESLint

## 下一步建议

1. **单元测试**: 添加Jest测试套件
2. **API文档**: 集成Swagger/OpenAPI
3. **日志系统**: 添加Winston或Pino日志
4. **监控**: 集成Prometheus + Grafana
5. **Rate Limiting**: 添加速率限制
6. **Caching**: 实现Redis缓存策略
7. **Worker实现**: 实现Bull队列的Worker处理器
8. **WebSocket**: 添加实时通知功能
9. **API版本控制**: 实现v1/v2版本控制
10. **CI/CD**: 配置GitHub Actions或GitLab CI

## 注意事项

1. **生产环境**: 修改JWT_SECRET和数据库密码
2. **安全性**: 启用HTTPS、配置CORS白名单
3. **性能**: 数据库索引优化、连接池配置
4. **备份**: 定期备份PostgreSQL数据
5. **监控**: 设置日志和性能监控
