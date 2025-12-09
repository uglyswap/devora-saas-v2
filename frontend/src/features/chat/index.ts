/**
 * AI Chat Feature - Main Export
 * Agent: AI Chat Engineer
 *
 * Export centralisé pour le module de chat AI
 */

// Components
export { ChatPanel } from './components/ChatPanel';
export { ChatMessage } from './components/ChatMessage';
export { ChatInput } from './components/ChatInput';
export { ExecutionPlanCard } from './components/ExecutionPlanCard';
export { CodeDiff } from './components/CodeDiff';
export { StreamingIndicator } from './components/StreamingIndicator';
export { SuggestedPrompts } from './components/SuggestedPrompts';

// Hooks
export { useAIChat } from './hooks/useAIChat';
export { useStreamingResponse } from './hooks/useStreamingResponse';

// Store
export { useAIChatStore } from './stores/aiChatStore';

// Types
export type {
  AIChatMessage,
  ChatSession,
  ExecutionPlan,
  ExecutionStep,
  FileChange,
  FileDiff,
  DiffChunk,
  ChatRequest,
  ChatResponse,
  ChatOptions,
  ChatContext,
  StreamChunk,
  StreamChunkType,
  SuggestedPrompt,
  PromptCategory,
  PlanStatus,
  StepStatus,
  StepAction,
} from './types/chat.types';
