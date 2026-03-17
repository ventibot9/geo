# GEO Platform - Backend API 服务详细规范

## 文档信息
- **版本**: v1.0.0
- **模块**: Backend API Service
- **日期**: 2026-03-17
- **维护者**: GEO Platform Team

---

## 1. 模块职责

### 1.1 核心功能
1. **用户认证管理**
   - 用户注册 / 登录
   - JWT Token 生成与验证
   - 密码加密 (bcrypt)

2. **企业多租户管理**
   - 企业注册 / 信息修改
   - 企业用户关联
   - 多租户数据隔离

3. **扫描任务管理**
   - 创建 / 删除 / 查询扫描任务
   - 任务状态更新
   - 任务结果存储

4. **AI 改写任务管理**
   - 创建改写任务
   - 任务状态跟踪
   - 结果查询

5. **引用监控数据管理**
   - 引用数据查询
   - 统计报表生成
   - 趋势分析

6. **任务队列调度**
   - Bull 队列管理
   - 任务分发与重试
   - 优先级调度

### 1.2 非职责
- 不直接进行网站爬取 (由 Scanner Service 负责)
- 不调用 AI 模型 API (由 AI Service 负责)
- 不进行 AI 引擎查询 (由 Monitor Service 负责)
- 不直接生成报告 (由各微服务负责)

---

## 2. API 接口设计

### 2.1 认证接口 (`/api/auth`)

#### POST /api/auth/register
**功能**: 用户注册

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "enterprise_name": "Example Company",
  "enterprise_domain": "example.com"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxx",
    "email": "user@example.com",
    "enterprise_id": "ent_xxx",
    "role": "admin"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**错误响应**:
- `400`: 邮箱格式错误 / 密码太短
- `409`: 邮箱已注册

---

#### POST /api/auth/login
**功能**: 用户登录

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxx",
    "email": "user@example.com",
    "enterprise_id": "ent_xxx",
    "role": "admin",
    "enterprise_name": "Example Company"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**错误响应**:
- `401`: 邮箱或密码错误
- `429`: 登录次数过多 (限流)

---

#### GET /api/auth/profile
**功能**: 获取当前用户信息

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_xxx",
    "email": "user@example.com",
    "role": "admin",
    "created_at": "2026-03-17T10:00:00Z",
    "enterprise": {
      "id": "ent_xxx",
      "name": "Example Company",
      "domain": "example.com",
      "plan": "pro",
      "status": "active"
    }
  }
}
```

**错误响应**:
- `401`: Token 无效或过期

---

#### PUT /api/auth/profile
**功能**: 更新用户信息

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "password": "newpassword123"
}
```

**响应**:
```json
{
  "success": true,
  "message": "用户信息已更新"
}
```

---

### 2.2 扫描任务接口 (`/api/scans`)

#### POST /api/scans/create
**功能**: 创建扫描任务

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "site_id": "site_xxx",
  "scan_type": "full",
  "schedule": {
    "enabled": true,
    "cron": "0 9 * * *"
  },
  "options": {
    "max_pages": 1000,
    "depth": 3,
    "follow_external_links": false
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "scan_task_id": "scan_xxx",
    "status": "pending",
    "created_at": "2026-03-17T10:00:00Z"
  }
}
```

---

#### GET /api/scans/list
**功能**: 获取扫描任务列表

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码 (默认 1)
- `limit`: 每页数量 (默认 20)
- `status`: 状态筛选 (pending/running/completed/failed)

**响应**:
```json
{
  "success": true,
  "data": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "items": [
      {
        "scan_task_id": "scan_xxx",
        "site_id": "site_xxx",
        "status": "completed",
        "ai_score": 85,
        "pages_scanned": 950,
        "created_at": "2026-03-17T10:00:00Z",
        "completed_at": "2026-03-17T10:30:00Z"
      }
    ]
  }
}
```

---

#### GET /api/scans/:id
**功能**: 获取扫描任务详情

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "data": {
    "scan_task_id": "scan_xxx",
    "site": {
      "id": "site_xxx",
      "url": "https://example.com",
      "name": "主站"
    },
    "status": "completed",
    "ai_score": 85,
    "grade": "B",
    "pages_scanned": 950,
    "scoring_breakdown": {
      "title_structure": 25,
      "tables_used": 18,
      "data_completeness": 22,
      "content_clarity": 12,
      "format_compatibility": 8
    },
    "pages": [
      {
        "content_page_id": "page_xxx",
        "url": "https://example.com/page1",
        "title": "Example Page",
        "ai_score": 82,
        "suggestions": ["建议添加 H2 标题", "建议使用表格展示数据"]
      }
    ],
    "created_at": "2026-03-17T10:00:00Z",
    "completed_at": "2026-03-17T10:30:00Z"
  }
}
```

