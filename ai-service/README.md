# GEO Platform AI Rewrite Service

GEO平台AI驱动的内容改写和结构优化服务。

## 功能特性

- 🤖 **多模型支持**：OpenAI GPT-4 / Anthropic Claude / 本地Llama
- 📝 **内容结构优化**：自动重新组织标题层级
- 📊 **数据提取**：将关键数据提取为表格
- 🔄 **批量改写**：支持批量处理多条内容
- ✅ **质量评估**：自动评估改写质量
- 📚 **历史记录**：保存所有改写历史
- 🚀 **RESTful API**：标准的REST API接口

## 技术栈

- Python 3.11
- FastAPI
- SQLAlchemy (异步)
- OpenAI API / Anthropic API

## 快速开始

### 本地运行

1. 复制环境变量配置
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的API密钥

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 启动服务
```bash
python -m app.main
```

或使用 uvicorn：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## API 文档

服务启动后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口说明

### 1. 单条改写

```http
POST /api/v1/rewrite
Content-Type: application/json

{
  "content": "原始内容",
  "model_provider": "anthropic",
  "temperature": 0.7,
  "optimize_structure": true,
  "extract_tables": true
}
```

### 2. 批量改写

```http
POST /api/v1/rewrite/batch
Content-Type: application/json

{
  "contents": ["内容1", "内容2"],
  "model_provider": "anthropic",
  "temperature": 0.7
}
```

### 3. 质量评估

```http
POST /api/v1/rewrite/evaluate
Content-Type: application/json

{
  "original": "原始内容",
  "rewritten": "改写后内容",
  "model_provider": "anthropic"
}
```

### 4. 获取历史记录

```http
GET /api/v1/rewrite/history?limit=50
```

### 5. 获取可用模型

```http
GET /api/v1/rewrite/models
```

## Prompt 工程说明

### 核心设计原则

1. **结构化优先**：明确要求输出Markdown格式，清晰的标题层级
2. **数据提取**：将关键参数提取为表格
3. **完整性保证**：确保核心信息不丢失
4. **AI友好**：输出格式对AI引擎读取友好

### Prompt 模板

#### 系统提示词（System Prompt）

```
你是一个专业的内容优化助手，擅长将非结构化或半结构化的内容转换为AI引擎易于读取和理解的格式。

你的核心能力：
1. 结构化组织：将混乱的内容重新组织为清晰的层级结构
2. 格式转换：转换为标准的API文档或技术文档格式
3. 数据提取：将关键参数、配置项提取为表格
4. 完整性保持：确保核心信息不丢失
5. Markdown格式：使用结构化的Markdown格式输出

输出要求：
- 使用标准Markdown语法
- 标题层级清晰（H1/H2/H3）
- 关键数据用表格展示
- 代码块使用正确的语法高亮
- 保持技术准确性
```

#### 用户提示词构建

```
请对以下内容进行改写优化。

优化目标：
- 重新组织标题层级，使其清晰有序
- 优化段落结构，提高可读性
- 将关键参数、配置数据提取为表格
- 使用表格展示结构化数据
- 保持核心信息完整性
- 使用结构化Markdown格式
- 确保技术准确性

原始内容：
{content}
```

#### 质量评估 Prompt

```
请评估以下改写内容的质量。

原始内容：
{original}

改写后内容：
{rewritten}

评估维度（0-1分）：
1. 完整性：是否保留了所有关键信息
2. 清晰度：表达是否清晰易懂
3. 结构化：是否具有良好的结构
4. 可读性：是否符合AI引擎阅读习惯

请以JSON格式输出评估结果...
```

### Prompt 优化要点

1. **角色定位**：明确模型是"专业的内容优化助手"
2. **任务明确**：清晰说明"将非结构化内容转换为AI引擎易读格式"
3. **输出格式**：强制要求Markdown格式
4. **结构要求**：H1/H2/H3层级 + 表格展示
5. **完整性约束**："保持核心信息完整性"
6. **技术准确性**：强调保持技术细节准确

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| OPENAI_API_KEY | OpenAI API密钥 | - |
| OPENAI_BASE_URL | OpenAI API地址 | https://api.openai.com/v1 |
| OPENAI_MODEL | 默认OpenAI模型 | gpt-4-turbo-preview |
| ANTHROPIC_API_KEY | Anthropic API密钥 | - |
| ANTHROPIC_MODEL | 默认Anthropic模型 | claude-3-opus-20240229 |
| LLAMA_API_BASE | 本地Llama API地址 | http://localhost:11434/v1 |
| LLAMA_MODEL | 默认Llama模型 | llama2 |
| DEFAULT_MODEL | 默认模型提供商 | anthropic |
| DATABASE_URL | 数据库连接字符串 | sqlite+aiosqlite:///./rewrites.db |

## 项目结构

```
ai-service/
├── app/
│   ├── adapters/          # 大模型适配器
│   │   ├── base.py
│   │   ├── openai_adapter.py
│   │   ├── anthropic_adapter.py
│   │   └── llama_adapter.py
│   ├── models/            # 数据模型
│   │   ├── schemas.py
│   │   └── database.py
│   ├── prompts/           # Prompt模板
│   │   └── templates.py
│   ├── routers/           # API路由
│   │   └── rewrite.py
│   ├── services/          # 业务逻辑
│   │   ├── model_factory.py
│   │   └── rewrite_service.py
│   ├── database.py        # 数据库配置
│   └── main.py            # FastAPI入口
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 许可证

MIT
