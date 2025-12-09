/**
 * Example TypeScript API Client for Devora Frontend
 *
 * Usage:
 * 1. Copy devora-api-types.ts to your frontend project
 * 2. Copy this file to src/lib/api-client.ts
 * 3. Use in components
 *
 * Example:
 * ```tsx
 * import { apiClient } from '@/lib/api-client';
 *
 * const projects = await apiClient.projects.list();
 * const user = await apiClient.auth.login(email, password);
 * ```
 */

// Import generated types
import type {
  UserCreate,
  UserResponse,
  Token,
  ProjectCreate,
  ProjectResponse,
  AgenticRequest,
  AgenticResponse,
  FullStackRequest,
  FullStackResponse,
  SubscriptionPlanResponse,
  CheckoutSessionResponse,
  InvoiceResponse,
} from './devora-api-types';

/**
 * API Client Configuration
 */
interface ApiConfig {
  baseUrl: string;
  timeout?: number;
}

/**
 * API Error Response
 */
interface ApiError {
  error: string;
  message: string;
  detail?: string;
}

/**
 * Generic API Response
 */
interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  success: boolean;
}

/**
 * Main API Client Class
 */
class DevoraApiClient {
  private baseUrl: string;
  private token: string | null = null;
  private timeout: number;

  constructor(config: ApiConfig) {
    this.baseUrl = config.baseUrl;
    this.timeout = config.timeout || 30000;
  }

  /**
   * Set authentication token
   */
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('devora_token', token);
    }
  }

  /**
   * Clear authentication token
   */
  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('devora_token');
    }
  }

  /**
   * Get authentication token
   */
  getToken(): string | null {
    if (this.token) return this.token;
    if (typeof window !== 'undefined') {
      return localStorage.getItem('devora_token');
    }
    return null;
  }

  /**
   * Generic request method
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getToken();

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After') || '60';
        throw new Error(`Rate limit exceeded. Retry after ${retryAfter} seconds.`);
      }

      // Handle unauthorized
      if (response.status === 401) {
        this.clearToken();
        throw new Error('Authentication required. Please log in again.');
      }

      // Parse response
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || data.detail || 'Request failed');
      }

      return data as T;
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timeout');
        }
        throw error;
      }
      throw new Error('Unknown error occurred');
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Authentication endpoints
   */
  auth = {
    /**
     * Register new user
     */
    register: async (data: UserCreate): Promise<UserResponse> => {
      return this.request<UserResponse>('/api/v2/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    /**
     * Login user
     */
    login: async (email: string, password: string): Promise<Token> => {
      const token = await this.request<Token>('/api/v2/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      this.setToken(token.access_token);
      return token;
    },

    /**
     * Logout user
     */
    logout: () => {
      this.clearToken();
    },

    /**
     * Request password reset
     */
    requestPasswordReset: async (email: string): Promise<{ message: string }> => {
      return this.request('/api/v2/auth/password-reset', {
        method: 'POST',
        body: JSON.stringify({ email }),
      });
    },

    /**
     * OAuth login URL
     */
    getOAuthUrl: (provider: 'google' | 'github'): string => {
      return `${this.baseUrl}/api/v2/auth/oauth/${provider}`;
    },
  };

  /**
   * Project endpoints
   */
  projects = {
    /**
     * List all projects
     */
    list: async (): Promise<ProjectResponse[]> => {
      return this.request<ProjectResponse[]>('/api/v2/projects');
    },

    /**
     * Get project by ID
     */
    get: async (id: string): Promise<ProjectResponse> => {
      return this.request<ProjectResponse>(`/api/v2/projects/${id}`);
    },

    /**
     * Create new project
     */
    create: async (data: ProjectCreate): Promise<ProjectResponse> => {
      return this.request<ProjectResponse>('/api/v2/projects', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    /**
     * Update project
     */
    update: async (id: string, data: Partial<ProjectCreate>): Promise<ProjectResponse> => {
      return this.request<ProjectResponse>(`/api/v2/projects/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    /**
     * Delete project
     */
    delete: async (id: string): Promise<void> => {
      return this.request<void>(`/api/v2/projects/${id}`, {
        method: 'DELETE',
      });
    },
  };

  /**
   * Code generation endpoints
   */
  generate = {
    /**
     * Generate code with agentic system (HTML/CSS/JS)
     */
    agentic: async (request: AgenticRequest): Promise<AgenticResponse> => {
      return this.request<AgenticResponse>('/api/generate/agentic', {
        method: 'POST',
        body: JSON.stringify(request),
      });
    },

    /**
     * Generate full-stack Next.js project
     */
    fullstack: async (request: FullStackRequest): Promise<FullStackResponse> => {
      return this.request<FullStackResponse>('/api/generate/fullstack', {
        method: 'POST',
        body: JSON.stringify(request),
      });
    },
  };

  /**
   * Billing endpoints
   */
  billing = {
    /**
     * Get subscription plans
     */
    getPlans: async (): Promise<SubscriptionPlanResponse> => {
      return this.request<SubscriptionPlanResponse>('/api/v2/billing/plans');
    },

    /**
     * Create checkout session
     */
    createCheckoutSession: async (): Promise<CheckoutSessionResponse> => {
      return this.request<CheckoutSessionResponse>('/api/billing/create-checkout-session', {
        method: 'POST',
      });
    },

    /**
     * Create portal session
     */
    createPortalSession: async (): Promise<{ url: string }> => {
      return this.request<{ url: string }>('/api/billing/create-portal-session', {
        method: 'POST',
      });
    },

    /**
     * List invoices
     */
    listInvoices: async (): Promise<InvoiceResponse[]> => {
      return this.request<InvoiceResponse[]>('/api/billing/invoices');
    },
  };

  /**
   * Deployment endpoints
   */
  deploy = {
    /**
     * Export to GitHub
     */
    toGithub: async (projectId: string, repoName: string, githubToken: string, isPrivate = false) => {
      return this.request('/api/github/export', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          repo_name: repoName,
          github_token: githubToken,
          private: isPrivate,
        }),
      });
    },

    /**
     * Deploy to Vercel
     */
    toVercel: async (projectId: string, projectName: string, vercelToken: string) => {
      return this.request('/api/vercel/deploy', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          project_name: projectName,
          vercel_token: vercelToken,
        }),
      });
    },
  };
}

/**
 * Create API client instance
 */
export const apiClient = new DevoraApiClient({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

/**
 * React hook for API client (optional)
 */
export function useApiClient() {
  return apiClient;
}

/**
 * Example usage in React component:
 *
 * ```tsx
 * import { apiClient } from '@/lib/api-client';
 * import { ProjectResponse } from '@/types/devora-api-types';
 *
 * export default function ProjectsPage() {
 *   const [projects, setProjects] = useState<ProjectResponse[]>([]);
 *   const [loading, setLoading] = useState(true);
 *
 *   useEffect(() => {
 *     async function fetchProjects() {
 *       try {
 *         const data = await apiClient.projects.list();
 *         setProjects(data);
 *       } catch (error) {
 *         console.error('Failed to fetch projects:', error);
 *       } finally {
 *         setLoading(false);
 *       }
 *     }
 *     fetchProjects();
 *   }, []);
 *
 *   return (
 *     <div>
 *       {loading ? (
 *         <p>Loading...</p>
 *       ) : (
 *         <ul>
 *           {projects.map(project => (
 *             <li key={project.id}>{project.name}</li>
 *           ))}
 *         </ul>
 *       )}
 *     </div>
 *   );
 * }
 * ```
 */
