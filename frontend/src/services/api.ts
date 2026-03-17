import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios';

// API 响应接口
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
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

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response;

    // 如果返回的 code 不是 200，认为是错误
    if (data.code !== 200) {
      // token 过期或无效
      if (data.code === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(new Error(data.message || '请求失败'));
    }

    return response;
  },
  (error) => {
    // 网络错误
    if (error.response) {
      const { status, data } = error.response;
      if (status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(new Error(data?.message || '请求失败'));
    }
    return Promise.reject(new Error(error.message || '网络错误'));
  }
);

// 通用请求方法
const request = async <T = any>(
  config: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  try {
    const response = await apiClient.request<ApiResponse<T>>(config);
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

// API 方法
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    request<T>({ method: 'GET', url, ...config }),

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    request<T>({ method: 'POST', url, data, ...config }),

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    request<T>({ method: 'PUT', url, data, ...config }),

  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    request<T>({ method: 'DELETE', url, ...config }),
};

export default api;
