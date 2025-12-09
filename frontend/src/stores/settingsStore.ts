/**
 * Settings Store - Zustand
 * Agent: Frontend State Management Specialist
 *
 * Gestion des parametres utilisateur avec persistance locale
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { UserSettings, NotificationSettings, GenerationMode } from '../types';

// ============================================
// Types
// ============================================

type Theme = 'light' | 'dark' | 'system';

interface SettingsState extends UserSettings {
  // Additional State
  isLoading: boolean;
  isSidebarCollapsed: boolean;
  activePanel: 'files' | 'chat' | 'preview' | 'settings';
  previewMode: 'desktop' | 'tablet' | 'mobile';
  showPreview: boolean;

  // Theme Actions
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;

  // Editor Actions
  setEditorFontSize: (size: number) => void;
  setEditorTabSize: (size: number) => void;
  setEditorWordWrap: (enabled: boolean) => void;
  setShowLineNumbers: (show: boolean) => void;

  // Auto-Save Actions
  setAutoSave: (enabled: boolean) => void;
  setAutoSaveDelay: (delay: number) => void;

  // Notification Actions
  setNotifications: (settings: Partial<NotificationSettings>) => void;
  toggleNotification: (key: keyof NotificationSettings) => void;

  // API Settings
  setDefaultModel: (model: string) => void;
  setApiKey: (key: string | undefined) => void;

  // Language Settings
  setLanguage: (language: string) => void;

  // UI State Actions
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
  setActivePanel: (panel: 'files' | 'chat' | 'preview' | 'settings') => void;
  setPreviewMode: (mode: 'desktop' | 'tablet' | 'mobile') => void;
  setShowPreview: (show: boolean) => void;
  togglePreview: () => void;

  // Utility Actions
  reset: () => void;
  importSettings: (settings: Partial<UserSettings>) => void;
  exportSettings: () => UserSettings;
}

// ============================================
// Default Values
// ============================================

const defaultNotifications: NotificationSettings = {
  email: true,
  push: true,
  generationComplete: true,
  subscriptionReminder: true,
};

const defaultSettings: UserSettings = {
  theme: 'system',
  language: 'fr',
  editorFontSize: 14,
  editorTabSize: 2,
  editorWordWrap: true,
  autoSave: true,
  autoSaveDelay: 5000, // 5 seconds
  showLineNumbers: true,
  notifications: defaultNotifications,
  defaultModel: 'gpt-4',
  apiKey: undefined,
};

const initialState = {
  ...defaultSettings,
  isLoading: false,
  isSidebarCollapsed: false,
  activePanel: 'files' as const,
  previewMode: 'desktop' as const,
  showPreview: true,
};

// ============================================
// Theme Helper
// ============================================

const applyTheme = (theme: Theme) => {
  if (typeof window === 'undefined') return;

  const root = window.document.documentElement;
  root.classList.remove('light', 'dark');

  if (theme === 'system') {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
    root.classList.add(systemTheme);
  } else {
    root.classList.add(theme);
  }
};

// ============================================
// Store
// ============================================

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,

        // ========================================
        // Theme Actions
        // ========================================

        setTheme: (theme: Theme) => {
          set((state) => {
            state.theme = theme;
          });
          applyTheme(theme);
        },

        toggleTheme: () => {
          const currentTheme = get().theme;
          const themes: Theme[] = ['light', 'dark', 'system'];
          const currentIndex = themes.indexOf(currentTheme);
          const nextTheme = themes[(currentIndex + 1) % themes.length];

          set((state) => {
            state.theme = nextTheme;
          });
          applyTheme(nextTheme);
        },

        // ========================================
        // Editor Actions
        // ========================================

        setEditorFontSize: (size: number) => {
          // Clamp between 10 and 24
          const clampedSize = Math.min(Math.max(size, 10), 24);
          set((state) => {
            state.editorFontSize = clampedSize;
          });
        },

        setEditorTabSize: (size: number) => {
          // Clamp between 2 and 8
          const clampedSize = Math.min(Math.max(size, 2), 8);
          set((state) => {
            state.editorTabSize = clampedSize;
          });
        },

        setEditorWordWrap: (enabled: boolean) => {
          set((state) => {
            state.editorWordWrap = enabled;
          });
        },

        setShowLineNumbers: (show: boolean) => {
          set((state) => {
            state.showLineNumbers = show;
          });
        },

        // ========================================
        // Auto-Save Actions
        // ========================================

        setAutoSave: (enabled: boolean) => {
          set((state) => {
            state.autoSave = enabled;
          });
        },

        setAutoSaveDelay: (delay: number) => {
          // Clamp between 1 second and 60 seconds
          const clampedDelay = Math.min(Math.max(delay, 1000), 60000);
          set((state) => {
            state.autoSaveDelay = clampedDelay;
          });
        },

        // ========================================
        // Notification Actions
        // ========================================

        setNotifications: (settings: Partial<NotificationSettings>) => {
          set((state) => {
            state.notifications = { ...state.notifications, ...settings };
          });
        },

        toggleNotification: (key: keyof NotificationSettings) => {
          set((state) => {
            state.notifications[key] = !state.notifications[key];
          });
        },

        // ========================================
        // API Settings
        // ========================================

        setDefaultModel: (model: string) => {
          set((state) => {
            state.defaultModel = model;
          });
        },

        setApiKey: (key: string | undefined) => {
          set((state) => {
            state.apiKey = key;
          });
        },

        // ========================================
        // Language Settings
        // ========================================

        setLanguage: (language: string) => {
          set((state) => {
            state.language = language;
          });

          // Trigger i18next language change if available
          if (typeof window !== 'undefined' && (window as any).i18n) {
            (window as any).i18n.changeLanguage(language);
          }
        },

        // ========================================
        // UI State Actions
        // ========================================

        setSidebarCollapsed: (collapsed: boolean) => {
          set((state) => {
            state.isSidebarCollapsed = collapsed;
          });
        },

        toggleSidebar: () => {
          set((state) => {
            state.isSidebarCollapsed = !state.isSidebarCollapsed;
          });
        },

        setActivePanel: (panel: 'files' | 'chat' | 'preview' | 'settings') => {
          set((state) => {
            state.activePanel = panel;
          });
        },

        setPreviewMode: (mode: 'desktop' | 'tablet' | 'mobile') => {
          set((state) => {
            state.previewMode = mode;
          });
        },

        setShowPreview: (show: boolean) => {
          set((state) => {
            state.showPreview = show;
          });
        },

        togglePreview: () => {
          set((state) => {
            state.showPreview = !state.showPreview;
          });
        },

        // ========================================
        // Utility Actions
        // ========================================

        reset: () => {
          set((state) => {
            Object.assign(state, initialState);
          });
          applyTheme(defaultSettings.theme);
        },

        importSettings: (settings: Partial<UserSettings>) => {
          set((state) => {
            if (settings.theme) state.theme = settings.theme;
            if (settings.language) state.language = settings.language;
            if (settings.editorFontSize) state.editorFontSize = settings.editorFontSize;
            if (settings.editorTabSize) state.editorTabSize = settings.editorTabSize;
            if (settings.editorWordWrap !== undefined)
              state.editorWordWrap = settings.editorWordWrap;
            if (settings.autoSave !== undefined) state.autoSave = settings.autoSave;
            if (settings.autoSaveDelay) state.autoSaveDelay = settings.autoSaveDelay;
            if (settings.showLineNumbers !== undefined)
              state.showLineNumbers = settings.showLineNumbers;
            if (settings.notifications)
              state.notifications = { ...state.notifications, ...settings.notifications };
            if (settings.defaultModel) state.defaultModel = settings.defaultModel;
            if (settings.apiKey !== undefined) state.apiKey = settings.apiKey;
          });

          // Apply theme after import
          const newTheme = settings.theme || get().theme;
          applyTheme(newTheme);
        },

        exportSettings: (): UserSettings => {
          const state = get();
          return {
            theme: state.theme,
            language: state.language,
            editorFontSize: state.editorFontSize,
            editorTabSize: state.editorTabSize,
            editorWordWrap: state.editorWordWrap,
            autoSave: state.autoSave,
            autoSaveDelay: state.autoSaveDelay,
            showLineNumbers: state.showLineNumbers,
            notifications: { ...state.notifications },
            defaultModel: state.defaultModel,
            // Intentionally exclude apiKey for security
          };
        },
      })),
      {
        name: 'devora-settings-store',
        partialize: (state) => ({
          // Persist all settings except sensitive data
          theme: state.theme,
          language: state.language,
          editorFontSize: state.editorFontSize,
          editorTabSize: state.editorTabSize,
          editorWordWrap: state.editorWordWrap,
          autoSave: state.autoSave,
          autoSaveDelay: state.autoSaveDelay,
          showLineNumbers: state.showLineNumbers,
          notifications: state.notifications,
          defaultModel: state.defaultModel,
          isSidebarCollapsed: state.isSidebarCollapsed,
          showPreview: state.showPreview,
          // Note: apiKey is NOT persisted for security
        }),
        onRehydrateStorage: () => (state) => {
          // Apply theme after rehydration
          if (state?.theme) {
            applyTheme(state.theme);
          }
        },
      }
    ),
    { name: 'SettingsStore' }
  )
);

// ============================================
// Selectors
// ============================================

export const selectTheme = (state: SettingsState): Theme => state.theme;

export const selectEditorSettings = (state: SettingsState) => ({
  fontSize: state.editorFontSize,
  tabSize: state.editorTabSize,
  wordWrap: state.editorWordWrap,
  lineNumbers: state.showLineNumbers,
});

export const selectNotificationSettings = (state: SettingsState): NotificationSettings =>
  state.notifications;

export const selectAutoSaveSettings = (state: SettingsState) => ({
  enabled: state.autoSave,
  delay: state.autoSaveDelay,
});

export const selectApiSettings = (state: SettingsState) => ({
  model: state.defaultModel,
  apiKey: state.apiKey,
});

export const selectUIState = (state: SettingsState) => ({
  sidebarCollapsed: state.isSidebarCollapsed,
  activePanel: state.activePanel,
  previewMode: state.previewMode,
  showPreview: state.showPreview,
});

// ============================================
// Available Models Configuration
// ============================================

export const AVAILABLE_MODELS = [
  { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI', recommended: true },
  { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', provider: 'OpenAI', recommended: true },
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'OpenAI', recommended: false },
  { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'Anthropic', recommended: true },
  { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'Anthropic', recommended: false },
] as const;

export const SUPPORTED_LANGUAGES = [
  { code: 'fr', name: 'Francais', flag: '' },
  { code: 'en', name: 'English', flag: '' },
  { code: 'es', name: 'Espanol', flag: '' },
  { code: 'de', name: 'Deutsch', flag: '' },
] as const;
