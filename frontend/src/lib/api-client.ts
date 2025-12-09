/**
 * Centralized API Client for Devora
 * Handles all HTTP requests with proper error handling, retries, and token management
 */

import axios, {
  AxiosInstance,
  AxiosError,
  AxiosRequestConfig,
  InternalAxiosRequestConfig,
} from 'axios';

// Types
interface ApiError {
  message: string;
  code?: string;
  status: number;
  details?: Record<string, unknown>;
}

interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  success: boolean;
}

interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  retryCondition: (error: AxiosError) => boolean;
}

// Default configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 30000;

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  retryCondition: (error: AxiosError) => {
    // Retry on network errors or 5xx server errors
    return (
      !error.response ||
      (error.response.status >= 500 && error.response.status <= 599)
    );
  },
};

// Custom error class
export class ApiClientError extends Error {
  public status: number;
  public code?: string;
  public details?: Record<string, unknown>;

  constructor(error: ApiError) {
    super(error.message);
    this.name = 'ApiClientError';
    this.status = error.status;
    this.code = error.code;
    this.details = error.details;
  }

  isUnauthorized(): boolean {
    return this.status === 401;
  }

  isForbidden(): boolean {
    return this.status === 403;
  }

  isNotFound(): boolean {
    return this.status === 404;
  }

  isValidationError(): boolean {
    return this.status === 422;
  }

  isServerError(): boolean {
    return this.status >= 500;
  }
}

// Token management
const tokenManager = {
  getAccessToken: (): string | null => {
    return localStorage.getItem('access_token');
  },

  setAccessToken: (token: string): void => {
    localStorage.setItem('access_token', token);
  },

  removeAccessToken: (): void => {
    localStorage.removeItem('access_token');
  },

  getRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token');
  },

  setRefreshToken: (token: string): void => {
    localStorage.setItem('refresh_token', token);
  },

  removeRefreshToken: (): void => {
    localStorage.removeItem('refresh_token');
  },

  clearTokens: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Create axios instance
const createApiClient = (config?: Partial<AxiosRequestConfig>): AxiosInstance => {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: DEFAULT_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
    ...config,
  });

  // Request interceptor - add auth token
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = tokenManager.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // Add request ID for tracing
      config.headers['X-Request-ID'] = generateRequestId();

      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor - handle errors
  instance.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean;
        _retryCount?: number;
      };

      // Handle 401 - try to refresh token
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = tokenManager.getRefreshToken();
          if (refreshToken) {
            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token } = response.data;
            tokenManager.setAccessToken(access_token);
            if (refresh_token) {
              tokenManager.setRefreshToken(refresh_token);
            }

            // Retry original request
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return instance(originalRequest);
          }
        } catch (refreshError) {
          // Refresh failed - clear tokens and redirect to login
          tokenManager.clearTokens();
          window.dispatchEvent(new CustomEvent('auth:logout'));
          return Promise.reject(refreshError);
        }
      }

      // Transform error to ApiClientError
      const apiError = transformError(error);
      return Promise.reject(new ApiClientError(apiError));
    }
  );

  return instance;
};

// Utility functions
function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

function transformError(error: AxiosError): ApiError {
  if (error.response) {
    const data = error.response.data as Record<string, unknown>;
    return {
      message: (data?.detail as string) || (data?.message as string) || 'An error occurred',
      code: data?.code as string,
      status: error.response.status,
      details: data,
    };
  }

  if (error.request) {
    return {
      message: 'Network error - please check your connection',
      code: 'NETWORK_ERROR',
      status: 0,
    };
  }

  return {
    message: error.message || 'An unexpected error occurred',
    code: 'UNKNOWN_ERROR',
    status: 0,
  };
}

// Retry wrapper
async function withRetry<T>(
  fn: () => Promise<T>,
  config: RetryConfig = DEFAULT_RETRY_CONFIG
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      if (
        error instanceof AxiosError &&
        attempt < config.maxRetries &&
        config.retryCondition(error)
      ) {
        await sleep(config.retryDelay * Math.pow(2, attempt)); // Exponential backoff
        continue;
      }

      throw error;
    }
  }

  throw lastError;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Main API client instance
const apiClient = createApiClient();

