# GEO Platform - Frontend 前端界面详细规范

## 文档信息
- **版本**: v1.0.0
- **模块**: Frontend Management UI
- **日期**: 2026-03-17
- **维护者**: GEO Platform Team

---

## 1. 模块职责

### 1.1 核心功能
1. **用户认证界面**
   - 登录页面
   - 注册页面
   - 密码重置 (未来功能)

2. **企业管理后台**
   - Dashboard (数据统计)
   - 网站扫描配置管理
   - 扫描结果查看
   - AI 改写编辑器
   - 引用监控面板
   - 数据分析仪表盘

3. **用户体验**
   - 响应式设计 (桌面 / 平板 / 手机)
   - 国际化支持 (中文 / 英文)
   - 主题切换 (亮色 / 暗色)

### 1.2 非职责
- 不直接调用 AI 模型 API (通过 Backend)
- 不直接进行网站爬取 (通过 Backend)
- 不存储敏感数据 (所有存储通过 Backend)

---

## 2. 页面设计

### 2.1 登录页面 (`/login`)

#### 组件结构
```tsx
<AuthLayout>
  <div className="login-container">
    <div className="login-box">
      <Logo />
      <h1>GEO Platform</h1>
      <p>生成式引擎优化平台</p>

      <LoginForm />
      <SocialLoginButtons />

      <div className="login-footer">
        <Link to="/register">没有账号？立即注册</Link>
        <Link to="/forgot-password">忘记密码？</Link>
      </div>
    </div>
  </div>
</AuthLayout>
```

#### 表单字段
- **邮箱**: email (必填，格式验证)
- **密码**: password (必填，最小 8 字符)
- **记住我**: checkbox (可选，存储到 LocalStorage)

#### 验证规则
```typescript
interface LoginForm {
  email: string;      // 必须是有效邮箱格式
  password: string;   // 最小 8 字符，必须包含字母和数字
}
```

#### 错误处理
- 空字段: 显示红色边框 + 错误提示
- 格式错误: 实时验证，显示错误信息
- 认证失败: 显示 "邮箱或密码错误" Toast
- 网络错误: 显示 "网络连接失败，请重试"

---

### 2.2 注册页面 (`/register`)

#### 组件结构
```tsx
<AuthLayout>
  <div className="register-container">
    <div className="register-box">
      <Logo />
      <h1>创建账号</h1>

      <RegisterForm />

      <div className="register-footer">
        <Link to="/login">已有账号？立即登录</Link>
      </div>
    </div>
  </div>
</AuthLayout>
```

#### 表单字段
- **邮箱**: email (必填，格式验证，唯一性检查)
- **密码**: password (必填，最小 8 字符)
- **确认密码**: confirmPassword (必填，必须与密码一致)
- **企业名称**: companyName (必填，最大 100 字符)
- **企业域名**: companyDomain (必填，URL 格式)

#### 验证规则
```typescript
interface RegisterForm {
  email: string;              // 必须是有效邮箱格式
  password: string;           // 最小 8 字符
  confirmPassword: string;    // 必须与 password 一致
  companyName: string;        // 最大 100 字符
  companyDomain: string;       // 必须是有效 URL
}
```

#### 注册流程
```
1. 用户填写表单
   ↓
2. 前端验证格式
   ↓
3. 提交到 Backend API
   ↓
4. 等待响应
   ↓
5a. 成功: 自动登录，跳转到 Dashboard
5b. 失败: 显示错误信息，保留表单数据
```

---

### 2.3 Dashboard (`/dashboard`)

