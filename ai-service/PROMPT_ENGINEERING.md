# Prompt 工程说明文档

## 设计理念

GEO平台AI改写服务的 Prompt 设计遵循以下核心理念：

1. **结构化优先**：输出必须是结构化的 Markdown 格式
2. **AI 引擎友好**：输出格式对 AI 引擎读取和处理友好
3. **信息完整性**：确保不丢失任何关键信息
4. **数据可视化**：将结构化数据提取为表格

---

## 系统提示词（System Prompt）

### 完整版本

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

### 设计要点解析

| 要素 | 说明 |
|------|------|
| 角色定位 | "专业的内容优化助手" - 明确身份和能力 |
| 目标受众 | "AI引擎" - 输出需要被机器读取 |
| 核心能力 | 5项明确的能力清单 |
| 输出要求 | 6项具体的格式要求 |

---

## 用户提示词（User Prompt）

### 基础模板

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

### 动态构建逻辑

```python
def build_rewrite_prompt(
    content: str,
    optimize_structure: bool = True,
    extract_tables: bool = True,
) -> str:
    """构建改写 Prompt"""

    goals = []

    if optimize_structure:
        goals.append("- 重新组织标题层级，使其清晰有序")
        goals.append("- 优化段落结构，提高可读性")

    if extract_tables:
        goals.append("- 将关键参数、配置数据提取为表格")
        goals.append("- 使用表格展示结构化数据")

    goals.extend([
        "- 保持核心信息完整性",
        "- 使用结构化Markdown格式",
        "- 确保技术准确性",
    ])

    return f"""请对以下内容进行改写优化。

优化目标：
{chr(10).join(goals)}

原始内容：
{content}"""
```

---

## 质量评估 Prompt

### 完整版本

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

请以JSON格式输出评估结果，包含以下字段：
- overall_score: 总体评分（0-1）
- completeness: 完整性评分（0-1）
- clarity: 清晰度评分（0-1）
- structure: 结构化评分（0-1）
- suggestions: 改进建议列表（数组）
```

### 评估维度说明

| 维度 | 说明 | 评分标准 |
|------|------|----------|
| 完整性 | 是否保留所有关键信息 | 0=大量遗漏，1=完全保留 |
| 清晰度 | 表达是否清晰易懂 | 0=难以理解，1=非常清晰 |
| 结构化 | 是否具有良好的结构 | 0=混乱，1=结构完美 |
| 可读性 | 是否符合AI引擎阅读习惯 | 0=难以解析，1=易于解析 |

---

## Prompt 优化要点

### 1. 角色定位

**错误示例**：
```
你是一个AI助手，帮我改写这段内容。
```

**正确示例**：
```
你是一个专业的内容优化助手，擅长将非结构化或半结构化的内容转换为AI引擎易于读取和理解的格式。
```

**优化说明**：
- 明确角色身份
- 定义核心能力
- 明确输出目标

---

### 2. 任务明确性

**错误示例**：
```
改写下面的内容。
```

**正确示例**：
```
请将此内容重新组织为AI引擎易读的格式。
```

**优化说明**：
- 明确任务目标
- 定义输出标准

---

### 3. 结构要求

**错误示例**：
```
使用良好的格式。
```

**正确示例**：
```
添加清晰的标题层级（H1/H2/H3）
```

**优化说明**：
- 具体的格式要求
- 明确的层级说明

---

### 4. 数据提取

**错误示例**：
```
把数据整理一下。
```

**正确示例**：
```
将关键数据提取为表格
```

**优化说明**：
- 明确提取对象
- 指定输出格式（表格）

---

### 5. 完整性约束

**错误示例**：
```
不要删太多。
```

**正确示例**：
```
保持核心信息完整性
```

**优化说明**：
- 明确保留原则
- 定义核心信息

---

### 6. 输出格式

**错误示例**：
```
输出要好看。
```

**正确示例**：
```
使用结构化Markdown格式
```

**优化说明**：
- 明确输出格式
- 定义结构化标准

---

## 不同场景的 Prompt 调整

### 场景1：API 文档改写

```python
user_prompt = f"""请将以下API文档重新组织为标准格式。

要求：
- 按照API文档标准格式组织
- 提取所有端点为表格
- 明确参数说明和返回格式
- 保持所有示例代码

原始API文档：
{content}"""
```

### 场景2：技术文档优化

```python
user_prompt = f"""请优化以下技术文档。

要求：
- 添加清晰的章节标题
- 将技术参数提取为表格
- 保留所有代码示例
- 确保术语一致性

原始技术文档：
{content}"""
```

### 场景3：配置说明整理

```python
user_prompt = f"""请整理以下配置说明。

要求：
- 将所有配置项提取为表格
- 表格包含：参数名、类型、默认值、说明
- 按功能分组展示
- 保留所有注释说明

原始配置说明：
{content}"""
```

---

## 最佳实践

### 1. 温度参数选择

| 任务场景 | 推荐温度 | 说明 |
|----------|----------|------|
| 结构优化 | 0.3-0.5 | 低温度保证格式稳定 |
| 内容改写 | 0.6-0.8 | 中等温度保持一定创造性 |
| 质量评估 | 0.2-0.4 | 低温度保证评估客观 |

### 2. Token 限制

```python
# 普通改写任务
max_tokens = 4096

# 长文档处理
max_tokens = 8192

# 质量评估
max_tokens = 1024
```

### 3. 错误处理

```python
try:
    result = await adapter.generate(prompt, max_tokens=4096)
    # 解析和验证结果
except Exception as e:
    # 降级处理：使用简化版本或返回错误
    pass
```

---

## 性能优化建议

### 1. Prompt 缓存

将常用的 Prompt 模板缓存起来，避免重复构建：

```python
PROMPT_CACHE = {}

def get_cached_prompt(key: str, template: str, **kwargs) -> str:
    """获取缓存的 Prompt"""
    if key not in PROMPT_CACHE:
        PROMPT_CACHE[key] = template.format(**kwargs)
    return PROMPT_CACHE[key]
```

### 2. 批量处理

批量改写时，可以并行处理以提高效率：

```python
import asyncio

async def batch_rewrite(contents: list) -> list:
    """批量改写（并行）"""
    tasks = [rewrite_single(content) for content in contents]
    return await asyncio.gather(*tasks)
```

### 3. 流式响应

对于长文档，使用流式响应可以更快地获得部分结果：

```python
async def stream_rewrite(content: str):
    """流式改写"""
    async for chunk in adapter.stream_generate(prompt):
        yield chunk
```

---

## 持续优化方向

1. **Few-shot Learning**：添加示例提升效果
2. **Prompt Chaining**：多步骤处理复杂任务
3. **自适应 Prompt**：根据内容类型自动调整 Prompt
4. **反馈机制**：收集用户反馈持续优化 Prompt
5. **A/B 测试**：对比不同 Prompt 版本的效果

---

## 参考资源

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library)
- [Structuring Chat Models](https://platform.openai.com/docs/guides/structured-outputs)
