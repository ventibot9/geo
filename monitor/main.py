"""
GEO平台引用监控服务 - 主程序
"""

import sys
import signal
import logging
from pathlib import Path

from scheduler.tasks import MonitorScheduler
from reporter.generator import ReportGenerator
from database import get_db
from utils.keywords import KeywordManager
from config import COMPANY_KEYWORDS, SCHEDULE_CONFIG


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MonitorService:
    """监控服务主类"""

    def __init__(self):
        self.scheduler = None
        self.running = False

    def initialize(self):
        """初始化服务"""
        logger.info("Initializing GEO Monitor Service...")

        # 初始化数据库
        db = get_db()
        logger.info("Database initialized")

        # 初始化关键词管理器
        km = KeywordManager(COMPANY_KEYWORDS)
        logger.info(f"Keywords loaded: {km.export_summary()}")

        # 初始化调度器
        self.scheduler = MonitorScheduler()
        logger.info("Scheduler initialized")

    def start(self):
        """启动服务"""
        if self.running:
            logger.warning("Service already running")
            return

        logger.info("Starting GEO Monitor Service...")

        try:
            # 启动调度器
            self.scheduler.start()

            self.running = True
            logger.info("Service started successfully")
            logger.info(f"Monitor interval: {SCHEDULE_CONFIG['monitor_interval']}")
            logger.info(f"Report interval: {SCHEDULE_CONFIG['report_interval']}")

            # 注册信号处理
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            logger.info("Press Ctrl+C to stop")

        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            self.stop()
            sys.exit(1)

    def stop(self):
        """停止服务"""
        if not self.running:
            return

        logger.info("Stopping GEO Monitor Service...")

        if self.scheduler:
            self.scheduler.stop()

        self.running = False
        logger.info("Service stopped")

    def run_once(self):
        """运行一次监控（不启动调度器）"""
        logger.info("Running one-time monitor task...")

        self.initialize()

        try:
            # 手动触发一次监控
            self.scheduler.trigger_now()
            logger.info("One-time monitor completed")

            # 生成报告
            generator = ReportGenerator()
            json_file, text_file = generator.generate_full_report()
            logger.info(f"Report generated: {json_file}")

        except Exception as e:
            logger.error(f"One-time monitor failed: {e}")
            raise

    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="GEO平台引用监控服务"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="运行一次监控后退出"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成当前报告"
    )

    args = parser.parse_args()

    service = MonitorService()

    try:
        if args.report:
            # 只生成报告
            service.initialize()
            generator = ReportGenerator()
            json_file, text_file = generator.generate_full_report()
            print(f"Report generated:")
            print(f"  JSON: {json_file}")
            print(f"  Text: {text_file}")

        elif args.once:
            # 运行一次
            service.run_once()

        else:
            # 启动服务
            service.initialize()
            service.start()

            # 保持运行
            import time
            while service.running:
                time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        service.stop()
    except Exception as e:
        logger.error(f"Service error: {e}")
        service.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