#### 布局结构
```tsx
<MainLayout>
  <div className="dashboard">
    {/* 概览卡片 */}
    <div className="stats-cards">
      <StatsCard
        title="扫描任务"
        value={scanStats.total}
        icon={<ScanIcon />}
        trend={scanStats.trend}
      />
      <StatsCard
        title="AI 友好度"
        value={scanStats.avgScore}
        icon={<AIIcon />}
        trend={scanStats.scoreTrend}
      />
      <StatsCard
        title="引用次数"
        value={citationStats.total}
        icon={<CitationIcon />}
        trend={citationStats.trend}
      />
      <StatsCard
        title="改写次数"
        value={rewriteStats.total}
        icon={<RewriteIcon />}
        trend={rewriteStats.trend}
      />
    </div>

    {/* 图表区域 */}
    <div className="charts-container">
      <div className="chart-box">
        <h3>AI 友好度趋势 (7天)</h3>
        <LineChart data={aiScoreTrend} />
      </div>
      <div className="chart-box">
        <h3>引用引擎分布</h3>
        <PieChart data={engineDistribution} />
      </div>
    </div>

    {/* 最近活动 */}
    <div className="recent-activity">
      <h3>最近活动</h3>
      <ActivityList activities={recentActivities} />
    </div>
  </div>
</MainLayout>
```

#### 数据加载策略
```typescript
// 1. 页面加载时并行请求数据
useEffect(() => {
  Promise.all([
    fetchScanStats(),
    fetchCitationStats(),
    fetchRewriteStats(),
    fetchAiScoreTrend(),
    fetchEngineDistribution(),
    fetchRecentActivities()
  ]);
}, []);

// 2. 使用 React Query 缓存
const { data: scanStats } = useQuery('scan-stats', fetchScanStats, {
  staleTime: 5 * 60 * 1000,  // 5 分钟内不刷新
  cacheTime: 10 * 60 * 1000  // 10 分钟后过期
});
```

#### 刷新机制
- **自动刷新**: 每 5 分钟自动刷新数据
- **手动刷新**: 右上角刷新按钮
- **实时更新**: WebSocket 推送扫描任务进度

---

### 2.4 扫描配置页面 (`/scan-config`)

#### 组件结构
```tsx
<MainLayout>
  <div className="scan-config">
    <div className="page-header">
      <h1>网站扫描配置</h1>
      <Button type="primary" onClick={handleAddSite}>
        + 添加网站
      </Button>
    </div>

    {/* 网站列表 */}
    <div className="site-list">
      {sites.map(site => (
        <SiteCard
          key={site.id}
          site={site}
          onEdit={handleEditSite}
          onDelete={handleDeleteSite}
          onToggleSchedule={handleToggleSchedule}
          onRunScan={handleRunScan}
        />
      ))}
    </div>

    {/* 添加/编辑网站模态框 */}
    <SiteModal
      visible={modalVisible}
      site={editingSite}
      onSave={handleSaveSite}
      onCancel={handleCloseModal}
    />
  </div>
</MainLayout>
```

#### SiteCard 组件
```tsx
<div className="site-card">
  <div className="site-info">
    <h3>{site.name}</h3>
    <p>{site.url}</p>
    <Tag color={site.status === 'active' ? 'green' : 'gray'}>
      {site.status === 'active' ? '启用' : '禁用'}
    </Tag>
  </div>

  <div className="site-actions">
    <Button onClick={() => handleRunScan(site.id)}>
      立即扫描
    </Button>
    <Button onClick={() => handleToggleSchedule(site.id)}>
      {site.schedule_enabled ? '暂停计划' : '启用计划'}
    </Button>
    <Dropdown menu={menu}>
      <Menu.Item onClick={() => handleEditSite(site.id)}>
        编辑
      </Menu.Item>
      <Menu.Item onClick={() => handleDeleteSite(site.id)} danger>
        删除
      </Menu.Item>
    </Dropdown>
  </div>

  <div className="scan-schedule">
    <span>扫描计划: </span>
    <Tag>{site.schedule_cron}</Tag>
    <span>上次扫描: </span>
    <Time value={site.last_scan_at} />
  </div>
</div>
```

#### 扫描选项配置
```typescript
interface ScanOptions {
  // 基础选项
  max_pages: number;           // 最大扫描页面数 (默认 1000)
  depth: number;               // 扫描深度 (默认 3)
  follow_external_links: boolean;  // 是否跟踪外部链接 (默认 false)

  // 高级选项
  scan_images: boolean;        // 是否扫描图片
  scan_pdf: boolean;          // 是否扫描 PDF
  exclude_patterns: string[];  // 排除路径模式 (如 [/admin/, /api/])

  // 调度选项
  schedule_enabled: boolean;    // 是否启用定时扫描
  schedule_cron: string;     // CRON 表达式 (如 "0 9 * * *" 表示每天 9 点)
}
```

