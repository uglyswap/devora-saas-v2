import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/button';
import {
  Settings, CreditCard, Shield, LogOut, Code2, FolderOpen,
  User, ChevronDown, Plus, LayoutDashboard, HelpCircle, Sparkles
} from 'lucide-react';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasActiveSubscription, isTrialing, getTrialDaysLeft } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const menuRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;
  const trialDays = getTrialDaysLeft();

  return (
    <header className="border-b border-white/5 bg-[#0a0a0b]/95 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <div className="bg-gradient-to-br from-emerald-400 to-emerald-600 p-2 rounded-lg">
              <Code2 className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">
              Devora
            </span>
          </button>

          {/* Center Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            <Button
              variant="ghost"
              onClick={() => navigate('/dashboard')}
              className={`${isActive('/dashboard')
                ? 'text-white bg-white/10'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <LayoutDashboard className="w-4 h-4 mr-2" />
              Tableau de bord
            </Button>

            <Button
              variant="ghost"
              onClick={() => navigate('/editor')}
              className={`${isActive('/editor')
                ? 'text-white bg-white/10'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Plus className="w-4 h-4 mr-2" />
              Créer
            </Button>

            {/* Admin Panel - Only for admins */}
            {user?.is_admin && (
              <Button
                variant="ghost"
                onClick={() => navigate('/admin')}
                className={`${isActive('/admin')
                  ? 'text-yellow-400 bg-yellow-500/20 border border-yellow-500/30'
                  : 'text-yellow-400/80 hover:text-yellow-300 hover:bg-yellow-500/10 border border-yellow-500/20'
                }`}
              >
                <Shield className="w-4 h-4 mr-2" />
                SuperAdmin
              </Button>
            )}
          </nav>

          {/* Right Side - User Menu */}
          <div className="flex items-center gap-3">
            {/* Trial Badge */}
            {isTrialing() && trialDays > 0 && (
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-emerald-500/20 to-blue-500/20 border border-emerald-500/30 rounded-full">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-xs font-medium text-emerald-300">
                  Essai: {trialDays}j restants
                </span>
              </div>
            )}

            {/* User Dropdown */}
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-white/5 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-blue-600 flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium text-white truncate max-w-[120px]">
                    {user?.full_name || user?.email?.split('@')[0]}
                  </p>
                  <p className="text-xs text-gray-500">
                    {hasActiveSubscription() ? (isTrialing() ? 'Essai' : 'Pro') : 'Gratuit'}
                  </p>
                </div>
                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-64 bg-[#1a1a1d] border border-white/10 rounded-xl shadow-xl py-2 z-50">
                  {/* User Info Header */}
                  <div className="px-4 py-3 border-b border-white/10">
                    <p className="font-medium text-white">{user?.full_name || 'Utilisateur'}</p>
                    <p className="text-sm text-gray-500 truncate">{user?.email}</p>
                    {user?.is_admin && (
                      <span className="inline-flex items-center gap-1 mt-2 px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">
                        <Shield className="w-3 h-3" />
                        SuperAdmin
                      </span>
                    )}
                  </div>

                  {/* Menu Items */}
                  <div className="py-2">
                    <button
                      onClick={() => { navigate('/dashboard'); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      <FolderOpen className="w-4 h-4" />
                      Mes projets
                    </button>

                    <button
                      onClick={() => { navigate('/billing'); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      <CreditCard className="w-4 h-4" />
                      Facturation
                    </button>

                    <button
                      onClick={() => { navigate('/settings'); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      <Settings className="w-4 h-4" />
                      Paramètres
                    </button>

                    <button
                      onClick={() => { navigate('/support'); setShowUserMenu(false); }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors"
                    >
                      <HelpCircle className="w-4 h-4" />
                      Support
                    </button>

                    {/* Admin Section */}
                    {user?.is_admin && (
                      <>
                        <div className="my-2 border-t border-white/10" />
                        <button
                          onClick={() => { navigate('/admin'); setShowUserMenu(false); }}
                          className="w-full flex items-center gap-3 px-4 py-2.5 text-yellow-400 hover:text-yellow-300 hover:bg-yellow-500/10 transition-colors"
                        >
                          <Shield className="w-4 h-4" />
                          Dashboard SuperAdmin
                        </button>
                      </>
                    )}
                  </div>

                  {/* Logout */}
                  <div className="pt-2 border-t border-white/10">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      Déconnexion
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navigation;
