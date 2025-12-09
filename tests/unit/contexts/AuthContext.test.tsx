import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '@contexts/AuthContext';
import axios from 'axios';

/**
 * Tests unitaires pour AuthContext
 * Vérifie: Login, Logout, Register, Session persistence
 */

vi.mock('axios');

const mockAxios = axios as any;

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Login', () => {
    it('should login user successfully', async () => {
      const mockUser = { id: '1', email: 'test@test.com' };
      const mockToken = 'mock-token-123';

      mockAxios.post.mockResolvedValueOnce({
        data: { user: mockUser, token: mockToken },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        await result.current.login('test@test.com', 'password123');
      });

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
        expect(localStorage.getItem('token')).toBe(mockToken);
      });
    });

    it('should throw error on failed login', async () => {
      mockAxios.post.mockRejectedValueOnce({
        response: { data: { error: 'Invalid credentials' } },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await expect(async () => {
        await act(async () => {
          await result.current.login('wrong@test.com', 'wrongpass');
        });
      }).rejects.toThrow();

      expect(result.current.user).toBeNull();
      expect(localStorage.getItem('token')).toBeNull();
    });

    it('should save user data to localStorage', async () => {
      const mockUser = { id: '1', email: 'test@test.com' };
      const mockToken = 'mock-token-123';

      mockAxios.post.mockResolvedValueOnce({
        data: { user: mockUser, token: mockToken },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        await result.current.login('test@test.com', 'password123');
      });

      await waitFor(() => {
        expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUser));
        expect(localStorage.getItem('token')).toBe(mockToken);
      });
    });
  });

  describe('Logout', () => {
    it('should logout user and clear state', async () => {
      const mockUser = { id: '1', email: 'test@test.com' };
      localStorage.setItem('user', JSON.stringify(mockUser));
      localStorage.setItem('token', 'mock-token');

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      act(() => {
        result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
      expect(localStorage.getItem('token')).toBeNull();
    });
  });

  describe('Register', () => {
    it('should register user successfully', async () => {
      const mockUser = { id: '1', email: 'newuser@test.com' };
      const mockToken = 'mock-token-123';

      mockAxios.post.mockResolvedValueOnce({
        data: { user: mockUser, token: mockToken },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        await result.current.register({
          email: 'newuser@test.com',
          password: 'password123',
          name: 'New User',
        });
      });

      await waitFor(() => {
        expect(result.current.user).toEqual(mockUser);
        expect(localStorage.getItem('token')).toBe(mockToken);
      });
    });

    it('should throw error on failed registration', async () => {
      mockAxios.post.mockRejectedValueOnce({
        response: { data: { error: 'Email already exists' } },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await expect(async () => {
        await act(async () => {
          await result.current.register({
            email: 'existing@test.com',
            password: 'password123',
          });
        });
      }).rejects.toThrow();

      expect(result.current.user).toBeNull();
    });
  });

  describe('Session Persistence', () => {
    it('should restore user from localStorage on mount', () => {
      const mockUser = { id: '1', email: 'test@test.com' };
      localStorage.setItem('user', JSON.stringify(mockUser));
      localStorage.setItem('token', 'mock-token');

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.user).toEqual(mockUser);
    });

    it('should set loading to false after checking localStorage', async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });

    it('should handle corrupted localStorage data gracefully', () => {
      localStorage.setItem('user', 'invalid-json{{{');

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.user).toBeNull();
      expect(result.current.loading).toBe(false);
    });
  });

  describe('Token Refresh', () => {
    it('should refresh token when expired', async () => {
      const mockUser = { id: '1', email: 'test@test.com' };
      const newToken = 'new-token-456';

      localStorage.setItem('user', JSON.stringify(mockUser));
      localStorage.setItem('token', 'expired-token');

      mockAxios.post.mockResolvedValueOnce({
        data: { token: newToken },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      // Simulate token refresh
      await act(async () => {
        // This would be called by axios interceptor
        await result.current.refreshToken?.();
      });

      await waitFor(() => {
        expect(localStorage.getItem('token')).toBe(newToken);
      });
    });
  });

  describe('API Error Handling', () => {
    it('should handle network errors', async () => {
      mockAxios.post.mockRejectedValueOnce(new Error('Network Error'));

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await expect(async () => {
        await act(async () => {
          await result.current.login('test@test.com', 'password123');
        });
      }).rejects.toThrow('Network Error');
    });

    it('should handle server errors', async () => {
      mockAxios.post.mockRejectedValueOnce({
        response: { status: 500, data: { error: 'Internal Server Error' } },
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await expect(async () => {
        await act(async () => {
          await result.current.login('test@test.com', 'password123');
        });
      }).rejects.toThrow();
    });
  });
});
