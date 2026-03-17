import { Router } from 'express';
import authRoutes from './authRoutes';
import scanRoutes from './scanRoutes';
import healthRoutes from './healthRoutes';

const router = Router();

// 健康检查
router.use('/health', healthRoutes);

// API路由
router.use('/auth', authRoutes);
router.use('/scans', scanRoutes);

export default router;
