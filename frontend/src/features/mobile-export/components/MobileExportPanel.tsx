/**
 * MobileExportPanel Component
 * Full panel for mobile export with preview and conversion tools
 * @version 1.0.0
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MobileFramework,
  SourceFile,
  ExportPreview,
  ExportHistoryItem,
  FrameworkInfo,
  FRAMEWORK_CONFIG
} from '../types/mobile-export.types';
import { useMobileExport } from '../hooks/useMobileExport';

interface MobileExportPanelProps {
  projectName: string;
  files: SourceFile[];
  onExportComplete?: (downloadUrl: string) => void;
  className?: string;
}

type TabType = 'export' | 'preview' | 'converter' | 'history';

export const MobileExportPanel: React.FC<MobileExportPanelProps> = ({
  projectName,
  files,
  onExportComplete,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('export');
  const [selectedFramework, setSelectedFramework] = useState<MobileFramework>('expo-router');
  const [useTypeScript, setUseTypeScript] = useState(true);
  const [includeNavigation, setIncludeNavigation] = useState(true);
  const [frameworks, setFrameworks] = useState<FrameworkInfo[]>([]);
  const [history, setHistory] = useState<ExportHistoryItem[]>([]);

  // Converter state
  const [converterInput, setConverterInput] = useState('');
  const [converterOutput, setConverterOutput] = useState('');
  const [converterMode, setConverterMode] = useState<'component' | 'tailwind'>('component');

  const {
    isExporting,
    currentExport,
    preview,
    error,
    exportToMobile,
    previewExport,
    downloadExport,
    convertComponent,
    convertTailwind,
    getFrameworks,
    getHistory,
    reset
  } = useMobileExport({
    onExportComplete: (result) => {
      if (result.downloadUrl) {
        onExportComplete?.(result.downloadUrl);
      }
    }
  });

  // Load frameworks and history on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [frameworksData, historyData] = await Promise.all([
        getFrameworks(),
        getHistory()
      ]);
      setFrameworks(frameworksData);
      setHistory(historyData);
    } catch {
      // Use local config as fallback
    }
  };

  const handleExport = async () => {
    const result = await exportToMobile({
      projectName,
      files,
      framework: selectedFramework,
      useTypeScript,
      includeNavigation
    });

    if (result.success) {
      loadData(); // Refresh history
    }
  };

  const handlePreview = async () => {
    await previewExport({
      projectName,
      files,
      framework: selectedFramework,
      useTypeScript,
      includeNavigation
    });
  };

  const handleConvert = async () => {
    if (converterMode === 'component') {
      const result = await convertComponent(converterInput, 'Component.tsx');
      setConverterOutput(result.converted || result.warnings.join('\n'));
    } else {
      const styles = await convertTailwind(converterInput);
      setConverterOutput(JSON.stringify(styles, null, 2));
    }
  };

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'export', label: 'Export', icon: '📱' },
    { id: 'preview', label: 'Preview', icon: '👁️' },
    { id: 'converter', label: 'Converter', icon: '🔄' },
    { id: 'history', label: 'History', icon: '📋' }
  ];

  return (
    <div className={`bg-gray-900 border border-gray-800 rounded-xl overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-pink-600/20 to-orange-500/20 border-b border-gray-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">📱</span>
            <div>
              <h3 className="font-semibold text-white">Mobile Export</h3>
              <p className="text-xs text-gray-400">Convert to React Native / Expo</p>
            </div>
          </div>
          <div className="text-sm text-gray-400">
            {files.length} file{files.length !== 1 ? 's' : ''} selected
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex-1 px-4 py-2 text-sm font-medium transition-colors
              ${activeTab === tab.id
                ? 'text-pink-400 border-b-2 border-pink-400 bg-pink-500/10'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }
            `}
          >
            <span className="mr-1">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4">
        <AnimatePresence mode="wait">
          {/* Export Tab */}
          {activeTab === 'export' && (
            <motion.div
              key="export"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* Framework Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Framework
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(Object.entries(FRAMEWORK_CONFIG) as [MobileFramework, typeof FRAMEWORK_CONFIG['expo-router']][]).map(
                    ([id, config]) => (
                      <button
                        key={id}
                        onClick={() => setSelectedFramework(id)}
                        className={`
                          p-3 rounded-lg border text-left transition-all
                          ${selectedFramework === id
                            ? 'border-pink-500 bg-pink-500/10'
                            : 'border-gray-700 hover:border-gray-600'
                          }
                        `}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{config.icon}</span>
                          <span className="font-medium text-white text-sm">{config.name}</span>
                        </div>
                        {config.recommended && (
                          <span className="mt-1 inline-block px-1.5 py-0.5 text-xs bg-green-500/20 text-green-400 rounded">
                            Recommended
                          </span>
                        )}
                      </button>
                    )
                  )}
                </div>
              </div>

              {/* Options */}
              <div className="space-y-3">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useTypeScript}
                    onChange={(e) => setUseTypeScript(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-pink-500 focus:ring-pink-500"
                  />
                  <span className="text-sm text-gray-300">Use TypeScript</span>
                </label>
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeNavigation}
                    onChange={(e) => setIncludeNavigation(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-pink-500 focus:ring-pink-500"
                  />
                  <span className="text-sm text-gray-300">Include Navigation Setup</span>
                </label>
              </div>

              {/* Export Button */}
              <motion.button
                onClick={handleExport}
                disabled={isExporting || files.length === 0}
                className={`
                  w-full py-3 rounded-lg font-medium transition-all
                  ${isExporting
                    ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-pink-600 to-orange-500 hover:from-pink-500 hover:to-orange-400 text-white'
                  }
                `}
                whileHover={!isExporting ? { scale: 1.02 } : {}}
                whileTap={!isExporting ? { scale: 0.98 } : {}}
              >
                {isExporting ? (
                  <span className="flex items-center justify-center gap-2">
                    <motion.div
                      className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    />
                    Converting to Mobile...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <span>📱</span>
                    Export to {FRAMEWORK_CONFIG[selectedFramework].name}
                  </span>
                )}
              </motion.button>

              {/* Result */}
              {currentExport?.success && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-green-400 font-medium">✅ Export Ready!</span>
                    <button
                      onClick={() => downloadExport(currentExport.id)}
                      className="px-3 py-1 bg-green-600 hover:bg-green-500 text-white text-sm rounded"
                    >
                      Download ZIP
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-400">
                    <div>📦 {currentExport.filesCount} files</div>
                    <div>🔄 {currentExport.stats.components_converted} components</div>
                    <div>📄 {currentExport.stats.pages_created} pages</div>
                    <div>🎨 {currentExport.stats.styles_converted} styles</div>
                  </div>
                </motion.div>
              )}

              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm"
                >
                  {error}
                </motion.div>
              )}
            </motion.div>
          )}

          {/* Preview Tab */}
          {activeTab === 'preview' && (
            <motion.div
              key="preview"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              <button
                onClick={handlePreview}
                disabled={files.length === 0}
                className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Generate Preview
              </button>

              {preview && (
                <div className="space-y-3">
                  <div className="flex justify-between text-sm text-gray-400">
                    <span>{preview.files.length} files will be created</span>
                    <span>{(preview.totalSize / 1024).toFixed(1)} KB</span>
                  </div>

                  <div className="max-h-64 overflow-y-auto space-y-1">
                    {preview.files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between px-3 py-2 bg-gray-800 rounded text-sm"
                      >
                        <span className="text-gray-300 font-mono truncate">{file.path}</span>
                        <span className="text-gray-500 text-xs">{file.size}B</span>
                      </div>
                    ))}
                  </div>

                  {preview.warnings.length > 0 && (
                    <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                      <div className="text-yellow-400 text-sm font-medium mb-1">Warnings:</div>
                      {preview.warnings.map((warning, index) => (
                        <div key={index} className="text-yellow-400/80 text-xs">• {warning}</div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          )}

          {/* Converter Tab */}
          {activeTab === 'converter' && (
            <motion.div
              key="converter"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* Mode Selection */}
              <div className="flex gap-2">
                <button
                  onClick={() => setConverterMode('component')}
                  className={`
                    flex-1 py-2 rounded-lg text-sm font-medium transition-colors
                    ${converterMode === 'component'
                      ? 'bg-pink-500/20 text-pink-400'
                      : 'bg-gray-800 text-gray-400 hover:text-white'
                    }
                  `}
                >
                  Component
                </button>
                <button
                  onClick={() => setConverterMode('tailwind')}
                  className={`
                    flex-1 py-2 rounded-lg text-sm font-medium transition-colors
                    ${converterMode === 'tailwind'
                      ? 'bg-pink-500/20 text-pink-400'
                      : 'bg-gray-800 text-gray-400 hover:text-white'
                    }
                  `}
                >
                  Tailwind → StyleSheet
                </button>
              </div>

              {/* Input */}
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  {converterMode === 'component' ? 'React Component' : 'Tailwind Classes'}
                </label>
                <textarea
                  value={converterInput}
                  onChange={(e) => setConverterInput(e.target.value)}
                  placeholder={converterMode === 'component'
                    ? 'Paste your React component here...'
                    : 'e.g., flex items-center justify-between p-4 bg-white rounded-lg'
                  }
                  className="w-full h-32 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white font-mono text-sm resize-none focus:outline-none focus:border-pink-500"
                />
              </div>

              <button
                onClick={handleConvert}
                disabled={!converterInput.trim()}
                className="w-full py-2 bg-pink-600 hover:bg-pink-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
              >
                Convert
              </button>

              {/* Output */}
              {converterOutput && (
                <div>
                  <label className="block text-sm text-gray-400 mb-1">
                    {converterMode === 'component' ? 'React Native Component' : 'StyleSheet Object'}
                  </label>
                  <pre className="w-full h-32 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-green-400 font-mono text-sm overflow-auto">
                    {converterOutput}
                  </pre>
                </div>
              )}
            </motion.div>
          )}

          {/* History Tab */}
          {activeTab === 'history' && (
            <motion.div
              key="history"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-2"
            >
              {history.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No exports yet
                </div>
              ) : (
                history.map(item => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-3 bg-gray-800 rounded-lg"
                  >
                    <div>
                      <div className="font-medium text-white">{item.projectName}</div>
                      <div className="text-xs text-gray-500">
                        {item.filesCount} files • {new Date(item.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                    <button
                      onClick={() => downloadExport(item.id)}
                      className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded"
                    >
                      Download
                    </button>
                  </div>
                ))
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default MobileExportPanel;
