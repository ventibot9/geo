import prisma from '../config/database';
import { queueService, ScanJobData } from './queueService';

export interface CreateScanData {
  enterpriseId: string;
  siteConfigId: string;
}

export const scanService = {
  async createScanTask(data: CreateScanData) {
    const { enterpriseId, siteConfigId } = data;

    // 获取站点配置
    const siteConfig = await prisma.siteConfig.findFirst({
      where: {
        id: siteConfigId,
        enterpriseId,
        active: true,
      },
    });

    if (!siteConfig) {
      throw new Error('站点配置不存在或未激活');
    }

    // 创建扫描任务
    const scanTask = await prisma.scanTask.create({
      data: {
        enterpriseId,
        siteConfigId,
        status: 'pending',
        startedAt: new Date(),
      },
    });

    // 添加到队列
    const jobData: ScanJobData = {
      enterpriseId,
      siteConfigId,
      url: siteConfig.url,
    };

    await queueService.addScanJob(jobData, {
      jobId: scanTask.id,
      priority: 10,
    });

    return scanTask;
  },

  async getScanTaskById(taskId: string, enterpriseId: string) {
    const scanTask = await prisma.scanTask.findFirst({
      where: {
        id: taskId,
        enterpriseId,
      },
      include: {
        contentPages: {
          select: {
            id: true,
            url: true,
            title: true,
            aiScore: true,
            wordCount: true,
            lastScannedAt: true,
          },
          orderBy: {
            aiScore: 'desc',
          },
          take: 10,
        },
      },
    });

    if (!scanTask) {
      throw new Error('扫描任务不存在');
    }

    return scanTask;
  },

  async listScanTasks(enterpriseId: string, page = 1, limit = 20) {
    const skip = (page - 1) * limit;

    const [tasks, total] = await Promise.all([
      prisma.scanTask.findMany({
        where: { enterpriseId },
        include: {
          siteConfig: {
            select: {
              url: true,
            },
          },
        },
        orderBy: {
          createdAt: 'desc',
        },
        skip,
        take: limit,
      }),
      prisma.scanTask.count({
        where: { enterpriseId },
      }),
    ]);

    return {
      tasks,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    };
  },

  async updateScanTaskStatus(
    taskId: string,
    status: string,
    data?: {
      totalPages?: number;
      processedPages?: number;
      avgAiScore?: number;
      maxAiScore?: number;
      minAiScore?: number;
      errorMessage?: string;
      completedAt?: Date;
    }
  ) {
    return await prisma.scanTask.update({
      where: { id: taskId },
      data: {
        status,
        ...data,
        updatedAt: new Date(),
      },
    });
  },

  async deleteScanTask(taskId: string, enterpriseId: string) {
    // 先验证所有权
    const scanTask = await prisma.scanTask.findFirst({
      where: {
        id: taskId,
        enterpriseId,
      },
    });

    if (!scanTask) {
      throw new Error('扫描任务不存在或无权删除');
    }

    // 删除任务（级联删除相关内容页面）
    await prisma.scanTask.delete({
      where: { id: taskId },
    });

    return { message: '删除成功' };
  },
};
