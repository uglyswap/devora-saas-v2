import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ProtectedRoute from '@components/ProtectedRoute';
import { AuthContext } from '@contexts/AuthContext';

/**
 * Tests unitaires pour ProtectedRoute
 * Vérifie: Authentication guards, Subscription guards, Redirections
 */

const mockNavigate = vi.fn();

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Navigate: ({ to }: { to: string }) => {
      mockNavigate(to);
      return <div data-testid="navigate">{to}</div>;
    },
  };
});

describe('ProtectedRoute', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  describe('Authentication Guard', () => {
    it('should redirect to login if user is not authenticated', () => {
      const authContextValue = {
        user: null,
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      expect(mockNavigate).toHaveBeenCalledWith('/login');
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });

    it('should render children if user is authenticated', () => {
      const authContextValue = {
        user: { id: '1', email: 'test@test.com', subscriptionStatus: 'active' },
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('should show loading state while checking authentication', () => {
      const authContextValue = {
        user: null,
        loading: true,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      // Should not redirect while loading
      expect(mockNavigate).not.toHaveBeenCalled();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });

  describe('Subscription Guard', () => {
    it('should redirect to billing if subscription is required but inactive', () => {
      const authContextValue = {
        user: { id: '1', email: 'test@test.com', subscriptionStatus: 'inactive' },
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute requireSubscription={true}>
              <div>Premium Content</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      expect(mockNavigate).toHaveBeenCalledWith('/billing');
      expect(screen.queryByText('Premium Content')).not.toBeInTheDocument();
    });

    it('should render children if subscription is active and required', () => {
      const authContextValue = {
        user: { id: '1', email: 'test@test.com', subscriptionStatus: 'active' },
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute requireSubscription={true}>
              <div>Premium Content</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      expect(screen.getByText('Premium Content')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('should render children if subscription not required', () => {
      const authContextValue = {
        user: { id: '1', email: 'test@test.com', subscriptionStatus: 'inactive' },
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute requireSubscription={false}>
              <div>Free Content</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      expect(screen.getByText('Free Content')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('should allow trial users to access subscription-required content', () => {
      const authContextValue = {
        user: { id: '1', email: 'test@test.com', subscriptionStatus: 'trialing' },
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute requireSubscription={true}>
              <div>Premium Content</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      expect(screen.getByText('Premium Content')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Admin Guard', () => {
    it('should redirect non-admin users from admin routes', () => {
      const authContextValue = {
        user: { id: '1', email: 'test@test.com', role: 'user' },
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute requireAdmin={true}>
              <div>Admin Panel</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      expect(screen.queryByText('Admin Panel')).not.toBeInTheDocument();
    });

    it('should allow admin users to access admin routes', () => {
      const authContextValue = {
        user: { id: '1', email: 'admin@test.com', role: 'admin' },
        loading: false,
        login: vi.fn(),
        logout: vi.fn(),
        register: vi.fn(),
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextValue}>
            <ProtectedRoute requireAdmin={true}>
              <div>Admin Panel</div>
            </ProtectedRoute>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      expect(screen.getByText('Admin Panel')).toBeInTheDocument();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });
});
