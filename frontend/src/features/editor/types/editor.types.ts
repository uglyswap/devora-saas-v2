/**
 * Devora Editor - Type Definitions
 */

export interface EditorFile {
  id: string;
  name: string;
  content: string;
  language: string;
  path: string;
  isDirty: boolean;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface EditorProject {
  id: string;
  name: string;
  description: string;
  files: EditorFile[];
  conversationHistory: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  vercelUrl?: string;
  githubUrl?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status: 'sending' | 'sent' | 'error' | 'streaming';
  executionPlan?: ExecutionPlan;
  codeChanges?: CodeChange[];
}

export interface ExecutionPlan {
  id: string;
  description: string;
  steps: ExecutionStep[];
  status: 'pending' | 'approved' | 'executing' | 'completed' | 'cancelled';
  requiresConfirmation: boolean;
}

export interface ExecutionStep {
  id: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  fileChanges?: string[];
  error?: string;
}

export interface CodeChange {
  filePath: string;
  originalContent: string;
  newContent: string;
  diff?: string;
  type: 'create' | 'modify' | 'delete';
}

export type PreviewMode = 'desktop' | 'tablet' | 'mobile';
export type EditorTheme = 'vs-dark' | 'light' | 'hc-black';

export interface EditorSettings {
  theme: EditorTheme;
  fontSize: number;
  tabSize: number;
  wordWrap: 'on' | 'off' | 'wordWrapColumn';
  minimap: boolean;
  lineNumbers: 'on' | 'off' | 'relative';
  autoSave: boolean;
  autoSaveDelay: number;
}

export interface EditorState {
  // Project
  project: EditorProject | null;
  projectId: string | null;
  
  // Files
  files: Record<string, EditorFile>;
  activeFileId: string | null;
  openFileIds: string[];
  
  // UI State
  sidebarOpen: boolean;
  chatOpen: boolean;
  previewMode: PreviewMode;
  isFullscreen: boolean;
  
  // Generation
  isGenerating: boolean;
  generationProgress: number;
  
  // Settings
  settings: EditorSettings;
  
  // Status
  hasUnsavedChanges: boolean;
  lastSaved: Date | null;
  error: string | null;
}

export interface EditorActions {
  // Project
  loadProject: (projectId: string) => Promise<void>;
  saveProject: () => Promise<void>;
  createProject: (name: string, description: string) => Promise<string>;
  
  // Files
  setActiveFile: (fileId: string) => void;
  updateFileContent: (fileId: string, content: string) => void;
  createFile: (file: Omit<EditorFile, 'id' | 'isDirty'>) => string;
  deleteFile: (fileId: string) => void;
  renameFile: (fileId: string, newName: string) => void;
  closeFile: (fileId: string) => void;
  
  // UI
  toggleSidebar: () => void;
  toggleChat: () => void;
  setPreviewMode: (mode: PreviewMode) => void;
  toggleFullscreen: () => void;
  
  // Generation
  generateCode: (prompt: string) => Promise<void>;
  cancelGeneration: () => void;
  
  // Settings
  updateSettings: (settings: Partial<EditorSettings>) => void;
  
  // Error
  clearError: () => void;
}

export type EditorStore = EditorState & EditorActions;
