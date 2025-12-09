/**
 * Hook pour la gestion des fichiers (add, delete, update)
 */

import { useCallback } from 'react';
import { toast } from 'sonner';
import { useEditorStore } from './useEditorState';
import { ProjectFile } from '../../../types/project';

/**
 * Map des extensions vers les langages Monaco
 */
const LANGUAGE_MAP: Record<string, string> = {
  html: 'html',
  css: 'css',
  js: 'javascript',
  ts: 'typescript',
  tsx: 'typescriptreact',
  jsx: 'javascriptreact',
  json: 'json',
  md: 'markdown',
  sql: 'sql',
};

/**
 * Hook pour gérer les fichiers du projet
 */
export function useFileManager() {
  const { project, currentFileIndex, addFile, deleteFile, setCurrentFileIndex } =
    useEditorStore();

  /**
   * Ajouter un nouveau fichier
   */
  const addNewFile = useCallback(() => {
    const fileName = prompt('Nom du fichier (ex: app.js, styles.css):');
    if (!fileName) return;

    const extension = fileName.split('.').pop() || 'txt';
    const language = LANGUAGE_MAP[extension] || 'plaintext';

    const newFile: ProjectFile = {
      name: fileName,
      content: '',
      language: language as any,
    };

    addFile(newFile);
    toast.success(`Fichier "${fileName}" créé`);
  }, [addFile]);

  /**
   * Supprimer un fichier
   */
  const deleteFileAt = useCallback(
    (index: number) => {
      if (project.files.length <= 1) {
        toast.error('Vous devez avoir au moins un fichier');
        return;
      }

      if (window.confirm('Supprimer ce fichier ?')) {
        const fileName = project.files[index].name;
        deleteFile(index);
        toast.success(`Fichier "${fileName}" supprimé`);
      }
    },
    [project.files, deleteFile]
  );

  /**
   * Sélectionner un fichier
   */
  const selectFile = useCallback(
    (index: number) => {
      if (index >= 0 && index < project.files.length) {
        setCurrentFileIndex(index);
      }
    },
    [project.files.length, setCurrentFileIndex]
  );

  /**
   * Obtenir le fichier courant
   */
  const getCurrentFile = useCallback((): ProjectFile | null => {
    return project.files[currentFileIndex] || null;
  }, [project.files, currentFileIndex]);

  return {
    files: project.files,
    currentFileIndex,
    currentFile: getCurrentFile(),
    addNewFile,
    deleteFileAt,
    selectFile,
  };
}
