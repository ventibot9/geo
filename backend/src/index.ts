import { config } from './config';
import app from './app';
import { queueService } from './services/queueService';

const startServer = async () => {
  try {
    // 启动HTTP服务器
    const server = app.listen(config.port, () => {
      console.log(`
🚀 GEO Platform API Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment: ${config.nodeEnv}
Port: ${config.port}
API: http://localhost:${config.port}
Health: http://localhost:${config.port}/api/health
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      `);
    });

    // 优雅关闭
    const gracefulShutdown = async (signal: string) => {
      console.log(`\n收到 ${signal} 信号，开始优雅关闭...`);
      
      server.close(async () => {
        console.log('HTTP服务器已关闭');
        
        try {
          await queueService.close();
          console.log('队列服务已关闭');
          process.exit(0);
        } catch (error) {
          console.error('关闭队列服务时出错:', error);
          process.exit(1);
        }
      });

      // 强制关闭超时
      setTimeout(() => {
        console.error('强制关闭超时');
        process.exit(1);
      }, 10000);
    };

    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));

  } catch (error) {
    console.error('启动服务器时出错:', error);
    process.exit(1);
  }
};

startServer();
