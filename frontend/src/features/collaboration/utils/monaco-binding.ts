/**
 * Binding entre Monaco Editor et Yjs pour la synchronisation
 */

import * as Y from 'yjs';
import type { editor as monacoEditor } from 'monaco-editor';
import type { WebsocketProvider } from 'y-websocket';

export class MonacoBinding {
  private ydoc: Y.Doc;
  private ytext: Y.Text;
  private editor: monacoEditor.IStandaloneCodeEditor;
  private provider: WebsocketProvider;
  private isLocalChange = false;
  private disposables: Array<() => void> = [];

  constructor(
    ydoc: Y.Doc,
    ytext: Y.Text,
    editor: monacoEditor.IStandaloneCodeEditor,
    provider: WebsocketProvider
  ) {
    this.ydoc = ydoc;
    this.ytext = ytext;
    this.editor = editor;
    this.provider = provider;

    this.setupBindings();
  }

  private setupBindings(): void {
    // Observe les changements Yjs et les applique à Monaco
    const ytextObserver = (event: Y.YTextEvent, transaction: Y.Transaction) => {
      // Ignore les changements locaux
      if (transaction.local) return;

      this.isLocalChange = true;

      event.delta.forEach((delta) => {
        const model = this.editor.getModel();
        if (!model) return;

        if (delta.retain !== undefined) {
          // Position avancée, rien à faire
        } else if (delta.insert !== undefined) {
          // Insertion de texte
          const position = model.getPositionAt(delta.retain || 0);
          const insertText = Array.isArray(delta.insert)
            ? delta.insert.join('')
            : String(delta.insert);

          this.editor.executeEdits('yjs', [
            {
              range: {
                startLineNumber: position.lineNumber,
                startColumn: position.column,
                endLineNumber: position.lineNumber,
                endColumn: position.column,
              },
              text: insertText,
            },
          ]);
        } else if (delta.delete !== undefined) {
          // Suppression de texte
          const startPos = model.getPositionAt(delta.retain || 0);
          const endPos = model.getPositionAt((delta.retain || 0) + delta.delete);

          this.editor.executeEdits('yjs', [
            {
              range: {
                startLineNumber: startPos.lineNumber,
                startColumn: startPos.column,
                endLineNumber: endPos.lineNumber,
                endColumn: endPos.column,
              },
              text: '',
            },
          ]);
        }
      });

      this.isLocalChange = false;
    };

    this.ytext.observe(ytextObserver);
    this.disposables.push(() => this.ytext.unobserve(ytextObserver));

    // Observe les changements Monaco et les applique à Yjs
    const monacoListener = this.editor.onDidChangeModelContent((event) => {
      // Ignore les changements provenant de Yjs
      if (this.isLocalChange) return;

      const model = this.editor.getModel();
      if (!model) return;

      this.ydoc.transact(() => {
        event.changes
          .sort((a, b) => b.rangeOffset - a.rangeOffset)
          .forEach((change) => {
            if (change.rangeLength > 0) {
              this.ytext.delete(change.rangeOffset, change.rangeLength);
            }
            if (change.text.length > 0) {
              this.ytext.insert(change.rangeOffset, change.text);
            }
          });
      });
    });

    this.disposables.push(() => monacoListener.dispose());

    // Synchronise le contenu initial
    const initialContent = this.ytext.toString();
    if (initialContent !== this.editor.getValue()) {
      this.isLocalChange = true;
      this.editor.setValue(initialContent);
      this.isLocalChange = false;
    }

    // Gère les changements de curseur
    const cursorListener = this.editor.onDidChangeCursorPosition((event) => {
      if (this.provider.awareness) {
        this.provider.awareness.setLocalStateField('cursor', {
          line: event.position.lineNumber,
          column: event.position.column,
        });
      }
    });

    this.disposables.push(() => cursorListener.dispose());

    // Gère les changements de sélection
    const selectionListener = this.editor.onDidChangeCursorSelection((event) => {
      if (this.provider.awareness && event.selection) {
        this.provider.awareness.setLocalStateField('selection', {
          start: {
            line: event.selection.startLineNumber,
            column: event.selection.startColumn,
          },
          end: {
            line: event.selection.endLineNumber,
            column: event.selection.endColumn,
          },
        });
      }
    });

    this.disposables.push(() => selectionListener.dispose());
  }

  /**
   * Détruit le binding et nettoie les ressources
   */
  destroy(): void {
    this.disposables.forEach((dispose) => dispose());
    this.disposables = [];
  }
}

/**
 * Crée un binding entre Monaco et Yjs
 */
export function createMonacoBinding(
  editor: monacoEditor.IStandaloneCodeEditor,
  provider: WebsocketProvider,
  textName = 'monaco'
): MonacoBinding {
  const ydoc = provider.doc;
  const ytext = ydoc.getText(textName);

  return new MonacoBinding(ydoc, ytext, editor, provider);
}
