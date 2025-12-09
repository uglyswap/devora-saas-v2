/**
 * Stores Index - Zustand
 * Agent: Frontend State Management Specialist
 *
 * Export central de tous les stores et leurs selectors
 */

// ============================================
// Store Exports
// ============================================

export { useProjectStore } from './projectStore';
export type { } from './projectStore';

export { useChatStore } from './chatStore';
export type { } from './chatStore';

export { useAuthStore, getAuthHeaders } from './authStore';
export type { } from './authStore';

export {
  useSettingsStore,
  AVAILABLE_MODELS,
  SUPPORTED_LANGUAGES,
} from './settingsStore';
export type { } from './settingsStore';

// ============================================
// Selector Exports - Project Store
// ============================================

export {
  selectCurrentFile,
  selectFileByName,
  selectFileNames,
  selectProjectById,
} from './projectStore';

// ============================================
// Selector Exports - Chat Store
// ============================================

export {
  selectLastUserMessage,
  selectLastAssistantMessage,
  selectConversationHistory,
  selectIsGenerating,
} from './chatStore';

// ============================================
// Selector Exports - Auth Store
// ============================================

export {
  selectUser,
  selectIsAuthenticated,
  selectIsAdmin,
  selectSubscriptionStatus,
  selectCanAccessPremium,
} from './authStore';

// ============================================
// Selector Exports - Settings Store
// ============================================

export {
  selectTheme,
  selectEditorSettings,
  selectNotificationSettings,
  selectAutoSaveSettings,
  selectApiSettings,
  selectUIState,
} from './settingsStore';

// ============================================
// Combined Selectors & Utilities
// ============================================

import { useProjectStore } from './projectStore';
import { useChatStore } from './chatStore';
import { useAuthStore } from './authStore';
import { useSettingsStore } from './settingsStore';

/**
 * Reset tous les stores (utile pour logout ou reset complet)
 */
export const resetAllStores = (): void => {
  useProjectStore.getState().reset();
  useChatStore.getState().reset();
  useAuthStore.getState().reset();
  useSettingsStore.getState().reset();
};

/**
 * Verifie si l'utilisateur peut generer du code
 * (authentifie + abonnement actif)
 */
export const canGenerate = (): boolean => {
  const authState = useAuthStore.getState();
  return !!authState.user && authState.hasActiveSubscription();
};

/**
 * Recupere le contexte complet pour une generation
 */
export const getGenerationContext = () => {
  const projectState = useProjectStore.getState();
  const chatState = useChatStore.getState();
  const settingsState = useSettingsStore.getState();
  const authState = useAuthStore.getState();

  return {
    project: projectState.project,
    currentFiles: projectState.project?.files || [],
    conversationHistory: projectState.project?.conversation_history || [],
    model: settingsState.defaultModel,
    apiKey: settingsState.apiKey,
    userId: authState.user?.id,
    projectId: projectState.project?.id,
    mode: chatState.generationMode,
  };
};

/**
 * Hook combine pour l'etat de l'editeur
 * Utilise dans les composants d'edition
 */
export const useEditorState = () => {
  const project = useProjectStore((s) => s.project);
  const selectedFile = useProjectStore((s) => s.selectedFile);
  const hasUnsavedChanges = useProjectStore((s) => s.hasUnsavedChanges);
  const isSaving = useProjectStore((s) => s.isSaving);
  const updateFile = useProjectStore((s) => s.updateFile);
  const selectFile = useProjectStore((s) => s.selectFile);
  const saveProject = useProjectStore((s) => s.saveProject);

  const editorSettings = useSettingsStore((s) => ({
    fontSize: s.editorFontSize,
    tabSize: s.editorTabSize,
    wordWrap: s.editorWordWrap,
    lineNumbers: s.showLineNumbers,
  }));

  const autoSave = useSettingsStore((s) => s.autoSave);
  const autoSaveDelay = useSettingsStore((s) => s.autoSaveDelay);

  const currentFile = project?.files.find((f) => f.name === selectedFile) || null;

  return {
    project,
    files: project?.files || [],
    currentFile,
    selectedFile,
    hasUnsavedChanges,
    isSaving,
    editorSettings,
    autoSave,
    autoSaveDelay,
    updateFile,
    selectFile,
    saveProject,
  };
};

/**
 * Hook combine pour l'etat du chat
 */
export const useChatState = () => {
  const messages = useChatStore((s) => s.messages);
  const isGenerating = useChatStore((s) => s.isGenerating);
  const isThinking = useChatStore((s) => s.isThinking);
  const progress = useChatStore((s) => s.progress);
  const error = useChatStore((s) => s.error);
  const generationMode = useChatStore((s) => s.generationMode);
  const currentModel = useChatStore((s) => s.currentModel);

  const generate = useChatStore((s) => s.generate);
  const generateWithStreaming = useChatStore((s) => s.generateWithStreaming);
  const cancelGeneration = useChatStore((s) => s.cancelGeneration);
  const clearMessages = useChatStore((s) => s.clearMessages);
  const setGenerationMode = useChatStore((s) => s.setGenerationMode);
  const setModel = useChatStore((s) => s.setModel);

  return {
    messages,
    isGenerating,
    isThinking,
    progress,
    error,
    generationMode,
    currentModel,
    generate,
    generateWithStreaming,
    cancelGeneration,
    clearMessages,
    setGenerationMode,
    setModel,
  };
};

/**
 * Hook combine pour l'etat d'authentification
 */
export const useAuthState = () => {
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.token);
  const isLoading = useAuthStore((s) => s.isLoading);
  const isInitialized = useAuthStore((s) => s.isInitialized);
  const error = useAuthStore((s) => s.error);

  const login = useAuthStore((s) => s.login);
  const register = useAuthStore((s) => s.register);
  const logout = useAuthStore((s) => s.logout);
  const refreshUser = useAuthStore((s) => s.refreshUser);
  const initialize = useAuthStore((s) => s.initialize);
  const hasActiveSubscription = useAuthStore((s) => s.hasActiveSubscription);
  const isTrialing = useAuthStore((s) => s.isTrialing);
  const getTrialDaysLeft = useAuthStore((s) => s.getTrialDaysLeft);

  const isAuthenticated = !!token && !!user;
  const isAdmin = user?.is_admin || false;
  const canAccessPremium =
    user?.subscription_status === 'active' || user?.subscription_status === 'trialing';

  return {
    user,
    token,
    isLoading,
    isInitialized,
    error,
    isAuthenticated,
    isAdmin,
    canAccessPremium,
    login,
    register,
    logout,
    refreshUser,
    initialize,
    hasActiveSubscription,
    isTrialing,
    getTrialDaysLeft,
  };
};
