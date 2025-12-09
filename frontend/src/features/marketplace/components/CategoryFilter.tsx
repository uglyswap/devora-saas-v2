/**
 * CategoryFilter Component - Filtres par catégorie
 * Affiche les boutons de filtrage par catégorie + "All"
 */
import React from 'react';
import { TemplateCategory, CATEGORY_LABELS } from '../types/marketplace.types';

interface CategoryFilterProps {
  selectedCategory?: TemplateCategory | null;
  onCategoryChange: (category: TemplateCategory | null) => void;
}

export const CategoryFilter: React.FC<CategoryFilterProps> = ({
  selectedCategory,
  onCategoryChange,
}) => {
  const categories = Object.values(TemplateCategory);

  return (
    <div className="flex flex-wrap gap-2">
      {/* All button */}
      <button
        onClick={() => onCategoryChange(null)}
        className={`px-4 py-2 rounded-lg font-medium transition-colors ${
          !selectedCategory
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        All
      </button>

      {/* Category buttons */}
      {categories.map((category) => (
        <button
          key={category}
          onClick={() => onCategoryChange(category)}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedCategory === category
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {CATEGORY_LABELS[category]}
        </button>
      ))}
    </div>
  );
};
