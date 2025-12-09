/**
 * SubmitTemplateForm Component - Formulaire de soumission de template
 * Permet aux users de soumettre leurs propres templates
 */
import React, { useState } from 'react';
import {
  TemplateCategory,
  TemplateCreateRequest,
  CATEGORY_LABELS,
} from '../types/marketplace.types';

interface SubmitTemplateFormProps {
  onSubmit: (data: TemplateCreateRequest) => Promise<void>;
  loading?: boolean;
}

export const SubmitTemplateForm: React.FC<SubmitTemplateFormProps> = ({
  onSubmit,
  loading = false,
}) => {
  const [formData, setFormData] = useState<TemplateCreateRequest>({
    name: '',
    slug: '',
    description: '',
    category: TemplateCategory.SAAS,
    tags: [],
    stack: {},
    features: [],
    preview_images: [],
    demo_url: '',
    files_url: '',
  });

  const [tagInput, setTagInput] = useState('');
  const [featureInput, setFeatureInput] = useState('');
  const [imageInput, setImageInput] = useState('');

  const handleInputChange = (
    field: keyof TemplateCreateRequest,
    value: any
  ) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleAddTag = () => {
    if (tagInput.trim() && formData.tags!.length < 10) {
      setFormData({
        ...formData,
        tags: [...(formData.tags || []), tagInput.trim()],
      });
      setTagInput('');
    }
  };

  const handleRemoveTag = (index: number) => {
    setFormData({
      ...formData,
      tags: formData.tags!.filter((_, i) => i !== index),
    });
  };

  const handleAddFeature = () => {
    if (featureInput.trim() && formData.features!.length < 20) {
      setFormData({
        ...formData,
        features: [...(formData.features || []), featureInput.trim()],
      });
      setFeatureInput('');
    }
  };

  const handleRemoveFeature = (index: number) => {
    setFormData({
      ...formData,
      features: formData.features!.filter((_, i) => i !== index),
    });
  };

  const handleAddImage = () => {
    if (imageInput.trim() && formData.preview_images!.length < 5) {
      setFormData({
        ...formData,
        preview_images: [...(formData.preview_images || []), imageInput.trim()],
      });
      setImageInput('');
    }
  };

  const handleRemoveImage = (index: number) => {
    setFormData({
      ...formData,
      preview_images: formData.preview_images!.filter((_, i) => i !== index),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  // Auto-generate slug from name
  const handleNameChange = (name: string) => {
    handleInputChange('name', name);
    if (!formData.slug) {
      const slug = name
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-');
      handleInputChange('slug', slug);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Template Name *
        </label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => handleNameChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="My Awesome Template"
        />
      </div>

      {/* Slug */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Slug * (URL-friendly)
        </label>
        <input
          type="text"
          required
          value={formData.slug}
          onChange={(e) => handleInputChange('slug', e.target.value)}
          pattern="^[a-z0-9-]+$"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="my-awesome-template"
        />
        <p className="mt-1 text-xs text-gray-500">
          Only lowercase letters, numbers and hyphens
        </p>
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Description * (min 20 characters)
        </label>
        <textarea
          required
          value={formData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          rows={4}
          minLength={20}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="Describe your template, what it does, and who it's for..."
        />
      </div>

      {/* Category */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Category *
        </label>
        <select
          required
          value={formData.category}
          onChange={(e) =>
            handleInputChange('category', e.target.value as TemplateCategory)
          }
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {/* Tags */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tags (max 10)
        </label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="react, typescript, tailwind..."
          />
          <button
            type="button"
            onClick={handleAddTag}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Add
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.tags?.map((tag, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm flex items-center gap-1"
            >
              {tag}
              <button
                type="button"
                onClick={() => handleRemoveTag(i)}
                className="text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      {/* Stack */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Frontend Stack
          </label>
          <input
            type="text"
            value={formData.stack.frontend || ''}
            onChange={(e) =>
              handleInputChange('stack', { ...formData.stack, frontend: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="React, Vue, Svelte..."
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Backend Stack
          </label>
          <input
            type="text"
            value={formData.stack.backend || ''}
            onChange={(e) =>
              handleInputChange('stack', { ...formData.stack, backend: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="FastAPI, Express, Django..."
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Database
          </label>
          <input
            type="text"
            value={formData.stack.database || ''}
            onChange={(e) =>
              handleInputChange('stack', { ...formData.stack, database: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="PostgreSQL, MongoDB..."
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Auth
          </label>
          <input
            type="text"
            value={formData.stack.auth || ''}
            onChange={(e) =>
              handleInputChange('stack', { ...formData.stack, auth: e.target.value })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Supabase, Auth0..."
          />
        </div>
      </div>

      {/* Features */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Features (max 20)
        </label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={featureInput}
            onChange={(e) => setFeatureInput(e.target.value)}
            onKeyPress={(e) =>
              e.key === 'Enter' && (e.preventDefault(), handleAddFeature())
            }
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="User authentication, Dashboard..."
          />
          <button
            type="button"
            onClick={handleAddFeature}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Add
          </button>
        </div>
        <ul className="space-y-1">
          {formData.features?.map((feature, i) => (
            <li key={i} className="flex items-center justify-between py-1 px-2 bg-gray-50 rounded">
              <span className="text-sm">{feature}</span>
              <button
                type="button"
                onClick={() => handleRemoveFeature(i)}
                className="text-red-600 hover:text-red-800"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Preview Images */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Preview Images (max 5 URLs)
        </label>
        <div className="flex gap-2 mb-2">
          <input
            type="url"
            value={imageInput}
            onChange={(e) => setImageInput(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="https://example.com/image.png"
          />
          <button
            type="button"
            onClick={handleAddImage}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Add
          </button>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {formData.preview_images?.map((url, i) => (
            <div key={i} className="relative aspect-video bg-gray-100 rounded overflow-hidden">
              <img src={url} alt={`Preview ${i + 1}`} className="w-full h-full object-cover" />
              <button
                type="button"
                onClick={() => handleRemoveImage(i)}
                className="absolute top-1 right-1 w-6 h-6 bg-red-600 text-white rounded-full hover:bg-red-700"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Demo URL */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Demo URL (optional)
        </label>
        <input
          type="url"
          value={formData.demo_url}
          onChange={(e) => handleInputChange('demo_url', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="https://demo.example.com"
        />
      </div>

      {/* Files URL */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Template Files URL * (Supabase Storage)
        </label>
        <input
          type="url"
          required
          value={formData.files_url}
          onChange={(e) => handleInputChange('files_url', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          placeholder="https://storage.supabase.co/.../template.zip"
        />
        <p className="mt-1 text-xs text-gray-500">
          Upload your template ZIP to Supabase Storage and paste the URL here
        </p>
      </div>

      {/* Submit */}
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {loading ? 'Submitting...' : 'Submit Template'}
        </button>
      </div>
    </form>
  );
};
