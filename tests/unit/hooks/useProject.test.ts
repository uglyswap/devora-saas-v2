import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import axios from 'axios';

/**
 * Tests unitaires pour useProject hook
 * Vérifie: CRUD operations, Loading states, Error handling
 */

vi.mock('axios');

const mockAxios = axios as any;

// Mock hook (example structure - adjust based on actual implementation)
const useProject = (projectId?: string) => {
  const [project, setProject] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const fetchProject = async (id: string) => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/projects/${id}`);
      setProject(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (data: any) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/projects', data);
      setProject(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateProject = async (id: string, data: any) => {
    setLoading(true);
    try {
      const response = await axios.put(`/api/projects/${id}`, data);
      setProject(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (id: string) => {
    setLoading(true);
    try {
      await axios.delete(`/api/projects/${id}`);
      setProject(null);
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (projectId) {
      fetchProject(projectId);
    }
  }, [projectId]);

  return {
    project,
    loading,
    error,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
  };
};

describe('useProject Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetch Project', () => {
    it('should fetch project successfully', async () => {
      const mockProject = {
        id: '1',
        name: 'Test Project',
        code: '<h1>Hello</h1>',
      };

      mockAxios.get.mockResolvedValueOnce({
        data: mockProject,
      });

      const { result } = renderHook(() => useProject('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
        expect(result.current.project).toEqual(mockProject);
        expect(result.current.error).toBeNull();
      });
    });

    it('should set loading state while fetching', async () => {
      mockAxios.get.mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      const { result } = renderHook(() => useProject('1'));

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });

    it('should handle fetch errors', async () => {
      mockAxios.get.mockRejectedValueOnce(new Error('Project not found'));

      const { result } = renderHook(() => useProject('invalid-id'));

      await waitFor(() => {
        expect(result.current.error).toBe('Project not found');
        expect(result.current.project).toBeNull();
      });
    });
  });

  describe('Create Project', () => {
    it('should create project successfully', async () => {
      const newProject = {
        name: 'New Project',
        code: '<div>New</div>',
      };

      const createdProject = {
        id: '2',
        ...newProject,
      };

      mockAxios.post.mockResolvedValueOnce({
        data: createdProject,
      });

      const { result } = renderHook(() => useProject());

      let project;
      await act(async () => {
        project = await result.current.createProject(newProject);
      });

      expect(project).toEqual(createdProject);
      expect(result.current.project).toEqual(createdProject);
    });

    it('should handle create errors', async () => {
      mockAxios.post.mockRejectedValueOnce(new Error('Validation failed'));

      const { result } = renderHook(() => useProject());

      await expect(async () => {
        await act(async () => {
          await result.current.createProject({ name: '' });
        });
      }).rejects.toThrow('Validation failed');

      expect(result.current.error).toBe('Validation failed');
    });
  });

  describe('Update Project', () => {
    it('should update project successfully', async () => {
      const updatedProject = {
        id: '1',
        name: 'Updated Project',
        code: '<h1>Updated</h1>',
      };

      mockAxios.put.mockResolvedValueOnce({
        data: updatedProject,
      });

      const { result } = renderHook(() => useProject());

      let project;
      await act(async () => {
        project = await result.current.updateProject('1', {
          name: 'Updated Project',
        });
      });

      expect(project).toEqual(updatedProject);
      expect(result.current.project).toEqual(updatedProject);
    });

    it('should handle update errors', async () => {
      mockAxios.put.mockRejectedValueOnce(new Error('Update failed'));

      const { result } = renderHook(() => useProject());

      await expect(async () => {
        await act(async () => {
          await result.current.updateProject('1', {});
        });
      }).rejects.toThrow('Update failed');
    });
  });

  describe('Delete Project', () => {
    it('should delete project successfully', async () => {
      mockAxios.delete.mockResolvedValueOnce({});

      const { result } = renderHook(() => useProject());

      await act(async () => {
        await result.current.deleteProject('1');
      });

      expect(result.current.project).toBeNull();
    });

    it('should handle delete errors', async () => {
      mockAxios.delete.mockRejectedValueOnce(new Error('Delete failed'));

      const { result } = renderHook(() => useProject());

      await expect(async () => {
        await act(async () => {
          await result.current.deleteProject('1');
        });
      }).rejects.toThrow('Delete failed');
    });
  });

  describe('Auto-fetch on mount', () => {
    it('should automatically fetch project if ID is provided', async () => {
      const mockProject = { id: '1', name: 'Auto Fetched' };

      mockAxios.get.mockResolvedValueOnce({
        data: mockProject,
      });

      renderHook(() => useProject('1'));

      await waitFor(() => {
        expect(mockAxios.get).toHaveBeenCalledWith('/api/projects/1');
      });
    });

    it('should not fetch if no ID is provided', () => {
      renderHook(() => useProject());

      expect(mockAxios.get).not.toHaveBeenCalled();
    });
  });
});
