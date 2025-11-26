import { useQuery, UseQueryResult } from '@tanstack/react-query'
import productService from '../services/productService'
import { Product, Category, ProductFilters, PaginatedProducts } from '../types/product'

// Query keys for React Query
export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (filters: ProductFilters) => [...productKeys.lists(), filters] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (id: number) => [...productKeys.details(), id] as const,
  search: (query: string, filters: ProductFilters) => [...productKeys.all, 'search', query, filters] as const,
  categories: ['categories'] as const,
}

// Hook to fetch paginated products with filters
export const useProducts = (
  filters: ProductFilters = {}
): UseQueryResult<PaginatedProducts, Error> => {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: () => productService.getProducts(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  })
}

// Hook to fetch single product by ID
export const useProduct = (id: number): UseQueryResult<Product, Error> => {
  return useQuery({
    queryKey: productKeys.detail(id),
    queryFn: () => productService.getProductById(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    enabled: !!id, // Only run query if id is provided
  })
}

// Hook to search products
export const useProductSearch = (
  query: string,
  filters: ProductFilters = {}
): UseQueryResult<PaginatedProducts, Error> => {
  return useQuery({
    queryKey: productKeys.search(query, filters),
    queryFn: () => productService.searchProducts(query, filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
    enabled: query.length > 0, // Only search if query is not empty
  })
}

// Hook to fetch categories
export const useCategories = (): UseQueryResult<Category[], Error> => {
  return useQuery({
    queryKey: productKeys.categories,
    queryFn: () => productService.getCategories(),
    staleTime: 60 * 60 * 1000, // 1 hour (categories don't change often)
    gcTime: 2 * 60 * 60 * 1000, // 2 hours
  })
}
