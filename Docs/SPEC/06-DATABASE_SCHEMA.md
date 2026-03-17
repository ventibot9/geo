# GEO Platform - Database Schema 数据库设计详细规范

## 文档信息
- **版本**: v1.0.0
- **模块**: Database Schema
- **日期**: 2026-03-17
- **维护者**: GEO Platform Team

---

## 1. 数据库选型

### 1.1 PostgreSQL 选择理由
- **关系型数据**: 支持复杂查询和事务
- **JSONB 支持**: 适合存储半结构化数据 (扫描结果、评分详情)
- **全文搜索**: 内置全文索引，支持文本搜索
- **性能优秀**: 支持百万级数据量
- **开源免费**: 无商业许可成本

### 1.2 Redis 选择理由
- **内存数据库**: 响应速度 < 1ms
- **数据结构丰富**: String / Hash / List / Set / Sorted Set
- **持久化**: AOF + RDB 双重持久化
- **集群支持**: 支持分片和哨兵

---

## 2. 数据库 Schema (PostgreSQL)

### 2.1 Enterprise (企业表)
```sql
CREATE TABLE enterprises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(255) NOT NULL UNIQUE,
    plan VARCHAR(20) NOT NULL DEFAULT 'free',  -- free/pro/enterprise
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active/suspended/deleted
    settings JSONB DEFAULT '{}',  -- 企业设置 (主题、语言等)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_enterprises_domain ON enterprises(domain);
CREATE INDEX idx_enterprises_status ON enterprises(status);
CREATE INDEX idx_enterprises_plan ON enterprises(plan);
```

