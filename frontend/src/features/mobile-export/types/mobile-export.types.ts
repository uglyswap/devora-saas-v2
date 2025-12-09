/**
 * Mobile Export Types
 * @version 1.0.0
 */

export type MobileFramework = 'expo-router' | 'expo' | 'react-native-cli';

export interface SourceFile {
  name: string;
  content: string;
  type?: 'component' | 'page' | 'style' | 'util' | 'unknown';
}

export interface ExportRequest {
  projectId?: string;
  projectName: string;
  files: SourceFile[];
  framework: MobileFramework;
  useTypeScript?: boolean;
  includeNavigation?: boolean;
}

export interface ExportedFile {
  path: string;
  original?: string;
  size: number;
}

export interface ExportStats {
  components_converted: number;
  pages_created: number;
  styles_converted: number;
  total_files: number;
}

export interface ExportResult {
  id: string;
  success: boolean;
  downloadUrl?: string;
  error?: string;
  stats: ExportStats;
  warnings: string[];
  filesCount: number;
  createdAt: string;
}

export interface ExportPreview {
  files: ExportedFile[];
  totalSize: number;
  framework: MobileFramework;
  warnings: string[];
}

export interface FrameworkInfo {
  id: MobileFramework;
  name: string;
  description: string;
  features: string[];
  recommended: boolean;
}

export interface ConvertedComponent {
  success: boolean;
  converted: string;
  warnings: string[];
}

export interface ExportHistoryItem {
  id: string;
  projectName: string;
  filesCount: number;
  createdAt: string;
}

// Framework configurations
export const FRAMEWORK_CONFIG: Record<MobileFramework, {
  name: string;
  icon: string;
  description: string;
  recommended: boolean;
}> = {
  'expo-router': {
    name: 'Expo Router',
    icon: '📱',
    description: 'File-based routing like Next.js',
    recommended: true
  },
  'expo': {
    name: 'Expo',
    icon: '⚡',
    description: 'Standard Expo with React Navigation',
    recommended: false
  },
  'react-native-cli': {
    name: 'React Native CLI',
    icon: '⚛️',
    description: 'Bare React Native without Expo',
    recommended: false
  }
};

export function getFrameworkConfig(framework: MobileFramework) {
  return FRAMEWORK_CONFIG[framework] || FRAMEWORK_CONFIG['expo-router'];
}
