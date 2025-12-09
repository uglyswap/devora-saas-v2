/**
 * OptimizedEditorExample.jsx
 *
 * Example d'integration des optimisations Frontend Squad
 * dans une page editeur simplifiee.
 *
 * Demontre:
 * - Utilisation hooks personnalises
 * - Composants UI optimises
 * - Design system tokens
 * - Performance patterns
 *
 * @author Frontend Squad
 * @version 1.0.0
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Save, Play, Download, Settings, Code, Eye } from 'lucide-react';

// Hooks personnalises optimises
import {
  useDebounce,
  useLocalStorage,
  useMediaQuery,
  useCopyToClipboard,
  useKeyCombo
} from '../hooks';

// Composants UI optimises
import { Button } from '../components/ui/optimized/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/optimized/Card';
import { Input } from '../components/ui/optimized/Input';
import { Modal } from '../components/ui/optimized/Modal';

// Context optimise
import { useAuth } from '../contexts/AuthContext.optimized';

// Preview optimise
import WebContainerPreview from '../components/preview/WebContainerPreview.optimized';

/**
 * FileEditor - Composant memoize pour edition fichier
 */
const FileEditor = React.memo(function FileEditor({ fileName, content, onChange }) {
  // Debounce les changements pour optimiser performance
  const [localContent, setLocalContent] = useState(content);
  const debouncedContent = useDebounce(localContent, 300);

  // Propager les changements debounced
  React.useEffect(() => {
    onChange(debouncedContent);
  }, [debouncedContent, onChange]);

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-2 bg-gray-800 border-b border-gray-700 flex items-center gap-2">
        <Code className="w-4 h-4 text-blue-400" />
        <span className="text-sm text-gray-300 font-mono">{fileName}</span>
      </div>
      <textarea
        value={localContent}
        onChange={(e) => setLocalContent(e.target.value)}
        className="flex-1 p-4 bg-gray-900 text-gray-200 font-mono text-sm resize-none focus:outline-none custom-scrollbar"
        placeholder="Start coding..."
        spellCheck={false}
      />
    </div>
  );
});

/**
 * Toolbar - Composant memoize pour barre d'outils
 */
const Toolbar = React.memo(function Toolbar({
  onSave,
  onRun,
  onExport,
  onSettings,
  isSaving
}) {
  return (
    <div className="h-14 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
      <div className="flex items-center gap-2">
        <h1 className="text-lg font-semibold text-white">Optimized Editor</h1>
        <span className="px-2 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded text-xs text-emerald-400 font-medium">
          Performance Optimized
        </span>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onSave}
          loading={isSaving}
          leftIcon={<Save className="w-4 h-4" />}
        >
          Save
        </Button>

        <Button
          variant="gradient"
          size="sm"
          onClick={onRun}
          leftIcon={<Play className="w-4 h-4" />}
        >
          Run
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={onExport}
          leftIcon={<Download className="w-4 h-4" />}
        >
          Export
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={onSettings}
          leftIcon={<Settings className="w-4 h-4" />}
        >
          Settings
        </Button>
      </div>
    </div>
  );
});

/**
 * OptimizedEditorExample - Composant principal
 */
