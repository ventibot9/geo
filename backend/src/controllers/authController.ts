import { Request, Response } from 'express';
import { authService } from '../services/authService';
import { AuthRequest } from '../middleware/auth';

export const authController = {
  async register(req: Request, res: Response) {
    try {
      const { email, password, name, enterpriseName, domain } = req.body;

      // 基本验证
      if (!email || !password || !name || !enterpriseName || !domain) {
        return res.status(400).json({ error: '请填写所有必填字段' });
      }

      if (password.length < 6) {
        return res.status(400).json({ error: '密码至少6个字符' });
      }

      const result = await authService.register({
        email,
        password,
        name,
        enterpriseName,
        domain,
      });

      res.status(201).json({
        message: '注册成功',
        ...result,
      });
    } catch (error: any) {
      console.error('注册错误:', error);
      res.status(400).json({ error: error.message || '注册失败' });
    }
  },

  async login(req: Request, res: Response) {
    try {
      const { email, password } = req.body;

      if (!email || !password) {
        return res.status(400).json({ error: '请填写邮箱和密码' });
      }

      const result = await authService.login({ email, password });

      res.json({
        message: '登录成功',
        ...result,
      });
    } catch (error: any) {
      console.error('登录错误:', error);
      res.status(401).json({ error: error.message || '登录失败' });
    }
  },

  async getProfile(req: AuthRequest, res: Response) {
    try {
      if (!req.user) {
        return res.status(401).json({ error: '未认证' });
      }

      const user = await authService.getUserById(req.user.id);

      res.json(user);
    } catch (error: any) {
      console.error('获取用户信息错误:', error);
      res.status(404).json({ error: error.message || '用户不存在' });
    }
  },
};
