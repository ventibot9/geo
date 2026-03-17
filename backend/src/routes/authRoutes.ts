import { Router } from 'express';
import { authController } from '../controllers/authController';
import { authenticate } from '../middleware/auth';

const router = Router();

// 公开路由
router.post('/register', authController.register);
router.post('/login', authController.login);

// 认证路由
router.get('/profile', authenticate, authController.getProfile);

export default router;
