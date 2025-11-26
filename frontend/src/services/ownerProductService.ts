import api from './api'
import { Product, Category } from '../types/product'

export interface ProductCreateData {
  title: string
  description: string
  category_id: number
  sku: string
  unit_size: string
  consumer_price: number
  distributor_price: number
  stock_quantity: number
  is_subscription_available: boolean
}

export interface ProductUpdateData {
  title?: string
  description?: string
  category_id?: number
  sku?: string
  unit_size?: string
  consumer_price?: number
  distributor_price?: number
  stock_quantity?: number
  is_subscription_available?: boolean
  is_active?: boolean
}

export interface StockUpdateData {
  quantity_delta: number
}

export interface ImageUploadProgress {
  loaded: number
  total: number
  percentage: number
}

const ownerProductService = {
  // Create a new product
  createProduct: async (productData: ProductCreateData): Promise<Product> => {
    const response = await api.post('/api/v1/owner/products', productData)
    return response.data
  },

  // Update an existing product
  updateProduct: async (productId: number, productData: ProductUpdateData): Promise<Product> => {
    const response = await api.put(`/api/v1/owner/products/${productId}`, productData)
    return response.data
  },

  // Delete a product (soft delete)
  deleteProduct: async (productId: number): Promise<void> => {
    await api.delete(`/api/v1/owner/products/${productId}`)
  },

  // Upload product image with progress tracking
  uploadImage: async (
    productId: number,
    file: File,
    altText: string,
    displayOrder: number,
    onProgress?: (progress: ImageUploadProgress) => void
  ): Promise<{ id: number; url: string; alt_text: string; display_order: number }> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('alt_text', altText)
    formData.append('display_order', displayOrder.toString())

    const response = await api.post(`/api/v1/owner/products/${productId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          })
        }
      },
    })

    return response.data
  },

  // Delete a product image
  deleteImage: async (productId: number, imageId: number): Promise<void> => {
    await api.delete(`/api/v1/owner/products/${productId}/images/${imageId}`)
  },

  // Update stock quantity
  updateStock: async (productId: number, quantityDelta: number): Promise<Product> => {
    const response = await api.put(`/api/v1/owner/products/${productId}/stock`, {
      quantity_delta: quantityDelta,
    })
    return response.data
  },

  // Create a new category
  createCategory: async (categoryData: {
    name: string
    slug: string
    parent_id?: number | null
    display_order: number
  }): Promise<Category> => {
    const response = await api.post('/api/v1/owner/categories', categoryData)
    return response.data
  },

  // Update a category
  updateCategory: async (
    categoryId: number,
    categoryData: {
      name?: string
      slug?: string
      parent_id?: number | null
      display_order?: number
    }
  ): Promise<Category> => {
    const response = await api.put(`/api/v1/owner/categories/${categoryId}`, categoryData)
    return response.data
  },

  // Delete a category
  deleteCategory: async (categoryId: number): Promise<void> => {
    await api.delete(`/api/v1/owner/categories/${categoryId}`)
  },
}

export default ownerProductService