---

### 2.5 扫描结果页面 (`/scan-results`)

#### 组件结构
```tsx
<MainLayout>
  <div className="scan-results">
    <div className="page-header">
      <h1>扫描结果</h1>
      <div className="filters">
        <Select
          value={selectedSite}
          onChange={setSelectedSite}
          options={siteOptions}
          placeholder="选择网站"
        />
        <Select
          value={selectedStatus}
          onChange={setSelectedStatus}
          options={statusOptions}
          placeholder="状态筛选"
        />
        <RangePicker
          value={dateRange}
          onChange={setDateRange}
          placeholder="日期范围"
        />
      </div>
    </div>

    {/* 统计信息 */}
    <div className="stats-summary">
      <Statistic title="总扫描次数" value={totalScans} />
      <Statistic title="平均 AI 友好度" value={avgAiScore} suffix="分" />
      <Statistic title="平均页面数" value={avgPages} />
    </div>

    {/* 扫描任务列表 */}
    <Table
      columns={columns}
      dataSource={scanTasks}
      rowKey="id"
      pagination={{
        current: page,
        pageSize: limit,
        total: total,
        onChange: (page, pageSize) => {
          setPage(page);
          setLimit(pageSize);
        }
      }}
      loading={loading}
    />
  </div>
</MainLayout>
```

#### 表格列定义
```typescript
const columns = [
  {
    title: '网站',
    dataIndex: 'site_name',
    key: 'site_name',
    render: (name, record) => (
      <Link to={`/scan-results/${record.id}`}>
        {name}
      </Link>
    )
  },
  {
    title: 'AI 友好度',
    dataIndex: 'ai_score',
    key: 'ai_score',
    render: (score) => (
      <Progress
        percent={score}
        status={score >= 80 ? 'success' : score >= 60 ? 'normal' : 'exception'}
        format={(percent) => `${percent}分`}
      />
    )
  },
  {
    title: '页面数',
    dataIndex: 'pages_scanned',
    key: 'pages_scanned',
    render: (count) => count.toLocaleString()
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    render: (status) => (
      <Tag color={statusColors[status]}>
        {statusLabels[status]}
      </Tag>
    )
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    render: (date) => <Time value={date} format="YYYY-MM-DD HH:mm" />
  },
  {
    title: '操作',
    key: 'actions',
    render: (_, record) => (
      <Space>
        <Button onClick={() => viewDetails(record.id)}>查看</Button>
        <Button onClick={() => reRunScan(record.id)}>重新扫描</Button>
        <Dropdown menu={moreMenu}>
          <Menu.Item>导出报告</Menu.Item>
          <Menu.Item danger>删除</Menu.Item>
        </Dropdown>
      </Space>
    )
  }
];
```

---

### 2.6 AI 改写编辑器 (`/rewrite-editor`)