---

#### DELETE /api/scans/:id
**功能**: 删除扫描任务 (仅管理员)

**请求头**:
```
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "message": "扫描任务已删除"
}
```

**错误响应**:
- `403`: 无权限 (非管理员)

---

### 2.3 AI 改写接口 (`/api/ai`)

#### POST /api/ai/rewrite
**功能**: 创建 AI 改写任务

**请求头**:
```
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "content_page_id": "page_xxx",
  "model": "gpt-4-turbo-preview",
  "options": {
    "add_tables": true,
    "optimize_structure": true,
    "extract_parameters": true
  }
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "rewrite_record_id": "rewrite_xxx",
    "status": "pending",
    "model": "gpt-4-turbo-preview",
    "created_at": "2026-03-17T10:00:00Z"
  }
}
```

---

#### GET /api/ai/history
**功能**: 获取改写历史

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `content_page_id`: 内容页 ID (可选)
- `model`: 模型筛选 (可选)

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "rewrite_record_id": "rewrite_xxx",
      "content_page_id": "page_xxx",
      "original_content": "...",
      "rewritten_content": "...",
      "model": "gpt-4-turbo-preview",
      "quality_score": 88,
      "status": "completed",
      "created_at": "2026-03-17T10:00:00Z"
    }
  ]
}
```

---

### 2.4 引用监控接口 (`/api/monitor`)

#### GET /api/monitor/citations
**功能**: 获取引用数据

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期
- `ai_engine`: AI 引擎筛选 (chatgpt/claude/wenxin)

**响应**:
```json
{
  "success": true,
  "data": {
    "total_citations": 1250,
    "engine_breakdown": {
      "chatgpt": 850,
      "claude": 300,
      "wenxin": 100
    },
    "trend": [
      {
        "date": "2026-03-10",
        "count": 120
      },
      {
        "date": "2026-03-11",
        "count": 135
      }
    ]
  }
}
```

---

#### GET /api/monitor/trends
**功能**: 获取引用趋势分析

**请求头**:
```
Authorization: Bearer <token>
```

**查询参数**:
- `period`: 周期 (7d/30d/90d)

**响应**:
```json
{
  "success": true,
  "data": {
    "period": "30d",
    "total_citations": 1250,
    "avg_daily": 41.7,
    "growth_rate": "+12.5%",
    "top_keywords": [
      {
        "keyword": "AI 优化",
        "count": 350,
        "trend": "up"
      }
    ],
    "engine_performance": {
      "chatgpt": {
        "citations": 850,
        "avg_confidence": 0.85,
        "trend": "stable"
      }
    }
  }
}
```

---

### 2.5 健康检查接口

#### GET /api/health
**功能**: 服务健康检查

**响应**:
```json
{
  "status": "ok",
  "timestamp": "2026-03-17T10:00:00Z",
  "dependencies": {
    "database": {
      "status": "connected",
      "latency_ms": 5
    },
    "redis": {
      "status": "connected",
      "latency_ms": 2
    }
  },
  "queues": {
    "scan-queue": {
      "waiting": 3,
      "active": 1
    },
    "rewrite-queue": {
      "waiting": 0,
      "active": 0
    }
  }
}
```

---

## 3. 数据模型

### 3.1 Enterprise (企业)
```typescript
{
  id: string,              // UUID
  name: string,            // 企业名称
  domain: string,          // 域名
  plan: string,            // 订阅计划 (free/pro/enterprise)
  status: string,          // 状态 (active/suspended/deleted)
  created_at: DateTime,
  updated_at: DateTime
}
```

### 3.2 User (用户)
```typescript
{
  id: string,              // UUID
  email: string,           // 邮箱 (唯一)
  password_hash: string,   // bcrypt 哈希
  enterprise_id: string,    // 企业 ID (外键)
  role: string,           // 角色 (admin/user/viewer)
  created_at: DateTime,
  last_login_at: DateTime
}
```

### 3.3 SiteConfig (网站配置)
```typescript
{
  id: string,              // UUID
  enterprise_id: string,    // 企业 ID (外键)
  name: string,            // 网站名称
  url: string,            // 网站 URL
  scan_schedule: {        // 扫描计划
    enabled: boolean,
    cron: string          // CRON 表达式
  },
  options: {              // 扫描选项
    max_pages: number,
    depth: number,
    follow_external_links: boolean
  },
  created_at: DateTime
}
```

### 3.4 ScanTask (扫描任务)
```typescript
{
  id: string,              // UUID
  site_id: string,         // 网站 ID (外键)
  enterprise_id: string,    // 企业 ID (外键)
  status: string,          // 状态 (pending/running/completed/failed)
  ai_score: number,         // AI 友好度总分 (0-100)
  grade: string,           // 等级 (A/B/C/D/E)
  pages_scanned: number,    // 扫描页面数
  completed_at: DateTime,
  created_at: DateTime
}
```

### 3.5 ContentPage (内容页面)
```typescript
{
  id: string,              // UUID
  scan_task_id: string,    // 扫描任务 ID (外键)
  url: string,            // 页面 URL
  title: string,          // 页面标题
  content: text,          // 页面内容 (HTML/Markdown)
  ai_score: number,         // AI 友好度分数
  scoring_breakdown: {     // 评分详情
    title_structure: number,
    tables_used: number,
    data_completeness: number,
    content_clarity: number,
    format_compatibility: number
  },
  suggestions: string[],    // 优化建议
  created_at: DateTime
}
```

### 3.6 RewriteRecord (改写记录)
```typescript
{
  id: string,              // UUID
  content_page_id: string, // 内容页 ID (外键)
  enterprise_id: string,    // 企业 ID (外键)
  original_content: text,  // 原始内容
  rewritten_content: text,  // 改写后内容
  model: string,           // 使用的模型
  quality_score: number,    // 改写质量分数
  status: string,          // 状态 (pending/processing/completed/failed)
  created_at: DateTime,
  completed_at: DateTime
}
```

### 3.7 CitationData (引用数据)
```typescript
{
  id: string,              // UUID
  enterprise_id: string,    // 企业 ID (外键)
  ai_engine: string,       // AI 引擎 (chatgpt/claude/wenxin)
  keyword: string,         // 关键词
  count: number,           // 引用次数
  confidence_score: number, // 置信度 (0-1)
  date: DateTime,          // 统计日期
  created_at: DateTime
}
```

### 3.8 JobRecord (任务队列记录)
```typescript
{
  id: string,              // UUID
  queue: string,          // 队列名称 (scan-queue/rewrite-queue)
  task_id: string,        // 任务 ID
  status: string,          // 状态 (pending/active/completed/failed)
  attempts: number,        // 尝试次数
  error_message: string,    // 错误信息
  created_at: DateTime,
  completed_at: DateTime
}
```

---

## 4. 业务逻辑

### 4.1 认证流程
```typescript
// 1. 用户注册
async function register(email, password, enterpriseName, enterpriseDomain) {
  // 验证邮箱格式
  if (!validateEmail(email)) throw new Error('邮箱格式错误');

  // 验证密码强度
  if (!validatePassword(password)) throw new Error('密码太弱');

  // 检查邮箱是否已注册
  const existingUser = await prisma.user.findUnique({ where: { email } });
  if (existingUser) throw new Error('邮箱已注册');

  // 创建企业
  const enterprise = await prisma.enterprise.create({
    data: {
      name: enterpriseName,
      domain: enterpriseDomain,
      plan: 'free',
      status: 'active'
    }
  });

  // 哈希密码
  const passwordHash = await bcrypt.hash(password, 10);

  // 创建用户 (默认角色 admin)
  const user = await prisma.user.create({
    data: {
      email,
      password_hash: passwordHash,
      enterprise_id: enterprise.id,
      role: 'admin'
    }
  });

  // 生成 JWT Token
  const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: '7d' });

  return { user, token };
}
```

### 4.2 扫描任务调度
```typescript
// 1. 创建扫描任务
async function createScanTask(siteId, options, userId) {
  // 获取网站配置
  const site = await prisma.siteConfig.findUnique({ where: { id: siteId } });

  // 创建扫描任务
  const scanTask = await prisma.scanTask.create({
    data: {
      site_id: siteId,
      enterprise_id: site.enterprise_id,
      status: 'pending'
    }
  });

  // 加入 Bull 队列
  await scanQueue.add({
    task_id: scanTask.id,
    site_url: site.url,
    options
  }, {
    priority: options.priority || 5,
    attempts: 3
  });

  return scanTask;
}

