/**
 * Marketplace Types - Devora Templates Marketplace
 * Types TypeScript pour les templates, reviews et downloads
 */

// ============================================
// ENUMS
// ============================================

export enum TemplateStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ARCHIVED = 'archived',
}

export enum TemplateCategory {
  SAAS = 'saas',
  ECOMMERCE = 'ecommerce',
  DASHBOARD = 'dashboard',
  LANDING_PAGE = 'landing_page',
  BLOG_CMS = 'blog_cms',
  PORTFOLIO = 'portfolio',
  ADMIN = 'admin',
}

export enum SortBy {
  RELEVANCE = 'relevance',
  DOWNLOADS = 'downloads',
  RATING = 'rating',
  RECENT = 'recent',
}

// ============================================
// INTERFACES
// ============================================

export interface TemplateStack {
  frontend?: string;
  backend?: string;
  database?: string;
  auth?: string;
  other?: Record<string, string>;
}

export interface MarketplaceTemplate {
  id: string;
  name: string;
  slug: string;
  description: string;
  author_id: string;
  category: TemplateCategory;
  tags: string[];
  stack: TemplateStack;
  features: string[];
  downloads_count: number;
  rating_average: number;
  rating_count: number;
  preview_images: string[];
  demo_url?: string;
  files_url: string;
  status: TemplateStatus;
  is_official: boolean;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
  published_at?: string;

  // Données enrichies
  author_username?: string;
  author_email?: string;
}

export interface TemplateCreateRequest {
  name: string;
  slug: string;
  description: string;
  category: TemplateCategory;
  tags?: string[];
  stack: TemplateStack;
  features?: string[];
  preview_images?: string[];
  demo_url?: string;
  files_url: string;
}

export interface TemplateUpdateRequest {
  name?: string;
  description?: string;
  category?: TemplateCategory;
  tags?: string[];
  stack?: TemplateStack;
  features?: string[];
  preview_images?: string[];
  demo_url?: string;
  status?: TemplateStatus;
}

export interface Review {
  id: string;
  template_id: string;
  user_id: string;
  rating: number;
  title?: string;
  content?: string;
  created_at: string;

  // Données enrichies
  user_username?: string;
  user_email?: string;
}

export interface ReviewCreateRequest {
  rating: number;
  title?: string;
  content?: string;
}

export interface ReviewUpdateRequest {
  rating?: number;
  title?: string;
  content?: string;
}

export interface TemplateStats {
  total_downloads: number;
  total_reviews: number;
  average_rating: number;
  rating_distribution: Record<string, number>;
}

export interface TemplateListResponse {
  templates: MarketplaceTemplate[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TemplateFilters {
  search?: string;
  category?: TemplateCategory;
  tags?: string[];
  sort_by?: SortBy;
  page?: number;
  page_size?: number;
  featured_only?: boolean;
  official_only?: boolean;
}

export interface DownloadResponse {
  download_url: string;
  template_id: string;
}

// ============================================
// CATEGORY LABELS
// ============================================

export const CATEGORY_LABELS: Record<TemplateCategory, string> = {
  [TemplateCategory.SAAS]: 'SaaS',
  [TemplateCategory.ECOMMERCE]: 'E-commerce',
  [TemplateCategory.DASHBOARD]: 'Dashboard',
  [TemplateCategory.LANDING_PAGE]: 'Landing Page',
  [TemplateCategory.BLOG_CMS]: 'Blog/CMS',
  [TemplateCategory.PORTFOLIO]: 'Portfolio',
  [TemplateCategory.ADMIN]: 'Admin',
};

export const STATUS_LABELS: Record<TemplateStatus, string> = {
  [TemplateStatus.DRAFT]: 'Draft',
  [TemplateStatus.PENDING]: 'Pending Review',
  [TemplateStatus.APPROVED]: 'Approved',
  [TemplateStatus.REJECTED]: 'Rejected',
  [TemplateStatus.ARCHIVED]: 'Archived',
};

// ============================================
// HELPERS
// ============================================

export const getCategoryColor = (category: TemplateCategory): string => {
  const colors: Record<TemplateCategory, string> = {
    [TemplateCategory.SAAS]: 'blue',
    [TemplateCategory.ECOMMERCE]: 'green',
    [TemplateCategory.DASHBOARD]: 'purple',
    [TemplateCategory.LANDING_PAGE]: 'orange',
    [TemplateCategory.BLOG_CMS]: 'pink',
    [TemplateCategory.PORTFOLIO]: 'cyan',
    [TemplateCategory.ADMIN]: 'red',
  };
  return colors[category];
};

export const getStatusColor = (status: TemplateStatus): string => {
  const colors: Record<TemplateStatus, string> = {
    [TemplateStatus.DRAFT]: 'gray',
    [TemplateStatus.PENDING]: 'yellow',
    [TemplateStatus.APPROVED]: 'green',
    [TemplateStatus.REJECTED]: 'red',
    [TemplateStatus.ARCHIVED]: 'gray',
  };
  return colors[status];
};

export const formatDownloadCount = (count: number): string => {
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}k`;
  }
  return count.toString();
};

export const formatRating = (rating: number): string => {
  return rating.toFixed(1);
};
