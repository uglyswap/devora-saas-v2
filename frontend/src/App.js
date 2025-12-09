import React, { Suspense, lazy, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import CookieConsent from './components/CookieConsent';
import ErrorBoundary from './components/ErrorBoundary';
import CommandPalette from './components/CommandPalette';
import KeyboardShortcuts from './components/KeyboardShortcuts';
import ConnectionStatus from './components/ConnectionStatus';
import { LoadingProvider } from './components/GlobalLoading';
import { Toaster } from './components/ui/sonner';
import './App.css';

// Lazy load pages for better performance
const HomePage = lazy(() => import('./pages/HomePage'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const UnifiedEditor = lazy(() => import('./pages/UnifiedEditor'));
const CreateProject = lazy(() => import('./pages/CreateProject'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Billing = lazy(() => import('./pages/Billing'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const TermsOfService = lazy(() => import('./pages/TermsOfService'));
const PrivacyPolicy = lazy(() => import('./pages/PrivacyPolicy'));
const Support = lazy(() => import('./pages/Support'));

// Loading fallback component
const PageLoader = () => (
  <div className="min-h-screen bg-gray-900 flex items-center justify-center">
    <div className="flex flex-col items-center gap-4">
      <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
      <p className="text-gray-400 text-sm">Chargement...</p>
    </div>
  </div>
);

function App() {
  const [shortcutsOpen, setShortcutsOpen] = useState(false);

  return (
    <ErrorBoundary>
      <LoadingProvider>
        <AuthProvider>
          <div className="App">
            <BrowserRouter>
              {/* Global Command Palette - Cmd+K */}
              <CommandPalette />

              {/* Keyboard Shortcuts Modal - Press ? to open */}
              <KeyboardShortcuts open={shortcutsOpen} onOpenChange={setShortcutsOpen} />

              {/* Connection Status Indicator */}
              <ConnectionStatus />

              {/* Routes with Suspense for lazy loading */}
              <Suspense fallback={<PageLoader />}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/billing" element={<ProtectedRoute><Billing /></ProtectedRoute>} />
                  <Route path="/dashboard" element={<ProtectedRoute requireSubscription={true}><Dashboard /></ProtectedRoute>} />
                  <Route path="/new" element={<ProtectedRoute requireSubscription={true}><CreateProject /></ProtectedRoute>} />
                  <Route path="/editor" element={<ProtectedRoute requireSubscription={true}><UnifiedEditor /></ProtectedRoute>} />
                  <Route path="/editor/:projectId" element={<ProtectedRoute requireSubscription={true}><UnifiedEditor /></ProtectedRoute>} />
                  <Route path="/create" element={<ProtectedRoute requireSubscription={true}><CreateProject /></ProtectedRoute>} />
                  <Route path="/ultimate" element={<ProtectedRoute requireSubscription={true}><UnifiedEditor /></ProtectedRoute>} />
                  <Route path="/ultimate/:projectId" element={<ProtectedRoute requireSubscription={true}><UnifiedEditor /></ProtectedRoute>} />
                  <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
                  <Route path="/admin" element={<ProtectedRoute><AdminDashboard /></ProtectedRoute>} />
                  <Route path="/legal/terms" element={<TermsOfService />} />
                  <Route path="/legal/privacy" element={<PrivacyPolicy />} />
                  <Route path="/support" element={<Support />} />
                </Routes>
              </Suspense>

              <CookieConsent />
            </BrowserRouter>
            <Toaster position="top-right" richColors />
          </div>
        </AuthProvider>
      </LoadingProvider>
    </ErrorBoundary>
  );
}

export default App;
