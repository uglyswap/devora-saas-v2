/**
 * Deployment Types
 * @version 1.0.0
 */

export type DeployProvider = 'vercel' | 'netlify' | 'railway';

export type DeploymentStatus =
  | 'pending'
  | 'queued'
  | 'building'
  | 'deploying'
  | 'ready'
  | 'error'
  | 'canceled';

export interface DeploymentFile {
  name: string;
  content: string;
  language?: string;
}

export interface DeploymentRequest {
  projectId?: string;
  projectName: string;
  files: DeploymentFile[];
  provider: DeployProvider;
  envVars?: Record<string, string>;
  framework?: string;
}

export interface DeploymentResponse {
  id: string;
  success: boolean;
  status: DeploymentStatus;
  url?: string;
  error?: string;
  progress: number;
  provider: DeployProvider;
  deploymentId?: string;
  createdAt?: string;
  logs?: string[];
}

export interface DeploymentHistoryItem {
  id: string;
  projectName: string;
  provider: DeployProvider;
  status: DeploymentStatus;
  url?: string;
  createdAt: string;
}

export interface ProviderInfo {
  id: DeployProvider;
  name: string;
  available: boolean;
  requiresToken: boolean;
  features: string[];
}

export interface DeployProgressEvent {
  event: 'start' | 'progress' | 'log' | 'complete' | 'error';
  data: {
    id: string;
    status?: string;
    progress?: number;
    message?: string;
    url?: string;
    error?: string;
    logs?: string[];
  };
}

// Provider config
export const PROVIDER_CONFIG: Record<DeployProvider, {
  name: string;
  icon: string;
  color: string;
  bgColor: string;
  description: string;
}> = {
  vercel: {
    name: 'Vercel',
    icon: '▲',
    color: '#000000',
    bgColor: '#ffffff',
    description: 'Deploy frontend & full-stack apps with serverless functions'
  },
  netlify: {
    name: 'Netlify',
    icon: '◈',
    color: '#00C7B7',
    bgColor: '#0E1E25',
    description: 'Build, deploy, and manage modern web projects'
  },
  railway: {
    name: 'Railway',
    icon: '🚂',
    color: '#0B0D0E',
    bgColor: '#A855F7',
    description: 'Infrastructure for the modern stack'
  }
};

export function getProviderConfig(provider: DeployProvider) {
  return PROVIDER_CONFIG[provider] || PROVIDER_CONFIG.vercel;
}

export function getStatusColor(status: DeploymentStatus): string {
  const colors: Record<DeploymentStatus, string> = {
    pending: '#6b7280',    // gray
    queued: '#f59e0b',     // amber
    building: '#3b82f6',   // blue
    deploying: '#8b5cf6',  // purple
    ready: '#22c55e',      // green
    error: '#ef4444',      // red
    canceled: '#6b7280'    // gray
  };
  return colors[status] || '#6b7280';
}

export function getStatusLabel(status: DeploymentStatus): string {
  const labels: Record<DeploymentStatus, string> = {
    pending: 'Pending',
    queued: 'Queued',
    building: 'Building',
    deploying: 'Deploying',
    ready: 'Ready',
    error: 'Error',
    canceled: 'Canceled'
  };
  return labels[status] || status;
}