#### 组件结构
```tsx
<MainLayout>
  <div className="rewrite-editor">
    <div className="editor-container">
      {/* 左侧：内容选择 */}
      <div className="content-selector">
        <h2>选择内容</h2>
        <TreeSelect
          value={selectedPage}
          onChange={setSelectedPage}
          treeData={contentTree}
          placeholder="选择要改写的页面"
        />

        <div className="content-preview">
          <h3>原始内容</h3>
          <MarkdownViewer content={originalContent} />
        </div>
      </div>

      {/* 右侧：改写编辑器 */}
      <div className="rewrite-area">
        <h2>AI 改写</h2>

        {/* 模型选择 */}
        <div className="model-selector">
          <Radio.Group value={selectedModel} onChange={setSelectedModel}>
            <Radio value="gpt-4-turbo-preview">GPT-4 Turbo</Radio>
            <Radio value="claude-3-opus">Claude 3 Opus</Radio>
            <Radio value="llama-2-7b">Llama 2 7B (本地)</Radio>
          </Radio.Group>
        </div>

        {/* 改写选项 */}
        <div className="rewrite-options">
          <Checkbox checked={addTables} onChange={setAddTables}>
            添加数据表格
          </Checkbox>
          <Checkbox checked={optimizeStructure} onChange={setOptimizeStructure}>
            优化内容结构
          </Checkbox>
          <Checkbox checked={extractParameters} onChange={setExtractParameters}>
            提取关键参数
          </Checkbox>
        </div>

        {/* 改写按钮 */}
        <Button
          type="primary"
          size="large"
          loading={rewriting}
          onClick={handleRewrite}
          disabled={!selectedPage}
        >
          {rewriting ? '改写中...' : '开始改写'}
        </Button>

        {/* 改写进度 */}
        {rewriting && (
          <Progress
            percent={rewriteProgress}
            status={rewriteStatus}
          />
        )}

        {/* 改写结果 */}
        {rewriteResult && (
          <div className="rewrite-result">
            <h3>改写结果</h3>
            <div className="result-comparison">
              <div className="before">
                <h4>改写前</h4>
                <MarkdownViewer content={originalContent} />
              </div>
              <div className="after">
                <h4>改写后</h4>
                <MarkdownViewer content={rewriteResult.content} />
              </div>
            </div>
            <div className="quality-metrics">
              <h4>质量评分</h4>
              <Progress percent={rewriteResult.qualityScore} />
              <div className="metrics-details">
                <MetricItem label="结构优化" value={rewriteResult.structureScore} />
                <MetricItem label="表格质量" value={rewriteResult.tableScore} />
                <MetricItem label="参数提取" value={rewriteResult.parameterScore} />
              </div>
            </div>
            <div className="result-actions">
              <Button onClick={handleAccept}>接受改写</Button>
              <Button onClick={handleReject}>拒绝</Button>
              <Button onClick={handleEdit}>手动调整</Button>
            </div>
          </div>
        )}
      </div>
    </div>

    {/* 改写历史 */}
    <div className="rewrite-history">
      <h2>改写历史</h2>
      <Timeline>
        {history.map(item => (
          <Timeline.Item
            key={item.id}
            timestamp={item.created_at}
            color={item.status === 'completed' ? 'green' : 'red'}
          >
            <p>模型: {item.model}</p>
            <p>质量分: {item.quality_score}</p>
            <Button size="small" onClick={() => viewHistory(item.id)}>
              查看
            </Button>
          </Timeline.Item>
        ))}
      </Timeline>
    </div>
  </div>
</MainLayout>
```

#### 编辑器功能
- **Markdown 预览**: 实时渲染 Markdown 内容
- **代码高亮**: 支持语法高亮
- **差异对比**: 显示改写前后差异
- **手动编辑**: 允许用户手动调整改写结果
- **撤销重做**: 保存编辑历史
- **导出功能**: 导出为 Markdown / HTML / PDF

---

### 2.7 引用监控面板 (`/citation-monitor`)

#### 组件结构
```tsx
<MainLayout>
  <div className="citation-monitor">
    <div className="page-header">
      <h1>引用监控</h1>
      <div className="filters">
        <Select
          value={selectedEngine}
          onChange={setSelectedEngine}
          options={engineOptions}
          placeholder="AI 引擎"
        />
        <RangePicker
          value={dateRange}
          onChange={setDateRange}
          placeholder="时间范围"
        />
        <Button onClick={handleRefresh}>刷新</Button>
      </div>
    </div>

    {/* 引用统计 */}
    <div className="citation-stats">
      <Card title="总引用次数">
        <Statistic value={totalCitations} />
      </Card>
      <Card title="日均引用">
        <Statistic value={avgDailyCitations} />
      </Card>
      <Card title="引用增长率">
        <Statistic
          value={growthRate}
          prefix="+"
          suffix="%"
          valueStyle={{ color: growthRate > 0 ? '#3f8600' : '#cf1322' }}
        />
      </Card>
    </div>

    {/* 引用趋势图表 */}
    <div className="trend-chart">
      <Card title="引用趋势 (30天)">
        <LineChart
          data={citationTrend}
          xField="date"
          yField="count"
          series={[{ name: 'ChatGPT', data: chatgptData }, { name: 'Claude', data: claudeData }]}
        />
      </Card>
    </div>

    {/* 热门关键词 */}
    <div className="top-keywords">
      <Card title="热门关键词">
        <Table
          columns={keywordColumns}
          dataSource={topKeywords}
          rowKey="keyword"
          pagination={false}
        />
      </Card>
    </div>

    {/* AI 引擎分布 */}
    <div className="engine-distribution">
      <Card title="AI 引擎分布">
        <PieChart data={engineDistribution} />
      </Card>
    </div>
  </div>
</MainLayout>
```