// 2. Scanner Service 消费任务
scanQueue.process(async (job) => {
  const { task_id, site_url, options } = job.data;

  // 更新任务状态为 running
  await prisma.scanTask.update({
    where: { id: task_id },
    data: { status: 'running' }
  });

  try {
    // 调用 Scanner Service (HTTP API)
    const result = await axios.post('http://scanner:5001/scan', {
      url: site_url,
      options
    });

    // 保存扫描结果
    await saveScanResults(task_id, result);

    // 更新任务状态为 completed
    await prisma.scanTask.update({
      where: { id: task_id },
      data: {
        status: 'completed',
        ai_score: result.ai_score,
        grade: result.grade,
        pages_scanned: result.pages_scanned,
        completed_at: new Date()
      }
    });

  } catch (error) {
    // 更新任务状态为 failed
    await prisma.scanTask.update({
      where: { id: task_id },
      data: {
        status: 'failed'
      }
    });

    throw error;
  }
});
```

### 4.3 多租户隔离
```typescript
// 1. 自动注入企业 ID
prisma.$use(async (params, next) => {
  // 从 JWT Token 中提取 enterprise_id
  const enterpriseId = extractEnterpriseIdFromToken();

  // 在所有查询中自动注入 enterprise_id
  if (params.model === 'User' || params.model === 'SiteConfig') {
    params.args.where = {
      ...params.args.where,
      enterprise_id: enterpriseId
    };
  }

  return next(params);
});

