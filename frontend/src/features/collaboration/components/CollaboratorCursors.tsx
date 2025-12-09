/**
 * Affichage des curseurs des collaborateurs dans l'éditeur
 */

import React, { useEffect, useRef } from 'react';
import type { editor as monacoEditor } from 'monaco-editor';
import type { User } from '../types';

interface CollaboratorCursorsProps {
  editor: monacoEditor.IStandaloneCodeEditor | null;
  users: User[];
  className?: string;
}

interface CursorDecoration {
  id: string[];
  userId: string;
}

export function CollaboratorCursors({ editor, users, className = '' }: CollaboratorCursorsProps) {
  const decorationsRef = useRef<Map<string, CursorDecoration>>(new Map());

  useEffect(() => {
    if (!editor) return;

    // Nettoie les anciennes décorations
    const oldDecorations = Array.from(decorationsRef.current.values()).flatMap((d) => d.id);
    if (oldDecorations.length > 0) {
      editor.deltaDecorations(oldDecorations, []);
    }

    // Crée les nouvelles décorations
    const newDecorations = new Map<string, CursorDecoration>();

    users.forEach((user) => {
      if (!user.cursor) return;

      const { line, column } = user.cursor;

      // Crée la décoration du curseur
      const decorationIds = editor.deltaDecorations(
        [],
        [
          {
            range: {
              startLineNumber: line,
              startColumn: column,
              endLineNumber: line,
              endColumn: column,
            },
            options: {
              className: `collaborator-cursor collaborator-cursor-${user.id}`,
              beforeContentClassName: 'collaborator-cursor-line',
              stickiness: 1, // NeverGrowsWhenTypingAtEdges
            },
          },
          {
            range: {
              startLineNumber: line,
              startColumn: column,
              endLineNumber: line,
              endColumn: column,
            },
            options: {
              afterContentClassName: 'collaborator-cursor-label',
              after: {
                content: user.name,
                inlineClassName: 'collaborator-cursor-label-text',
              },
              stickiness: 1,
            },
          },
        ]
      );

      newDecorations.set(user.id, {
        id: decorationIds,
        userId: user.id,
      });
    });

    decorationsRef.current = newDecorations;

    // Injecte les styles CSS dynamiques pour les couleurs
    injectCursorStyles(users);

    return () => {
      // Nettoie toutes les décorations lors du démontage
      const allDecorations = Array.from(decorationsRef.current.values()).flatMap((d) => d.id);
      if (allDecorations.length > 0 && editor) {
        editor.deltaDecorations(allDecorations, []);
      }
    };
  }, [editor, users]);

  return null; // Ce composant ne rend rien directement
}

/**
 * Injecte les styles CSS pour les curseurs des utilisateurs
 */
function injectCursorStyles(users: User[]) {
  const styleId = 'collaborator-cursor-styles';
  let styleElement = document.getElementById(styleId) as HTMLStyleElement | null;

  if (!styleElement) {
    styleElement = document.createElement('style');
    styleElement.id = styleId;
    document.head.appendChild(styleElement);
  }

  const styles = users
    .map(
      (user) => `
    .collaborator-cursor-${user.id} {
      position: relative;
    }

    .collaborator-cursor-${user.id} .collaborator-cursor-line {
      content: '';
      position: absolute;
      width: 2px;
      height: 1.2em;
      background-color: ${user.color};
      z-index: 100;
      pointer-events: none;
    }

    .collaborator-cursor-${user.id} .collaborator-cursor-label {
      position: absolute;
      top: -1.5em;
      left: 0;
      padding: 2px 6px;
      background-color: ${user.color};
      color: white;
      font-size: 0.75em;
      font-weight: 500;
      border-radius: 3px;
      white-space: nowrap;
      z-index: 101;
      pointer-events: none;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .collaborator-cursor-${user.id}::before {
      content: '';
      position: absolute;
      width: 0;
      height: 0;
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
      border-top: 4px solid ${user.color};
      top: -1.5em;
      left: 2px;
      z-index: 100;
      pointer-events: none;
    }
  `
    )
    .join('\n');

  // Ajoute les styles de base
  const baseStyles = `
    .collaborator-cursor {
      position: relative;
    }

    .collaborator-cursor-label-text {
      user-select: none;
      pointer-events: none;
    }
  `;

  styleElement.textContent = baseStyles + styles;
}
