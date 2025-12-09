/**
 * CodeDiff Component
 * Agent: AI Chat Engineer
 *
 * Affichage des différences de code (diff viewer)
 */

import React from 'react';
import type { FileChange, DiffChunk } from '../types/chat.types';

export interface CodeDiffProps {
  fileChange: FileChange;
  showLineNumbers?: boolean;
  maxHeight?: string;
  className?: string;
}

export const CodeDiff: React.FC<CodeDiffProps> = ({
  fileChange,
  showLineNumbers = true,
  maxHeight = '400px',
  className = '',
}) => {
  const { path, action, oldContent, newContent, diff } = fileChange;

  // Simple line-by-line diff if no diff provided
  const renderSimpleDiff = () => {
    if (action === 'create' && newContent) {
      return (
        <div className="font-mono text-sm">
          {newContent.split('\n').map((line, i) => (
            <div key={i} className="bg-green-50 border-l-4 border-green-500 px-4 py-1">
              {showLineNumbers && <span className="text-gray-400 mr-4">{i + 1}</span>}
              <span className="text-green-700">+ {line}</span>
            </div>
          ))}
        </div>
      );
    }

    if (action === 'delete' && oldContent) {
      return (
        <div className="font-mono text-sm">
          {oldContent.split('\n').map((line, i) => (
            <div key={i} className="bg-red-50 border-l-4 border-red-500 px-4 py-1">
              {showLineNumbers && <span className="text-gray-400 mr-4">{i + 1}</span>}
              <span className="text-red-700">- {line}</span>
            </div>
          ))}
        </div>
      );
    }

    // For update, show both old and new
    const oldLines = oldContent?.split('\n') || [];
    const newLines = newContent?.split('\n') || [];
    const maxLines = Math.max(oldLines.length, newLines.length);

    return (
      <div className="font-mono text-sm">
        {Array.from({ length: maxLines }).map((_, i) => {
          const oldLine = oldLines[i];
          const newLine = newLines[i];
          const isDifferent = oldLine !== newLine;

          if (oldLine === undefined) {
            return (
              <div key={i} className="bg-green-50 border-l-4 border-green-500 px-4 py-1">
                {showLineNumbers && <span className="text-gray-400 mr-4">{i + 1}</span>}
                <span className="text-green-700">+ {newLine}</span>
              </div>
            );
          }

          if (newLine === undefined) {
            return (
              <div key={i} className="bg-red-50 border-l-4 border-red-500 px-4 py-1">
                {showLineNumbers && <span className="text-gray-400 mr-4">{i + 1}</span>}
                <span className="text-red-700">- {oldLine}</span>
              </div>
            );
          }

          if (isDifferent) {
            return (
              <React.Fragment key={i}>
                <div className="bg-red-50 border-l-4 border-red-500 px-4 py-1">
                  {showLineNumbers && <span className="text-gray-400 mr-4">{i + 1}</span>}
                  <span className="text-red-700">- {oldLine}</span>
                </div>
                <div className="bg-green-50 border-l-4 border-green-500 px-4 py-1">
                  {showLineNumbers && <span className="text-gray-400 mr-4">{i + 1}</span>}
                  <span className="text-green-700">+ {newLine}</span>
                </div>
              </React.Fragment>
            );
          }

          return (
            <div key={i} className="bg-gray-50 px-4 py-1">
              {showLineNumbers && <span className="text-gray-400 mr-4">{i + 1}</span>}
              <span className="text-gray-700">{oldLine}</span>
            </div>
          );
        })}
      </div>
    );
  };

  // Render structured diff if available
  const renderStructuredDiff = () => {
    if (!diff) return renderSimpleDiff();

    return (
      <div className="font-mono text-sm">
        {diff.changes.map((chunk: DiffChunk, i: number) => {
          const bgColor =
            chunk.type === 'add'
              ? 'bg-green-50 border-l-4 border-green-500'
              : chunk.type === 'remove'
              ? 'bg-red-50 border-l-4 border-red-500'
              : 'bg-gray-50';

          const textColor =
            chunk.type === 'add'
              ? 'text-green-700'
              : chunk.type === 'remove'
              ? 'text-red-700'
              : 'text-gray-700';

          const prefix = chunk.type === 'add' ? '+ ' : chunk.type === 'remove' ? '- ' : '  ';

          return (
            <div key={i} className={`${bgColor} px-4 py-1`}>
              {showLineNumbers && <span className="text-gray-400 mr-4">{chunk.lineNumber}</span>}
              <span className={textColor}>
                {prefix}
                {chunk.content}
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className={`border rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gray-100 px-4 py-2 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-gray-700">{path}</span>
          <span
            className={`text-xs px-2 py-1 rounded ${
              action === 'create'
                ? 'bg-green-100 text-green-700'
                : action === 'delete'
                ? 'bg-red-100 text-red-700'
                : 'bg-blue-100 text-blue-700'
            }`}
          >
            {action}
          </span>
        </div>
        {diff && (
          <div className="flex items-center gap-4 text-sm">
            <span className="text-green-600">+{diff.additions}</span>
            <span className="text-red-600">-{diff.deletions}</span>
          </div>
        )}
      </div>

      {/* Diff Content */}
      <div className="overflow-auto" style={{ maxHeight }}>
        {renderStructuredDiff()}
      </div>
    </div>
  );
};

export default CodeDiff;
