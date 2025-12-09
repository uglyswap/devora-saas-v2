/**
 * Devora Frontend TypeScript Types
 * Agent: Frontend State Management Specialist
 *
 * Types pour les stores Zustand et l'API
 */

// ============================================
// User Types
// ============================================

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  subscription_status: SubscriptionStatus;
  current_period_end?: string;
  created_at: string;
}

export type SubscriptionStatus = 'inactive' | 'active' | 'trialing' | 'canceled' | 'past_due';

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// ============================================
// Project Types
// ============================================

export interface Project {
  id: string;
  name: string;
  description?: string;
  project_type?: ProjectType;
  files: ProjectFile[];
  conversation_history: ConversationMessage[];
  conversation_id?: string;
  github_repo_url?: string;
  vercel_url?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  project_type?: ProjectType;
  files?: ProjectFileCreate[];
  conversation_history?: ConversationMessage[];
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  files?: ProjectFileCreate[];
  conversation_history?: ConversationMessage[];
}

export type ProjectType = 'saas' | 'ecommerce' | 'blog' | 'dashboard' | 'api' | 'custom';

// ============================================
// File Types
// ============================================

export interface ProjectFile {
  name: string;
  content: string;
  language: string;
}

export interface ProjectFileCreate {
  name: string;
  content: string;
  language: string;
}

// ============================================
// Chat & Generation Types
// ============================================

export interface ConversationMessage {
  role: MessageRole;
  content: string;
}

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  isThinking?: boolean;
  isStreaming?: boolean;
}

export interface GenerationProgress {
  step: string;
  progress: number;
  message: string;
  currentFile?: string;
  isComplete: boolean;
}

export interface GenerationResult {
  success: boolean;
  files: ProjectFile[];
  message: string;
  iterations?: number;
  context_compressed?: boolean;
  memory_enabled?: boolean;
}

export interface GenerateRequest {
  message: string;
  model?: string;
  api_key: string;
  conversation_history?: ConversationMessage[];
}

export interface AgenticRequest {
  message: string;
  model?: string;
  api_key: string;
  current_files?: ProjectFile[];
  conversation_history?: ConversationMessage[];
  project_id?: string;
  user_id?: string;
}

export interface FullStackRequest {
  message: string;
  model?: string;
  api_key: string;
  current_files?: ProjectFile[];
  conversation_history?: ConversationMessage[];
  project_type?: ProjectType;
  project_id?: string;
  user_id?: string;
}

// ============================================
// Billing Types
// ============================================

export interface SubscriptionPlan {
  name: string;
  price: number;
  currency: string;
  interval: string;
  features: string[];
}

export interface CheckoutSession {
  session_id: string;
  url: string;
}

export interface Invoice {
  id: string;
  amount: number;
  currency: string;
  status: InvoiceStatus;
  invoice_pdf?: string;
  created: number;
}

export type InvoiceStatus = 'paid' | 'open' | 'void' | 'uncollectible';

// ============================================
// Settings Types
// ============================================

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  editorFontSize: number;
  editorTabSize: number;
  editorWordWrap: boolean;
  autoSave: boolean;
  autoSaveDelay: number;
  showLineNumbers: boolean;
  notifications: NotificationSettings;
  defaultModel: string;
  apiKey?: string;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  generationComplete: boolean;
  subscriptionReminder: boolean;
}

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
// Utility Types
// ============================================

export type GenerationMode = 'simple' | 'agentic' | 'fullstack';

export interface FileTreeItem {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: FileTreeItem[];
  language?: string;
}

export interface EditorTab {
  name: string;
  content: string;
  language: string;
  isDirty: boolean;
}
