# GEO Platform - Content Scanner 内容扫描器详细规范

## 文档信息
- **版本**: v1.0.0
- **模块**: Content Scanner Service
- **日期**: 2026-03-17
- **维护者**: GEO Platform Team

---

## 1. 模块职责

### 1.1 核心功能
1. **网站爬虫**
   - 静态页面爬取 (BeautifulSoup)
   - 动态页面爬取 (Puppeteer)
   - 支持 SPA 应用

2. **内容解析**
   - HTML 结构分析
   - 标题层级提取 (H1/H2/H3)
   - 表格识别
   - 数据完整性检查

3. **AI 友好度评分**
   - 5 维度评分系统
   - 每维度 0-100 分，总分 0-100 分
   - 等级划分 (A/B/C/D/E)

4. **优化建议生成**
   - 针对性改进建议
   - 按优先级排序

5. **结构化报告生成**
   - JSON 格式
   - Markdown 格式
   - 文本格式

---

## 2. 爬虫设计

### 2.1 SimpleCrawler (静态爬虫)
```python
class SimpleCrawler:
    def __init__(self, max_pages=1000, depth=3, timeout=30):
        self.max_pages = max_pages
        self.depth = depth
        self.timeout = timeout
        self.visited_urls = set()

    async def fetch(self, url: str) -> dict:
        """获取网页内容"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = await aiohttp.get(url, headers=headers, timeout=self.timeout)
        return {
            'url': url,
            'status_code': response.status,
            'content': await response.text(),
            'headers': dict(response.headers)
        }

    def parse_html(self, html: str) -> dict:
        """解析 HTML 内容"""
        soup = BeautifulSoup(html, 'lxml')
        return {
            'title': soup.find('h1').get_text(strip=True),
            'h2_count': len(soup.find_all('h2')),
            'h3_count': len(soup.find_all('h3')),
            'table_count': len(soup.find_all('table')),
            'links': [a['href'] for a in soup.find_all('a', href=True)]
        }

    async def crawl(self, start_url: str) -> list:
        """爬取网站"""
        queue = [(start_url, 0)]  # (url, depth)
        results = []

        while queue and len(results) < self.max_pages:
            url, depth = queue.pop(0)

            if depth > self.depth or url in self.visited_urls:
                continue

            self.visited_urls.add(url)

            try:
                page_data = await self.fetch(url)
                parsed = self.parse_html(page_data['content'])
                results.append({**page_data, **parsed})

                # 添加链接到队列
                for link in parsed['links'][:10]:  # 限制每页最多 10 个链接
                    if link not in self.visited_urls:
                        queue.append((link, depth + 1))

            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")

        return results
```

### 2.2 WebCrawler (动态爬虫)
```python
class WebCrawler(SimpleCrawler):
    def __init__(self, headless=True, wait_for=None):
        super().__init__()
        self.headless = headless
        self.wait_for = wait_for  # 等待选择器，如 '.content-loaded'

    async def fetch(self, url: str) -> dict:
        """使用 Puppeteer 获取动态内容"""
        browser = await pypeteer.launch(headless=self.headless)
        page = await browser.newPage()

        try:
            await page.goto(url, waitUntil='networkidle2', timeout=self.timeout * 1000)

            # 等待特定元素
            if self.wait_for:
                await page.waitForSelector(self.wait_for, timeout=5000)

            content = await page.content()

            return {
                'url': url,
                'status_code': 200,
                'content': content
            }

        finally:
            await browser.close()

    def parse_html(self, html: str) -> dict:
        """解析 HTML，支持动态生成的内容"""
        soup = BeautifulSoup(html, 'lxml')
        return {
            'title': soup.find('h1').get_text(strip=True),
            'h2_count': len(soup.find_all('h2')),
            'h3_count': len(soup.find_all('h3')),
            'table_count': len(soup.find_all('table')),
            'meta_tags': {meta.get('name'): meta.get('content') for meta in soup.find_all('meta')},
            'data_attributes': self._extract_data_attributes(soup)
        }

    def _extract_data_attributes(self, soup) -> dict:
        """提取 data-* 属性"""
        data_attrs = {}
        for element in soup.find_all(attrs={'data-*': True}):
            for key, value in element.attrs.items():
                if key.startswith('data-'):
                    data_attrs[key] = value
        return data_attrs
```

---

## 3. AI 友好度评分算法

### 3.1 评分维度

