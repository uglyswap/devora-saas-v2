/**
 * Project Store - Zustand
 * Agent: Frontend State Management Specialist
 *
 * Gestion de l'etat des projets avec persistance locale
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import axios from 'axios';
import type {
  Project,
  ProjectCreate,
  ProjectFile,
  ProjectFileCreate,
  ConversationMessage,
} from '../types';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// ============================================
// Types
// ============================================

interface ProjectState {
  // State
  project: Project | null;
  projects: Project[];
  selectedFile: string | null;
  isLoading: boolean;
  isSaving: boolean;
  isLoadingList: boolean;
  error: string | null;
  lastSaved: number | null;
  hasUnsavedChanges: boolean;

  // Project CRUD Actions
  loadProject: (id: string) => Promise<void>;
  loadProjects: () => Promise<void>;
  saveProject: () => Promise<void>;
  createProject: (data: ProjectCreate) => Promise<string>;
  deleteProject: (id: string) => Promise<void>;
  duplicateProject: (id: string) => Promise<string>;

  // File Actions
  selectFile: (name: string | null) => void;
  updateFile: (name: string, content: string) => void;
  createFile: (name: string, content?: string, language?: string) => void;
  deleteFile: (name: string) => void;
  renameFile: (oldName: string, newName: string) => void;

  // Project State Actions
  setProject: (project: Project | null) => void;
  updateProjectMeta: (data: Partial<Pick<Project, 'name' | 'description'>>) => void;
  addConversationMessage: (message: ConversationMessage) => void;
  setFiles: (files: ProjectFile[]) => void;

  // Utility Actions
  reset: () => void;
  clearError: () => void;
  markAsSaved: () => void;
}

// ============================================
// Initial State
// ============================================

const initialState = {
  project: null,
  projects: [],
  selectedFile: null,
  isLoading: false,
  isSaving: false,
  isLoadingList: false,
  error: null,
  lastSaved: null,
  hasUnsavedChanges: false,
};

// ============================================
// Utility Functions
// ============================================

/**
 * Detecte le langage d'un fichier selon son extension
 */
const detectLanguage = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  const languageMap: Record<string, string> = {
    js: 'javascript',
    jsx: 'javascript',
    ts: 'typescript',
    tsx: 'typescript',
    py: 'python',
    html: 'html',
    css: 'css',
    scss: 'scss',
    sass: 'sass',
    less: 'less',
    json: 'json',
    md: 'markdown',
    yaml: 'yaml',
    yml: 'yaml',
    xml: 'xml',
    sql: 'sql',
    sh: 'shell',
    bash: 'shell',
    dockerfile: 'dockerfile',
    gitignore: 'plaintext',
    env: 'plaintext',
  };
  return languageMap[ext] || 'plaintext';
};

// ============================================
// Store
// ============================================

