/**
 * Project Types
 * Types related to projects and file management in Devora SaaS
 */

/**
 * Supported programming languages for syntax highlighting and file handling
 */
export type Language =
  | 'typescript'
  | 'javascript'
  | 'tsx'
  | 'jsx'
  | 'css'
  | 'scss'
  | 'less'
  | 'html'
  | 'json'
  | 'sql'
  | 'python'
  | 'markdown'
  | 'yaml'
  | 'xml'
  | 'shell'
  | 'dockerfile'
  | 'graphql'
  | 'rust'
  | 'go'
  | 'java'
  | 'php'
  | 'ruby'
  | 'swift'
  | 'kotlin'
  | 'plaintext';

/**
 * File extension to language mapping
 */
export const EXTENSION_TO_LANGUAGE: Record<string, Language> = {
  '.ts': 'typescript',
  '.tsx': 'tsx',
  '.js': 'javascript',
  '.jsx': 'jsx',
  '.css': 'css',
  '.scss': 'scss',
  '.less': 'less',
  '.html': 'html',
  '.htm': 'html',
  '.json': 'json',
  '.sql': 'sql',
  '.py': 'python',
  '.md': 'markdown',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.xml': 'xml',
  '.sh': 'shell',
  '.bash': 'shell',
  '.dockerfile': 'dockerfile',
  '.graphql': 'graphql',
  '.gql': 'graphql',
  '.rs': 'rust',
  '.go': 'go',
  '.java': 'java',
  '.php': 'php',
  '.rb': 'ruby',
  '.swift': 'swift',
  '.kt': 'kotlin',
  '.txt': 'plaintext',
};

/**
 * Represents a single file within a project
 */
export interface ProjectFile {
  /** File name with extension (e.g., "index.tsx") */
  name: string;
  /** Full file path relative to project root (e.g., "src/components/Button.tsx") */
  path?: string;
  /** File content as string */
  content: string;
  /** Programming language for syntax highlighting */
  language: Language;
  /** File size in bytes (computed from content if not provided) */
  size?: number;
  /** Last modified timestamp */
  lastModified?: string;
  /** Whether the file has unsaved changes */
  isDirty?: boolean;
}

/**
 * Project status in the system
 */
export type ProjectStatus = 'draft' | 'active' | 'archived' | 'deleted';

/**
 * Project visibility settings
 */
export type ProjectVisibility = 'private' | 'public' | 'shared';

/**
 * Full project entity as stored in the database
 */
export interface Project {
  /** Unique project identifier (UUID) */
  id: string;
  /** Project name */
  name: string;
  /** Project description */
  description: string;
  /** Array of files in the project */
  files: ProjectFile[];
  /** Owner user ID */
  user_id: string;
  /** Project status */
  status?: ProjectStatus;
  /** Visibility setting */
  visibility?: ProjectVisibility;
  /** Tags for categorization */
  tags?: string[];
  /** Project thumbnail URL */
  thumbnail_url?: string;
  /** Creation timestamp (ISO 8601) */
  created_at: string;
  /** Last update timestamp (ISO 8601) */
  updated_at: string;
  /** Last accessed timestamp */
  last_accessed_at?: string;
}

/**
 * Data required to create a new project
 */
export interface ProjectCreate {
  /** Project name (required) */
  name: string;
  /** Project description (optional) */
  description?: string;
  /** Initial files (optional) */
  files?: ProjectFile[];
  /** Initial visibility (defaults to private) */
  visibility?: ProjectVisibility;
  /** Initial tags */
  tags?: string[];
}

/**
 * Data for updating an existing project
 */
export interface ProjectUpdate {
  /** Updated name */
  name?: string;
  /** Updated description */
  description?: string;
  /** Updated files */
  files?: ProjectFile[];
  /** Updated status */
  status?: ProjectStatus;
  /** Updated visibility */
  visibility?: ProjectVisibility;
  /** Updated tags */
  tags?: string[];
}

/**
 * Project summary for list views (lightweight version)
 */
export interface ProjectSummary {
  id: string;
  name: string;
  description: string;
  file_count: number;
  status: ProjectStatus;
  visibility: ProjectVisibility;
  tags: string[];
  thumbnail_url?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Project filter options for queries
 */
export interface ProjectFilter {
  /** Filter by status */
  status?: ProjectStatus;
  /** Filter by visibility */
  visibility?: ProjectVisibility;
  /** Filter by tags (any match) */
  tags?: string[];
  /** Search in name and description */
  search?: string;
  /** Sort field */
  sort_by?: 'name' | 'created_at' | 'updated_at' | 'last_accessed_at';
  /** Sort direction */
  sort_order?: 'asc' | 'desc';
}

/**
 * Project statistics
 */
export interface ProjectStats {
  /** Total file count */
  total_files: number;
  /** Total size in bytes */
  total_size: number;
  /** File count by language */
  files_by_language: Record<Language, number>;
  /** Lines of code count */
  lines_of_code: number;
}

/**
 * Helper function to detect language from file name
 */
export function detectLanguage(fileName: string): Language {
  const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
  return EXTENSION_TO_LANGUAGE[ext] || 'plaintext';
}

/**
 * Helper function to create a new ProjectFile
 */
export function createProjectFile(
  name: string,
  content: string,
  language?: Language
): ProjectFile {
  return {
    name,
    content,
    language: language || detectLanguage(name),
    size: new Blob([content]).size,
    lastModified: new Date().toISOString(),
    isDirty: false,
  };
}