### 2.2 User (用户表)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hash
    enterprise_id UUID NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',  -- admin/user/viewer
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- active/suspended/deleted
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_enterprise FOREIGN KEY (enterprise_id) REFERENCES enterprises(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_enterprise ON users(enterprise_id);
CREATE INDEX idx_users_status ON users(status);
```

### 2.3 SiteConfig (网站配置表)
```sql
CREATE TABLE site_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enterprise_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL,
    scan_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    scan_schedule JSONB DEFAULT '{}',  -- {enabled: boolean, cron: string}
    scan_options JSONB DEFAULT '{}',  -- {max_pages: number, depth: number, ...}
    last_scan_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_site_enterprise FOREIGN KEY (enterprise_id) REFERENCES enterprises(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_site_configs_enterprise ON site_configs(enterprise_id);
CREATE INDEX idx_site_configs_url ON site_configs(url);
```

### 2.4 ScanTask (扫描任务表)
```sql
CREATE TABLE scan_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,
    enterprise_id UUID NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/running/completed/failed
    ai_score INTEGER CHECK (ai_score >= 0 AND ai_score <= 100),
    grade VARCHAR(1) CHECK (grade IN ('A', 'B', 'C', 'D', 'E')),
    pages_scanned INTEGER DEFAULT 0,
    pages_failed INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_scan_site FOREIGN KEY (site_id) REFERENCES site_configs(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_scan_tasks_site ON scan_tasks(site_id);
CREATE INDEX idx_scan_tasks_status ON scan_tasks(status);
CREATE INDEX idx_scan_tasks_created ON scan_tasks(created_at DESC);
CREATE INDEX idx_scan_tasks_enterprise ON scan_tasks(enterprise_id);
```

### 2.5 ContentPage (内容页面表)
```sql
CREATE TABLE content_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_task_id UUID NOT NULL,
    url VARCHAR(500) NOT NULL,
    title VARCHAR(255),
    content TEXT,  -- HTML 内容
    ai_score INTEGER CHECK (ai_score >= 0 AND ai_score <= 100),
    scoring_breakdown JSONB DEFAULT '{}',  -- 详细评分
    suggestions JSONB DEFAULT '[]',  -- 优化建议数组
    word_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_content_scan FOREIGN KEY (scan_task_id) REFERENCES scan_tasks(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_content_pages_scan ON content_pages(scan_task_id);
CREATE INDEX idx_content_pages_url ON content_pages(url);
CREATE INDEX idx_content_pages_score ON content_pages(ai_score DESC);
CREATE INDEX idx_content_pages_created ON content_pages(created_at DESC);

-- 全文搜索索引 (支持中文分词)
CREATE INDEX idx_content_pages_content_fulltext ON content_pages
    USING gin(to_tsvector('simple', content));
```

### 2.6 RewriteRecord (改写记录表)
```sql
CREATE TABLE rewrite_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_page_id UUID NOT NULL,
    enterprise_id UUID NOT NULL,
    original_content TEXT,
    rewritten_content TEXT,
    model VARCHAR(50) NOT NULL,  -- gpt-4-turbo-preview, claude-3-opus, etc.
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/processing/completed/failed
    tokens_used INTEGER DEFAULT 0,
    accepted BOOLEAN DEFAULT NULL,  -- 用户是否接受改写
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_rewrite_content FOREIGN KEY (content_page_id) REFERENCES content_pages(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_rewrite_content_page ON rewrite_records(content_page_id);
CREATE INDEX idx_rewrite_model ON rewrite_records(model);
CREATE INDEX idx_rewrite_status ON rewrite_records(status);
CREATE INDEX idx_rewrite_enterprise ON rewrite_records(enterprise_id);
```

### 2.7 CitationData (引用数据表)
```sql
CREATE TABLE citation_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enterprise_id UUID NOT NULL,
    ai_engine VARCHAR(20) NOT NULL,  -- chatgpt/claude/wenxin
    keyword VARCHAR(100) NOT NULL,
    category VARCHAR(50),  -- 产品/品牌/技术/其他
    count INTEGER NOT NULL DEFAULT 1,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    query_text TEXT,
    response_excerpt TEXT,  -- AI 回答摘录
    date DATE NOT NULL,  -- 统计日期 (精确到天)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_citation_enterprise FOREIGN KEY (enterprise_id) REFERENCES enterprises(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_citation_enterprise ON citation_data(enterprise_id);
CREATE INDEX idx_citation_engine ON citation_data(ai_engine);
CREATE INDEX idx_citation_keyword ON citation_data(keyword);
CREATE INDEX idx_citation_date ON citation_data(date DESC);
CREATE INDEX idx_citation_composite ON citation_data(enterprise_id, date, ai_engine);
```

### 2.8 JobRecord (任务队列记录表)
```sql
CREATE TABLE job_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    queue_name VARCHAR(50) NOT NULL,  -- scan-queue/rewrite-queue/monitor-queue
    task_id UUID NOT NULL,
    task_type VARCHAR(50) NOT NULL,  -- scan/rewrite/monitor
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/active/completed/failed
    priority INTEGER DEFAULT 5,  -- 1-10, 1 最高
    attempts INTEGER DEFAULT 0,
    error_message TEXT,
    result JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_job_queue ON job_records(queue_name, status);
CREATE INDEX idx_job_task ON job_records(task_id);
CREATE INDEX idx_job_created ON job_records(created_at DESC);
```

---

## 3. 数据库优化

### 3.1 分区表 (按时间分区)
```sql
-- citation_data 按月分区
CREATE TABLE citation_data (
    id UUID,
    enterprise_id UUID NOT NULL,
    ai_engine VARCHAR(20) NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    count INTEGER NOT NULL,
    confidence_score DECIMAL(3,2),
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (date);

-- 创建分区 (每月一个)
CREATE TABLE citation_data_202601 PARTITION OF citation_data
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE citation_data_202602 PARTITION OF citation_data
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- 创建未来分区
CREATE TABLE citation_data_202603 PARTITION OF citation_data
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
```

### 3.2 触发器 (自动更新)
```sql
-- 自动更新 enterprises.updated_at
CREATE OR REPLACE FUNCTION update_enterprise_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enterprise_updated
    BEFORE UPDATE ON enterprises
    FOR EACH ROW
    EXECUTE FUNCTION update_enterprise_updated_at();
```

### 3.3 视图 (统计查询)
```sql
-- 企业扫描统计视图
CREATE OR REPLACE VIEW enterprise_scan_stats AS
SELECT
    e.id AS enterprise_id,
    e.name AS enterprise_name,
    COUNT(st.id) AS total_scans,
    AVG(st.ai_score) AS avg_ai_score,
    MAX(st.completed_at) AS last_scan_at
FROM enterprises e
LEFT JOIN scan_tasks st ON st.enterprise_id = e.id
GROUP BY e.id, e.name;
```

---

## 4. Redis 数据结构

### 4.1 Session 存储
```python
# Key: session:{session_id}
# Value: JSON (用户信息)
# TTL: 7 天 (7 * 24 * 60 * 60)
# Example:
session:abc123 -> {
    "user_id": "user_xxx",
    "enterprise_id": "ent_xxx",
    "created_at": "2026-03-17T10:00:00Z"
}
```

### 4.2 缓存策略
```python
# 1. 用户信息缓存
# Key: user:{user_id}
# Value: JSON (用户详细信息)
# TTL: 10 分钟 (600 秒)
user:user_xxx -> {...}

# 2. 扫描结果缓存
# Key: scan:{scan_task_id}
# Value: JSON (扫描结果)
# TTL: 30 分钟 (1800 秒)
scan:scan_xxx -> {...}

# 3. 引用数据缓存
# Key: citations:{enterprise_id}:{period}
# Value: JSON (统计数据)
# TTL: 5 分钟 (300 秒)
citations:ent_xxx:30d -> {...}

# 4. API 限流
# Key: ratelimit:{user_id}:{endpoint}
# Value: Integer (请求次数)
# TTL: 1 分钟 (60 秒)
ratelimit:user_xxx:/api/scans -> 5
```

### 4.3 Bull 队列数据结构
```python
# 任务数据
{
    "task_id": "scan_xxx",
    "site_url": "https://example.com",
    "options": {
        "max_pages": 1000,
        "depth": 3
    },
    "priority": 5,
    "attempts": 0
}

# 队列元数据
# Key: bull:{queue_name}:meta
# Value: JSON (队列统计信息)
bull:scan-queue:meta -> {
    "paused": false,
    "maxLen": 1000,
    "id": "scan-queue"
}
```

---

## 5. 数据迁移

### 5.1 初始化脚本
```sql
-- 初始化数据库
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 中文分词支持

-- 创建所有表
(执行上面的 CREATE TABLE 语句)

-- 插入种子数据
INSERT INTO enterprises (id, name, domain, plan, status) VALUES
    ('00000000-0000-0000-0000-000000000001', '演示企业', 'demo.example.com', 'free', 'active');

INSERT INTO users (id, email, password_hash, enterprise_id, role, status) VALUES
    ('00000000-0000-0000-0000-000000000002', 'admin@demo.com',
     '$2a$10$abcdefghijklmnopqrstuvwxyz...',  -- bcrypt hash
     '00000000-0000-0000-0000-000000000001', 'admin', 'active');
```

### 5.2 清理策略
```sql
-- 清理 90 天前的引用数据
DELETE FROM citation_data
WHERE date < CURRENT_DATE - INTERVAL '90 days';

-- 清理 30 天前完成的任务记录
DELETE FROM job_records
WHERE completed_at < CURRENT_TIMESTAMP - INTERVAL '30 days';

-- 清理已完成超过 7 天的失败任务记录
DELETE FROM job_records
WHERE status = 'failed' AND completed_at < CURRENT_TIMESTAMP - INTERVAL '7 days';
```

---

## 6. 备份与恢复

### 6.1 备份策略
```bash
# 每日全量备份
0 2 * * * * pg_dump -U geo_user -d geo_platform -F c -f /backup/geo_$(date +\%Y\%m\%d).sql

# 每小时增量备份 (WAL)
# PostgreSQL 自动执行 WAL 归档

# Redis 备份
0 */6 * * * * redis-cli --rdb /backup/dump_$(date +\%Y\%m\%d\%H\%M).rdb
```

### 6.2 恢复流程
```bash
# 1. 停止应用服务
docker-compose down

# 2. 恢复 PostgreSQL
psql -U geo_user -d geo_platform < /backup/geo_20260317.sql

# 3. 恢复 Redis
redis-cli --rdb /backup/dump_20260317142000.rdb

# 4. 重启应用服务
docker-compose up -d
```

---

## 7. 性能监控

### 7.1 慢查询日志
```sql
-- 启用慢查询日志 (超过 100ms)
ALTER SYSTEM SET log_min_duration_statement = 100;
ALTER SYSTEM SET log_statement = 'all';

-- 查看慢查询
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 7.2 连接池监控
```sql
-- 查看当前连接数
SELECT count(*) FROM pg_stat_activity;

-- 查看连接池状态
SELECT pool_name, active_count, idle_count
FROM pg_pool_status;
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-17
**下次审查**: 2026-04-17
