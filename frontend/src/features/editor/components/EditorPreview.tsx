/**
 * Composant Preview avec support Full-Stack et Vercel
 */

import React, { useRef, useEffect, useCallback } from 'react';
import {
  Eye,
  Play,
  PanelLeftOpen,
  ExternalLink,
  Rocket,
  Loader2,
} from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { useEditorStore } from '../hooks/useEditorState';
import { useExportDeploy } from '../hooks/useExportDeploy';
import { isFullStackProject } from '../types/editor.types';

interface EditorPreviewProps {
  showToggleButton?: boolean;
}

export const EditorPreview: React.FC<EditorPreviewProps> = ({
  showToggleButton = false,
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const {
    project,
    showEditor,
    previewUrl,
    previewLoading,
    setShowEditor,
  } = useEditorStore();

  const { generateVercelPreview } = useExportDeploy();

  const isFullStack = isFullStackProject(project.files);

  /**
   * Mettre à jour le preview HTML/CSS/JS
   */
  const updatePreview = useCallback(() => {
    if (!iframeRef.current) return;

    if (isFullStack) {
      // Message informatif pour les projets Full-Stack
      const fullStackMessage = `
<!DOCTYPE html>
<html>
<head>
  <title>Preview Full-Stack</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: white;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .container {
      text-align: center;
      max-width: 500px;
    }
    .icon {
      font-size: 64px;
      margin-bottom: 24px;
    }
    h1 {
      font-size: 24px;
      margin-bottom: 16px;
      background: linear-gradient(90deg, #10b981, #3b82f6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    p {
      color: #9ca3af;
      line-height: 1.6;
      margin-bottom: 24px;
    }
    .stack {
      display: flex;
      gap: 8px;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 24px;
    }
    .badge {
      background: rgba(255,255,255,0.1);
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 12px;
      border: 1px solid rgba(255,255,255,0.1);
    }
    .info {
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 12px;
      padding: 16px;
      font-size: 14px;
      color: #93c5fd;
    }
    .arrow { margin: 0 8px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">🚀</div>
    <h1>Projet Full-Stack Next.js</h1>
    <p>
      Ce projet utilise Next.js 14+ avec App Router, TypeScript et des fonctionnalités serveur.
      L'aperçu instantané n'est pas disponible pour ce type de projet.
    </p>
    <div class="stack">
      <span class="badge">Next.js 14+</span>
      <span class="badge">TypeScript</span>
      <span class="badge">Tailwind CSS</span>
      <span class="badge">Supabase</span>
    </div>
    <div class="info">
      <strong>💡 Pour voir l'aperçu :</strong><br/>
      Cliquez sur le bouton <strong>"Preview Vercel"</strong> ci-dessus<br/>
      <span class="arrow">→</span> Déploiement en ~30-60 secondes
    </div>
  </div>
</body>
</html>
      `;
      iframeRef.current.srcdoc = fullStackMessage;
      return;
    }

    // Preview standard HTML/CSS/JS
    const defaultFiles = ['index.html', 'styles.css', 'script.js'];

    const htmlFile =
      project.files.find(
        (f) => f.name.endsWith('.html') && !defaultFiles.includes(f.name)
      ) || project.files.find((f) => f.name.endsWith('.html'));

    const cssFile =
      project.files.find(
        (f) => f.name.endsWith('.css') && !defaultFiles.includes(f.name)
      ) || project.files.find((f) => f.name.endsWith('.css'));

    const jsFile =
      project.files.find(
        (f) => f.name.endsWith('.js') && !defaultFiles.includes(f.name)
      ) || project.files.find((f) => f.name.endsWith('.js'));

    let html =
      htmlFile?.content ||
      '<!DOCTYPE html><html><head></head><body><h1>Pas de fichier HTML</h1></body></html>';

    // Injecter le CSS
    if (cssFile && html.includes('</head>')) {
      html = html.replace('</head>', `<style>${cssFile.content}</style></head>`);
    }

    // Injecter le JS
    if (jsFile && html.includes('</body>')) {
      html = html.replace('</body>', `<script>${jsFile.content}</script></body>`);
    }

    iframeRef.current.srcdoc = html;
  }, [project.files, isFullStack]);

  // Mettre à jour le preview quand les fichiers changent
  useEffect(() => {
    const timer = setTimeout(() => {
      updatePreview();
    }, 50);
    return () => clearTimeout(timer);
  }, [project.files, showEditor, updatePreview]);

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-2 border-b border-gray-200 bg-gray-50 flex justify-between items-center flex-shrink-0">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-blue-500" />
          <span className="text-sm font-medium text-gray-700">
            {isFullStack ? 'Aperçu Full-Stack' : 'Aperçu'}
          </span>
          {isFullStack && (
            <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">
              Next.js
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Show editor toggle button when editor is hidden */}
          {showToggleButton && (
            <Button
              data-testid="show-editor-button"
              variant="ghost"
              size="sm"
              onClick={() => setShowEditor(true)}
              className="text-gray-600 hover:text-gray-900"
              title="Afficher l'éditeur"
            >
              <PanelLeftOpen className="w-4 h-4" />
            </Button>
          )}
          {/* Show Vercel Preview button for Full-Stack projects */}
          {isFullStack && (
            <>
              {previewUrl ? (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => window.open(previewUrl, '_blank')}
                  className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                  title="Ouvrir le preview"
                >
                  <ExternalLink className="w-4 h-4 mr-1" />
                  Voir Preview
                </Button>
              ) : (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={generateVercelPreview}
                  disabled={previewLoading}
                  className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                  title="Déployer un preview sur Vercel"
                >
                  {previewLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-1" />
                  ) : (
                    <Rocket className="w-4 h-4 mr-1" />
                  )}
                  Preview Vercel
                </Button>
              )}
            </>
          )}

          {/* Refresh button for simple projects */}
          {!isFullStack && (
            <Button
              data-testid="refresh-preview-button"
              variant="ghost"
              size="sm"
              onClick={updatePreview}
              className="text-gray-600 hover:text-gray-900"
            >
              <Play className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Preview content */}
      <div className="flex-1 overflow-hidden relative">
        {/* Show iframe for simple projects OR Full-Stack info message */}
        <iframe
          ref={iframeRef}
          data-testid="preview-iframe"
          title="Preview"
          className="w-full h-full border-0"
          sandbox="allow-scripts allow-modals"
        />

        {/* Overlay with Vercel preview iframe for Full-Stack when URL exists */}
        {isFullStack && previewUrl && (
          <div className="absolute inset-0 bg-white">
            <iframe
              src={previewUrl}
              title="Vercel Preview"
              className="w-full h-full border-0"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            />
          </div>
        )}
      </div>
    </div>
  );
};
