/**
 * ReviewList Component - Liste des avis utilisateurs
 * Affiche les reviews avec possibilité d'éditer/supprimer ses propres reviews
 */
import React, { useState } from 'react';
import { Review } from '../types/marketplace.types';
import { RatingStars } from './RatingStars';

interface ReviewListProps {
  reviews: Review[];
  currentUserId?: string;
  onEdit?: (reviewId: string, rating: number, title: string, content: string) => void;
  onDelete?: (reviewId: string) => void;
}

export const ReviewList: React.FC<ReviewListProps> = ({
  reviews,
  currentUserId,
  onEdit,
  onDelete,
}) => {
  const [editingReviewId, setEditingReviewId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({
    rating: 5,
    title: '',
    content: '',
  });

  const handleEditClick = (review: Review) => {
    setEditingReviewId(review.id);
    setEditForm({
      rating: review.rating,
      title: review.title || '',
      content: review.content || '',
    });
  };

  const handleSaveEdit = (reviewId: string) => {
    if (onEdit) {
      onEdit(reviewId, editForm.rating, editForm.title, editForm.content);
    }
    setEditingReviewId(null);
  };

  const handleCancelEdit = () => {
    setEditingReviewId(null);
  };

  const handleDelete = (reviewId: string) => {
    if (window.confirm('Are you sure you want to delete this review?')) {
      onDelete?.(reviewId);
    }
  };

  if (reviews.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">No reviews yet. Be the first to review!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {reviews.map((review) => {
        const isEditing = editingReviewId === review.id;
        const isOwner = currentUserId === review.user_id;

        return (
          <div
            key={review.id}
            className="border-b border-gray-200 pb-6 last:border-b-0"
          >
            {isEditing ? (
              // Edit Mode
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rating
                  </label>
                  <RatingStars
                    rating={editForm.rating}
                    interactive
                    onChange={(rating) => setEditForm({ ...editForm, rating })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) =>
                      setEditForm({ ...editForm, title: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Summary of your review"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Review
                  </label>
                  <textarea
                    value={editForm.content}
                    onChange={(e) =>
                      setEditForm({ ...editForm, content: e.target.value })
                    }
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Share your experience with this template..."
                  />
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleSaveEdit(review.id)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Save
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              // Display Mode
              <>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* User info */}
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                        <span className="text-gray-600 font-semibold">
                          {(review.user_username || 'A')[0].toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {review.user_username || 'Anonymous'}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(review.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    {/* Rating */}
                    <div className="mb-2">
                      <RatingStars rating={review.rating} size="sm" />
                    </div>

                    {/* Title */}
                    {review.title && (
                      <h4 className="font-semibold text-gray-900 mb-1">
                        {review.title}
                      </h4>
                    )}

                    {/* Content */}
                    {review.content && (
                      <p className="text-gray-700 whitespace-pre-wrap">
                        {review.content}
                      </p>
                    )}
                  </div>

                  {/* Actions (only for owner) */}
                  {isOwner && (
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => handleEditClick(review)}
                        className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(review.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        );
      })}
    </div>
  );
};
