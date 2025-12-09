/**
 * Devora Collaboration - Type Definitions
 */

export interface Collaborator {
  id: string;
  userId: string;
  name: string;
  email?: string;
  avatar?: string;
  color: string;
  cursor?: CursorPosition;
  selection?: SelectionRange;
  isActive: boolean;
  lastSeen: Date;
}

export interface CursorPosition {
  line: number;
  column: number;
  fileId: string;
}

export interface SelectionRange {
  startLine: number;
  startColumn: number;
  endLine: number;
  endColumn: number;
  fileId: string;
}

export interface CollaborationRoom {
  id: string;
  projectId: string;
  collaborators: Collaborator[];
  createdAt: Date;
  isActive: boolean;
}

export type ConnectionStatus = 'connecting' | 'connected' | 'syncing' | 'synced' | 'disconnected' | 'error';

export interface CollaborationState {
  // Connection
  isConnected: boolean;
  isSynced: boolean;
  connectionStatus: ConnectionStatus;
  
  // Room
  roomId: string | null;
  collaborators: Collaborator[];
  
  // Local user
  localUserId: string | null;
  localUserColor: string;
  
  // Awareness
  awarenessStates: Map<string, AwarenessState>;
}

export interface AwarenessState {
  user: {
    id: string;
    name: string;
    color: string;
  };
  cursor?: CursorPosition;
  selection?: SelectionRange;
}

export interface CollaborationActions {
  // Connection
  connect: (projectId: string, userId: string, userName: string) => Promise<void>;
  disconnect: () => void;
  
  // Cursor
  updateCursor: (position: CursorPosition) => void;
  updateSelection: (selection: SelectionRange | null) => void;
  
  // Presence
  setUserInfo: (name: string, color?: string) => void;
}

export type CollaborationStore = CollaborationState & CollaborationActions;

// WebSocket message types
export type CollabMessageType = 
  | 'sync-step-1'
  | 'sync-step-2'
  | 'sync-update'
  | 'awareness-update'
  | 'cursor-update'
  | 'user-joined'
  | 'user-left';

export interface CollabMessage {
  type: CollabMessageType;
  payload: unknown;
  timestamp: number;
}

// Additional types for hooks
export interface User {
  id: string;
  name: string;
  color: string;
  avatar?: string;
  cursor?: CursorPosition;
  selection?: Selection;
}

export interface Selection {
  start: { line: number; column: number };
  end: { line: number; column: number };
}

export interface CollaborationConfig {
  wsUrl: string;
  documentId: string;
  user: User;
  autoConnect?: boolean;
}

export interface CollaborationHookState {
  status: ConnectionStatus;
  users: Map<number, User>;
  currentUser: User;
  latency: number;
  error?: string;
}

export interface CollaborationHookReturn {
  state: CollaborationHookState;
  connect: () => Promise<void>;
  disconnect: () => void;
  updateCursor: (position: CursorPosition) => void;
  updateSelection: (selection: Selection) => void;
  isConnected: boolean;
  activeUsers: User[];
}

export interface CollaborationContextValue {
  state: CollaborationHookState;
  actions: {
    connect: () => Promise<void>;
    disconnect: () => void;
    updateCursor: (position: CursorPosition) => void;
    updateSelection: (selection: Selection) => void;
  };
}