#### 维度 1: 标题结构 (30 分)
```python
def evaluate_title_structure(soup) -> dict:
    score = 0
    details = {}

    # H1 唯一性 (10 分)
    h1_tags = soup.find_all('h1')
    if len(h1_tags) == 1:
        score += 10
        details['h1_unique'] = True
    else:
        details['h1_unique'] = False

    # H2 存在 (10 分)
    h2_tags = soup.find_all('h2')
    if len(h2_tags) > 0:
        score += 10
        details['h2_exists'] = True
        details['h2_count'] = len(h2_tags)
    else:
        details['h2_exists'] = False

    # H3 存在 (5 分)
    h3_tags = soup.find_all('h3')
    if len(h3_tags) > 0:
        score += 5
        details['h3_exists'] = True
    else:
        details['h3_exists'] = False

    # 层级连续性 (5 分)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    is_continuous = True
    for i in range(len(headings) - 1):
        current_level = int(headings[i].name[1])
        next_level = int(headings[i + 1].name[1])
        if next_level > current_level + 1:  # 不能跳跃
            is_continuous = False
            break

    if is_continuous:
        score += 5
        details['hierarchy_continuous'] = True
    else:
        details['hierarchy_continuous'] = False

    return {'score': score, 'max_score': 30, 'details': details}
```

#### 维度 2: 表格使用 (20 分)
```python
def evaluate_tables(soup) -> dict:
    score = 0
    details = {}

    tables = soup.find_all('table')

    # 表格存在 (5 分)
    if len(tables) > 0:
        score += 5
        details['tables_exist'] = True
    else:
        details['tables_exist'] = False

    # 表头存在 (5 分)
    has_headers = any(
        table.find('thead') or table.find_all('th')
        for table in tables
    )
    if has_headers:
        score += 5
        details['has_headers'] = True
    else:
        details['has_headers'] = False

    # 表格结构 (5 分)
    well_structured_tables = 0
    for table in tables:
        if table.find('thead') and table.find('tbody'):
            well_structured_tables += 1

    if well_structured_tables / len(tables) > 0.7:  # 70% 的表格结构良好
        score += 5
        details['well_structured'] = True
    else:
        details['well_structured'] = False

    # 数据完整性 (5 分)
    tables_with_data = 0
    for table in tables:
        tbody = table.find('tbody')
        if tbody and len(tbody.find_all('tr')) > 1:
            tables_with_data += 1

    if tables_with_data / len(tables) > 0.5:
        score += 5
        details['data_complete'] = True
    else:
        details['data_complete'] = False

    return {'score': score, 'max_score': 20, 'details': details}
```

#### 维度 3: 数据完整性 (25 分)
```python
def evaluate_data_completeness(soup) -> dict:
    score = 0
    details = {}

    # data-* 属性 (10 分)
    elements_with_data_attrs = soup.find_all(attrs={'data-*': True})
    data_attr_count = len(elements_with_data_attrs)
    score += min(data_attr_count, 10)  # 最多 10 分
    details['data_attrs_count'] = data_attr_count

    # Meta 标签 (8 分)
    meta_tags = soup.find_all('meta')
    essential_metas = ['description', 'keywords', 'author', 'og:title', 'og:description']
    essential_count = sum(
        1 for meta in meta_tags
        if meta.get('name') in essential_metas
    )
    score += (essential_count / len(essential_metas)) * 8
    details['meta_tags'] = essential_count

    # 链接完整性 (4 分)
    links = soup.find_all('a', href=True)
    links_with_title = sum(1 for link in links if link.get('title'))
    score += (links_with_title / len(links)) * 4
    details['links_with_title_ratio'] = f"{links_with_title}/{len(links)}"

    # 图片 alt 属性 (3 分)
    images = soup.find_all('img')
    images_with_alt = sum(1 for img in images if img.get('alt'))
    score += (images_with_alt / len(images)) * 3
    details['images_with_alt_ratio'] = f"{images_with_alt}/{len(images)}"

    return {'score': score, 'max_score': 25, 'details': details}
```

#### 维度 4: 内容清晰度 (15 分)
```python
def evaluate_content_clarity(soup) -> dict:
    score = 0
    details = {}

    # 段落结构 (5 分)
    paragraphs = soup.find_all('p')
    if len(paragraphs) > 0:
        score += 5
        details['paragraphs'] = len(paragraphs)

    # 列表使用 (5 分)
    lists = soup.find_all(['ul', 'ol'])
    if len(lists) > 0:
        score += 5
        details['lists'] = len(lists)

    # 代码块 (5 分)
    code_blocks = soup.find_all(['pre', 'code'])
    if len(code_blocks) > 0:
        score += 5
        details['code_blocks'] = len(code_blocks)

    return {'score': score, 'max_score': 15, 'details': details}
```

