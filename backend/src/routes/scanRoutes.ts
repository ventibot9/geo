import { Router } from 'express';
import { scanController } from '../controllers/scanController';
import { authenticate, authorize } from '../middleware/auth';

const router = Router();

// 所有扫描路由都需要认证
router.use(authenticate);

router.post('/create', scanController.createScanTask);
router.get('/list', scanController.listScanTasks);
router.get('/:id', scanController.getScanTask);
router.delete('/:id', authorize('admin'), scanController.deleteScanTask);

export default router;
