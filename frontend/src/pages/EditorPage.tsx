/**
 * EditorPage - Container principal refactoré
 * Architecture modulaire avec hooks et composants séparés
 */

import React, { useEffect, useCallback, useState } from 'react';
import SplitPane from 'react-split-pane';
import { EditorToolbar } from '../features/editor/components/EditorToolbar';
import { EditorChat } from '../features/editor/components/EditorChat';
import { EditorFileTabs } from '../features/editor/components/EditorFileTabs';
import { EditorMain } from '../features/editor/components/EditorMain';
import { EditorPreview } from '../features/editor/components/EditorPreview';
import { useEditorStore } from '../features/editor/hooks/useEditorState';
import { useEditorActions } from '../features/editor/hooks/useEditorActions';
import { useFileManager } from '../features/editor/hooks/useFileManager';
import '../pages/EditorPage.css';

const EditorPage: React.FC = () => {
  const { showEditor, copied, setCopied } = useEditorStore();
  const { loadProject, loadSettings } = useEditorActions();
  const { currentFile } = useFileManager();

  // Charger le projet et les paramètres au montage
  useEffect(() => {
    loadProject();
    loadSettings();
  }, [loadProject, loadSettings]);

  // Copier le code du fichier courant
  const handleCopyCode = useCallback(async () => {
    if (!currentFile) return;

    try {
      await navigator.clipboard.writeText(currentFile.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Error copying code:', error);
    }
  }, [currentFile, setCopied]);

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0b]">
      {/* Header Toolbar */}
      <EditorToolbar />

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <SplitPane
          split="vertical"
          minSize={250}
          maxSize={600}
          defaultSize={320}
        >
          {/* Chat Panel */}
          <EditorChat />

          {/* Code Editor & Preview */}
          <div className="h-full flex flex-col overflow-hidden min-w-0">
            {/* File Tabs - Toujours visibles */}
            <EditorFileTabs />

            {/* Editor & Preview Split */}
            <div className="flex-1 overflow-hidden">
              {showEditor ? (
                <SplitPane split="vertical" minSize={300} defaultSize="50%">
                  {/* Code Editor */}
                  <EditorMain onCopyCode={handleCopyCode} />

                  {/* Preview */}
                  <EditorPreview />
                </SplitPane>
              ) : (
                /* Preview uniquement quand l'éditeur est masqué */
                <EditorPreview showToggleButton={true} />
              )}
            </div>
          </div>
        </SplitPane>
      </div>
    </div>
  );
};

export default EditorPage;
