/**
 * API Types
 * Types related to API communication, requests, and responses
 */

/**
 * Standard API error structure
 */
export interface ApiError {
  /** Error message */
  detail: string;
  /** HTTP status code */
  status_code: number;
  /** Error code for programmatic handling */
  code?: string;
  /** Field-specific errors (for validation) */
  errors?: Record<string, string[]>;
  /** Request ID for debugging */
  request_id?: string;
  /** Timestamp of the error */
  timestamp?: string;
}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  /** Response data on success */
  data?: T;
  /** Error information on failure */
  error?: ApiError;
  /** Additional metadata */
  meta?: ResponseMeta;
}

/**
 * Response metadata
 */
export interface ResponseMeta {
  /** Request ID for tracing */
  request_id?: string;
  /** Response timestamp */
  timestamp?: string;
  /** API version */
  version?: string;
  /** Deprecation warnings */
  warnings?: string[];
}

/**
 * Paginated response structure
 */
export interface PaginatedResponse<T> {
  /** Array of items */
  items: T[];
  /** Total number of items (across all pages) */
  total: number;
  /** Current page number (1-indexed) */
  page: number;
  /** Items per page */
  limit: number;
  /** Whether there are more pages */
  has_more: boolean;
  /** Total number of pages */
  total_pages?: number;
  /** Cursor for next page (for cursor-based pagination) */
  next_cursor?: string;
  /** Cursor for previous page */
  prev_cursor?: string;
}

/**
 * Pagination request parameters
 */
export interface PaginationParams {
  /** Page number (1-indexed) */
  page?: number;
  /** Items per page */
  limit?: number;
  /** Cursor for cursor-based pagination */
  cursor?: string;
  /** Sort field */
  sort_by?: string;
  /** Sort direction */
  sort_order?: 'asc' | 'desc';
}

/**
 * HTTP request methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

/**
 * Request configuration
 */
export interface RequestConfig {
  /** Request headers */
  headers?: Record<string, string>;
  /** Query parameters */
  params?: Record<string, string | number | boolean | undefined>;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Whether to include credentials */
  withCredentials?: boolean;
  /** Abort signal for cancellation */
  signal?: AbortSignal;
  /** Response type */
  responseType?: 'json' | 'text' | 'blob' | 'arraybuffer';
}

/**
 * API request state (for React hooks)
 */
export interface RequestState<T> {
  /** Response data */
  data: T | null;
  /** Loading state */
  loading: boolean;
  /** Error state */
  error: ApiError | null;
  /** Whether request has been made */
  isIdle: boolean;
  /** Whether request is in progress */
  isLoading: boolean;
  /** Whether request succeeded */
  isSuccess: boolean;
  /** Whether request failed */
  isError: boolean;
}

/**
 * Mutation state (for POST/PUT/DELETE operations)
 */
export interface MutationState<T, TVariables = unknown> {
  /** Response data */
  data: T | null;
  /** Loading state */
  loading: boolean;
  /** Error state */
  error: ApiError | null;
  /** Execute the mutation */
  mutate: (variables: TVariables) => Promise<T>;
  /** Reset mutation state */
  reset: () => void;
}

/**
 * Retry configuration
 */
export interface RetryConfig {
  /** Maximum number of retries */
  maxRetries: number;
  /** Base delay in milliseconds */
  baseDelay: number;
  /** Maximum delay in milliseconds */
  maxDelay: number;
  /** Whether to use exponential backoff */
  exponentialBackoff: boolean;
  /** Status codes to retry on */
  retryStatusCodes: number[];
}

/**
 * Default retry configuration
 */
export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  exponentialBackoff: true,
  retryStatusCodes: [408, 429, 500, 502, 503, 504],
};

/**
 * Rate limit information from response headers
 */
export interface RateLimitInfo {
  /** Maximum requests allowed */
  limit: number;
  /** Remaining requests in window */
  remaining: number;
  /** Seconds until rate limit resets */
  resetIn: number;
  /** Timestamp when rate limit resets */
  resetAt: Date;
}

/**
 * Webhook event structure
 */
export interface WebhookEvent<T = unknown> {
  /** Event ID */
  id: string;
  /** Event type */
  type: string;
  /** Event data */
  data: T;
  /** Event timestamp */
  created_at: string;
  /** API version */
  api_version: string;
}

/**
 * Batch request item
 */
export interface BatchRequestItem<T = unknown> {
  /** Request ID */
  id: string;
  /** HTTP method */
  method: HttpMethod;
  /** Request path */
  path: string;
  /** Request body */
  body?: T;
  /** Request headers */
  headers?: Record<string, string>;
}

/**
 * Batch response item
 */
export interface BatchResponseItem<T = unknown> {
  /** Request ID (matches request) */
  id: string;
  /** HTTP status code */
  status: number;
  /** Response body */
  body?: T;
  /** Error details */
  error?: ApiError;
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  /** Overall status */
  status: 'healthy' | 'degraded' | 'unhealthy';
  /** Version information */
  version: string;
  /** Uptime in seconds */
  uptime: number;
  /** Service dependencies status */
  services: Record<string, {
    status: 'up' | 'down';
    latency_ms?: number;
    message?: string;
  }>;
  /** Timestamp */
  timestamp: string;
}

/**
 * Common API endpoints
 */
export const API_ENDPOINTS = {
  // Auth
  AUTH_LOGIN: '/auth/login',
  AUTH_REGISTER: '/auth/register',
  AUTH_LOGOUT: '/auth/logout',
  AUTH_REFRESH: '/auth/refresh',
  AUTH_PASSWORD_RESET: '/auth/password-reset',
  AUTH_PASSWORD_RESET_CONFIRM: '/auth/password-reset/confirm',

  // Users
  USERS_ME: '/users/me',
  USERS_PROFILE: '/users/profile',
  USERS_PREFERENCES: '/users/preferences',

  // Projects
  PROJECTS: '/projects',
  PROJECT_BY_ID: (id: string) => `/projects/${id}`,
  PROJECT_FILES: (id: string) => `/projects/${id}/files`,

  // Generation
  GENERATE: '/generate',
  GENERATE_STREAM: '/generate/stream',

  // Subscriptions
  SUBSCRIPTIONS: '/subscriptions',
  SUBSCRIPTION_CHECKOUT: '/subscriptions/checkout',
  SUBSCRIPTION_PORTAL: '/subscriptions/portal',

  // Health
  HEALTH: '/health',
} as const;

/**
 * Create a typed API error
 */
export function createApiError(
  detail: string,
  statusCode: number,
  code?: string
): ApiError {
  return {
    detail,
    status_code: statusCode,
    code,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Check if an error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    'status_code' in error
  );
}

/**
 * Extract error message from various error types
 */
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.detail;
  }
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unexpected error occurred';
}
