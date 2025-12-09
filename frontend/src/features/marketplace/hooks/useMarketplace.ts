/**
 * useMarketplace Hook - API client pour la marketplace
 * Gère les appels API pour templates, reviews et downloads
 */
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  MarketplaceTemplate,
  TemplateListResponse,
  TemplateFilters,
  TemplateCreateRequest,
  TemplateUpdateRequest,
  Review,
  ReviewCreateRequest,
  ReviewUpdateRequest,
  TemplateStats,
  DownloadResponse,
  SortBy,
} from '../types/marketplace.types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// ============================================
// HOOKS
// ============================================

/**
 * Hook principal pour la marketplace
 * Gère la liste de templates avec filtres et pagination
 */
export const useMarketplace = (initialFilters?: TemplateFilters) => {
  const [templates, setTemplates] = useState<MarketplaceTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 0,
  });
  const [filters, setFilters] = useState<TemplateFilters>(initialFilters || {
    sort_by: SortBy.RECENT,
    page: 1,
    page_size: 20,
  });

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();

      if (filters.search) params.append('search', filters.search);
      if (filters.category) params.append('category', filters.category);
      if (filters.tags && filters.tags.length > 0) {
        params.append('tags', filters.tags.join(','));
      }
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.page_size) params.append('page_size', filters.page_size.toString());
      if (filters.featured_only) params.append('featured_only', 'true');
      if (filters.official_only) params.append('official_only', 'true');

      const response = await axios.get<TemplateListResponse>(
        `${API_BASE_URL}/api/marketplace/templates?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      setTemplates(response.data.templates);
      setPagination({
        total: response.data.total,
        page: response.data.page,
        page_size: response.data.page_size,
        total_pages: response.data.total_pages,
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch templates');
      console.error('Error fetching templates:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  const updateFilters = (newFilters: Partial<TemplateFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const nextPage = () => {
    if (pagination.page < pagination.total_pages) {
      updateFilters({ page: pagination.page + 1 });
    }
  };

  const prevPage = () => {
    if (pagination.page > 1) {
      updateFilters({ page: pagination.page - 1 });
    }
  };

  const goToPage = (page: number) => {
    if (page >= 1 && page <= pagination.total_pages) {
      updateFilters({ page });
    }
  };

  return {
    templates,
    loading,
    error,
    pagination,
    filters,
    updateFilters,
    refresh: fetchTemplates,
    nextPage,
    prevPage,
    goToPage,
  };
};

/**
 * Hook pour récupérer un template par ID
 */
export const useTemplate = (templateId: string | undefined) => {
  const [template, setTemplate] = useState<MarketplaceTemplate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplate = useCallback(async () => {
    if (!templateId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get<MarketplaceTemplate>(
        `${API_BASE_URL}/api/marketplace/templates/${templateId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      setTemplate(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch template');
      console.error('Error fetching template:', err);
    } finally {
      setLoading(false);
    }
  }, [templateId]);

  useEffect(() => {
    fetchTemplate();
  }, [fetchTemplate]);

  return { template, loading, error, refresh: fetchTemplate };
};

/**
 * Hook pour créer/modifier un template
 */
export const useTemplateActions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createTemplate = async (
    data: TemplateCreateRequest
  ): Promise<MarketplaceTemplate | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post<MarketplaceTemplate>(
        `${API_BASE_URL}/api/marketplace/templates`,
        data,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create template');
      console.error('Error creating template:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateTemplate = async (
    templateId: string,
    data: TemplateUpdateRequest
  ): Promise<MarketplaceTemplate | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.patch<MarketplaceTemplate>(
        `${API_BASE_URL}/api/marketplace/templates/${templateId}`,
        data,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update template');
      console.error('Error updating template:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const deleteTemplate = async (templateId: string): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      await axios.delete(`${API_BASE_URL}/api/marketplace/templates/${templateId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      return true;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete template');
      console.error('Error deleting template:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { createTemplate, updateTemplate, deleteTemplate, loading, error };
};

/**
 * Hook pour gérer les reviews
 */
export const useReviews = (templateId: string | undefined) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReviews = useCallback(async () => {
    if (!templateId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get<Review[]>(
        `${API_BASE_URL}/api/marketplace/templates/${templateId}/reviews`
      );

      setReviews(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch reviews');
      console.error('Error fetching reviews:', err);
    } finally {
      setLoading(false);
    }
  }, [templateId]);

  useEffect(() => {
    fetchReviews();
  }, [fetchReviews]);

  const createReview = async (data: ReviewCreateRequest): Promise<Review | null> => {
    if (!templateId) return null;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post<Review>(
        `${API_BASE_URL}/api/marketplace/templates/${templateId}/reviews`,
        data,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      setReviews((prev) => [response.data, ...prev]);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create review');
      console.error('Error creating review:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateReview = async (
    reviewId: string,
    data: ReviewUpdateRequest
  ): Promise<Review | null> => {
    if (!templateId) return null;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.patch<Review>(
        `${API_BASE_URL}/api/marketplace/templates/${templateId}/reviews/${reviewId}`,
        data,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      setReviews((prev) =>
        prev.map((r) => (r.id === reviewId ? response.data : r))
      );
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update review');
      console.error('Error updating review:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const deleteReview = async (reviewId: string): Promise<boolean> => {
    if (!templateId) return false;

    setLoading(true);
    setError(null);

    try {
      await axios.delete(
        `${API_BASE_URL}/api/marketplace/templates/${templateId}/reviews/${reviewId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      setReviews((prev) => prev.filter((r) => r.id !== reviewId));
      return true;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete review');
      console.error('Error deleting review:', err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    reviews,
    loading,
    error,
    refresh: fetchReviews,
    createReview,
    updateReview,
    deleteReview,
  };
};

/**
 * Hook pour les statistiques d'un template
 */
export const useTemplateStats = (templateId: string | undefined) => {
  const [stats, setStats] = useState<TemplateStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    if (!templateId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get<TemplateStats>(
        `${API_BASE_URL}/api/marketplace/templates/${templateId}/stats`
      );

      setStats(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch stats');
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  }, [templateId]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, loading, error, refresh: fetchStats };
};
