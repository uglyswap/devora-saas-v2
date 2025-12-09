import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import DocsSidebar from './DocsSidebar';
import { getNextDoc, getPrevDoc, getDocByHref } from '../config/navigation';

interface DocsLayoutProps {
  children: React.ReactNode;
}

export const DocsLayout: React.FC<DocsLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const location = useLocation();

  const currentDoc = getDocByHref(location.pathname);
  const nextDoc = getPrevDoc(location.pathname);
  const prevDoc = getNextDoc(location.pathname);

  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
        <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden p-2 rounded-md text-gray-600 hover:bg-gray-100"
                aria-label="Toggle sidebar"
              >
                {sidebarOpen ? (
                  <X className="w-5 h-5" />
                ) : (
                  <Menu className="w-5 h-5" />
                )}
              </button>

              <Link to="/" className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg" />
                <span className="text-xl font-bold text-gray-900">Devora</span>
              </Link>

              <Link
                to="/docs/getting-started/introduction"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Documentation
              </Link>
            </div>

            {/* Search */}
            <div className="hidden md:flex items-center flex-1 max-w-lg mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search documentation..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              <Link
                to="/dashboard"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Dashboard
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-8xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex gap-8">
          {/* Sidebar - Desktop */}
          <aside className="hidden lg:block w-64 flex-shrink-0 py-8">
            <div className="sticky top-24">
              <DocsSidebar />
            </div>
          </aside>

          {/* Sidebar - Mobile */}
          {sidebarOpen && (
            <div className="fixed inset-0 z-40 lg:hidden">
              <div
                className="fixed inset-0 bg-black bg-opacity-50"
                onClick={() => setSidebarOpen(false)}
              />
              <div className="fixed inset-y-0 left-0 w-64 bg-white p-6 overflow-y-auto">
                <DocsSidebar />
              </div>
            </div>
          )}

          {/* Main Content Area */}
          <main className="flex-1 min-w-0 py-8">
            <article className="prose prose-slate max-w-3xl">
              {children}
            </article>

            {/* Navigation Footer */}
            <div className="mt-12 pt-8 border-t border-gray-200">
              <div className="flex items-center justify-between">
                {prevDoc ? (
                  <Link
                    to={prevDoc.href}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <div className="text-left">
                      <div className="text-xs text-gray-500">Previous</div>
                      <div>{prevDoc.title}</div>
                    </div>
                  </Link>
                ) : (
                  <div />
                )}

                {nextDoc && (
                  <Link
                    to={nextDoc.href}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <div className="text-right">
                      <div className="text-xs text-gray-500">Next</div>
                      <div>{nextDoc.title}</div>
                    </div>
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                )}
              </div>
            </div>
          </main>

          {/* Table of Contents - Desktop */}
          <aside className="hidden xl:block w-64 flex-shrink-0 py-8">
            <div className="sticky top-24">
              <h4 className="text-sm font-semibold text-gray-900 mb-4">
                On this page
              </h4>
              <nav className="space-y-2 text-sm">
                {/* Table of contents will be auto-generated from headings */}
              </nav>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
};

export default DocsLayout;
