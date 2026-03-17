# GEO Platform AI Rewrite Service - API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: v1
- **认证方式**: 暂无（后续可添加 API Key 认证）

## API 端点

### 1. 单条改写

改写单条内容，自动优化结构和提取表格。

**请求**

```http
POST /api/v1/rewrite
Content-Type: application/json
```

**请求体**

```json
{
  "content": "原始内容字符串",
  "model_provider": "anthropic",
  "model": "claude-3-opus-20240229",
  "temperature": 0.7,
  "optimize_structure": true,
  "extract_tables": true,
  "system_prompt": null
}
```

**参数说明**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| content | string | 是 | - | 原始内容 |
| model_provider | string | 否 | anthropic | 模型提供商：openai/anthropic/llama |
| model | string | 否 | - | 指定模型名称 |
| temperature | number | 否 | 0.7 | 温度参数 0-1 |
| optimize_structure | boolean | 否 | true | 是否优化结构 |
| extract_tables | boolean | 否 | true | 是否提取表格 |
| system_prompt | string | 否 | - | 自定义系统提示 |

**响应**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "original": "原始内容...",
  "rewritten": "改写后的内容...",
  "model_provider": "anthropic",
  "model": "claude-3-opus-20240229",
  "created_at": "2024-03-17T05:43:00Z",
  "quality": null
}
```

---

### 2. 批量改写

批量改写多条内容。

**请求**

```http
POST /api/v1/rewrite/batch
Content-Type: application/json
```

**请求体**

```json
{
  "contents": [
    "内容1",
    "内容2",
    "内容3"
  ],
  "model_provider": "anthropic",
  "model": null,
  "temperature": 0.7,
  "optimize_structure": true,
  "extract_tables": true
}
```

**参数说明**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| contents | array | 是 | - | 内容列表（1-50条） |
| model_provider | string | 否 | anthropic | 模型提供商 |
| model | string | 否 | - | 指定模型名称 |
| temperature | number | 否 | 0.7 | 温度参数 |
| optimize_structure | boolean | 否 | true | 是否优化结构 |
| extract_tables | boolean | 否 | true | 是否提取表格 |

**响应**

```json
[
  {
    "id": "record-id-1",
    "original": "内容1...",
    "rewritten": "改写后内容1...",
    "model_provider": "anthropic",
    "model": "claude-3-opus-20240229",
    "created_at": "2024-03-17T05:43:00Z",
    "quality": null
  },
  {
    "id": "record-id-2",
    "original": "内容2...",
    "rewritten": "改写后内容2...",
    "model_provider": "anthropic",
    "model": "claude-3-opus-20240229",
    "created_at": "2024-03-17T05:43:01Z",
    "quality": null
  }
]
```

---

### 3. 质量评估

评估改写内容的质量。

**请求**

```http
POST /api/v1/rewrite/evaluate
Content-Type: application/json
```

**请求体**

```json
{
  "original": "原始内容",
  "rewritten": "改写后内容",
  "model_provider": "anthropic"
}
```

**参数说明**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| original | string | 是 | - | 原始内容 |
| rewritten | string | 是 | - | 改写后内容 |
| model_provider | string | 否 | anthropic | 评估用的模型 |

**响应**

```json
{
  "overall_score": 0.85,
  "completeness": 0.9,
  "clarity": 0.8,
  "structure": 0.85,
  "suggestions": [
    "建议增加更多示例代码",
    "部分术语可以添加解释"
  ]
}
```

---

### 4. 获取改写历史

获取最近的改写历史记录。

**请求**

```http
GET /api/v1/rewrite/history?limit=50
```

**参数说明**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | integer | 否 | 50 | 返回记录数量 |

**响应**

```json
[
  {
    "id": "record-id",
    "original": "原始内容前200字符...",
    "rewritten": "改写后内容前200字符...",
    "model_provider": "anthropic",
    "model": "claude-3-opus-20240229",
    "created_at": "2024-03-17T05:43:00Z",
    "quality_score": null
  }
]
```

---

### 5. 获取单条记录

获取指定ID的改写记录详情。

**请求**

```http
GET /api/v1/rewrite/record/{record_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| record_id | string | 是 | 记录ID |

**响应**

```json
{
  "id": "record-id",
  "original": "完整的原始内容...",
  "rewritten": "完整的改写后内容...",
  "model_provider": "anthropic",
  "model": "claude-3-opus-20240229",
  "created_at": "2024-03-17T05:43:00Z",
  "quality_score": 0.85,
  "quality_details": {
    "completeness": 0.9,
    "clarity": 0.8,
    "structure": 0.85,
    "suggestions": [...]
  }
}
```

---

### 6. 获取可用模型

获取当前配置的可用模型列表。

**请求**

```http
GET /api/v1/rewrite/models
```

**响应**

```json
[
  {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "available": true
  },
  {
    "provider": "anthropic",
    "model": "claude-3-opus-20240229",
    "available": true
  },
  {
    "provider": "llama",
    "model": "llama2",
    "available": true
  }
]
```

---

### 7. 健康检查

服务健康检查。

**请求**

```http
GET /api/v1/rewrite/health
```

**响应**

```json
{
  "status": "ok",
  "models": 3
}
```

---

## 错误响应

所有错误响应遵循以下格式：

```json
{
  "detail": "错误信息描述"
}
```

**常见错误码**

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### cURL 示例

```bash
# 单条改写
curl -X POST "http://localhost:8000/api/v1/rewrite" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "GEO平台是一个地理信息系统...",
    "model_provider": "anthropic",
    "optimize_structure": true
  }'

# 获取历史
curl "http://localhost:8000/api/v1/rewrite/history?limit=10"

# 质量评估
curl -X POST "http://localhost:8000/api/v1/rewrite/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "original": "原始内容",
    "rewritten": "改写后内容"
  }'
```

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 单条改写
response = requests.post(
    f"{BASE_URL}/api/v1/rewrite",
    json={
        "content": "GEO平台是一个地理信息系统...",
        "model_provider": "anthropic",
        "optimize_structure": True,
    }
)
result = response.json()
print(result["rewritten"])

# 批量改写
response = requests.post(
    f"{BASE_URL}/api/v1/rewrite/batch",
    json={
        "contents": ["内容1", "内容2"],
        "model_provider": "anthropic",
    }
)
results = response.json()

# 质量评估
response = requests.post(
    f"{BASE_URL}/api/v1/rewrite/evaluate",
    json={
        "original": "原始内容",
        "rewritten": "改写后内容",
    }
)
evaluation = response.json()
print(f"总体评分: {evaluation['overall_score']}")
```

---

## 注意事项

1. **API 限流**: 当前版本未实现限流，生产环境建议添加
2. **认证**: 当前版本无认证，后续可添加 API Key 或 JWT
3. **数据持久化**: 使用 SQLite 存储，生产环境建议切换到 PostgreSQL
4. **流式响应**: 当前版本使用非流式响应，可升级为 SSE
5. **错误处理**: 建议在生产环境完善错误日志和监控
