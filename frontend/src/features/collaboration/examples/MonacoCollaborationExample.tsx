/**
 * Exemple d'intégration de la collaboration avec Monaco Editor
 */

import React, { useEffect, useRef, useState } from 'react';
import Editor, { Monaco } from '@monaco-editor/react';
import type { editor as monacoEditor } from 'monaco-editor';
import { useCollaboration, useAwareness } from '../hooks';
import { ConnectionStatus, PresenceIndicator, CollaboratorCursors } from '../components';
import { createMonacoBinding } from '../utils/monaco-binding';
import type { MonacoBinding } from '../utils/monaco-binding';

interface MonacoCollaborationExampleProps {
  projectId: string;
  filePath: string;
  userId: string;
  userName: string;
  defaultValue?: string;
  language?: string;
}

export function MonacoCollaborationExample({
  projectId,
  filePath,
  userId,
  userName,
  defaultValue = '',
  language = 'typescript',
}: MonacoCollaborationExampleProps) {
  const editorRef = useRef<monacoEditor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const bindingRef = useRef<MonacoBinding | null>(null);

  const [isEditorReady, setIsEditorReady] = useState(false);

  // Configuration de la collaboration
  const wsUrl = process.env.REACT_APP_COLLABORATION_WS || 'ws://localhost:4000';
  const documentId = `${projectId}/${filePath}`;

  const collaboration = useCollaboration({
    wsUrl,
    documentId,
    user: {
      id: userId,
      name: userName,
      color: '', // Sera généré automatiquement
    },
    autoConnect: isEditorReady,
  });

  const awareness = useAwareness(
    collaboration.isConnected ? (collaboration as any).providerRef?.current : null
  );

  // Gère le montage de l'éditeur
  function handleEditorDidMount(
    editor: monacoEditor.IStandaloneCodeEditor,
    monaco: Monaco
  ) {
    editorRef.current = editor;
    monacoRef.current = monaco;
    setIsEditorReady(true);

    // Configure l'éditeur
    editor.updateOptions({
      fontSize: 14,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout: true,
    });
  }

  // Setup du binding Monaco-Yjs
  useEffect(() => {
    if (!isEditorReady || !editorRef.current || !collaboration.isConnected) {
      return;
    }

    // Crée le binding
    const provider = (collaboration as any).providerRef?.current;
    if (provider) {
      bindingRef.current = createMonacoBinding(editorRef.current, provider);
      console.log('✓ Monaco binding created');
    }

    return () => {
      if (bindingRef.current) {
        bindingRef.current.destroy();
        bindingRef.current = null;
        console.log('✓ Monaco binding destroyed');
      }
    };
  }, [isEditorReady, collaboration.isConnected]);

  return (
    <div className="flex flex-col h-full">
      {/* Barre d'outils */}
      <div className="flex items-center justify-between px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-3">
          <ConnectionStatus
            status={collaboration.state.status}
            latency={collaboration.state.latency}
          />
          <PresenceIndicator users={collaboration.activeUsers} />
        </div>

        <div className="text-sm text-gray-600 dark:text-gray-400">
          {filePath}
        </div>
      </div>

      {/* Éditeur */}
      <div className="flex-1 relative">
        <Editor
          defaultLanguage={language}
          defaultValue={defaultValue}
          onMount={handleEditorDidMount}
          theme="vs-dark"
          options={{
            readOnly: !collaboration.isConnected,
          }}
        />

        {/* Curseurs des collaborateurs */}
        {isEditorReady && (
          <CollaboratorCursors
            editor={editorRef.current}
            users={Array.from(awareness.users.values())}
          />
        )}
      </div>

      {/* Message d'erreur */}
      {collaboration.state.error && (
        <div className="px-4 py-2 bg-red-50 dark:bg-red-900/20 border-t border-red-200 dark:border-red-800">
          <p className="text-sm text-red-600 dark:text-red-400">
            Erreur: {collaboration.state.error}
          </p>
        </div>
      )}
    </div>
  );
}