#### 维度 5: 格式兼容性 (10 分)
```python
def evaluate_format_compatibility(soup) -> dict:
    score = 0
    details = {}

    # 语义化标签 (5 分)
    semantic_tags = ['article', 'section', 'nav', 'aside', 'header', 'footer', 'main']
    found_semantic = sum(1 for tag in semantic_tags if soup.find(tag))
    score += min(found_semantic, 5)
    details['semantic_tags'] = found_semantic

    # Markdown 友好 (5 分)
    # 检查是否易于转换为 Markdown
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    tables = soup.find_all('table')
    lists = soup.find_all(['ul', 'ol'])
    code = soup.find_all(['pre', 'code'])

    if len(headings) > 0 and (len(tables) > 0 or len(lists) > 0):
        score += 5
        details['markdown_friendly'] = True
    else:
        details['markdown_friendly'] = False

    return {'score': score, 'max_score': 10, 'details': details}
```

### 3.2 总分计算
```python
def calculate_ai_friendliness_score(soup) -> dict:
    """计算 AI 友好度总分"""
    evaluations = {
        'title_structure': evaluate_title_structure(soup),
        'tables_used': evaluate_tables(soup),
        'data_completeness': evaluate_data_completeness(soup),
        'content_clarity': evaluate_content_clarity(soup),
        'format_compatibility': evaluate_format_compatibility(soup)
    }

    total_score = sum(e['score'] for e in evaluations.values())
    max_score = sum(e['max_score'] for e in evaluations.values())

    # 等级划分
    percentage = (total_score / max_score) * 100
    if percentage >= 90:
        grade = 'A'
    elif percentage >= 80:
        grade = 'B'
    elif percentage >= 70:
        grade = 'C'
    elif percentage >= 60:
        grade = 'D'
    else:
        grade = 'E'

    return {
        'total_score': total_score,
        'max_score': max_score,
        'percentage': percentage,
        'grade': grade,
        'evaluations': evaluations,
        'suggestions': generate_suggestions(evaluations)
    }
```

### 3.3 优化建议生成
```python
def generate_suggestions(evaluations: dict) -> list:
    """生成优化建议"""
    suggestions = []

    # 标题结构建议
    if not evaluations['title_structure']['details']['h1_unique']:
        suggestions.append({
            'priority': 'high',
            'category': '标题结构',
            'message': '页面应该只有一个 H1 标题'
        })

    if not evaluations['title_structure']['details']['h2_exists']:
        suggestions.append({
            'priority': 'medium',
            'category': '标题结构',
            'message': '建议添加 H2 标题来组织内容'
        })

    # 表格使用建议
    if not evaluations['tables_used']['details']['tables_exist']:
        suggestions.append({
            'priority': 'high',
            'category': '数据展示',
            'message': '使用表格来展示结构化数据，AI 引擎更容易提取'
        })

    # 数据完整性建议
    if evaluations['data_completeness']['details']['data_attrs_count'] < 5:
        suggestions.append({
            'priority': 'medium',
            'category': '数据完整性',
            'message': '添加更多 data-* 属性来标注关键信息'
        })

    # 格式兼容性建议
    if not evaluations['format_compatibility']['details']['markdown_friendly']:
        suggestions.append({
            'priority': 'low',
            'category': '格式优化',
            'message': '使用语义化 HTML 标签，提高 Markdown 转换质量'
        })

    return suggestions
```

---

## 4. 报告生成

### 4.1 JSON 格式
```python
def generate_json_report(scan_result: dict) -> str:
    """生成 JSON 格式报告"""
    report = {
        'scan_id': scan_result['scan_id'],
        'url': scan_result['url'],
        'timestamp': scan_result['timestamp'],
        'score': scan_result['total_score'],
        'grade': scan_result['grade'],
        'pages': scan_result['pages']
    }
    return json.dumps(report, ensure_ascii=False, indent=2)
```

