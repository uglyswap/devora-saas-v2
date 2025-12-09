/**
 * DeploymentPanel Component
 * Full deployment panel with provider config and history
 * @version 1.0.0
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  DeployProvider,
  DeploymentFile,
  DeploymentHistoryItem,
  ProviderInfo,
  PROVIDER_CONFIG,
  getStatusColor,
  getStatusLabel
} from '../types/deployment.types';
import { useDeployment } from '../hooks/useDeployment';

interface DeploymentPanelProps {
  projectName: string;
  files: DeploymentFile[];
  envVars?: Record<string, string>;
  isOpen: boolean;
  onClose: () => void;
  onDeployComplete?: (url: string) => void;
}

export const DeploymentPanel: React.FC<DeploymentPanelProps> = ({
  projectName,
  files,
  envVars,
  isOpen,
  onClose,
  onDeployComplete
}) => {
  const [activeTab, setActiveTab] = useState<'deploy' | 'config' | 'history'>('deploy');
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [history, setHistory] = useState<DeploymentHistoryItem[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<DeployProvider>('vercel');
  const [tokenInput, setTokenInput] = useState('');
  const [savingToken, setSavingToken] = useState(false);

  const {
    isDeploying,
    progress,
    status,
    currentDeployment,
    logs,
    error,
    deployWithStream,
    getProviders,
    getHistory,
    saveProviderToken,
    reset
  } = useDeployment({
    onComplete: (result) => {
      if (result.url) {
        onDeployComplete?.(result.url);
        loadHistory();
      }
    }
  });

  // Load providers and history
  useEffect(() => {
    if (isOpen) {
      loadProviders();
      loadHistory();
    }
  }, [isOpen]);

  const loadProviders = async () => {
    try {
      const data = await getProviders();
      setProviders(data);
    } catch (err) {
      console.error('Failed to load providers:', err);
    }
  };

  const loadHistory = async () => {
    try {
      const data = await getHistory(10);
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleDeploy = () => {
    deployWithStream({
      projectName,
      files,
      provider: selectedProvider,
      envVars
    });
  };

  const handleSaveToken = async () => {
    if (!tokenInput.trim()) return;

    setSavingToken(true);
    try {
      await saveProviderToken(selectedProvider, tokenInput.trim());
      setTokenInput('');
      loadProviders();
    } catch (err) {
      console.error('Failed to save token:', err);
    } finally {
      setSavingToken(false);
    }
  };

  const providerConfig = PROVIDER_CONFIG[selectedProvider];
  const selectedProviderInfo = providers.find(p => p.id === selectedProvider);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-2xl max-h-[80vh] overflow-hidden shadow-2xl"
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="text-2xl">🚀</span>
              Deploy {projectName}
            </h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-700">
            {(['deploy', 'config', 'history'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`
                  flex-1 px-4 py-3 text-sm font-medium transition-colors
                  ${activeTab === tab
                    ? 'text-indigo-400 border-b-2 border-indigo-400 bg-gray-800/50'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/30'
                  }
                `}
              >
                {tab === 'deploy' && '🚀 Deploy'}
                {tab === 'config' && '⚙️ Configuration'}
                {tab === 'history' && '📜 History'}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(80vh-140px)]">
            {/* Deploy Tab */}
            {activeTab === 'deploy' && (
              <div className="space-y-6">
                {/* Provider Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">
                    Select Provider
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {(Object.entries(PROVIDER_CONFIG) as [DeployProvider, typeof PROVIDER_CONFIG['vercel']][]).map(
                      ([providerId, config]) => {
                        const providerInfo = providers.find(p => p.id === providerId);
                        const isAvailable = providerInfo?.available ?? false;

                        return (
                          <button
                            key={providerId}
                            onClick={() => setSelectedProvider(providerId)}
                            disabled={!isAvailable}
                            className={`
                              p-4 rounded-lg border-2 transition-all text-center
                              ${selectedProvider === providerId
                                ? 'border-indigo-500 bg-indigo-500/10'
                                : 'border-gray-700 hover:border-gray-600'
                              }
                              ${!isAvailable ? 'opacity-50 cursor-not-allowed' : ''}
                            `}
                          >
                            <span className="text-2xl block mb-2">{config.icon}</span>
                            <span className="text-white font-medium">{config.name}</span>
                            {!isAvailable && (
                              <span className="block text-xs text-amber-400 mt-1">
                                Token required
                              </span>
                            )}
                          </button>
                        );
                      }
                    )}
                  </div>
                </div>

                {/* Provider Info */}
                <div className="p-4 bg-gray-800 rounded-lg">
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">{providerConfig.icon}</span>
                    <div>
                      <h3 className="font-semibold text-white">{providerConfig.name}</h3>
                      <p className="text-sm text-gray-400">{providerConfig.description}</p>
                      {selectedProviderInfo && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {selectedProviderInfo.features.slice(0, 4).map((feature, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 text-xs bg-gray-700 text-gray-300 rounded"
                            >
                              {feature}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Files Summary */}
                <div className="p-4 bg-gray-800 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Files to Deploy</h4>
                  <div className="text-2xl font-bold text-white">{files.length} files</div>
                  <div className="text-sm text-gray-400 mt-1">
                    {(files.reduce((acc, f) => acc + f.content.length, 0) / 1024).toFixed(1)} KB total
                  </div>
                </div>

                {/* Deploy Button */}
                <motion.button
                  onClick={handleDeploy}
                  disabled={isDeploying || !selectedProviderInfo?.available}
                  className={`
                    w-full py-4 rounded-lg font-medium text-lg transition-all
                    ${isDeploying || !selectedProviderInfo?.available
                      ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white'
                    }
                  `}
                  whileHover={!isDeploying && selectedProviderInfo?.available ? { scale: 1.01 } : {}}
                  whileTap={!isDeploying && selectedProviderInfo?.available ? { scale: 0.99 } : {}}
                >
                  {isDeploying ? (
                    <span className="flex items-center justify-center gap-2">
                      <motion.div
                        className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      />
                      Deploying... {progress}%
                    </span>
                  ) : !selectedProviderInfo?.available ? (
                    'Configure Token First'
                  ) : (
                    `🚀 Deploy to ${providerConfig.name}`
                  )}
                </motion.button>

                {/* Progress */}
                {isDeploying && (
                  <div className="space-y-2">
                    <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                      />
                    </div>
                    {logs.length > 0 && (
                      <div className="p-3 bg-gray-800 rounded-lg max-h-32 overflow-y-auto">
                        {logs.slice(-5).map((log, i) => (
                          <div key={i} className="text-xs text-gray-400 font-mono">
                            {log}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Result */}
                {status === 'ready' && currentDeployment?.url && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg"
                  >
                    <div className="flex items-center gap-2 text-green-400 mb-2">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="font-medium">Deployment Successful!</span>
                    </div>
                    <a
                      href={currentDeployment.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-green-300 hover:text-green-200"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      {currentDeployment.url}
                    </a>
                  </motion.div>
                )}

                {/* Error */}
                {error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
                    {error}
                  </div>
                )}
              </div>
            )}

            {/* Config Tab */}
            {activeTab === 'config' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">
                    Provider Tokens
                  </label>

                  <div className="space-y-4">
                    {(Object.entries(PROVIDER_CONFIG) as [DeployProvider, typeof PROVIDER_CONFIG['vercel']][]).map(
                      ([providerId, config]) => {
                        const providerInfo = providers.find(p => p.id === providerId);

                        return (
                          <div
                            key={providerId}
                            className="p-4 bg-gray-800 rounded-lg"
                          >
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-2">
                                <span className="text-xl">{config.icon}</span>
                                <span className="font-medium text-white">{config.name}</span>
                              </div>
                              <span
                                className={`
                                  px-2 py-0.5 text-xs rounded-full
                                  ${providerInfo?.available
                                    ? 'bg-green-500/20 text-green-400'
                                    : 'bg-amber-500/20 text-amber-400'
                                  }
                                `}
                              >
                                {providerInfo?.available ? 'Configured' : 'Not configured'}
                              </span>
                            </div>

                            <div className="flex gap-2">
                              <input
                                type="password"
                                placeholder={`Enter ${config.name} API token`}
                                value={selectedProvider === providerId ? tokenInput : ''}
                                onChange={(e) => {
                                  setSelectedProvider(providerId);
                                  setTokenInput(e.target.value);
                                }}
                                className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                              />
                              <button
                                onClick={() => {
                                  setSelectedProvider(providerId);
                                  handleSaveToken();
                                }}
                                disabled={savingToken || !tokenInput.trim() || selectedProvider !== providerId}
                                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                              >
                                Save
                              </button>
                            </div>
                          </div>
                        );
                      }
                    )}
                  </div>
                </div>

                <div className="p-4 bg-gray-800 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-2">Where to get tokens?</h4>
                  <ul className="space-y-2 text-sm text-gray-400">
                    <li>
                      <strong className="text-white">Vercel:</strong>{' '}
                      <a href="https://vercel.com/account/tokens" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">
                        vercel.com/account/tokens
                      </a>
                    </li>
                    <li>
                      <strong className="text-white">Netlify:</strong>{' '}
                      <a href="https://app.netlify.com/user/applications#personal-access-tokens" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">
                        app.netlify.com → User Settings → Applications
                      </a>
                    </li>
                    <li>
                      <strong className="text-white">Railway:</strong>{' '}
                      <a href="https://railway.app/account/tokens" target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">
                        railway.app/account/tokens
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
              <div className="space-y-4">
                {history.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <span className="text-4xl block mb-2">📭</span>
                    No deployments yet
                  </div>
                ) : (
                  history.map((item) => (
                    <div
                      key={item.id}
                      className="p-4 bg-gray-800 rounded-lg flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xl">
                          {PROVIDER_CONFIG[item.provider as DeployProvider]?.icon || '🚀'}
                        </span>
                        <div>
                          <div className="font-medium text-white">{item.projectName}</div>
                          <div className="text-xs text-gray-400">
                            {new Date(item.createdAt).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className="px-2 py-0.5 text-xs rounded-full"
                          style={{
                            backgroundColor: `${getStatusColor(item.status)}20`,
                            color: getStatusColor(item.status)
                          }}
                        >
                          {getStatusLabel(item.status)}
                        </span>
                        {item.url && (
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </a>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default DeploymentPanel;
