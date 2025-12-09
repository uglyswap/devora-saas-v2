/**
 * DeployButton Component
 * One-click deployment button with provider selection
 * @version 1.0.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  DeployProvider,
  DeploymentFile,
  PROVIDER_CONFIG,
  getStatusColor,
  getStatusLabel
} from '../types/deployment.types';
import { useDeployment } from '../hooks/useDeployment';

interface DeployButtonProps {
  projectName: string;
  files: DeploymentFile[];
  envVars?: Record<string, string>;
  onDeployComplete?: (url: string) => void;
  onDeployError?: (error: string) => void;
  className?: string;
  disabled?: boolean;
}

export const DeployButton: React.FC<DeployButtonProps> = ({
  projectName,
  files,
  envVars,
  onDeployComplete,
  onDeployError,
  className = '',
  disabled = false
}) => {
  const [selectedProvider, setSelectedProvider] = useState<DeployProvider>('vercel');
  const [showProviderMenu, setShowProviderMenu] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  const {
    isDeploying,
    progress,
    status,
    currentDeployment,
    logs,
    error,
    deployWithStream,
    reset
  } = useDeployment({
    onComplete: (result) => {
      if (result.url) {
        onDeployComplete?.(result.url);
      }
    },
    onError: (err) => {
      onDeployError?.(err);
    }
  });

  const handleDeploy = () => {
    deployWithStream({
      projectName,
      files,
      provider: selectedProvider,
      envVars
    });
  };

  const providerConfig = PROVIDER_CONFIG[selectedProvider];

  return (
    <div className={`relative ${className}`}>
      {/* Main Deploy Button */}
      <div className="flex items-center gap-1">
        <motion.button
          onClick={handleDeploy}
          disabled={disabled || isDeploying || files.length === 0}
          className={`
            relative flex items-center gap-2 px-4 py-2 rounded-l-lg font-medium
            transition-all duration-200
            ${isDeploying
              ? 'bg-gray-700 text-gray-300 cursor-not-allowed'
              : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white'
            }
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          whileHover={!isDeploying && !disabled ? { scale: 1.02 } : {}}
          whileTap={!isDeploying && !disabled ? { scale: 0.98 } : {}}
        >
          {isDeploying ? (
            <>
              <motion.div
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              />
              <span>Deploying... {progress}%</span>
            </>
          ) : (
            <>
              <span className="text-lg">{providerConfig.icon}</span>
              <span>Deploy to {providerConfig.name}</span>
            </>
          )}
        </motion.button>

        {/* Provider Selector */}
        <motion.button
          onClick={() => setShowProviderMenu(!showProviderMenu)}
          disabled={isDeploying}
          className={`
            p-2 rounded-r-lg border-l border-white/20
            ${isDeploying
              ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white'
            }
          `}
          whileHover={!isDeploying ? { scale: 1.05 } : {}}
        >
          <svg
            className={`w-4 h-4 transition-transform ${showProviderMenu ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </motion.button>
      </div>

      {/* Provider Dropdown Menu */}
      <AnimatePresence>
        {showProviderMenu && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 mt-2 w-64 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50"
          >
            {(Object.entries(PROVIDER_CONFIG) as [DeployProvider, typeof PROVIDER_CONFIG['vercel']][]).map(
              ([providerId, config]) => (
                <button
                  key={providerId}
                  onClick={() => {
                    setSelectedProvider(providerId);
                    setShowProviderMenu(false);
                  }}
                  className={`
                    w-full flex items-center gap-3 p-3 text-left
                    hover:bg-gray-700 transition-colors
                    ${providerId === selectedProvider ? 'bg-gray-700' : ''}
                    ${providerId === 'vercel' ? 'rounded-t-lg' : ''}
                    ${providerId === 'railway' ? 'rounded-b-lg' : ''}
                  `}
                >
                  <span className="text-xl">{config.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium text-white">{config.name}</div>
                    <div className="text-xs text-gray-400">{config.description}</div>
                  </div>
                  {providerId === selectedProvider && (
                    <svg className="w-5 h-5 text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
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

      {/* Progress & Status Display */}
      <AnimatePresence>
        {(isDeploying || status) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3"
          >
            {/* Progress Bar */}
            {isDeploying && (
              <div className="mb-2">
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>
            )}

            {/* Status Badge */}
            {status && (
              <div className="flex items-center justify-between">
                <span
                  className="px-2 py-1 text-xs font-medium rounded-full"
                  style={{
                    backgroundColor: `${getStatusColor(status)}20`,
                    color: getStatusColor(status)
                  }}
                >
                  {getStatusLabel(status)}
                </span>

                {/* Action buttons */}
                <div className="flex gap-2">
                  {logs.length > 0 && (
                    <button
                      onClick={() => setShowLogs(!showLogs)}
                      className="text-xs text-gray-400 hover:text-white transition-colors"
                    >
                      {showLogs ? 'Hide' : 'Show'} Logs ({logs.length})
                    </button>
                  )}

                  {(status === 'ready' || status === 'error') && (
                    <button
                      onClick={reset}
                      className="text-xs text-gray-400 hover:text-white transition-colors"
                    >
                      Reset
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Success URL */}
            {status === 'ready' && currentDeployment?.url && (
              <motion.a
                href={currentDeployment.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 flex items-center gap-2 text-sm text-green-400 hover:text-green-300"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                {currentDeployment.url}
              </motion.a>
            )}

            {/* Error Message */}
            {error && (
              <motion.p
                className="mt-2 text-sm text-red-400"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                {error}
              </motion.p>
            )}

            {/* Logs */}
            <AnimatePresence>
              {showLogs && logs.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2 p-2 bg-gray-900 rounded-lg max-h-40 overflow-y-auto"
                >
                  {logs.map((log, index) => (
                    <div key={index} className="text-xs text-gray-400 font-mono">
                      {log}
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DeployButton;