### 4.2 Markdown 格式
```python
def generate_markdown_report(scan_result: dict) -> str:
    """生成 Markdown 格式报告"""
    md = f"""# AI 友好度扫描报告

**扫描 ID**: {scan_result['scan_id']}
**URL**: {scan_result['url']}
**时间**: {scan_result['timestamp']}

## 总分

**得分**: {scan_result['total_score']}/{scan_result['max_score']}
**百分比**: {scan_result['percentage']}%
**等级**: {scan_result['grade']}

## 分项评分

| 维度 | 得分 | 满分 | 详情 |
|------|------|------|------|
| 标题结构 | {scan_result['evaluations']['title_structure']['score']} | {scan_result['evaluations']['title_structure']['max_score']} | H1:{scan_result['evaluations']['title_structure']['details'].get('h1_unique', 'N/A')}, H2:{scan_result['evaluations']['title_structure']['details'].get('h2_count', 0)} |
| 表格使用 | {scan_result['evaluations']['tables_used']['score']} | {scan_result['evaluations']['tables_used']['max_score']} | 表格:{scan_result['evaluations']['tables_used']['details'].get('tables_exist', 'N/A')} |
| 数据完整性 | {scan_result['evaluations']['data_completeness']['score']} | {scan_result['evaluations']['data_completeness']['max_score']} | Meta:{scan_result['evaluations']['data_completeness']['details'].get('meta_tags', 0)} |
| 内容清晰度 | {scan_result['evaluations']['content_clarity']['score']} | {scan_result['evaluations']['content_clarity']['max_score']} | 段落:{scan_result['evaluations']['content_clarity']['details'].get('paragraphs', 0)} |
| 格式兼容性 | {scan_result['evaluations']['format_compatibility']['score']} | {scan_result['evaluations']['format_compatibility']['max_score']} | 语义化:{scan_result['evaluations']['format_compatibility']['details'].get('semantic_tags', 0)} |

## 优化建议

{chr(10).join(f"- [{s['priority']}] {s['message']}" for s in scan_result['suggestions'])}

## 扫描页面

{chr(10).join(f"### [{p['score']}分] {p['url']}" for p in scan_result['pages'])}
"""
    return md
```

---

## 5. CLI 工具

### 5.1 命令定义
```python
@click.group()
def cli():
    """GEO 内容扫描器"""
    pass

@cli.command()
@click.argument('url')
@click.option('--output', '-o', default='report.json', help='输出文件')
@click.option('--format', '-f', type=click.Choice(['json', 'markdown', 'text']), default='json')
@click.option('--max-pages', default=1000, help='最大扫描页面数')
@click.option('--depth', default=3, help='扫描深度')
@click.option('--wait-for', help='等待选择器 (如 .content-loaded)')
def scan(url, output, format, max_pages, depth, wait_for):
    """扫描单个 URL"""
    click.echo(f"开始扫描: {url}")

    # 选择爬虫类型
    if wait_for:
        crawler = WebCrawler(wait_for=wait_for)
    else:
        crawler = SimpleCrawler(max_pages=max_pages, depth=depth)

    # 执行扫描
    result = asyncio.run(crawler.crawl(url))

    # 计算评分
    for page in result:
        soup = BeautifulSoup(page['content'], 'lxml')
        page['ai_score'] = calculate_ai_friendliness_score(soup)

    # 生成报告
    if format == 'json':
        report = generate_json_report(result)
    elif format == 'markdown':
        report = generate_markdown_report(result)
    else:
        report = generate_text_report(result)

    # 保存报告
    with open(output, 'w', encoding='utf-8') as f:
        f.write(report)

    click.echo(f"报告已保存: {output}")

@cli.command()
@click.argument('urls_file', type=click.File('r'))
@click.option('--output', '-o', default='reports/')
def batch(urls_file, output):
    """批量扫描"""
    click.echo(f"批量扫描模式")

    urls = [line.strip() for line in urls_file if line.strip()]
    results = []

    for i, url in enumerate(urls):
        click.echo(f"扫描 {i + 1}/{len(urls)}: {url}")
        crawler = SimpleCrawler()
        result = asyncio.run(crawler.crawl(url))
        results.append(result)

    # 生成汇总报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output}/batch_report_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    click.echo(f"批量扫描完成: {output_file}")
```

---

## 6. 性能优化

### 6.1 并发控制
```python
# 使用 asyncio 实现并发请求
async def batch_fetch(urls: list, concurrency: int = 10) -> list:
    """并发获取多个 URL"""
    semaphore = asyncio.Semaphore(concurrency)

    async def fetch_with_semaphore(url):
        async with semaphore:
            return await fetch(url)

    tasks = [fetch_with_semaphore(url) for url in urls]
    results = await asyncio.gather(*tasks)

    return results
```

### 6.2 缓存机制
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def parse_html_cached(html: str) -> dict:
    """缓存解析结果"""
    return parse_html(html)
```

---

## 7. 错误处理

### 7.1 错误类型
```python
class ScanError(Exception):
    """扫描错误基类"""
    pass

class TimeoutError(ScanError):
    """超时错误"""
    pass

class ParseError(ScanError):
    """解析错误"""
    pass

class RateLimitError(ScanError):
    """限流错误"""
    pass

async def safe_scan(url: str) -> dict:
    """带错误处理的扫描"""
    try:
        return await crawler.crawl(url)
    except asyncio.TimeoutError:
        logger.error(f"Timeout: {url}")
        raise TimeoutError(f"扫描超时: {url}")
    except Exception as e:
        logger.error(f"Error: {url} - {e}")
        raise ScanError(f"扫描失败: {e}")
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-17
**下次审查**: 2026-04-17
