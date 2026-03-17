import { Request, Response } from 'express';
import prisma from '../config/database';
import redis from '../config/redis';
import { queueService } from '../services/queueService';

export const healthController = {
  async check(req: Request, res: Response) {
    try {
      // 检查数据库连接
      await prisma.$queryRaw`SELECT 1`;
      const dbStatus = 'healthy';

      // 检查Redis连接
      const redisStatus = redis.status === 'ready' ? 'healthy' : 'unhealthy';

      // 获取队列状态
      const queueStats = await queueService.getQueueStats();

      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: {
          database: dbStatus,
          redis: redisStatus,
          queues: queueStats,
        },
      });
    } catch (error: any) {
      console.error('健康检查错误:', error);
      res.status(503).json({
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: error.message,
      });
    }
  },
};
