"""Prompt 工程模板"""

SYSTEM_PROMPT = """你是一个专业的内容优化助手，擅长将非结构化或半结构化的内容转换为AI引擎易于读取和理解的格式。

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
- 保持技术准确性"""


STRUCTURE_OPTIMIZATION_PROMPT = """请将以下内容重新组织为AI引擎易读的格式。

要求：
1. 添加清晰的标题层级（H1/H2/H3）
2. 将关键数据提取为表格
3. 保持核心信息完整性
4. 使用结构化Markdown格式
5. 如果包含API接口，按API文档格式组织

原始内容：
{content}"""


DEFAULT_REWRITE_PROMPT = """请对以下内容进行改写优化。

优化目标：
{goals}

原始内容：
{content}"""


QUALITY_EVALUATION_PROMPT = """请评估以下改写内容的质量。

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
- overall_score: 总体评分
- completeness: 完整性评分
- clarity: 清晰度评分
- structure: 结构化评分
- suggestions: 改进建议列表
"""


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

    return DEFAULT_REWRITE_PROMPT.format(
        content=content,
        goals="\n".join(goals),
    )
