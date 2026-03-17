# GEO 平台 - 前端管理界面

基于 React 18 + TypeScript + Vite + Ant Design 构建的 GEO 平台前端管理系统。

## 技术栈

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Ant Design** - UI 组件库
- **React Router v6** - 路由管理
- **Zustand** - 状态管理
- **Axios** - HTTP 客户端
- **Day.js** - 日期处理

## 项目结构

```
frontend/
├── src/
│   ├── components/       # 公共组件
│   ├── layouts/          # 页面布局
│   │   ├── AuthLayout.tsx    # 认证页面布局（登录/注册）
│   │   └── MainLayout.tsx    # 主页面布局（带侧边栏）
│   ├── pages/            # 页面组件
│   │   ├── Login.tsx         # 登录页
│   │   ├── Register.tsx      # 注册页
│   │   ├── Dashboard.tsx     # 控制台
│   │   ├── ScanConfig.tsx    # 扫描配置页
│   │   ├── ScanResult.tsx    # 扫描结果页
│   │   ├── RewriteEditor.tsx # AI 改写编辑器
│   │   ├── CitationMonitor.tsx # 引用监控面板
│   │   └── Analytics.tsx     # 数据分析仪表盘
│   ├── router/           # 路由配置
│   │   └── index.tsx
│   ├── services/         # API 服务
│   │   └── api.ts            # Axios 封装
│   ├── stores/           # 状态管理
│   │   └── auth.ts           # 认证状态
│   ├── types/            # TypeScript 类型定义
│   │   └── index.ts
│   ├── utils/            # 工具函数
│   ├── App.tsx
│   ├── main.tsx          # 应用入口
│   └── index.css         # 全局样式
├── public/               # 静态资源
├── .env                  # 环境变量
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
└── package.json
```

## 核心功能

### 1. 认证系统
- 用户登录/注册
- Token 持久化存储
- 自动登录状态管理
- Token 过期自动登出

### 2. 路由结构
- `/login` - 登录页
- `/register` - 注册页
- `/dashboard` - 控制台
- `/scan-config` - 扫描配置
- `/scan-result` - 扫描结果
- `/rewrite-editor` - AI 改写编辑器
- `/citation-monitor` - 引用监控
- `/analytics` - 数据分析

### 3. 页面功能

#### Dashboard（控制台）
- 数据统计卡片
- 最近活动列表
- 实时数据刷新

#### ScanConfig（扫描配置）
- 创建扫描配置
- 编辑/删除配置
- 启用/暂停扫描
- 配置关键词

#### ScanResult（扫描结果）
- 查看扫描结果
- 可疑文章列表
- 相似度显示
- 详情查看

#### RewriteEditor（AI 改写编辑器）
- 原始文本输入
- AI 改写
- 相似度对比
- 结果复制

#### CitationMonitor（引用监控）
- 引用数据统计
- 趋势分析
- 搜索筛选
- 实时更新

#### Analytics（数据分析）
- 多维度统计
- 图表可视化
- 时间范围筛选
- 活动记录

## API 对接

后端 API 服务地址：`http://localhost:3001`

API 接口封装在 `src/services/api.ts` 中，包含：

- 请求拦截器（自动添加 Token）
- 响应拦截器（统一错误处理）
- Token 过期自动跳转登录

## 安装与运行

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```
访问：http://localhost:5173

### 生产构建
```bash
npm run build
```

### 预览构建
```bash
npm run preview
```

## 环境变量

创建 `.env` 文件配置：

```env
VITE_API_BASE_URL=http://localhost:3001
```

## 开发说明

### 添加新页面

1. 在 `src/pages/` 下创建页面组件
2. 在 `src/router/index.tsx` 中添加路由
3. 在 `src/layouts/MainLayout.tsx` 中添加菜单项

### 添加 API 接口

在 `src/services/api.ts` 中已有通用请求方法：

```typescript
api.get<T>(url, config)
api.post<T>(url, data, config)
api.put<T>(url, data, config)
api.delete<T>(url, config)
```

### 状态管理

使用 Zustand 进行状态管理，示例：

```typescript
import { create } from 'zustand';

export const useStore = create((set) => ({
  state: '',
  setState: (newState) => set({ state: newState }),
}));
```

## 浏览器兼容性

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## License

MIT