#### 热门关键词表格列
```typescript
const keywordColumns = [
  {
    title: '排名',
    dataIndex: 'rank',
    key: 'rank',
    render: (rank) => <Tag>#{rank}</Tag>
  },
  {
    title: '关键词',
    dataIndex: 'keyword',
    key: 'keyword'
  },
  {
    title: '引用次数',
    dataIndex: 'count',
    key: 'count',
    render: (count) => count.toLocaleString()
  },
  {
    title: '平均置信度',
    dataIndex: 'avg_confidence',
    key: 'avg_confidence',
    render: (score) => `${(score * 100).toFixed(1)}%`
  },
  {
    title: '趋势',
    dataIndex: 'trend',
    key: 'trend',
    render: (trend) => (
      <Tag color={trend === 'up' ? 'green' : 'red'}>
        {trend === 'up' ? '↑' : '↓'}
      </Tag>
    )
  }
];
```

---

### 2.8 数据分析仪表盘 (`/analytics`)

#### 组件结构
```tsx
<MainLayout>
  <div className="analytics">
    <div className="page-header">
      <h1>数据分析</h1>
      <div className="actions">
        <Select
          value={period}
          onChange={setPeriod}
          options={periodOptions}
        />
        <Button onClick={exportReport}>导出报告</Button>
      </div>
    </div>

    {/* 核心指标 */}
    <div className="kpi-cards">
      <KPICard
        title="GEO 优化覆盖率"
        value={geoCoverage}
        target={80}
        unit="%"
      />
      <KPICard
        title="平均 AI 友好度提升"
        value={aiScoreImprovement}
        target={15}
        unit="%"
      />
      <KPICard
        title="引用增长率"
        value={citationGrowth}
        target={20}
        unit="%"
      />
      <KPICard
        title="改写接受率"
        value={rewriteAcceptance}
        target={70}
        unit="%"
      />
    </div>

    {/* 多维分析图表 */}
    <div className="analysis-charts">
      <Card title="AI 友好度分布">
        <BarChart data={aiScoreDistribution} />
      </Card>
      <Card title="扫描频率分析">
        <Heatmap data={scanFrequency} />
      </Card>
      <Card title="改写质量趋势">
        <AreaChart data={rewriteQualityTrend} />
      </Card>
      <Card title="关键词影响力分析">
        <RadarChart data={keywordImpact} />
      </Card>
    </div>

    {/* 详细数据表格 */}
    <Card title="详细数据">
      <Tabs>
        <Tabs.TabPane tab="扫描任务" key="scans">
          <Table columns={scanColumns} dataSource={scanData} />
        </Tabs.TabPane>
        <Tabs.TabPane tab="AI 改写" key="rewrites">
          <Table columns={rewriteColumns} dataSource={rewriteData} />
        </Tabs.TabPane>
        <Tabs.TabPane tab="引用监控" key="citations">
          <Table columns={citationColumns} dataSource={citationData} />
        </Tabs.TabPane>
      </Tabs>
    </Card>
  </div>
</MainLayout>
```

#### KPI 卡片组件
```tsx
interface KPICardProps {
  title: string;      // 指标名称
  value: number;      // 当前值
  target: number;     // 目标值
  unit?: string;      // 单位
}

function KPICard({ title, value, target, unit }) {
  const percentage = (value / target) * 100;
  const status = percentage >= 100 ? 'success' : percentage >= 80 ? 'normal' : 'warning';

  return (
    <div className="kpi-card">
      <h3>{title}</h3>
      <div className="kpi-value">
        <span className="value">{value}</span>
        <span className="unit">{unit || ''}</span>
      </div>
      <Progress
        percent={Math.min(percentage, 100)}
        status={status}
        format={() => `${percentage.toFixed(0)}% (目标: ${target}${unit || ''})`}
      />
    </div>
  );
}
```

