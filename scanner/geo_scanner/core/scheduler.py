"""
扫描任务调度器
支持定时任务和批量调度
"""

import asyncio
import logging
from typing import List, Callable, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ScanTask:
    """扫描任务"""
    url: str
    priority: int = 0
    callback: Callable[[Dict[str, Any]], None] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskScheduler:
    """任务调度器"""

    def __init__(self, max_concurrent: int = 3):
        """
        初始化调度器

        Args:
            max_concurrent: 最大并发数
        """
        self.max_concurrent = max_concurrent
        self.task_queue = []
        self.running_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0

    def add_task(self, task: ScanTask):
        """
        添加任务

        Args:
            task: 扫描任务
        """
        self.task_queue.append(task)
        # 按优先级排序
        self.task_queue.sort(key=lambda t: -t.priority)
        logger.info(f"添加任务: {task.url} (优先级: {task.priority})")

    def add_tasks(self, tasks: List[ScanTask]):
        """
        批量添加任务

        Args:
            tasks: 扫描任务列表
        """
        for task in tasks:
            self.add_task(task)

    async def run_all(self, scan_func: Callable[[str], Dict[str, Any]]):
        """
        运行所有任务

        Args:
            scan_func: 扫描函数，接收URL，返回结果
        """
        logger.info(f"开始执行 {len(self.task_queue)} 个任务，最大并发: {self.max_concurrent}")

        workers = []
        for _ in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker(scan_func))
            workers.append(worker)

        await asyncio.gather(*workers, return_exceptions=True)

        logger.info(
            f"任务执行完成: 成功 {self.completed_tasks}, 失败 {self.failed_tasks}"
        )

    async def _worker(self, scan_func: Callable[[str], Dict[str, Any]]):
        """工作协程"""
        while self.task_queue:
            task = self.task_queue.pop(0)
            self.running_tasks += 1

            try:
                logger.info(f"正在扫描: {task.url}")
                result = await self._execute_scan(scan_func, task.url)

                if result.get('error'):
                    self.failed_tasks += 1
                    logger.error(f"扫描失败: {task.url}, 错误: {result['error']}")
                else:
                    self.completed_tasks += 1
                    logger.info(f"扫描完成: {task.url}, 得分: {result['scores']['total']}")

                    # 调用回调
                    if task.callback:
                        task.callback(result)

            except Exception as e:
                self.failed_tasks += 1
                logger.error(f"任务执行异常: {task.url}, {e}")
            finally:
                self.running_tasks -= 1

    async def _execute_scan(
        self,
        scan_func: Callable[[str], Dict[str, Any]],
        url: str
    ) -> Dict[str, Any]:
        """执行扫描（异步适配）"""
        # 如果是协程函数
        if asyncio.iscoroutinefunction(scan_func):
            return await scan_func(url)
        else:
            # 同步函数在线程池中执行
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, scan_func, url)

    def get_status(self) -> Dict[str, Any]:
        """获取调度状态"""
        return {
            'total_tasks': len(self.task_queue) + self.running_tasks + self.completed_tasks + self.failed_tasks,
            'pending_tasks': len(self.task_queue),
            'running_tasks': self.running_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'max_concurrent': self.max_concurrent,
        }


class PeriodicScheduler:
    """周期性调度器"""

    def __init__(self, interval_minutes: int = 60):
        """
        初始化周期调度器

        Args:
            interval_minutes: 执行间隔(分钟)
        """
        self.interval = timedelta(minutes=interval_minutes)
        self.last_run = None
        self.scan_urls = []

    def add_url(self, url: str):
        """添加要定期扫描的URL"""
        if url not in self.scan_urls:
            self.scan_urls.append(url)
            logger.info(f"添加定期扫描URL: {url}")

    def should_run(self) -> bool:
        """检查是否应该执行"""
        if self.last_run is None:
            return True

        return datetime.now() - self.last_run >= self.interval

    async def run_if_due(self, scan_func: Callable):
        """如果到了执行时间则运行"""
        if not self.should_run():
            return False

        logger.info(f"执行定期扫描任务: {len(self.scan_urls)} 个URL")

        scheduler = TaskScheduler(max_concurrent=3)
        for url in self.scan_urls:
            scheduler.add_task(ScanTask(url))

        await scheduler.run_all(scan_func)
        self.last_run = datetime.now()
        return True

    def reset(self):
        """重置定时器"""
        self.last_run = None
