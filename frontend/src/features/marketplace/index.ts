/**
 * Marketplace Feature - Main Export
 * Export centralisé pour le module marketplace
 */

// Components
export { TemplateCard } from './components/TemplateCard';
export { TemplateGrid } from './components/TemplateGrid';
export { CategoryFilter } from './components/CategoryFilter';
export { SearchBar } from './components/SearchBar';
export { RatingStars } from './components/RatingStars';
export { ReviewList } from './components/ReviewList';
export { SubmitTemplateForm } from './components/SubmitTemplateForm';

// Hooks
export { useMarketplace } from './hooks/useMarketplace';
export { useTemplateDownload } from './hooks/useTemplateDownload';

// Types
export type {
  MarketplaceTemplate,
  TemplateCreateRequest,
  TemplateUpdateRequest,
  Review,
  ReviewCreateRequest,
  ReviewUpdateRequest,
  TemplateStats,
  TemplateListResponse,
  TemplateFilters,
  DownloadResponse,
  TemplateStack,
} from './types/marketplace.types';

export {
  TemplateStatus,
  TemplateCategory,
  SortBy,
  CATEGORY_LABELS,
  STATUS_LABELS,
  getCategoryColor,
  getStatusColor,
  formatDownloadCount,
  formatRating,
} from './types/marketplace.types';
