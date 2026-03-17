# GEO Platform - AI Service AI 改写服务详细规范

## 文档信息
- **版本**: v1.0.0
- **模块**: AI Rewrite Service
- **日期**: 2026-03-17
- **维护者**: GEO Platform Team

---

## 1. 模块职责

### 1.1 核心功能
1. **多模型支持**
   - OpenAI GPT-4 Turbo
   - Anthropic Claude 3 Opus
   - 本地 Llama 模型

2. **内容结构优化**
   - 标题层级重新组织
   - 转换为 API 文档格式
   - 提取关键参数为表格

3. **批量改写**
   - 支持 1-50 条批量处理
   - 并发控制

4. **质量评估**
   - 多维度质量评分
   - 改进建议

---

## 2. 大模型适配器

### 2.1 基础适配器接口
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseModelAdapter(ABC):
    """大模型适配器基类"""

    @abstractmethod
    async def rewrite(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """改写内容"""
        pass

    @abstractmethod
    async def evaluate_quality(self, content: str) -> Dict[str, Any]:
        """评估内容质量"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass
```

### 2.2 OpenAI 适配器
```python
class OpenAIAdapter(BaseModelAdapter):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)

    async def rewrite(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """使用 OpenAI GPT-4 改写内容"""
        system_prompt = self._build_system_prompt(options)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )

        return {
            'content': response.choices[0].message.content,
            'model': self.model,
            'tokens_used': response.usage.total_tokens
        }

    def _build_system_prompt(self, options: Dict[str, Any]) -> str:
        """构建系统提示词"""
        prompt = """你是一个专业的内容优化助手，擅长将非结构化或半结构化的内容转换为AI引擎易于读取和理解的格式。

优化目标：
- 添加清晰的标题层级（H1/H2/H3）
- 将关键数据提取为表格
- 保持核心信息完整性
- 使用结构化 Markdown 格式

输出要求：
- 返回纯 Markdown 格式
- 使用三级标题结构
- 数据用 Markdown 表格呈现
"""

        if options.get('add_tables'):
            prompt += "\n- 所有数值型数据必须转换为表格"
        if options.get('optimize_structure'):
            prompt += "\n- 重新组织内容逻辑，使其更清晰"
        if options.get('extract_parameters'):
            prompt += "\n- 提取所有关键参数，用无序列表呈现"

        return prompt

    def get_model_name(self) -> str:
        return self.model
```

### 2.3 Anthropic 适配器
```python
class AnthropicAdapter(BaseModelAdapter):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def rewrite(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """使用 Claude 改写内容"""
        system_prompt = self._build_system_prompt(options)

        message = await self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": content}
            ]
        )

        return {
            'content': message.content[0].text,
            'model': self.model,
            'tokens_used': message.usage.input_tokens + message.usage.output_tokens
        }

    def _build_system_prompt(self, options: Dict[str, Any]) -> str:
        """Claude 专用系统提示词"""
        prompt = """你是一个专业的内容优化助手，擅长将非结构化或半结构化的内容转换为AI引擎易于读取和理解的格式。

你的任务是：
1. 添加清晰的标题层级（H1/H2/H3）
2. 将关键数据提取为表格
3. 保持核心信息完整性
4. 使用结构化 Markdown 格式

重要说明：
- 不要添加原内容中没有的信息
- 保持技术术语准确
- 优先保持原文的核心逻辑
"""

        if options.get('add_tables'):
            prompt += "\n\n额外要求：所有数值型数据必须转换为表格"

        return prompt

    def get_model_name(self) -> str:
        return self.model
```

### 2.4 本地 Llama 适配器
```python
class LlamaAdapter(BaseModelAdapter):
    def __init__(self, model_url: str = "http://localhost:11434", model: str = "llama2:7b"):
        self.model_url = model_url
        self.model = model

    async def rewrite(self, content: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """使用本地 Llama 模型改写"""
        system_prompt = self._build_system_prompt(options)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            "stream": False,
            "temperature": 0.7
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.model_url}/api/generate",
                json=payload,
                timeout=30000
            ) as response:
                data = await response.json()

                return {
                    'content': data.get('response', ''),
                    'model': self.model,
                    'tokens_used': 0  # 本地模型不计 token
                }

    def _build_system_prompt(self, options: Dict[str, Any]) -> str:
        """Llama 专用系统提示词"""
        prompt = "你是一个专业的内容优化助手。将内容转换为AI引擎易读的格式。"
        if options.get('add_tables'):
            prompt += " 用表格展示数据。"
        if options.get('optimize_structure'):
            prompt += " 优化内容结构。"

        return prompt

    def get_model_name(self) -> str:
        return self.model
```

---

## 3. Prompt 工程设计

### 3.1 系统提示词模板
```python
SYSTEM_PROMPT_TEMPLATE = """你是一个专业的内容优化助手，擅长将非结构化或半结构化的内容转换为AI引擎易于读取和理解的格式。

## 优化目标

1. 标题结构优化
   - 添加清晰的标题层级（H1/H2/H3）
   - 每个 H1 下面应该有 2-4 个 H2
   - 每个 H2 下面可以有 1-3 个 H3

2. 数据表格化
   - 识别所有数值型数据
   - 使用 Markdown 表格呈现
   - 表格应包含表头

3. 信息完整性
   - 不要删除原内容的核心信息
   - 补充缺失的细节（如参数说明）

4. 格式标准化
   - 使用结构化 Markdown 格式
   - 添加适当的代码块标记
   - 列表使用正确的符号 (- 或 *)

## 输出格式

返回纯 Markdown 格式，不要添加任何 Markdown 标记之外的说明文字。

## 示例

输入：
这是一个产品描述...

输出：
# 产品名称

## 产品概述

...内容...

## 技术参数

| 参数 | 值 |
|------|------|
| ... | ... |
"""
```

### 3.2 用户提示词构建
```python
def build_user_prompt(content: str, options: Dict[str, Any]) -> str:
    """构建用户提示词"""
    prompt = f"请将以下内容转换为AI引擎易读的格式：\n\n{content}\n\n"

    if options.get('add_tables'):
        prompt += "要求：所有数值型数据必须转换为表格。\n"

    if options.get('optimize_structure'):
        prompt += "要求：重新组织内容逻辑，使其更清晰。\n"

    if options.get('extract_parameters'):
        prompt += "要求：提取所有关键参数，用无序列表呈现。\n"

    return prompt
```

---

## 4. 质量评估

### 4.1 评估维度
```python
async def evaluate_rewrite_quality(original: str, rewritten: str) -> Dict[str, Any]:
    """评估改写质量"""

    # 1. 结构优化评分 (40 分)
    structure_score = await evaluate_structure_improvement(original, rewritten)

    # 2. 表格质量评分 (30 分)
    table_score = await evaluate_table_quality(rewritten)

    # 3. 参数提取评分 (20 分)
    parameter_score = await evaluate_parameter_extraction(rewritten)

    # 4. 信息保留评分 (10 分)
    retention_score = await evaluate_information_retention(original, rewritten)

    total_score = structure_score + table_score + parameter_score + retention_score

    return {
        'total_score': total_score,
        'max_score': 100,
        'structure_score': structure_score,
        'table_score': table_score,
        'parameter_score': parameter_score,
        'retention_score': retention_score
    }

async def evaluate_structure_improvement(original: str, rewritten: str) -> int:
    """评估结构优化"""
    original_headings = len(re.findall(r'^#{1,3}\s', original, re.MULTILINE))
    rewritten_headings = len(re.findall(r'^#{1,3}\s', rewritten, re.MULTILINE))

    improvement = rewritten_headings - original_headings
    score = min(improvement * 10, 40)  # 每个标题 10 分，最多 40 分

    return score
```

---

## 5. REST API 设计

### 5.1 API 端点
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="GEO AI Rewrite Service", version="1.0.0")

class RewriteRequest(BaseModel):
    content: str
    model: str = "gpt-4-turbo-preview"
    options: Dict[str, Any] = {}

class BatchRewriteRequest(BaseModel):
    contents: List[str]
    model: str = "gpt-4-turbo-preview"
    options: Dict[str, Any] = {}

@app.post("/api/v1/rewrite")
async def rewrite(request: RewriteRequest):
    """单条改写"""
    adapter = get_adapter(request.model)

    try:
        result = await adapter.rewrite(request.content, request.options)
        quality = await evaluate_rewrite_quality(request.content, result['content'])

        return {
            'success': True,
            'data': {
                'content': result['content'],
                'model': result['model'],
                'quality_score': quality['total_score'],
                'tokens_used': result['tokens_used']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rewrite/batch")
async def batch_rewrite(request: BatchRewriteRequest):
    """批量改写"""
    if len(request.contents) > 50:
        raise HTTPException(status_code=400, detail="批量最多支持 50 条内容")

    adapter = get_adapter(request.model)
    results = []

    for content in request.contents:
        result = await adapter.rewrite(content, request.options)
        quality = await evaluate_rewrite_quality(content, result['content'])
        results.append({
            'content': result['content'],
            'model': result['model'],
            'quality_score': quality['total_score']
        })

    return {
        'success': True,
        'data': results
    }

@app.get("/api/v1/rewrite/models")
async def get_models():
    """获取可用模型列表"""
    return {
        'success': True,
        'data': [
            {
                'id': 'gpt-4-turbo-preview',
                'name': 'GPT-4 Turbo',
                'provider': 'OpenAI',
                'supports_tables': True,
                'supports_parameters': True
            },
            {
                'id': 'claude-3-opus-20240229',
                'name': 'Claude 3 Opus',
                'provider': 'Anthropic',
                'supports_tables': True,
                'supports_parameters': True
            },
            {
                'id': 'llama2:7b',
                'name': 'Llama 2 7B',
                'provider': 'Local',
                'supports_tables': True,
                'supports_parameters': True
            }
        ]
    }

@app.get("/api/v1/rewrite/health")
async def health():
    """健康检查"""
    return {
        'status': 'ok',
        'models': {
            'openai': check_openai_key(),
            'anthropic': check_anthropic_key(),
            'llama': check_llama_connection()
        }
    }
```

---

## 6. 性能优化

### 6.1 并发控制
```python
from asyncio import Semaphore

CONCURRENCY_LIMIT = 5  # 最多同时 5 个改写任务
rewrite_semaphore = Semaphore(CONCURRENCY_LIMIT)

async def rewrite_with_semaphore(adapter, content, options):
    """带并发控制的改写"""
    async with rewrite_semaphore:
        return await adapter.rewrite(content, options)
```

### 6.2 缓存策略
```python
from functools import lru_cache
import hashlib

def cache_key(content: str, model: str, options: dict) -> str:
    """生成缓存键"""
    options_str = json.dumps(options, sort_keys=True)
    key_string = f"{model}:{content}:{options_str}"
    return hashlib.md5(key_string.encode()).hexdigest()

@lru_cache(maxsize=100)
async def cached_rewrite(adapter, content, options):
    """缓存改写结果"""
    key = cache_key(content, adapter.get_model_name(), options)
    return await adapter.rewrite(content, options)
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-17
**下次审查**: 2026-04-17