// 2. 示例查询 (自动添加 enterprise_id)
const users = await prisma.user.findMany();
// 实际执行的 SQL:
// SELECT * FROM users WHERE enterprise_id = 'xxx';
```

---

## 5. 任务队列设计

### 5.1 队列配置
```typescript
// 队列定义
const queues = {
  scanQueue: new Bull('scan-queue', redis, {
    defaultJobOptions: {
      attempts: 3,          // 重试次数
      backoff: {
        type: 'exponential',  // 指数退避
        delay: 2000        // 初始延迟 2 秒
      },
      removeOnComplete: 100, // 保留最近 100 个完成任务
      removeOnFail: 500     // 保留最近 500 个失败任务
    }
  }),

  rewriteQueue: new Bull('rewrite-queue', redis, {
    defaultJobOptions: {
      attempts: 2,
      backoff: {
        type: 'exponential',
        delay: 3000
      },
      removeOnComplete: 100,
      removeOnFail: 500
    }
  }),

  monitorQueue: new Bull('monitor-queue', redis, {
    defaultJobOptions: {
      attempts: 1,          // 监控任务不重试
      repeat: { cron: '0 */6 * * *' }  // 每 6 小时重复
    }
  })
};
```

### 5.2 优先级策略
```typescript
// 优先级定义 (1 = 最高, 10 = 最低)
enum JobPriority {
  URGENT = 1,        // 紧急任务
  HIGH = 3,           // 高优先级
  NORMAL = 5,         // 普通优先级
  LOW = 8             // 低优先级
  BACKGROUND = 10     // 后台任务
}

