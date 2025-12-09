/**
 * Composant principal de l'éditeur Monaco
 */

import React, { useCallback } from 'react';
import Editor from '@monaco-editor/react';
import { Code2, Copy, Check, PanelLeftClose } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { useEditorStore } from '../hooks/useEditorState';
import { useFileManager } from '../hooks/useFileManager';

interface EditorMainProps {
  onCopyCode: () => void;
}

export const EditorMain: React.FC<EditorMainProps> = ({ onCopyCode }) => {
  const { copied, setShowEditor, updateFileContent } = useEditorStore();
  const { currentFile, currentFileIndex } = useFileManager();

  const handleEditorChange = useCallback(
    (value: string | undefined) => {
      if (value !== undefined) {
        updateFileContent(currentFileIndex, value);
      }
    },
    [currentFileIndex, updateFileContent]
  );

  if (!currentFile) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <p>Aucun fichier sélectionné</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col border-r border-white/5">
      {/* Header */}
      <div className="p-2 border-b border-white/5 bg-black/20 flex justify-between items-center flex-shrink-0">
        <div className="flex items-center gap-2">
          <Code2 className="w-4 h-4 text-emerald-400" />
          <span className="text-sm font-medium">Éditeur</span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            data-testid="toggle-editor-button"
            variant="ghost"
            size="sm"
            onClick={() => setShowEditor(false)}
            className="text-gray-400 hover:text-white"
            title="Masquer l'éditeur"
          >
            <PanelLeftClose className="w-4 h-4" />
          </Button>
          <Button
            data-testid="copy-code-button"
            variant="ghost"
            size="sm"
            onClick={onCopyCode}
            className="text-gray-400 hover:text-white"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Monaco Editor */}
      <div className="flex-1">
        <Editor
          height="100%"
          language={currentFile.language}
          value={currentFile.content}
          onChange={handleEditorChange}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
          }}
        />
      </div>
    </div>
  );
};
