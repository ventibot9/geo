import { Response } from 'express';
import { scanService } from '../services/scanService';
import { AuthRequest } from '../middleware/auth';

export const scanController = {
  async createScanTask(req: AuthRequest, res: Response) {
    try {
      if (!req.user) {
        return res.status(401).json({ error: '未认证' });
      }

      const { siteConfigId } = req.body;

      if (!siteConfigId) {
        return res.status(400).json({ error: '请提供站点配置ID' });
      }

      const scanTask = await scanService.createScanTask({
        enterpriseId: req.user.enterpriseId,
        siteConfigId,
      });

      res.status(201).json({
        message: '扫描任务已创建',
        scanTask,
      });
    } catch (error: any) {
      console.error('创建扫描任务错误:', error);
      res.status(400).json({ error: error.message || '创建失败' });
    }
  },

  async getScanTask(req: AuthRequest, res: Response) {
    try {
      if (!req.user) {
        return res.status(401).json({ error: '未认证' });
      }

      const { id } = req.params;

      const scanTask = await scanService.getScanTaskById(
        id,
        req.user.enterpriseId
      );

      res.json(scanTask);
    } catch (error: any) {
      console.error('获取扫描任务错误:', error);
      res.status(404).json({ error: error.message || '任务不存在' });
    }
  },

  async listScanTasks(req: AuthRequest, res: Response) {
    try {
      if (!req.user) {
        return res.status(401).json({ error: '未认证' });
      }

      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 20;

      const result = await scanService.listScanTasks(
        req.user.enterpriseId,
        page,
        limit
      );

      res.json(result);
    } catch (error: any) {
      console.error('列出扫描任务错误:', error);
      res.status(500).json({ error: error.message || '获取列表失败' });
    }
  },

  async deleteScanTask(req: AuthRequest, res: Response) {
    try {
      if (!req.user) {
        return res.status(401).json({ error: '未认证' });
      }

      const { id } = req.params;

      const result = await scanService.deleteScanTask(
        id,
        req.user.enterpriseId
      );

      res.json(result);
    } catch (error: any) {
      console.error('删除扫描任务错误:', error);
      res.status(404).json({ error: error.message || '删除失败' });
    }
  },
};
