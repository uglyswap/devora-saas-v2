import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import CookieConsent from './components/CookieConsent';
import HomePage from './pages/HomePage';
import Dashboard from './pages/Dashboard';
// UNIFIED EDITOR - Single editor for all app creation
import UnifiedEditor from './pages/UnifiedEditor';
import SettingsPage from './pages/SettingsPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Billing from './pages/Billing';
// SUPERADMIN DASHBOARD with analytics
import AdminDashboard from './pages/AdminDashboard';
import TermsOfService from './pages/TermsOfService';
import PrivacyPolicy from './pages/PrivacyPolicy';
import Support from './pages/Support';
import { Toaster } from './components/ui/sonner';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected routes */}
            <Route path="/billing" element={
              <ProtectedRoute>
                <Billing />
              </ProtectedRoute>
            } />
            
            <Route path="/dashboard" element={
              <ProtectedRoute requireSubscription={true}>
                <Dashboard />
              </ProtectedRoute>
            } />
            
            {/* UNIFIED EDITOR - Single entry point for all app creation */}
            <Route path="/editor" element={
              <ProtectedRoute requireSubscription={true}>
                <UnifiedEditor />
              </ProtectedRoute>
            } />

            <Route path="/editor/:projectId" element={
              <ProtectedRoute requireSubscription={true}>
                <UnifiedEditor />
              </ProtectedRoute>
            } />

            {/* Create new project - redirects to UnifiedEditor */}
            <Route path="/create" element={
              <ProtectedRoute requireSubscription={true}>
                <UnifiedEditor />
              </ProtectedRoute>
            } />

            {/* Legacy route - redirect to unified editor */}
            <Route path="/ultimate" element={
              <ProtectedRoute requireSubscription={true}>
                <UnifiedEditor />
              </ProtectedRoute>
            } />

            <Route path="/ultimate/:projectId" element={
              <ProtectedRoute requireSubscription={true}>
                <UnifiedEditor />
              </ProtectedRoute>
            } />
            
            <Route path="/settings" element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            } />
            
            {/* ENTERPRISE ADMIN DASHBOARD */}
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            } />
            
            {/* Legal Pages */}
            <Route path="/legal/terms" element={<TermsOfService />} />
            <Route path="/legal/privacy" element={<PrivacyPolicy />} />
            
            {/* Support */}
            <Route path="/support" element={<Support />} />
          </Routes>
          <CookieConsent />
        </BrowserRouter>
        <Toaster position="top-right" richColors />
      </div>
    </AuthProvider>
  );
}

export default App;