// 添加任务时指定优先级
await scanQueue.add(taskData, { priority: JobPriority.HIGH });
```

### 5.3 并发控制
```typescript
// 设置队列并发数
scanQueue.process(10);      // 最多同时处理 10 个扫描任务
rewriteQueue.process(5);   // 最多同时处理 5 个改写任务
monitorQueue.process(2);   // 最多同时处理 2 个监控任务
```

---

## 6. 错误处理

### 6.1 统一错误响应格式
```typescript
// 错误响应结构
interface ErrorResponse {
  success: false,
  error: {
    code: string,        // 错误代码
    message: string,     // 错误描述
    details?: any        // 详细信息
  },
  timestamp: DateTime
}

// 示例错误响应
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_TOKEN",
    "message": "Token 无效或已过期",
    "details": {
      "token": "eyJhbGci...",
      "expired_at": "2026-03-24T10:00:00Z"
    }
  },
  "timestamp": "2026-03-17T10:00:00Z"
}
```

### 6.2 错误代码定义
| 错误代码 | HTTP 状态 | 描述 |
|---------|-----------|------|
| `AUTH_INVALID_CREDENTIALS` | 401 | 邮箱或密码错误 |
| `AUTH_INVALID_TOKEN` | 401 | Token 无效或过期 |
| `AUTH_EXPIRED_TOKEN` | 401 | Token 已过期 |
| `FORBIDDEN` | 403 | 无权限访问 |
| `VALIDATION_ERROR` | 400 | 请求参数验证失败 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `CONFLICT` | 409 | 资源冲突 (如邮箱已注册) |
| `RATE_LIMIT_EXCEEDED` | 429 | 超过速率限制 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务暂时不可用 |

---

## 7. 中间件设计

### 7.1 认证中间件
```typescript
export async function authMiddleware(req, res, next) {
  // 1. 提取 Token
  const token = req.headers['authorization']?.replace('Bearer ', '');

  // 2. 验证 Token
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;  // 将用户信息附加到请求对象
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      error: {
        code: 'AUTH_INVALID_TOKEN',
        message: 'Token 无效或已过期'
      }
    });
  }
}

// 使用示例
app.get('/api/protected', authMiddleware, handler);
```

### 7.2 验证中间件
```typescript
export function validationMiddleware(schema) {
  return (req, res, next) => {
    // 1. 验证请求体
    const { error } = schema.validate(req.body);

    // 2. 如果有错误，返回 400
    if (error) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: '请求参数验证失败',
          details: error.details
        }
      });
    }

    // 3. 验证通过，继续处理
    req.validatedBody = req.body;  // 添加验证后的数据
    next();
  };
}

// 使用示例
const registerSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  enterprise_name: Joi.string().required()
});