// API methods
export const api = {
  // Generic methods
  get: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
    withRetry(() => apiClient.get<ApiResponse<T>>(url, config).then((r) => r.data)),

  post: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    withRetry(() => apiClient.post<ApiResponse<T>>(url, data, config).then((r) => r.data)),

  put: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    withRetry(() => apiClient.put<ApiResponse<T>>(url, data, config).then((r) => r.data)),

  patch: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    withRetry(() => apiClient.patch<ApiResponse<T>>(url, data, config).then((r) => r.data)),

  delete: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
    withRetry(() => apiClient.delete<ApiResponse<T>>(url, config).then((r) => r.data)),

  // Auth endpoints
  auth: {
    login: (email: string, password: string) =>
      apiClient.post('/auth/login', { email, password }).then((r) => {
        const { access_token, refresh_token, user } = r.data;
        tokenManager.setAccessToken(access_token);
        if (refresh_token) tokenManager.setRefreshToken(refresh_token);
        return { user, access_token };
      }),

    register: (email: string, password: string, name?: string) =>
      apiClient.post('/auth/register', { email, password, name }).then((r) => r.data),

    logout: () => {
      tokenManager.clearTokens();
      return Promise.resolve();
    },

    getCurrentUser: () =>
      apiClient.get('/auth/me').then((r) => r.data),

    refreshToken: () =>
      apiClient.post('/auth/refresh', {
        refresh_token: tokenManager.getRefreshToken(),
      }).then((r) => {
        const { access_token, refresh_token } = r.data;
        tokenManager.setAccessToken(access_token);
        if (refresh_token) tokenManager.setRefreshToken(refresh_token);
        return r.data;
      }),
  },

  // Projects endpoints
  projects: {
    list: () => apiClient.get('/api/projects').then((r) => r.data),

    get: (id: string) => apiClient.get(`/api/projects/${id}`).then((r) => r.data),

    create: (data: { name: string; description?: string; template?: string }) =>
      apiClient.post('/api/projects', data).then((r) => r.data),

    update: (id: string, data: Partial<{ name: string; description: string }>) =>
      apiClient.put(`/api/projects/${id}`, data).then((r) => r.data),

    delete: (id: string) => apiClient.delete(`/api/projects/${id}`).then((r) => r.data),
  },

  // Conversations endpoints
  conversations: {
    list: (projectId: string) =>
      apiClient.get(`/api/conversations?project_id=${projectId}`).then((r) => r.data),

    get: (id: string) =>
      apiClient.get(`/api/conversations/${id}`).then((r) => r.data),

    create: (projectId: string, title?: string) =>
      apiClient.post('/api/conversations', { project_id: projectId, title }).then((r) => r.data),

    delete: (id: string) =>
      apiClient.delete(`/api/conversations/${id}`).then((r) => r.data),
  },

  // Chat/AI endpoints
  chat: {
    send: (conversationId: string, message: string) =>
      apiClient.post(`/api/chat/${conversationId}`, { message }).then((r) => r.data),

    stream: (conversationId: string, message: string) => {
      // Return EventSource for SSE streaming
      const token = tokenManager.getAccessToken();
      const url = `${API_BASE_URL}/api/chat/${conversationId}/stream?message=${encodeURIComponent(message)}`;

      return new EventSource(url, {
        // Note: EventSource doesn't support custom headers
        // Token should be passed via query param or cookies for SSE
      });
    },
  },

  // Files endpoints
  files: {
    list: (projectId: string) =>
      apiClient.get(`/api/files?project_id=${projectId}`).then((r) => r.data),

    get: (projectId: string, path: string) =>
      apiClient.get(`/api/files/${projectId}/${encodeURIComponent(path)}`).then((r) => r.data),

    save: (projectId: string, path: string, content: string) =>
      apiClient.post(`/api/files/${projectId}/${encodeURIComponent(path)}`, { content }).then((r) => r.data),

    delete: (projectId: string, path: string) =>
      apiClient.delete(`/api/files/${projectId}/${encodeURIComponent(path)}`).then((r) => r.data),
  },

  // Billing endpoints
  billing: {
    getSubscription: () =>
      apiClient.get('/api/billing/subscription').then((r) => r.data),

    createCheckoutSession: (priceId: string) =>
      apiClient.post('/api/billing/checkout', { price_id: priceId }).then((r) => r.data),

    createPortalSession: () =>
      apiClient.post('/api/billing/portal').then((r) => r.data),
  },

  // Deployment endpoints
  deployment: {
    deploy: (projectId: string, target: string) =>
      apiClient.post(`/api/deploy/${projectId}`, { target }).then((r) => r.data),

    status: (deploymentId: string) =>
      apiClient.get(`/api/deploy/${deploymentId}/status`).then((r) => r.data),
  },
};

// Export utilities
export { tokenManager, apiClient, createApiClient, withRetry };
export type { ApiResponse, ApiError };
