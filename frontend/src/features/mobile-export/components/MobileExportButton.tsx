/**
 * MobileExportButton Component
 * One-click export to React Native/Expo
 * @version 1.0.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MobileFramework,
  SourceFile,
  FRAMEWORK_CONFIG,
  getFrameworkConfig
} from '../types/mobile-export.types';
import { useMobileExport } from '../hooks/useMobileExport';

interface MobileExportButtonProps {
  projectName: string;
  files: SourceFile[];
  onExportComplete?: (downloadUrl: string) => void;
  onExportError?: (error: string) => void;
  className?: string;
  disabled?: boolean;
}

export const MobileExportButton: React.FC<MobileExportButtonProps> = ({
  projectName,
  files,
  onExportComplete,
  onExportError,
  className = '',
  disabled = false
}) => {
  const [selectedFramework, setSelectedFramework] = useState<MobileFramework>('expo-router');
  const [showFrameworkMenu, setShowFrameworkMenu] = useState(false);

  const {
    isExporting,
    currentExport,
    error,
    exportToMobile,
    downloadExport,
    reset
  } = useMobileExport({
    onExportComplete: (result) => {
      if (result.downloadUrl) {
        onExportComplete?.(result.downloadUrl);
      }
    },
    onExportError: (err) => {
      onExportError?.(err);
    }
  });

  const handleExport = async () => {
    await exportToMobile({
      projectName,
      files,
      framework: selectedFramework,
      useTypeScript: true,
      includeNavigation: true
    });
  };

  const handleDownload = () => {
    if (currentExport?.id) {
      downloadExport(currentExport.id);
    }
  };

  const frameworkConfig = getFrameworkConfig(selectedFramework);

  return (
    <div className={`relative ${className}`}>
      {/* Main Export Button */}
      <div className="flex items-center gap-1">
        <motion.button
          onClick={currentExport?.success ? handleDownload : handleExport}
          disabled={disabled || isExporting || files.length === 0}
          className={`
            relative flex items-center gap-2 px-4 py-2 rounded-l-lg font-medium
            transition-all duration-200
            ${isExporting
              ? 'bg-gray-700 text-gray-300 cursor-not-allowed'
              : currentExport?.success
                ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white'
                : 'bg-gradient-to-r from-pink-600 to-orange-500 hover:from-pink-500 hover:to-orange-400 text-white'
            }
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          whileHover={!isExporting && !disabled ? { scale: 1.02 } : {}}
          whileTap={!isExporting && !disabled ? { scale: 0.98 } : {}}
        >
          {isExporting ? (
            <>
              <motion.div
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
              <span>Converting...</span>
            </>
          ) : currentExport?.success ? (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Download ZIP</span>
            </>
          ) : (
            <>
              <span className="text-lg">{frameworkConfig.icon}</span>
              <span>Export to {frameworkConfig.name}</span>
            </>
          )}
        </motion.button>

        {/* Framework Selector */}
        {!currentExport?.success && (
          <motion.button
            onClick={() => setShowFrameworkMenu(!showFrameworkMenu)}
            disabled={isExporting}
            className={`
              p-2 rounded-r-lg border-l border-white/20
              ${isExporting
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-pink-600 to-orange-500 hover:from-pink-500 hover:to-orange-400 text-white'
              }
            `}
            whileHover={!isExporting ? { scale: 1.05 } : {}}
          >
            <svg
              className={`w-4 h-4 transition-transform ${showFrameworkMenu ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </motion.button>
        )}

        {/* Reset button after success */}
        {currentExport?.success && (
          <motion.button
            onClick={reset}
            className="p-2 rounded-r-lg border-l border-white/20 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white"
            whileHover={{ scale: 1.05 }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </motion.button>
        )}
      </div>

      {/* Framework Dropdown Menu */}
      <AnimatePresence>
        {showFrameworkMenu && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 mt-2 w-72 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50"
          >
            {(Object.entries(FRAMEWORK_CONFIG) as [MobileFramework, typeof FRAMEWORK_CONFIG['expo-router']][]).map(
              ([frameworkId, config], index, arr) => (
                <button
                  key={frameworkId}
                  onClick={() => {
                    setSelectedFramework(frameworkId);
                    setShowFrameworkMenu(false);
                  }}
                  className={`
                    w-full flex items-center gap-3 p-3 text-left
                    hover:bg-gray-700 transition-colors
                    ${frameworkId === selectedFramework ? 'bg-gray-700' : ''}
                    ${index === 0 ? 'rounded-t-lg' : ''}
                    ${index === arr.length - 1 ? 'rounded-b-lg' : ''}
                  `}
                >
                  <span className="text-xl">{config.icon}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-white">{config.name}</span>
                      {config.recommended && (
                        <span className="px-1.5 py-0.5 text-xs bg-green-500/20 text-green-400 rounded">
                          Recommended
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-400">{config.description}</div>
                  </div>
                  {frameworkId === selectedFramework && (
                    <svg className="w-5 h-5 text-pink-400" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>
              )
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Export Result Display */}
      <AnimatePresence>
        {(currentExport || error) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3"
          >
            {/* Success Stats */}
            {currentExport?.success && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg"
              >
                <div className="flex items-center gap-2 text-green-400 mb-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="font-medium">Export Ready!</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm text-gray-400">
                  <div>Components: {currentExport.stats.components_converted}</div>
                  <div>Pages: {currentExport.stats.pages_created}</div>
                  <div>Styles: {currentExport.stats.styles_converted}</div>
                  <div>Total: {currentExport.filesCount} files</div>
                </div>
                {currentExport.warnings.length > 0 && (
                  <div className="mt-2 text-xs text-yellow-400">
                    ⚠️ {currentExport.warnings.length} warning(s)
                  </div>
                )}
              </motion.div>
            )}

            {/* Error Display */}
            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg"
              >
                <div className="flex items-center gap-2 text-red-400">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm">{error}</span>
                </div>
                <button
                  onClick={reset}
                  className="mt-2 text-xs text-gray-400 hover:text-white"
                >
                  Try Again
                </button>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MobileExportButton;