export default function OptimizedEditorExample() {
  // Auth context optimise
  const { user } = useAuth();

  // Media queries pour responsive
  const isMobile = useMediaQuery('(max-width: 768px)');
  const prefersReducedMotion = useMediaQuery('(prefers-reduced-motion: reduce)');

  // LocalStorage pour persistence
  const [projectName, setProjectName] = useLocalStorage('editor-project-name', 'My Project');
  const [showPreview, setShowPreview] = useLocalStorage('editor-show-preview', true);

  // State local
  const [files, setFiles] = useState({
    'index.html': `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="container">
    <h1>Hello, Optimized World!</h1>
    <p>Built with Devora Frontend Squad optimizations</p>
  </div>
  <script src="script.js"></script>
</body>
</html>`,
    'style.css': `* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--devora-font-sans);
  background: var(--devora-bg-primary);
  color: var(--devora-text-primary);
  padding: var(--devora-space-8);
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--devora-space-6);
  background: var(--devora-bg-tertiary);
  border-radius: var(--devora-radius-xl);
  box-shadow: var(--devora-shadow-lg);
}

h1 {
  font-size: var(--devora-text-3xl);
  margin-bottom: var(--devora-space-4);
  background: linear-gradient(135deg, var(--devora-primary-400) 0%, var(--devora-accent-blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}`,
    'script.js': `console.log('Optimized app loaded!');

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM ready');
});`
  });

  const [selectedFile, setSelectedFile] = useState('index.html');
  const [isSaving, setIsSaving] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Copy to clipboard hook
  const [copiedText, copy] = useCopyToClipboard();

  // Memoized file list
  const fileList = useMemo(() => Object.keys(files), [files]);

  // Memoized files for preview (format attendu par WebContainerPreview)
  const previewFiles = useMemo(() => {
    return Object.entries(files).map(([name, content]) => ({
      name,
      content
    }));
  }, [files]);

  /**
   * Handlers - Tous memoizes avec useCallback
   */
  const handleFileChange = useCallback((content) => {
    setFiles(prev => ({
      ...prev,
      [selectedFile]: content
    }));
  }, [selectedFile]);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    // Simuler sauvegarde API
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Project saved:', { projectName, files });
    setIsSaving(false);
  }, [projectName, files]);

  const handleRun = useCallback(() => {
    console.log('Running project...');
    setShowPreview(true);
  }, [setShowPreview]);

  const handleExport = useCallback(() => {
    const blob = new Blob([JSON.stringify(files, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [files, projectName]);

  const handleCopyFile = useCallback(() => {
    copy(files[selectedFile]);
  }, [copy, files, selectedFile]);

  /**
   * Keyboard Shortcuts
   */
  useKeyCombo(['Control', 's'], (e) => {
    e.preventDefault();
    handleSave();
  });

  useKeyCombo(['Control', 'r'], (e) => {
    e.preventDefault();
    handleRun();
  });

  useKeyCombo(['Control', 'p'], (e) => {
    e.preventDefault();
    setShowPreview(prev => !prev);
  });

  /**
   * Render
   */
  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Toolbar */}
      <Toolbar
        onSave={handleSave}
        onRun={handleRun}
        onExport={handleExport}
        onSettings={() => setShowSettings(true)}
        isSaving={isSaving}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - File List */}
        {!isMobile && (
          <div className="w-56 bg-gray-800 border-r border-gray-700 flex flex-col">
            <div className="p-3 border-b border-gray-700">
              <Input
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="bg-gray-900 border-gray-700 text-sm"
                placeholder="Project name"
              />
            </div>

            <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
              <div className="text-xs text-gray-500 uppercase font-semibold mb-2 px-2">
                Files
              </div>
              {fileList.map(fileName => (
                <button
                  key={fileName}
                  onClick={() => setSelectedFile(fileName)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedFile === fileName
                      ? 'bg-emerald-600/20 text-emerald-400'
                      : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {fileName}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Editor */}
        <div className={`flex-1 flex ${showPreview ? 'w-1/2' : 'w-full'}`}>
          <FileEditor
            fileName={selectedFile}
            content={files[selectedFile]}
            onChange={handleFileChange}
          />
        </div>

        {/* Preview */}
        {showPreview && (
          <div className="w-1/2 border-l border-gray-700">
            <div className="h-full flex flex-col">
              <div className="px-4 py-2 bg-gray-800 border-b border-gray-700 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Eye className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-300">Preview</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPreview(false)}
                >
                  Hide
                </Button>
              </div>
              <div className="flex-1">
                <WebContainerPreview files={previewFiles} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Settings Modal */}
      <Modal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        title="Editor Settings"
        size="md"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowSettings(false)}>
              Cancel
            </Button>
            <Button onClick={() => setShowSettings(false)}>
              Save Settings
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Auto-save</span>
                  <input type="checkbox" defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Debounce delay</span>
                  <span className="text-sm text-gray-400">300ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Reduced motion</span>
                  <span className="text-sm text-gray-400">
                    {prefersReducedMotion ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Appearance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Theme</span>
                  <span className="text-sm text-gray-400">Dark</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Font size</span>
                  <span className="text-sm text-gray-400">14px</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Keyboard Shortcuts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-300">Save</span>
                  <code className="px-2 py-1 bg-gray-800 rounded text-gray-400">Ctrl+S</code>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Run</span>
                  <code className="px-2 py-1 bg-gray-800 rounded text-gray-400">Ctrl+R</code>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Toggle Preview</span>
                  <code className="px-2 py-1 bg-gray-800 rounded text-gray-400">Ctrl+P</code>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </Modal>

      {/* Toast notification (si copie reussie) */}
      {copiedText && (
        <div className="fixed bottom-4 right-4 bg-emerald-600 text-white px-4 py-2 rounded-lg shadow-lg animate-slide-up">
          Code copied to clipboard!
        </div>
      )}
    </div>
  );
}
