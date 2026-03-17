# GEO Platform - 生成式引擎优化SaaS平台

## 项目简介
GEO（Generative Engine Optimization）SaaS平台，帮助企业优化内容结构，提高AI引擎引用率。

## 核心功能

### 1. 自动内容扫描
- 爬取企业网站内容
- 分析内容结构化程度
- AI友好度评分（0-100分）
- 生成优化建议

### 2. AI智能改写
- 一键优化内容结构
- 转换为API文档格式
- 批量改写支持
- 多模型支持（GPT-4/Claude/Llama）

### 3. 引用监控
- 追踪ChatGPT/Claude/文心一言等AI引擎
- 统计曝光量
- 趋势分析报告

### 4. 数据分析
- GEO优化效果报表
- ROI分析
- 对比分析

## 技术架构

```
前端（React） ←→ 后端API（Node.js）
     ↓                ↓
  管理界面         任务调度
                   ↓
        ┌─────────────────────────┐
        │                        │
   内容扫描器              AI改写服务
   （Python）               （Python）
        │                        │
        └────────→ 引用监控 ←────┘
                    （Python）
```

## 项目结构

```
geo-platform/
├── backend/          # 后端API服务
├── frontend/         # 前端管理界面
├── scanner/          # 内容扫描器
├── ai-service/       # AI改写服务
├── monitor/         # 引用监控服务
├── docker-compose.yml
└── README.md
```

## 快速开始

### 前置要求
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 一键启动
```bash
# 克隆项目
cd /root/.openclaw/workspace-open-lead/geo-platform

# 启动所有服务
docker-compose up -d

# 访问前端
http://localhost:3000

# 访问后端API
http://localhost:3001
```

### 单独启动各模块

#### 后端API
```bash
cd backend
npm install
npm run dev
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

#### 内容扫描器
```bash
cd scanner
pip install -r requirements.txt
python main.py
```

#### AI改写服务
```bash
cd ai-service
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 引用监控服务
```bash
cd monitor
pip install -r requirements.txt
python main.py
```

## API 文档

### 认证
```
POST /api/auth/login
POST /api/auth/register
```

### 扫描任务
```
POST /api/scans/create
GET /api/scans/:id
GET /api/scans/list
```

### AI改写
```
POST /api/ai/rewrite
GET /api/ai/history
```

### 引用监控
```
GET /api/monitor/citations
GET /api/monitor/trends
```

## 数据模型

### Enterprise（企业）
- id, name, domain, plan, status

### User（用户）
- id, email, password, enterprise_id, role

### SiteConfig（网站配置）
- id, enterprise_id, url, scan_schedule

### ScanTask（扫描任务）
- id, enterprise_id, status, score, created_at

### ContentPage（内容页面）
- id, scan_task_id, url, title, content, ai_score

### CitationData（引用数据）
- id, enterprise_id, ai_engine, keyword, count, date

## 开发进度

- [x] 架构设计
- [ ] 后端API基础
- [ ] 前端管理界面
- [ ] 内容扫描器
- [ ] AI改写服务
- [ ] 引用监控服务
- [ ] Docker部署
- [ ] 测试

## 贡献

多Agent并行开发中，各子任务独立推进。

## 许可

MIT