---

## 3. 路由设计

### 3.1 路由结构
```typescript
const routes = [
  // 公开路由
  {
    path: '/login',
    element: <AuthLayout><Login /></AuthLayout>
  },
  {
    path: '/register',
    element: <AuthLayout><Register /></AuthLayout>
  },

  // 受保护路由 (需要认证)
  {
    path: '/',
    element: <MainLayout><Dashboard /></MainLayout>
  },
  {
    path: '/scan-config',
    element: <MainLayout><ScanConfig /></MainLayout>
  },
  {
    path: '/scan-results',
    element: <MainLayout><ScanResults /></MainLayout>
  },
  {
    path: '/scan-results/:id',
    element: <MainLayout><ScanResultDetail /></MainLayout>
  },
  {
    path: '/rewrite-editor',
    element: <MainLayout><RewriteEditor /></MainLayout>
  },
  {
    path: '/citation-monitor',
    element: <MainLayout><CitationMonitor /></MainLayout>
  },
  {
    path: '/analytics',
    element: <MainLayout><Analytics /></MainLayout>
  }
];
```

### 3.2 路由守卫
```typescript
// 认证守卫
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuthStore();

  if (loading) {
    return <Spin size="large" />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// 使用示例
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

---

## 4. 状态管理

### 4.1 Auth Store (Zustand)
```typescript
interface AuthState {
  // 状态
  user: User | null;
  token: string | null;
  loading: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
}

const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  loading: false,

  login: async (email, password) => {
    set({ loading: true });

    try {
      const response = await api.post('/auth/login', { email, password });
      const { user, token } = response.data;

      set({ user, token });
      localStorage.setItem('token', token);
    } catch (error) {
      message.error('登录失败');
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  logout: () => {
    set({ user: null, token: null });
    localStorage.removeItem('token');
    api.defaults.headers.common['Authorization'] = '';
  }
}));
```

### 4.2 UI Store (主题设置)
```typescript
interface UIState {
  theme: 'light' | 'dark';
  language: 'zh' | 'en';
  sidebarCollapsed: boolean;

  // Actions
  setTheme: (theme: 'light' | 'dark') => void;
  setLanguage: (language: 'zh' | 'en') => void;
  toggleSidebar: () => void;
}

