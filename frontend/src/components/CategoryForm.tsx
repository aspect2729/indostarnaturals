import React, { useState } from 'react'
import { Category } from '../types/product'

interface CategoryFormProps {
  category?: Category | null
  categories: Category[]
  onSubmit: (data: {
    name: string
    slug: string
    parent_id?: number | null
    display_order: number
  }) => Promise<void>
  onCancel: () => void
  loading?: boolean
}

const CategoryForm: React.FC<CategoryFormProps> = ({
  category,
  categories,
  onSubmit,
  onCancel,
  loading = false,
}) => {
  const [formData, setFormData] = useState({
    name: category?.name || '',
    slug: category?.slug || '',
    parent_id: category?.parent_id || null,
    display_order: category?.display_order?.toString() || '0',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target

    setFormData((prev) => ({
      ...prev,
      [name]: name === 'parent_id' ? (value ? parseInt(value) : null) : value,
    }))

    // Auto-generate slug from name
    if (name === 'name' && !category) {
      const slug = value
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '')
      setFormData((prev) => ({ ...prev, slug }))
    }

    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Category name is required'
    }

    if (!formData.slug.trim()) {
      newErrors.slug = 'Slug is required'
    } else if (!/^[a-z0-9-]+$/.test(formData.slug)) {
      newErrors.slug = 'Slug can only contain lowercase letters, numbers, and hyphens'
    }

    const displayOrder = parseInt(formData.display_order, 10)
    if (isNaN(displayOrder) || displayOrder < 0) {
      newErrors.display_order = 'Display order must be a non-negative integer'
    }

    // Check if parent is not self (for edit mode)
    if (category && formData.parent_id === category.id) {
      newErrors.parent_id = 'Category cannot be its own parent'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    await onSubmit({
      name: formData.name.trim(),
      slug: formData.slug.trim(),
      parent_id: formData.parent_id,
      display_order: parseInt(formData.display_order, 10),
    })
  }

  // Filter out current category from parent options (for edit mode)
  const availableParents = categories.filter((cat) => cat.id !== category?.id)

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Name */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Category Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
            errors.name ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="e.g., Jaggery Products"
        />
        {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
      </div>

      {/* Slug */}
      <div>
        <label htmlFor="slug" className="block text-sm font-medium text-gray-700 mb-1">
          Slug <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="slug"
          name="slug"
          value={formData.slug}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
            errors.slug ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="e.g., jaggery-products"
        />
        {errors.slug && <p className="mt-1 text-sm text-red-600">{errors.slug}</p>}
        <p className="mt-1 text-xs text-gray-500">
          URL-friendly identifier (lowercase, hyphens only)
        </p>
      </div>

      {/* Parent Category */}
      <div>
        <label htmlFor="parent_id" className="block text-sm font-medium text-gray-700 mb-1">
          Parent Category
        </label>
        <select
          id="parent_id"
          name="parent_id"
          value={formData.parent_id || ''}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
            errors.parent_id ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">None (Top Level)</option>
          {availableParents.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
        {errors.parent_id && <p className="mt-1 text-sm text-red-600">{errors.parent_id}</p>}
        <p className="mt-1 text-xs text-gray-500">
          Optional: Select a parent category to create a subcategory
        </p>
      </div>

      {/* Display Order */}
      <div>
        <label htmlFor="display_order" className="block text-sm font-medium text-gray-700 mb-1">
          Display Order <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          id="display_order"
          name="display_order"
          value={formData.display_order}
          onChange={handleChange}
          min="0"
          step="1"
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
            errors.display_order ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="0"
        />
        {errors.display_order && (
          <p className="mt-1 text-sm text-red-600">{errors.display_order}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          Lower numbers appear first in category lists
        </p>
      </div>

      {/* Action buttons */}
      <div className="flex space-x-3 pt-4 border-t">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {loading ? 'Saving...' : category ? 'Update Category' : 'Create Category'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="flex-1 bg-gray-200 text-gray-700 px-6 py-3 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}

export default CategoryForm
