// 用户相关
export interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  avatar?: string;
  createdAt: string;
}

// 登录请求
export interface LoginRequest {
  email: string;
  password: string;
}

// 注册请求
export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

// 企业信息
export interface Enterprise {
  id: string;
  name: string;
  domain: string;
  description?: string;
  logo?: string;
  plan: 'free' | 'pro' | 'enterprise';
  createdAt: string;
}

// 扫描配置
export interface ScanConfig {
  id: string;
  websiteUrl: string;
  scanFrequency: 'daily' | 'weekly' | 'monthly';
  keywords: string[];
  status: 'active' | 'paused' | 'stopped';
  lastScanAt?: string;
  nextScanAt?: string;
  createdAt: string;
}

// 扫描结果
export interface ScanResult {
  id: string;
  configId: string;
  websiteUrl: string;
  totalArticles: number;
  suspiciousArticles: number;
  processedAt: string;
  status: 'completed' | 'processing' | 'failed';
  details?: ArticleResult[];
}

// 文章结果
export interface ArticleResult {
  id: string;
  url: string;
  title: string;
  content: string;
  similarity: number;
  source?: string;
  createdAt: string;
}

// AI 改写记录
export interface RewriteRecord {
  id: string;
  originalText: string;
  rewrittenText: string;
  similarityBefore: number;
  similarityAfter: number;
  status: 'pending' | 'completed' | 'failed';
  createdAt: string;
}

// 引用监控数据
export interface CitationData {
  id: string;
  sourceUrl: string;
  title: string;
  citationCount: number;
  lastCitedAt: string;
  trend: 'up' | 'down' | 'stable';
}

// 分析数据
export interface AnalyticsData {
  totalArticles: number;
  totalRewrites: number;
  avgSimilarity: number;
  citationGrowth: number[];
  topCitations: CitationData[];
  recentActivity: ActivityItem[];
}

// 活动记录
export interface ActivityItem {
  id: string;
  type: 'scan' | 'rewrite' | 'citation' | 'alert';
  message: string;
  timestamp: string;
}
