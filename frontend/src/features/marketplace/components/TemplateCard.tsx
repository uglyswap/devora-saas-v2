/**
 * TemplateCard Component - Carte template pour la grille marketplace
 * Affiche preview, titre, description, rating, downloads, tags
 */
import React from 'react';
import { Link } from 'react-router-dom';
import {
  MarketplaceTemplate,
  CATEGORY_LABELS,
  getCategoryColor,
  formatDownloadCount,
  formatRating,
} from '../types/marketplace.types';
import { RatingStars } from './RatingStars';

interface TemplateCardProps {
  template: MarketplaceTemplate;
  onClick?: (template: MarketplaceTemplate) => void;
}

export const TemplateCard: React.FC<TemplateCardProps> = ({
  template,
  onClick,
}) => {
  const categoryColor = getCategoryColor(template.category);
  const previewImage = template.preview_images[0] || '/placeholder-template.png';

  const handleClick = () => {
    if (onClick) {
      onClick(template);
    }
  };

  return (
    <Link
      to={`/marketplace/templates/${template.id}`}
      onClick={handleClick}
      className="group block bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition-all duration-200 overflow-hidden"
    >
      {/* Preview Image */}
      <div className="relative aspect-video bg-gray-100 overflow-hidden">
        <img
          src={previewImage}
          alt={template.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
          loading="lazy"
        />

        {/* Badges */}
        <div className="absolute top-2 left-2 flex gap-2">
          {template.is_official && (
            <span className="px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded">
              Official
            </span>
          )}
          {template.is_featured && (
            <span className="px-2 py-1 bg-purple-600 text-white text-xs font-semibold rounded">
              Featured
            </span>
          )}
        </div>

        {/* Category Badge */}
        <div className="absolute top-2 right-2">
          <span
            className={`px-2 py-1 bg-${categoryColor}-100 text-${categoryColor}-800 text-xs font-medium rounded`}
          >
            {CATEGORY_LABELS[template.category]}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-1">
          {template.name}
        </h3>

        {/* Description */}
        <p className="mt-1 text-sm text-gray-600 line-clamp-2">
          {template.description}
        </p>

        {/* Author */}
        <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
          <svg
            className="w-4 h-4"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
              clipRule="evenodd"
            />
          </svg>
          <span>{template.author_username || 'Anonymous'}</span>
        </div>

        {/* Rating & Downloads */}
        <div className="mt-3 flex items-center justify-between">
          <div className="flex items-center gap-1">
            <RatingStars
              rating={template.rating_average}
              size="sm"
              showCount
              count={template.rating_count}
            />
          </div>

          <div className="flex items-center gap-1 text-sm text-gray-600">
            <svg
              className="w-4 h-4"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
            <span>{formatDownloadCount(template.downloads_count)}</span>
          </div>
        </div>

        {/* Tags */}
        {template.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {template.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded"
              >
                {tag}
              </span>
            ))}
            {template.tags.length > 3 && (
              <span className="px-2 py-0.5 text-gray-500 text-xs">
                +{template.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Stack Icons (si disponible) */}
        {template.stack && (
          <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-2 text-xs text-gray-500">
            {template.stack.frontend && (
              <span title={template.stack.frontend}>⚛️</span>
            )}
            {template.stack.backend && (
              <span title={template.stack.backend}>🔧</span>
            )}
            {template.stack.database && (
              <span title={template.stack.database}>🗄️</span>
            )}
          </div>
        )}
      </div>
    </Link>
  );
};