export const useProjectStore = create<ProjectState>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,

        // ========================================
        // Project CRUD Actions
        // ========================================

        loadProject: async (id: string) => {
          set((state) => {
            state.isLoading = true;
            state.error = null;
          });

          try {
            const response = await axios.get<Project>(`${API_URL}/api/projects/${id}`);
            const project = response.data;

            set((state) => {
              state.project = project;
              state.isLoading = false;
              state.hasUnsavedChanges = false;
              // Selectionner le premier fichier si disponible
              if (project.files && project.files.length > 0) {
                state.selectedFile = project.files[0].name;
              }
            });
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || error.message
              : 'Erreur lors du chargement du projet';

            set((state) => {
              state.error = message;
              state.isLoading = false;
            });
            throw new Error(message);
          }
        },

        loadProjects: async () => {
          set((state) => {
            state.isLoadingList = true;
            state.error = null;
          });

          try {
            const response = await axios.get<Project[]>(`${API_URL}/api/projects`);

            set((state) => {
              state.projects = response.data;
              state.isLoadingList = false;
            });
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || error.message
              : 'Erreur lors du chargement des projets';

            set((state) => {
              state.error = message;
              state.isLoadingList = false;
            });
          }
        },

        saveProject: async () => {
          const { project, hasUnsavedChanges } = get();
          if (!project || !hasUnsavedChanges) return;

          set((state) => {
            state.isSaving = true;
            state.error = null;
          });

          try {
            const response = await axios.put<Project>(
              `${API_URL}/api/projects/${project.id}`,
              {
                name: project.name,
                description: project.description,
                files: project.files,
                conversation_history: project.conversation_history,
              }
            );

            set((state) => {
              state.project = response.data;
              state.isSaving = false;
              state.lastSaved = Date.now();
              state.hasUnsavedChanges = false;
            });
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || error.message
              : 'Erreur lors de la sauvegarde';

            set((state) => {
              state.error = message;
              state.isSaving = false;
            });
            throw new Error(message);
          }
        },

        createProject: async (data: ProjectCreate) => {
          set((state) => {
            state.isLoading = true;
            state.error = null;
          });

          try {
            const response = await axios.post<Project>(`${API_URL}/api/projects`, data);
            const newProject = response.data;

            set((state) => {
              state.project = newProject;
              state.projects.unshift(newProject);
              state.isLoading = false;
              state.hasUnsavedChanges = false;
              state.selectedFile = newProject.files?.[0]?.name || null;
            });

            return newProject.id;
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || error.message
              : 'Erreur lors de la creation du projet';

            set((state) => {
              state.error = message;
              state.isLoading = false;
            });
            throw new Error(message);
          }
        },

        deleteProject: async (id: string) => {
          try {
            await axios.delete(`${API_URL}/api/projects/${id}`);

            set((state) => {
              state.projects = state.projects.filter((p) => p.id !== id);
              if (state.project?.id === id) {
                state.project = null;
                state.selectedFile = null;
                state.hasUnsavedChanges = false;
              }
            });
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || error.message
              : 'Erreur lors de la suppression';

            set((state) => {
              state.error = message;
            });
            throw new Error(message);
          }
        },

        duplicateProject: async (id: string) => {
          set((state) => {
            state.isLoading = true;
            state.error = null;
          });

          try {
            // Charger le projet source
            const response = await axios.get<Project>(`${API_URL}/api/projects/${id}`);
            const sourceProject = response.data;

            // Creer la copie
            const newProjectData: ProjectCreate = {
              name: `${sourceProject.name} (copie)`,
              description: sourceProject.description,
              project_type: sourceProject.project_type,
              files: sourceProject.files,
            };

            const createResponse = await axios.post<Project>(
              `${API_URL}/api/projects`,
              newProjectData
            );
            const newProject = createResponse.data;

            set((state) => {
              state.projects.unshift(newProject);
              state.isLoading = false;
            });

            return newProject.id;
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || error.message
              : 'Erreur lors de la duplication';

            set((state) => {
              state.error = message;
              state.isLoading = false;
            });
            throw new Error(message);
          }
        },

        // ========================================
        // File Actions
        // ========================================

        selectFile: (name: string | null) => {
          set((state) => {
            state.selectedFile = name;
          });
        },

        updateFile: (name: string, content: string) => {
          set((state) => {
            if (!state.project) return;

            const fileIndex = state.project.files.findIndex((f) => f.name === name);
            if (fileIndex !== -1) {
              state.project.files[fileIndex].content = content;
              state.hasUnsavedChanges = true;
            }
          });
        },

        createFile: (name: string, content = '', language?: string) => {
          set((state) => {
            if (!state.project) return;

            // Verifier si le fichier existe deja
            const exists = state.project.files.some((f) => f.name === name);
            if (exists) {
              state.error = `Le fichier "${name}" existe deja`;
              return;
            }

            const newFile: ProjectFile = {
              name,
              content,
              language: language || detectLanguage(name),
            };

            state.project.files.push(newFile);
            state.selectedFile = name;
            state.hasUnsavedChanges = true;
          });
        },

        deleteFile: (name: string) => {
          set((state) => {
            if (!state.project) return;

            const fileIndex = state.project.files.findIndex((f) => f.name === name);
            if (fileIndex === -1) return;

            state.project.files.splice(fileIndex, 1);
            state.hasUnsavedChanges = true;

            // Selectionner un autre fichier si le fichier supprime etait selectionne
            if (state.selectedFile === name) {
              state.selectedFile = state.project.files[0]?.name || null;
            }
          });
        },

        renameFile: (oldName: string, newName: string) => {
          set((state) => {
            if (!state.project) return;

            // Verifier si le nouveau nom existe deja
            const exists = state.project.files.some((f) => f.name === newName);
            if (exists) {
              state.error = `Le fichier "${newName}" existe deja`;
              return;
            }

            const fileIndex = state.project.files.findIndex((f) => f.name === oldName);
            if (fileIndex !== -1) {
              state.project.files[fileIndex].name = newName;
              state.project.files[fileIndex].language = detectLanguage(newName);
              state.hasUnsavedChanges = true;

              if (state.selectedFile === oldName) {
                state.selectedFile = newName;
              }
            }
          });
        },

        // ========================================
        // Project State Actions
        // ========================================

        setProject: (project: Project | null) => {
          set((state) => {
            state.project = project;
            state.hasUnsavedChanges = false;
            state.selectedFile = project?.files?.[0]?.name || null;
          });
        },

        updateProjectMeta: (data: Partial<Pick<Project, 'name' | 'description'>>) => {
          set((state) => {
            if (!state.project) return;

            if (data.name !== undefined) {
              state.project.name = data.name;
            }
            if (data.description !== undefined) {
              state.project.description = data.description;
            }
            state.hasUnsavedChanges = true;
          });
        },

        addConversationMessage: (message: ConversationMessage) => {
          set((state) => {
            if (!state.project) return;

            state.project.conversation_history.push(message);
            state.hasUnsavedChanges = true;
          });
        },

        setFiles: (files: ProjectFile[]) => {
          set((state) => {
            if (!state.project) return;

            state.project.files = files;
            state.hasUnsavedChanges = true;

            // Mettre a jour la selection si le fichier n'existe plus
            if (state.selectedFile && !files.some((f) => f.name === state.selectedFile)) {
              state.selectedFile = files[0]?.name || null;
            }
          });
        },

        // ========================================
        // Utility Actions
        // ========================================

        reset: () => {
          set((state) => {
            Object.assign(state, initialState);
          });
        },

        clearError: () => {
          set((state) => {
            state.error = null;
          });
        },

        markAsSaved: () => {
          set((state) => {
            state.hasUnsavedChanges = false;
            state.lastSaved = Date.now();
          });
        },
      })),
      {
        name: 'devora-project-store',
        partialize: (state) => ({
          // Ne persister que le projet courant (pas la liste complete)
          project: state.project,
          selectedFile: state.selectedFile,
        }),
      }
    ),
    { name: 'ProjectStore' }
  )
);

// ============================================
// Selectors
// ============================================

export const selectCurrentFile = (state: ProjectState): ProjectFile | null => {
  if (!state.project || !state.selectedFile) return null;
  return state.project.files.find((f) => f.name === state.selectedFile) || null;
};

export const selectFileByName = (state: ProjectState, name: string): ProjectFile | null => {
  if (!state.project) return null;
  return state.project.files.find((f) => f.name === name) || null;
};

export const selectFileNames = (state: ProjectState): string[] => {
  return state.project?.files.map((f) => f.name) || [];
};

export const selectProjectById = (state: ProjectState, id: string): Project | null => {
  return state.projects.find((p) => p.id === id) || null;
};
