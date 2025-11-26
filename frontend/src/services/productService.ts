import api from './api'
import { Product, Category, ProductFilters, PaginatedProducts } from '../types/product'

const productService = {
  // Get paginated list of products with filters
  getProducts: async (filters: ProductFilters = {}): Promise<PaginatedProducts> => {
    const params = new URLSearchParams()
    
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.page_size) params.append('page_size', filters.page_size.toString())
    if (filters.category_id) params.append('category_id', filters.category_id.toString())
    if (filters.min_price) params.append('min_price', filters.min_price.toString())
    if (filters.max_price) params.append('max_price', filters.max_price.toString())
    if (filters.search) params.append('search', filters.search)
    if (filters.is_subscription_available !== undefined) {
      params.append('is_subscription_available', filters.is_subscription_available.toString())
    }
    if (filters.sort_by) params.append('sort_by', filters.sort_by)

    const response = await api.get(`/api/v1/products?${params.toString()}`)
    return response.data
  },

  // Get single product by ID
  getProductById: async (id: number): Promise<Product> => {
    const response = await api.get(`/api/v1/products/${id}`)
    return response.data
  },

  // Search products
  searchProducts: async (query: string, filters: ProductFilters = {}): Promise<PaginatedProducts> => {
    const params = new URLSearchParams()
    
    params.append('q', query)
    if (filters.page) params.append('page', filters.page.toString())
    if (filters.page_size) params.append('page_size', filters.page_size.toString())
    if (filters.category_id) params.append('category_id', filters.category_id.toString())

    const response = await api.get(`/api/v1/products/search?${params.toString()}`)
    return response.data
  },

  // Get all categories
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/api/v1/categories')
    return response.data
  },
}

export default productService