const useUIStore = create<UIState>((set) => ({
  theme: localStorage.getItem('theme') as 'light' | 'dark' || 'light',
  language: localStorage.getItem('language') as 'zh' | 'en' || 'zh',
  sidebarCollapsed: false,

  setTheme: (theme) => {
    set({ theme });
    localStorage.setItem('theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  },

  setLanguage: (language) => {
    set({ language });
    localStorage.setItem('language', language);
  },

  toggleSidebar: () => {
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  }
}));
```

---

## 5. API 集成

### 5.1 Axios 配置
```typescript
import axios from 'axios';
import { message } from 'antd';

// 创建 axios 实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 (自动添加 Token)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 (统一错误处理)
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // 401 未授权 → 跳转登录
    if (error.response?.status === 401) {
      message.error('登录已过期，请重新登录');
      localStorage.removeItem('token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // 403 无权限
    if (error.response?.status === 403) {
      message.error('无权限访问');
      return Promise.reject(error);
    }

    // 429 限流
    if (error.response?.status === 429) {
      message.warning('请求过于频繁，请稍后再试');
      return Promise.reject(error);
    }

    // 其他错误
    const errorMessage = error.response?.data?.error?.message || '请求失败';
    message.error(errorMessage);
    return Promise.reject(error);
  }
);

export default api;
```

### 5.2 API 服务封装
```typescript
// auth.ts
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (data: RegisterData) =>
    api.post('/auth/register', data),

  getProfile: () =>
    api.get('/auth/profile'),

  updateProfile: (data: UpdateProfileData) =>
    api.put('/auth/profile', data)
};

// scan.ts
export const scanApi = {
  createTask: (data: CreateScanTaskData) =>
    api.post('/scans/create', data),

  getTasks: (params: QueryParams) =>
    api.get('/scans/list', { params }),

  getTask: (id: string) =>
    api.get(`/scans/${id}`),

  deleteTask: (id: string) =>
    api.delete(`/scans/${id}`)
};

// ai.ts
export const aiApi = {
  rewrite: (data: RewriteRequest) =>
    api.post('/ai/rewrite', data),

  getHistory: (params: QueryParams) =>
    api.get('/ai/history', { params })
};

// monitor.ts
export const monitorApi = {
  getCitations: (params: QueryParams) =>
    api.get('/monitor/citations', { params }),

  getTrends: (period: string) =>
    api.get('/monitor/trends', { params: { period } })
};
```

---

## 6. 响应式设计

### 6.1 断点定义
```scss
// 断点
$breakpoint-xs: 480px;
$breakpoint-sm: 576px;
$breakpoint-md: 768px;
$breakpoint-lg: 992px;
$breakpoint-xl: 1200px;
$breakpoint-xxl: 1600px;
```

### 6.2 布局适配
```scss
// MainLayout 响应式
.main-layout {
  display: flex;

  // 桌面端: 侧边栏固定
  @media (min-width: $breakpoint-lg) {
    .sidebar {
      width: 240px;
      position: fixed;
    }
    .content {
      margin-left: 240px;
    }
  }

  // 平板端: 侧边栏可折叠
  @media (min-width: $breakpoint-md) and (max-width: $breakpoint-lg - 1) {
    .sidebar {
      width: 200px;
    }
    .content {
      margin-left: 200px;
    }
  }

  // 移动端: 侧边栏隐藏
  @media (max-width: $breakpoint-md - 1) {
    .sidebar {
      display: none;
    }
    .content {
      margin-left: 0;
    }
  }
}
```

---

## 7. 性能优化

### 7.1 代码分割
```typescript
// 路由懒加载
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ScanConfig = lazy(() => import('./pages/ScanConfig'));

// 使用 Suspense 加载
<Suspense fallback={<Spin size="large" />}>
  <Routes>
    <Route path="/" element={<Dashboard />} />
    <Route path="/scan-config" element={<ScanConfig />} />
  </Routes>
</Suspense>
```

### 7.2 虚拟列表
```tsx
// 大数据量使用虚拟列表
import { List } from 'react-virtualized';

<VirtualList
  width={800}
  height={600}
  rowCount={scanTasks.length}
  rowHeight={80}
  rowRenderer={({ index, key, style }) => (
    <div key={key} style={style}>
      <ScanTaskItem task={scanTasks[index]} />
    </div>
  )}
/>
```

### 7.3 图片优化
```typescript
// 使用 WebP 格式
<picture>
  <source srcSet="logo.webp" type="image/webp" />
  <img src="logo.png" alt="Logo" />
</picture>

// 图片懒加载
<img
  src="image.jpg"
  loading="lazy"
  alt="Description"
/>

// CDN 加速
<img src={`${CDN_URL}/logo.png`} alt="Logo" />
```

---

## 8. 测试计划

### 8.1 单元测试
- **组件测试**: 所有页面组件单元测试
- **Hooks 测试**: 自定义 Hooks 测试
- **Store 测试**: Zustand Store 测试

### 8.2 集成测试
- **路由测试**: 路由守卫和导航测试
- **API 集成**: 真实 API 测试
- **端到端测试**: 关键用户流程测试

### 8.3 性能测试
- **首屏加载**: < 2s (3G 网络)
- **交互响应**: < 100ms (点击反馈)
- **Lighthouse 评分**: > 90 分

---

## 9. 部署说明

### 9.1 Vite 构建配置
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-antd': ['antd'],
          'vendor-other': ['axios', 'dayjs']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  }
});
```

### 9.2 Docker 配置
```dockerfile
# 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 9.3 Nginx 配置
```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  # SPA 路由支持
  location / {
    try_files $uri $uri/ /index.html;
  }

  # API 代理 (开发环境)
  location /api {
    proxy_pass http://backend:3001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  # 静态资源缓存
  location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }
}
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-17
**下次审查**: 2026-04-17
