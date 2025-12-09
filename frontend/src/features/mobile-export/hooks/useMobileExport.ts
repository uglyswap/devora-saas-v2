/**
 * useMobileExport Hook
 * Handle mobile export operations
 * @version 1.0.0
 */

import { useState, useCallback } from 'react';
import axios from 'axios';
import {
  MobileFramework,
  ExportRequest,
  ExportResult,
  ExportPreview,
  FrameworkInfo,
  ConvertedComponent,
  ExportHistoryItem
} from '../types/mobile-export.types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

interface UseMobileExportOptions {
  onExportComplete?: (result: ExportResult) => void;
  onExportError?: (error: string) => void;
}

interface UseMobileExportReturn {
  // State
  isExporting: boolean;
  currentExport: ExportResult | null;
  preview: ExportPreview | null;
  error: string | null;

  // Actions
  exportToMobile: (request: ExportRequest) => Promise<ExportResult>;
  previewExport: (request: ExportRequest) => Promise<ExportPreview>;
  downloadExport: (exportId: string) => void;
  convertComponent: (content: string, filename: string) => Promise<ConvertedComponent>;
  convertTailwind: (classes: string) => Promise<Record<string, unknown>>;
  getFrameworks: () => Promise<FrameworkInfo[]>;
  getHistory: (limit?: number) => Promise<ExportHistoryItem[]>;
  deleteExport: (exportId: string) => Promise<void>;

  // Utilities
  reset: () => void;
}

export function useMobileExport(options: UseMobileExportOptions = {}): UseMobileExportReturn {
  const { onExportComplete, onExportError } = options;

  const [isExporting, setIsExporting] = useState(false);
  const [currentExport, setCurrentExport] = useState<ExportResult | null>(null);
  const [preview, setPreview] = useState<ExportPreview | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reset = useCallback(() => {
    setIsExporting(false);
    setCurrentExport(null);
    setPreview(null);
    setError(null);
  }, []);

  /**
   * Export project to mobile
   */
  const exportToMobile = useCallback(async (request: ExportRequest): Promise<ExportResult> => {
    reset();
    setIsExporting(true);

    try {
      const response = await axios.post<ExportResult>(
        `${API_URL}/api/mobile/export`,
        {
          project_id: request.projectId,
          project_name: request.projectName,
          files: request.files.map(f => ({
            name: f.name,
            content: f.content,
            type: f.type || 'unknown'
          })),
          framework: request.framework,
          use_typescript: request.useTypeScript ?? true,
          include_navigation: request.includeNavigation ?? true
        }
      );

      const result: ExportResult = {
        id: response.data.id,
        success: response.data.success,
        downloadUrl: response.data.downloadUrl,
        error: response.data.error,
        stats: response.data.stats || {
          components_converted: 0,
          pages_created: 0,
          styles_converted: 0,
          total_files: 0
        },
        warnings: response.data.warnings || [],
        filesCount: response.data.filesCount || 0,
        createdAt: response.data.createdAt || new Date().toISOString()
      };

      setCurrentExport(result);

      if (result.success) {
        onExportComplete?.(result);
      } else {
        setError(result.error || 'Export failed');
        onExportError?.(result.error || 'Export failed');
      }

      return result;
    } catch (err: unknown) {
      const errorMsg = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'Export failed';
      setError(errorMsg);
      onExportError?.(errorMsg);
      throw err;
    } finally {
      setIsExporting(false);
    }
  }, [reset, onExportComplete, onExportError]);

  /**
   * Preview export without downloading
   */
  const previewExport = useCallback(async (request: ExportRequest): Promise<ExportPreview> => {
    setError(null);

    try {
      const response = await axios.post<ExportPreview>(
        `${API_URL}/api/mobile/preview`,
        {
          project_id: request.projectId,
          project_name: request.projectName,
          files: request.files.map(f => ({
            name: f.name,
            content: f.content,
            type: f.type || 'unknown'
          })),
          framework: request.framework,
          use_typescript: request.useTypeScript ?? true,
          include_navigation: request.includeNavigation ?? true
        }
      );

      const previewResult: ExportPreview = {
        files: response.data.files || [],
        totalSize: response.data.totalSize || 0,
        framework: response.data.framework || request.framework,
        warnings: response.data.warnings || []
      };

      setPreview(previewResult);
      return previewResult;
    } catch (err: unknown) {
      const errorMsg = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'Preview failed';
      setError(errorMsg);
      throw err;
    }
  }, []);

  /**
   * Download exported project
   */
  const downloadExport = useCallback((exportId: string) => {
    const downloadUrl = `${API_URL}/api/mobile/download/${exportId}`;
    window.open(downloadUrl, '_blank');
  }, []);

  /**
   * Convert a single component
   */
  const convertComponent = useCallback(async (
    content: string,
    filename: string
  ): Promise<ConvertedComponent> => {
    try {
      const response = await axios.post<ConvertedComponent>(
        `${API_URL}/api/mobile/convert/component`,
        { content, filename }
      );
      return response.data;
    } catch (err: unknown) {
      const errorMsg = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'Conversion failed';
      return {
        success: false,
        converted: '',
        warnings: [errorMsg]
      };
    }
  }, []);

  /**
   * Convert Tailwind classes to StyleSheet
   */
  const convertTailwind = useCallback(async (
    classes: string
  ): Promise<Record<string, unknown>> => {
    try {
      const response = await axios.post<{ styles: Record<string, unknown> }>(
        `${API_URL}/api/mobile/convert/styles`,
        { classes }
      );
      return response.data.styles;
    } catch {
      return {};
    }
  }, []);

  /**
   * Get available frameworks
   */
  const getFrameworks = useCallback(async (): Promise<FrameworkInfo[]> => {
    const response = await axios.get<FrameworkInfo[]>(
      `${API_URL}/api/mobile/frameworks`
    );
    return response.data;
  }, []);

  /**
   * Get export history
   */
  const getHistory = useCallback(async (limit = 20): Promise<ExportHistoryItem[]> => {
    const response = await axios.get<ExportHistoryItem[]>(
      `${API_URL}/api/mobile/history`,
      { params: { limit } }
    );
    return response.data;
  }, []);

  /**
   * Delete an export
   */
  const deleteExport = useCallback(async (exportId: string): Promise<void> => {
    await axios.delete(`${API_URL}/api/mobile/${exportId}`);
  }, []);

  return {
    // State
    isExporting,
    currentExport,
    preview,
    error,

    // Actions
    exportToMobile,
    previewExport,
    downloadExport,
    convertComponent,
    convertTailwind,
    getFrameworks,
    getHistory,
    deleteExport,

    // Utilities
    reset
  };
}

export default useMobileExport;
