# 快速开始指南

## 1. 安装依赖

```bash
cd /root/.openclaw/workspace-open-lead/geo-platform/ai-service
pip install -r requirements.txt
```

## 2. 配置API密钥

编辑 `.env` 文件，至少配置一个模型的API密钥：

```bash
# 编辑 .env 文件
nano .env
```

**Anthropic Claude（推荐）**:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEFAULT_MODEL=anthropic
```

**OpenAI GPT-4**:
```
OPENAI_API_KEY=sk-your-key-here
DEFAULT_MODEL=openai
```

**本地Llama（需要先启动Ollama）**:
```
LLAMA_API_BASE=http://localhost:11434/v1
DEFAULT_MODEL=llama
```

## 3. 启动服务

```bash
./start.sh
```

或使用 uvicorn：
```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 5. 测试服务

```bash
python3 example_test.py
```

## Docker部署

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## API示例

### 单条改写

```bash
curl -X POST "http://localhost:8000/api/v1/rewrite" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "GEO平台是一个地理信息系统。支持Shapefile、GeoJSON格式。",
    "model_provider": "anthropic",
    "optimize_structure": true
  }'
```

### 批量改写

```bash
curl -X POST "http://localhost:8000/api/v1/rewrite/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": ["内容1", "内容2"],
    "model_provider": "anthropic"
  }'
```

### 质量评估

```bash
curl -X POST "http://localhost:8000/api/v1/rewrite/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "original": "原始内容",
    "rewritten": "改写后内容"
  }'
```

## 常见问题

### Q: 提示 ModuleNotFoundError
A: 需要先安装依赖 `pip install -r requirements.txt`

### Q: 服务启动失败
A: 检查 `.env` 文件是否配置了API密钥

### Q: Docker无法访问宿主机服务
A: 使用 `host.docker.internal` 访问宿主机

### Q: 数据库文件在哪？
A: SQLite数据库位于 `data/rewrites.db`

## 下一步

- 阅读完整文档：`README.md`
- API接口文档：`API_DOCS.md`
- Prompt工程说明：`PROMPT_ENGINEERING.md`
- 项目总结：`PROJECT_SUMMARY.md`
