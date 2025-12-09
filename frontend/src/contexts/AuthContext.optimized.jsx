import React, { createContext, useState, useEffect, useContext, useMemo, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const AuthContext = createContext();

/**
 * AuthProvider - Optimized version with React.memo and performance optimizations
 *
 * Optimizations applied:
 * - useCallback for all functions to prevent re-creation
 * - useMemo for computed values
 * - Memoized context value to prevent unnecessary re-renders
 *
 * @version 2.0.0 - Optimized by Frontend Squad
 */
export const AuthProvider = React.memo(function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Memoized fetch user function
  const fetchUser = useCallback(async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  // Memoized login function
  const login = useCallback(async (email, password) => {
    const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
      email,
      password
    });
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    await fetchUser();
    return true;
  }, [fetchUser]);

  // Memoized register function
  const register = useCallback(async (email, password, fullName) => {
    const response = await axios.post(`${BACKEND_URL}/api/auth/register`, {
      email,
      password,
      full_name: fullName
    });
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    await fetchUser();
    return true;
  }, [fetchUser]);

  // Memoized logout function
  const logout = useCallback(() => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  }, []);

  // Memoized subscription check
  const hasActiveSubscription = useCallback(() => {
    if (!user) return false;
    return ['active', 'trialing'].includes(user.subscription_status);
  }, [user]);

  // Memoized trial check
  const isTrialing = useCallback(() => {
    return user?.subscription_status === 'trialing';
  }, [user]);

  // Memoized trial days calculation
  const getTrialDaysLeft = useCallback(() => {
    if (!user || !user.current_period_end) return 0;
    const endDate = new Date(user.current_period_end);
    const now = new Date();
    const daysLeft = Math.ceil((endDate - now) / (1000 * 60 * 60 * 24));
    return Math.max(0, daysLeft);
  }, [user]);

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    user,
    loading,
    login,
    register,
    logout,
    hasActiveSubscription,
    isTrialing,
    getTrialDaysLeft,
    refreshUser: fetchUser
  }), [
    user,
    loading,
    login,
    register,
    logout,
    hasActiveSubscription,
    isTrialing,
    getTrialDaysLeft,
    fetchUser
  ]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
});

/**
 * useAuth - Custom hook to access Auth context
 * Throws error if used outside of AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
