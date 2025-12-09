/**
 * Devora API TypeScript Types
 * Auto-generated from Pydantic schemas
 * DO NOT EDIT MANUALLY
 */

// ============================================
// User Types
// ============================================

export interface UserCreate {
  /** User email address */
  email: string;
  /** User full name */
  full_name?: string;
  /** User password (min 8 characters) */
  password: string;
}

export interface UserResponse {
  /** User email address */
  email: string;
  /** User full name */
  full_name?: string;
  /** User unique identifier */
  id: string;
  /** Whether user account is active */
  is_active?: boolean;
  /** Whether user has admin privileges */
  is_admin?: boolean;
  /** Current subscription status */
  subscription_status?: string;
  /** Subscription period end date */
  current_period_end?: string;
  /** Account creation timestamp */
  created_at: string;
}

export interface Token {
  /** JWT access token */
  access_token: string;
  /** Token type */
  token_type?: string;
}

// ============================================
// Project Types
// ============================================

export interface ConversationMessage {
  /** Message role */
  role: string;
  /** Message content */
  content: string;
}

export interface ProjectFileCreate {
  /** File name with extension */
  name: string;
  /** File content as string */
  content: string;
  /** Programming language or file type */
  language: string;
}

export interface ProjectFileResponse {
  /** File name with extension */
  name: string;
  /** File content as string */
  content: string;
  /** Programming language or file type */
  language: string;
}

export interface ProjectCreate {
  /** Project name */
  name: string;
  /** Project description */
  description?: string;
  /** Type of project (saas, ecommerce, blog, etc.) */
  project_type?: string;
  /** Initial project files */
  files?: ProjectFileCreate[];
  /** Conversation history */
  conversation_history?: ConversationMessage[];
}

export interface ProjectResponse {
  /** Project name */
  name: string;
  /** Project description */
  description?: string;
  /** Type of project (saas, ecommerce, blog, etc.) */
  project_type?: string;
  /** Project unique identifier */
  id: string;
  /** Project files */
  files?: ProjectFileResponse[];
  /** Conversation history */
  conversation_history?: ConversationMessage[];
  /** Associated conversation ID */
  conversation_id?: string;
  /** GitHub repository URL */
  github_repo_url?: string;
  /** Vercel deployment URL */
  vercel_url?: string;
  /** Project creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
}

// ============================================
// Billing Types
// ============================================

export interface SubscriptionPlanResponse {
  /** Plan name */
  name?: string;
  /** Plan price in EUR */
  price: number;
  /** Currency code */
  currency?: string;
  /** Billing interval */
  interval?: string;
  /** List of included features */
  features: string[];
}

export interface CheckoutSessionResponse {
  /** Stripe checkout session ID */
  session_id: string;
  /** Checkout session URL */
  url: any;
}

export interface InvoiceResponse {
  /** Invoice ID */
  id: string;
  /** Invoice amount */
  amount: number;
  /** Currency code */
  currency: string;
  /** Invoice status (paid, open, void, uncollectible) */
  status: string;
  /** PDF invoice URL */
  invoice_pdf?: any;
  /** Creation timestamp (Unix) */
  created: number;
}

// ============================================
// Generation Types
// ============================================

export interface GenerateRequest {
  /** User prompt for code generation */
  message: string;
  /** LLM model to use */
  model?: string;
  /** API key for LLM provider */
  api_key: string;
  /** Previous conversation context */
  conversation_history?: ConversationMessage[];
}

export interface GenerateResponse {
  /** Generated code or response */
  response: string;
  /** Model used for generation */
  model: string;
  /** Whether context compression was applied */
  context_compressed?: boolean;
}

export interface AgenticRequest {
  /** User request */
  message: string;
  /** LLM model */
  model?: string;
  /** API key */
  api_key: string;
  /** Current project files */
  current_files?: ProjectFileResponse[];
  /** Conversation history */
  conversation_history?: ConversationMessage[];
  /** Project ID for context */
  project_id?: string;
  /** User ID for memory integration */
  user_id?: string;
}

export interface AgenticResponse {
  /** Whether generation succeeded */
  success: boolean;
  /** Generated files */
  files: ProjectFileResponse[];
  /** Summary message */
  message: string;
  /** Number of agent iterations */
  iterations?: number;
  /** Generation progress events */
  progress_events?: ProgressEvent[];
  /** Context compression applied */
  context_compressed?: boolean;
  /** Compression statistics */
  compression_stats?: CompressionStats;
  /** Whether persistent memory was used */
  memory_enabled?: boolean;
}

export interface FullStackRequest {
  /** Project requirements */
  message: string;
  /** LLM model */
  model?: string;
  /** API key */
  api_key: string;
  /** Existing files */
  current_files?: ProjectFileResponse[];
  /** Conversation history */
  conversation_history?: ConversationMessage[];
  /** Project type (saas, ecommerce, blog, dashboard, api) */
  project_type?: string;
  /** Project ID */
  project_id?: string;
  /** User ID for memory */
  user_id?: string;
}

export interface FullStackResponse {
  /** Whether generation succeeded */
  success: boolean;
  /** Generated files */
  files: ProjectFileResponse[];
  /** Summary message */
  message: string;
  /** Number of agent iterations */
  iterations?: number;
  /** Generation progress events */
  progress_events?: ProgressEvent[];
  /** Context compression applied */
  context_compressed?: boolean;
  /** Compression statistics */
  compression_stats?: CompressionStats;
  /** Whether persistent memory was used */
  memory_enabled?: boolean;
  /** Generation mode */
  generation_mode?: string;
  /** Tech stack used */
  stack: Record<string, string[]>;
}

// ============================================
// Utility Types
// ============================================

export type SubscriptionStatus = 'inactive' | 'active' | 'canceled' | 'past_due';

export type ProjectType = 'saas' | 'ecommerce' | 'blog' | 'dashboard' | 'api' | 'custom';

export type MessageRole = 'user' | 'assistant' | 'system';

export type InvoiceStatus = 'paid' | 'open' | 'void' | 'uncollectible';

export type GenerationMode = 'simple' | 'agentic' | 'fullstack';

// ============================================
// API Response Types
// ============================================

export interface ApiError {
  error: string;
  message: string;
  detail?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  success: boolean;
}

// ============================================
// API Client Config
// ============================================

export interface ApiClientConfig {
  baseUrl: string;
  token?: string;
  timeout?: number;
}