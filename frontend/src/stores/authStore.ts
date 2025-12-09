/**
 * Auth Store - Zustand
 * Agent: Frontend State Management Specialist
 *
 * Gestion de l'authentification et de l'etat utilisateur
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import axios from 'axios';
import type { User, Token, SubscriptionStatus } from '../types';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// ============================================
// Types
// ============================================

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  fullName?: string;
}

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;

  // Auth Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateProfile: (data: Partial<Pick<User, 'full_name'>>) => Promise<void>;

  // Subscription Actions
  hasActiveSubscription: () => boolean;
  isTrialing: () => boolean;
  getTrialDaysLeft: () => number;
  getSubscriptionStatus: () => SubscriptionStatus;

  // Utility Actions
  setToken: (token: string) => void;
  initialize: () => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

// ============================================
// Initial State
// ============================================

const initialState = {
  user: null as User | null,
  token: null as string | null,
  isLoading: false,
  isInitialized: false,
  error: null as string | null,
};

// ============================================
// Axios Interceptor Setup
// ============================================

const setupAxiosInterceptors = (token: string | null) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

// ============================================
// Store
// ============================================

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,

        // ========================================
        // Auth Actions
        // ========================================

        login: async (credentials: LoginCredentials) => {
          set((state) => {
            state.isLoading = true;
            state.error = null;
          });

          try {
            const response = await axios.post<Token>(`${API_URL}/api/auth/login`, {
              email: credentials.email,
              password: credentials.password,
            });

            const { access_token } = response.data;

            // Store token
            localStorage.setItem('token', access_token);
            setupAxiosInterceptors(access_token);

            set((state) => {
              state.token = access_token;
            });

            // Fetch user data
            await get().refreshUser();

            set((state) => {
              state.isLoading = false;
            });
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || 'Email ou mot de passe incorrect'
              : 'Erreur lors de la connexion';

            set((state) => {
              state.error = message;
              state.isLoading = false;
            });
            throw new Error(message);
          }
        },

        register: async (data: RegisterData) => {
          set((state) => {
            state.isLoading = true;
            state.error = null;
          });

          try {
            const response = await axios.post<Token>(`${API_URL}/api/auth/register`, {
              email: data.email,
              password: data.password,
              full_name: data.fullName,
            });

            const { access_token } = response.data;

            // Store token
            localStorage.setItem('token', access_token);
            setupAxiosInterceptors(access_token);

            set((state) => {
              state.token = access_token;
            });

            // Fetch user data
            await get().refreshUser();

            set((state) => {
              state.isLoading = false;
            });
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || 'Erreur lors de l\'inscription'
              : 'Erreur lors de l\'inscription';

            set((state) => {
              state.error = message;
              state.isLoading = false;
            });
            throw new Error(message);
          }
        },

        logout: () => {
          // Clear storage
          localStorage.removeItem('token');
          setupAxiosInterceptors(null);

          // Reset state
          set((state) => {
            state.user = null;
            state.token = null;
            state.error = null;
          });

          // Redirect to login (if using router)
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        },

        refreshUser: async () => {
          const token = get().token || localStorage.getItem('token');
          if (!token) return;

          try {
            setupAxiosInterceptors(token);
            const response = await axios.get<User>(`${API_URL}/api/auth/me`);

            set((state) => {
              state.user = response.data;
              state.token = token;
            });
          } catch (error) {
            console.error('Failed to fetch user:', error);
            // Token invalid - logout
            get().logout();
          }
        },

        updateProfile: async (data: Partial<Pick<User, 'full_name'>>) => {
          const { user } = get();
          if (!user) return;

          set((state) => {
            state.isLoading = true;
            state.error = null;
          });

          try {
            const response = await axios.put<User>(`${API_URL}/api/auth/profile`, data);

            set((state) => {
              state.user = response.data;
              state.isLoading = false;
            });
          } catch (error) {
            const message = axios.isAxiosError(error)
              ? error.response?.data?.detail || 'Erreur lors de la mise a jour'
              : 'Erreur lors de la mise a jour';

            set((state) => {
              state.error = message;
              state.isLoading = false;
            });
            throw new Error(message);
          }
        },

        // ========================================
        // Subscription Actions
        // ========================================

        hasActiveSubscription: (): boolean => {
          const { user } = get();
          if (!user) return false;
          return ['active', 'trialing'].includes(user.subscription_status);
        },

        isTrialing: (): boolean => {
          const { user } = get();
          return user?.subscription_status === 'trialing';
        },

        getTrialDaysLeft: (): number => {
          const { user } = get();
          if (!user?.current_period_end) return 0;

          const endDate = new Date(user.current_period_end);
          const now = new Date();
          const daysLeft = Math.ceil(
            (endDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
          );
          return Math.max(0, daysLeft);
        },

        getSubscriptionStatus: (): SubscriptionStatus => {
          const { user } = get();
          return (user?.subscription_status as SubscriptionStatus) || 'inactive';
        },

        // ========================================
        // Utility Actions
        // ========================================

        setToken: (token: string) => {
          localStorage.setItem('token', token);
          setupAxiosInterceptors(token);

          set((state) => {
            state.token = token;
          });
        },

        initialize: async () => {
          const token = localStorage.getItem('token');

          if (token) {
            set((state) => {
              state.token = token;
            });

            setupAxiosInterceptors(token);

            try {
              await get().refreshUser();
            } catch (error) {
              console.error('Auth initialization failed:', error);
            }
          }

          set((state) => {
            state.isInitialized = true;
          });
        },

        clearError: () => {
          set((state) => {
            state.error = null;
          });
        },

        reset: () => {
          localStorage.removeItem('token');
          setupAxiosInterceptors(null);

          set((state) => {
            Object.assign(state, initialState);
            state.isInitialized = true;
          });
        },
      })),
      {
        name: 'devora-auth-store',
        partialize: (state) => ({
          token: state.token,
          user: state.user,
        }),
        onRehydrateStorage: () => (state) => {
          // Setup axios after rehydration
          if (state?.token) {
            setupAxiosInterceptors(state.token);
          }
        },
      }
    ),
    { name: 'AuthStore' }
  )
);

// ============================================
// Selectors
// ============================================

export const selectUser = (state: AuthState): User | null => state.user;

export const selectIsAuthenticated = (state: AuthState): boolean => {
  return !!state.token && !!state.user;
};

export const selectIsAdmin = (state: AuthState): boolean => {
  return state.user?.is_admin || false;
};

export const selectSubscriptionStatus = (state: AuthState): SubscriptionStatus => {
  return (state.user?.subscription_status as SubscriptionStatus) || 'inactive';
};

export const selectCanAccessPremium = (state: AuthState): boolean => {
  const status = state.user?.subscription_status;
  return status === 'active' || status === 'trialing';
};

// ============================================
// Auth Guard Hook Helper
// ============================================

export const getAuthHeaders = (): Record<string, string> => {
  const token = useAuthStore.getState().token;
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
};
