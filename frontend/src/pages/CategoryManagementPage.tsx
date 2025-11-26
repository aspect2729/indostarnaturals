import React, { useState, useEffect } from 'react'
import { Category } from '../types/product'
import productService from '../services/productService'
import ownerProductService from '../services/ownerProductService'
import CategoryForm from '../components/CategoryForm'

const CategoryManagementPage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  const [formLoading, setFormLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await productService.getCategories()
      setCategories(data)
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load categories')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCategory = async (data: {
    name: string
    slug: string
    parent_id?: number | null
    display_order: number
  }) => {
    try {
      setFormLoading(true)
      setError(null)
      await ownerProductService.createCategory(data)
      setShowCreateForm(false)
      await loadCategories()
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to create category')
      throw err
    } finally {
      setFormLoading(false)
    }
  }

  const handleUpdateCategory = async (data: {
    name?: string
    slug?: string
    parent_id?: number | null
    display_order?: number
  }) => {
    if (!editingCategory) return

    try {
      setFormLoading(true)
      setError(null)
      await ownerProductService.updateCategory(editingCategory.id, data)
      setEditingCategory(null)
      await loadCategories()
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to update category')
      throw err
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteCategory = async (categoryId: number) => {
    if (!confirm('Are you sure you want to delete this category? Products in this category will need to be reassigned.')) {
      return
    }

    try {
      setError(null)
      await ownerProductService.deleteCategory(categoryId)
      await loadCategories()
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to delete category')
    }
  }

  // Organize categories into hierarchy
  const getCategoryHierarchy = () => {
    const topLevel = categories.filter((cat) => !cat.parent_id)
    const children = categories.filter((cat) => cat.parent_id)

    return topLevel.map((parent) => ({
      ...parent,
      children: children.filter((child) => child.parent_id === parent.id),
    }))
  }

  if (showCreateForm) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Create New Category</h1>
        </div>
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
        <div className="bg-white rounded-lg shadow p-6">
          <CategoryForm
            categories={categories}
            onSubmit={handleCreateCategory}
            onCancel={() => {
              setShowCreateForm(false)
              setError(null)
            }}
            loading={formLoading}
          />
        </div>
      </div>
    )
  }

  if (editingCategory) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Edit Category</h1>
        </div>
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
        <div className="bg-white rounded-lg shadow p-6">
          <CategoryForm
            category={editingCategory}
            categories={categories}
            onSubmit={handleUpdateCategory}
            onCancel={() => {
              setEditingCategory(null)
              setError(null)
            }}
            loading={formLoading}
          />
        </div>
      </div>
    )
  }

  const hierarchy = getCategoryHierarchy()

  return (
    <div className="max-w-5xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Category Management</h1>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors font-medium"
        >
          + Create Category
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Categories list */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        </div>
      ) : categories.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500">No categories found</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="mt-4 text-green-600 hover:text-green-700 font-medium"
          >
            Create your first category
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Slug
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Display Order
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {hierarchy.map((parent) => (
                <React.Fragment key={parent.id}>
                  {/* Parent category */}
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{parent.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {parent.slug}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {parent.display_order}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => setEditingCategory(parent)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteCategory(parent.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>

                  {/* Child categories */}
                  {parent.children && parent.children.length > 0 && (
                    <>
                      {parent.children.map((child) => (
                        <tr key={child.id} className="hover:bg-gray-50 bg-gray-25">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900 pl-8">
                              <span className="text-gray-400 mr-2">└─</span>
                              {child.name}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {child.slug}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {child.display_order}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() => setEditingCategory(child)}
                              className="text-blue-600 hover:text-blue-900 mr-4"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteCategory(child.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default CategoryManagementPage
