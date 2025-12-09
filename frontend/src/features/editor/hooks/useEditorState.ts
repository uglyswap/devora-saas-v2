/**
 * Store Zustand centralisé pour l'éditeur
 * Remplace les 25+ useState du fichier original
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  EditorStore,
  EditorProject,
  ChatMessage,
  ModelOption,
  createEmptyProject,
} from '../types/editor.types';
import { ProjectFile } from '../../../types/project';

/**
 * État initial de l'éditeur
 */
const initialState = {
  // Projet
  project: createEmptyProject(),
  currentFileIndex: 0,

  // Chat IA
  chatMessages: [],
  generating: false,

  // Configuration IA
  apiKey: '',
  selectedModel: 'openai/gpt-4o',
  availableModels: [],
  useAgenticMode: true,
  useFullstackMode: false,

  // UI
  showEditor: true,
  copied: false,

  // Loading states
  loading: false,
  previewLoading: false,

  // Export & Deploy
  previewUrl: null,
  githubToken: '',
  vercelToken: '',

  // Dialogs
  showGithubDialog: false,
  showVercelDialog: false,
};

/**
 * Hook store Zustand avec immer pour les mutations
 */
export const useEditorStore = create<EditorStore>()(
  devtools(
    immer((set) => ({
      ...initialState,

      // ============ PROJET ============
      setProject: (project: EditorProject) =>
        set((state) => {
          state.project = project;
          // Restaurer l'historique de conversation s'il existe
          if (project.conversation_history?.length > 0) {
            state.chatMessages = project.conversation_history;
          }
          // Restaurer l'URL de preview si elle existe
          if (project.vercel_url) {
            state.previewUrl = project.vercel_url;
          }
          // Réinitialiser l'index du fichier
          state.currentFileIndex = 0;
        }),

      updateProjectName: (name: string) =>
        set((state) => {
          state.project.name = name;
        }),

      updateProjectDescription: (description: string) =>
        set((state) => {
          state.project.description = description;
        }),

      // ============ FICHIERS ============
      setCurrentFileIndex: (index: number) =>
        set((state) => {
          state.currentFileIndex = index;
        }),

      updateFileContent: (index: number, content: string) =>
        set((state) => {
          if (state.project.files[index]) {
            state.project.files[index].content = content;
          }
        }),

      addFile: (file: ProjectFile) =>
        set((state) => {
          state.project.files.push(file);
          state.currentFileIndex = state.project.files.length - 1;
        }),

      deleteFile: (index: number) =>
        set((state) => {
          if (state.project.files.length > 1) {
            state.project.files.splice(index, 1);
            // Ajuster l'index courant si nécessaire
            if (state.currentFileIndex >= index && state.currentFileIndex > 0) {
              state.currentFileIndex--;
            }
          }
        }),

      // ============ CHAT ============
      addChatMessage: (message: ChatMessage) =>
        set((state) => {
          state.chatMessages.push(message);
          // Synchroniser avec l'historique du projet
          state.project.conversation_history = state.chatMessages;
        }),

      clearChatMessages: () =>
        set((state) => {
          state.chatMessages = [];
          state.project.conversation_history = [];
        }),

      setGenerating: (generating: boolean) =>
        set((state) => {
          state.generating = generating;
        }),

      // ============ CONFIGURATION ============
      setApiKey: (apiKey: string) =>
        set((state) => {
          state.apiKey = apiKey;
        }),

      setSelectedModel: (model: string) =>
        set((state) => {
          state.selectedModel = model;
        }),

      setAvailableModels: (models: ModelOption[]) =>
        set((state) => {
          state.availableModels = models;
        }),

      setUseAgenticMode: (use: boolean) =>
        set((state) => {
          state.useAgenticMode = use;
        }),

      setUseFullstackMode: (use: boolean) =>
        set((state) => {
          state.useFullstackMode = use;
        }),

      // ============ UI ============
      setShowEditor: (show: boolean) =>
        set((state) => {
          state.showEditor = show;
        }),

      setCopied: (copied: boolean) =>
        set((state) => {
          state.copied = copied;
        }),

      // ============ LOADING ============
      setLoading: (loading: boolean) =>
        set((state) => {
          state.loading = loading;
        }),

      setPreviewLoading: (loading: boolean) =>
        set((state) => {
          state.previewLoading = loading;
        }),

      // ============ EXPORT & DEPLOY ============
      setPreviewUrl: (url: string | null) =>
        set((state) => {
          state.previewUrl = url;
          if (url) {
            state.project.vercel_url = url;
          }
        }),

      setGithubToken: (token: string) =>
        set((state) => {
          state.githubToken = token;
        }),

      setVercelToken: (token: string) =>
        set((state) => {
          state.vercelToken = token;
        }),

      // ============ DIALOGS ============
      setShowGithubDialog: (show: boolean) =>
        set((state) => {
          state.showGithubDialog = show;
        }),

      setShowVercelDialog: (show: boolean) =>
        set((state) => {
          state.showVercelDialog = show;
        }),

      // ============ RESET ============
      resetEditor: () =>
        set((state) => {
          Object.assign(state, initialState);
        }),
    })),
    { name: 'EditorStore' }
  )
);

/**
 * Sélecteurs optimisés pour éviter les re-renders inutiles
 */
export const selectProject = (state: EditorStore) => state.project;
export const selectCurrentFile = (state: EditorStore) =>
  state.project.files[state.currentFileIndex];
export const selectChatMessages = (state: EditorStore) => state.chatMessages;
export const selectGenerating = (state: EditorStore) => state.generating;
export const selectApiConfig = (state: EditorStore) => ({
  apiKey: state.apiKey,
  selectedModel: state.selectedModel,
  useAgenticMode: state.useAgenticMode,
  useFullstackMode: state.useFullstackMode,
});
export const selectLoading = (state: EditorStore) => ({
  loading: state.loading,
  previewLoading: state.previewLoading,
  generating: state.generating,
});
