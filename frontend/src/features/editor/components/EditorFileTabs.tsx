/**
 * Composant pour les onglets de fichiers
 */

import React from 'react';
import { FileCode, Plus, X } from 'lucide-react';
import { Button } from '../../../components/ui/button';
import { useFileManager } from '../hooks/useFileManager';

export const EditorFileTabs: React.FC = () => {
  const { files, currentFileIndex, selectFile, deleteFileAt, addNewFile } =
    useFileManager();

  return (
    <div className="border-b border-white/5 bg-black/20 flex items-center gap-2 px-4 py-2 overflow-x-auto flex-shrink-0 max-w-full">
      {files.map((file, idx) => (
        <div
          key={file.name}
          data-testid={`file-tab-${idx}`}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md cursor-pointer transition-colors flex-shrink-0 ${
            currentFileIndex === idx
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
          onClick={() => selectFile(idx)}
        >
          <FileCode className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm font-medium whitespace-nowrap">
            {file.name}
          </span>
          {files.length > 1 && (
            <button
              data-testid={`delete-file-${idx}`}
              onClick={(e) => {
                e.stopPropagation();
                deleteFileAt(idx);
              }}
              className="text-gray-500 hover:text-red-400 flex-shrink-0"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      ))}
      <Button
        data-testid="add-file-button"
        variant="ghost"
        size="sm"
        onClick={addNewFile}
        className="text-gray-400 hover:text-white flex-shrink-0"
      >
        <Plus className="w-4 h-4" />
      </Button>
    </div>
  );
};
