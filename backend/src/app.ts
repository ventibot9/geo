import express from 'express';
import cors from 'cors';
import { config } from './config';
import routes from './routes';
import { errorHandler, notFoundHandler } from './middleware/error';

const app = express();

// 中间件
app.use(cors({
  origin: config.cors.origin,
  credentials: true,
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 请求日志（开发环境）
if (config.nodeEnv === 'development') {
  app.use((req, res, next) => {
    console.log(`${req.method} ${req.path}`);
    next();
  });
}

// 路由
app.use('/api', routes);

// 根路径
app.get('/', (req, res) => {
  res.json({
    name: 'GEO Platform API',
    version: '1.0.0',
    status: 'running',
  });
});

// 错误处理
app.use(notFoundHandler);
app.use(errorHandler);

export default app;