app.post('/api/auth/register',
  validationMiddleware(registerSchema),
  registerHandler
);
```

### 7.3 错误处理中间件
```typescript
export function errorHandler(err, req, res, next) {
  // 1. 记录错误
  logger.error({
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method
  });

  // 2. 根据错误类型返回响应
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      success: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: err.message
      }
    });
  }

  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({
      success: false,
      error: {
        code: 'AUTH_INVALID_TOKEN',
        message: '未授权访问'
      }
    });
  }

  // 3. 默认返回 500
  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: '服务器内部错误'
    }
  });
}

// 注册全局错误处理
app.use(errorHandler);
```

---

## 8. 性能优化

### 8.1 数据库查询优化
```typescript
// 1. 使用索引
// Prisma Schema 中定义索引
model ContentPage {
  @@index([scan_task_id, url])  // 复合索引
  @@index([ai_score])           // 评分索引
}

// 2. 分页查询
const pages = await prisma.contentPage.findMany({
  where: { scan_task_id },
  skip: (page - 1) * limit,
  take: limit,
  orderBy: { ai_score: 'desc' }
});

// 3. 只选择需要的字段
const { id, url, title, ai_score } = await prisma.contentPage.findUnique({
  where: { id },
  select: { id: true, url: true, title: true, ai_score: true }
});
```

### 8.2 缓存策略
```typescript
// 1. 用户信息缓存
async function getUserInfo(userId) {
  const cacheKey = `user:${userId}`;
  const cached = await redis.get(cacheKey);

  if (cached) {
    return JSON.parse(cached);
  }

  const user = await prisma.user.findUnique({ where: { id: userId } });

  // 缓存 10 分钟
  await redis.setex(cacheKey, 600, JSON.stringify(user));

  return user;
}

// 2. API 响应缓存
async function getCitationData(enterpriseId, period) {
  const cacheKey = `citations:${enterpriseId}:${period}`;
  const cached = await redis.get(cacheKey);

  if (cached) {
    return JSON.parse(cached);
  }

  const data = await generateCitationData(enterpriseId, period);

  // 缓存 5 分钟
  await redis.setex(cacheKey, 300, JSON.stringify(data));

  return data;
}
```

### 8.3 连接池配置
```typescript
// Prisma 数据库连接池
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")

  // 连接池配置
  pool_timeout = 10
  connection_limit = 20
}

// Redis 连接池
const redis = new Redis({
  host: env('REDIS_HOST'),
  port: env('REDIS_PORT'),
  maxRetriesPerRequest: 3,
  enableReadyCheck: true,
  connectTimeout: 10000
});
```

---

## 9. 测试计划

### 9.1 单元测试
- **认证服务**: 注册/登录/Token 验证
- **扫描服务**: 任务创建/状态更新
- **改写服务**: 任务创建/结果查询
- **多租户隔离**: 企业数据隔离测试

### 9.2 集成测试
- **API 端到端**: 创建扫描任务 → 查询结果
- **队列集成**: 任务分发 → 消费 → 结果存储
- **数据库集成**: 所有 CRUD 操作测试

### 9.3 性能测试
- **API 响应时间**: P95 < 200ms
- **并发能力**: 100 并发用户
- **队列吞吐量**: 100 任务 / 秒

---

## 10. 部署说明

### 10.1 Docker 配置
```dockerfile
FROM node:20-alpine

WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm ci

# 复制源码
COPY . .

# 构建类型
RUN npm run build

# 暴露端口
EXPOSE 3001

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD node healthcheck.js

# 启动服务
CMD ["npm", "start"]
```

### 10.2 环境变量
```bash
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/geo

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key

# 端口
PORT=3001

# 环境
NODE_ENV=production
```

### 10.3 健康检查脚本
```javascript
// healthcheck.js
const http = require('http');

const options = {
  host: 'localhost',
  port: 3001,
  path: '/api/health',
  timeout: 2000
};

const request = http.request(options, (res) => {
  if (res.statusCode === 200) {
    process.exit(0);
  } else {
    process.exit(1);
  }
});

request.on('error', () => {
  process.exit(1);
});

request.end();
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-17
**下次审查**: 2026-04-17
