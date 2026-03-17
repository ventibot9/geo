import Bull, { Job, JobOptions } from 'bull';
import redis from '../config/redis';

export interface ScanJobData {
  enterpriseId: string;
  siteConfigId: string;
  url: string;
}

export interface RewriteJobData {
  contentPageId: string;
  model?: string;
}

export interface MonitorJobData {
  enterpriseId: string;
  keywords: string[];
}

class QueueService {
  private scanQueue: Bull.Queue<ScanJobData>;
  private rewriteQueue: Bull.Queue<RewriteJobData>;
  private monitorQueue: Bull.Queue<MonitorJobData>;

  constructor() {
    const queueConfig: JobOptions = {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000,
      },
      removeOnComplete: 100,
      removeOnFail: 500,
    };

    this.scanQueue = new Bull<ScanJobData>('scan-tasks', {
      connection: redis,
      defaultJobOptions: queueConfig,
    });

    this.rewriteQueue = new Bull<RewriteJobData>('rewrite-tasks', {
      connection: redis,
      defaultJobOptions: queueConfig,
    });

    this.monitorQueue = new Bull<MonitorJobData>('monitor-tasks', {
      connection: redis,
      defaultJobOptions: queueConfig,
    });

    this.setupEventListeners();
  }

  private setupEventListeners() {
    // 扫描队列事件
    this.scanQueue.on('completed', (job: Job<ScanJobData>, result) => {
      console.log(`扫描任务 ${job.id} 完成:`, result);
    });

    this.scanQueue.on('failed', (job: Job<ScanJobData>, err: Error) => {
      console.error(`扫描任务 ${job.id} 失败:`, err.message);
    });

    // 改写队列事件
    this.rewriteQueue.on('completed', (job: Job<RewriteJobData>, result) => {
      console.log(`改写任务 ${job.id} 完成:`, result);
    });

    this.rewriteQueue.on('failed', (job: Job<RewriteJobData>, err: Error) => {
      console.error(`改写任务 ${job.id} 失败:`, err.message);
    });

    // 监控队列事件
    this.monitorQueue.on('completed', (job: Job<MonitorJobData>, result) => {
      console.log(`监控任务 ${job.id} 完成:`, result);
    });

    this.monitorQueue.on('failed', (job: Job<MonitorJobData>, err: Error) => {
      console.error(`监控任务 ${job.id} 失败:`, err.message);
    });
  }

  // 添加扫描任务
  async addScanJob(data: ScanJobData, options?: JobOptions) {
    return await this.scanQueue.add(data, options);
  }

  // 添加改写任务
  async addRewriteJob(data: RewriteJobData, options?: JobOptions) {
    return await this.rewriteQueue.add(data, options);
  }

  // 添加监控任务
  async addMonitorJob(data: MonitorJobData, options?: JobOptions) {
    return await this.monitorQueue.add(data, {
      ...options,
      repeat: { every: 60 * 60 * 1000 }, // 每小时执行一次
    });
  }

  // 获取队列状态
  async getQueueStats() {
    const [scan, rewrite, monitor] = await Promise.all([
      this.scanQueue.getJobCounts(),
      this.rewriteQueue.getJobCounts(),
      this.monitorQueue.getJobCounts(),
    ]);

    return {
      scan,
      rewrite,
      monitor,
    };
  }

  // 处理任务（需要在worker中实现）
  processScanJob(processor: (job: Job<ScanJobData>) => Promise<any>) {
    this.scanQueue.process(processor);
  }

  processRewriteJob(processor: (job: Job<RewriteJobData>) => Promise<any>) {
    this.rewriteQueue.process(processor);
  }

  processMonitorJob(processor: (job: Job<MonitorJobData>) => Promise<any>) {
    this.monitorQueue.process(processor);
  }

  // 关闭队列
  async close() {
    await Promise.all([
      this.scanQueue.close(),
      this.rewriteQueue.close(),
      this.monitorQueue.close(),
    ]);
  }
}

export const queueService = new QueueService();
