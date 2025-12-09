/**
 * Devora AI Chat - Type Definitions
 */

export type MessageRole = 'user' | 'assistant' | 'system';
export type MessageStatus = 'sending' | 'sent' | 'error' | 'streaming';
export type ActionType = 'execute' | 'modify' | 'cancel' | 'approve' | 'reject';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  status: MessageStatus;
  executionPlan?: ExecutionPlan;
  codeChanges?: CodeChange[];
  actions?: ActionType[];
  metadata?: MessageMetadata;
}

export interface MessageMetadata {
  model?: string;
  tokens?: number;
  duration?: number;
  context?: string[];
}

export interface ExecutionPlan {
  id: string;
  title: string;
  description: string;
  steps: ExecutionStep[];
  codeChanges: CodeChange[];
  status: 'pending' | 'approved' | 'executing' | 'completed' | 'cancelled' | 'failed';
  requiresConfirmation: boolean;
  estimatedChanges: number;
}

export interface ExecutionStep {
  id: string;
  order: number;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  duration?: number;
  error?: string;
}

export interface CodeChange {
  id: string;
  filePath: string;
  type: 'create' | 'modify' | 'delete' | 'rename';
  originalContent?: string;
  newContent?: string;
  diff?: string;
  language?: string;
}

export interface ChatContext {
  projectId: string;
  projectName: string;
  currentFile?: {
    path: string;
    content: string;
    language: string;
  };
  allFiles: Array<{
    path: string;
    language: string;
  }>;
  conversationHistory: ChatMessage[];
}

export interface ChatState {
  // Messages
  messages: ChatMessage[];
  
  // Streaming
  isLoading: boolean;
  isStreaming: boolean;
  currentStreamContent: string;
  
  // Plans
  pendingPlan: ExecutionPlan | null;
  executingPlanId: string | null;
  
  // UI
  inputValue: string;
  showSuggestions: boolean;
  selectedSuggestionIndex: number;
}

export interface ChatActions {
  // Messages
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => string;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  deleteMessage: (id: string) => void;
  clearMessages: () => void;
  
  // Streaming
  appendToStream: (content: string) => void;
  finalizeStream: (messageId: string) => void;
  setLoading: (loading: boolean) => void;
  
  // Plans
  setPendingPlan: (plan: ExecutionPlan | null) => void;
  approvePlan: (planId: string) => Promise<void>;
  rejectPlan: (planId: string) => void;
  modifyPlan: (planId: string, modifications: string) => void;
  
  // UI
  setInputValue: (value: string) => void;
  toggleSuggestions: (show: boolean) => void;
  selectSuggestion: (index: number) => void;
}

export type ChatStore = ChatState & ChatActions;

// Suggested prompts
export interface SuggestedPrompt {
  id: string;
  text: string;
  category: 'feature' | 'fix' | 'refactor' | 'explain' | 'test';
  icon?: string;
}

export const defaultSuggestedPrompts: SuggestedPrompt[] = [
  { id: '1', text: 'Add user authentication with JWT', category: 'feature' },
  { id: '2', text: 'Create a responsive navigation component', category: 'feature' },
  { id: '3', text: 'Add dark mode support', category: 'feature' },
  { id: '4', text: 'Fix the layout on mobile devices', category: 'fix' },
  { id: '5', text: 'Optimize the performance of this component', category: 'refactor' },
  { id: '6', text: 'Explain how this code works', category: 'explain' },
  { id: '7', text: 'Write unit tests for this component', category: 'test' },
  { id: '8', text: 'Add form validation with error messages', category: 'feature' },
];
