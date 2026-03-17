"""
基于Puppeteer的网站爬虫模块
支持JS渲染页面抓取
"""

import asyncio
from typing import Dict, Any, Optional
from pyppeteer import launch
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class WebCrawler:
    """网站爬虫类，支持JS渲染"""

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        初始化爬虫

        Args:
            headless: 是否无头模式
            timeout: 超时时间(毫秒)
        """
        self.headless = headless
        self.timeout = timeout
        self.browser = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.browser = await launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.browser:
            await self.browser.close()

    async def fetch_page(
        self,
        url: str,
        wait_for: Optional[str] = None,
        wait_timeout: int = 5000
    ) -> Dict[str, Any]:
        """
        抓取页面内容

        Args:
            url: 目标URL
            wait_for: 等待的选择器
            wait_timeout: 等待超时(毫秒)

        Returns:
            包含页面信息的字典
        """
        if not self.browser:
            raise RuntimeError("Crawler not initialized. Use async with.")

        page = await self.browser.newPage()

        try:
            # 设置视口
            await page.setViewport({'width': 1920, 'height': 1080})

            # 设置User-Agent
            await page.setUserAgent(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )

            logger.info(f"正在访问: {url}")

            # 访问页面
            response = await page.goto(
                url,
                {'waitUntil': 'networkidle0', 'timeout': self.timeout}
            )

            # 等待特定元素
            if wait_for:
                try:
                    await page.waitForSelector(wait_for, {'timeout': wait_timeout})
                except Exception as e:
                    logger.warning(f"等待选择器失败: {wait_for}, {e}")

            # 获取HTML内容
            html = await page.content()
            soup = BeautifulSoup(html, 'lxml')

            # 提取页面信息
            result = {
                'url': url,
                'status': response.status if response else None,
                'title': soup.title.string if soup.title else '',
                'html': html,
                'soup': soup,
                'text': soup.get_text(separator='\n', strip=True),
                'meta': self._extract_meta(soup),
            }

            logger.info(f"抓取完成: {url}, 状态码: {result['status']}")
            return result

        except Exception as e:
            logger.error(f"抓取失败: {url}, 错误: {e}")
            return {
                'url': url,
                'status': None,
                'title': '',
                'html': '',
                'soup': BeautifulSoup('', 'lxml'),
                'text': '',
                'meta': {},
                'error': str(e)
            }
        finally:
            await page.close()

    def _extract_meta(self, soup: BeautifulSoup) -> Dict[str, str]:
        """提取页面meta信息"""
        meta = {}

        # 基础meta标签
        for tag in soup.find_all('meta'):
            if tag.get('name'):
                meta[tag['name']] = tag.get('content', '')
            elif tag.get('property'):
                meta[tag['property']] = tag.get('content', '')

        # Open Graph
        og = {
            'title': meta.get('og:title', ''),
            'description': meta.get('og:description', ''),
            'type': meta.get('og:type', ''),
            'image': meta.get('og:image', ''),
        }
        return og


class SimpleCrawler:
    """简单爬虫，不需要JS渲染"""

    @staticmethod
    def fetch(url: str) -> Dict[str, Any]:
        """
        抓取页面（无JS渲染）

        Args:
            url: 目标URL

        Returns:
            包含页面信息的字典
        """
        import requests

        try:
            headers = {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                )
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            return {
                'url': url,
                'status': response.status_code,
                'title': soup.title.string if soup.title else '',
                'html': response.text,
                'soup': soup,
                'text': soup.get_text(separator='\n', strip=True),
                'meta': {},
            }

        except Exception as e:
            logger.error(f"抓取失败: {url}, 错误: {e}")
            return {
                'url': url,
                'status': None,
                'title': '',
                'html': '',
                'soup': BeautifulSoup('', 'lxml'),
                'text': '',
                'meta': {},
                'error': str(e)
            }
