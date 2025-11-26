import React, { useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import FilterSidebar from '../components/FilterSidebar'
import SearchBar from '../components/SearchBar'
import Pagination from '../components/Pagination'
import { ProductFilters } from '../types/product'
import { useProducts, useCategories } from '../hooks/useProducts'
import { useCart } from '../contexts/CartContext'
import { useToast } from '../components/ToastContainer'

const ProductCatalogPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const { addToCart } = useCart()
  const { showToast } = useToast()
  
  // Initialize filters from URL params
  const [filters, setFilters] = useState<ProductFilters>({
    page: parseInt(searchParams.get('page') || '1'),
    page_size: 20,
    category_id: searchParams.get('category_id') ? parseInt(searchParams.get('category_id')!) : undefined,
    search: searchParams.get('search') || undefined,
    sort_by: (searchParams.get('sort_by') as ProductFilters['sort_by']) || undefined,
  })

  // Fetch products and categories using React Query
  const { data: productsData, isLoading, isError, error } = useProducts(filters)
  const { data: categories = [] } = useCategories()

  const products = productsData?.items || []
  const totalPages = productsData?.total_pages || 1

  // Update URL params when filters change
  const updateFilters = useCallback((newFilters: ProductFilters) => {
    setFilters(newFilters)
    
    // Update URL search params
    const params = new URLSearchParams()
    if (newFilters.page && newFilters.page > 1) params.set('page', newFilters.page.toString())
    if (newFilters.category_id) params.set('category_id', newFilters.category_id.toString())
    if (newFilters.search) params.set('search', newFilters.search)
    if (newFilters.sort_by) params.set('sort_by', newFilters.sort_by)
    
    setSearchParams(params)
  }, [setSearchParams])

  const handleSearch = useCallback((query: string) => {
    updateFilters({
      ...filters,
      search: query || undefined,
      page: 1,
    })
  }, [filters, updateFilters])

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    updateFilters({
      ...filters,
      sort_by: e.target.value as ProductFilters['sort_by'] || undefined,
      page: 1,
    })
  }

  const handlePageChange = (page: number) => {
    updateFilters({
      ...filters,
      page,
    })
    // Scroll to top when page changes
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleAddToCart = async (productId: number) => {
    try {
      await addToCart({ product_id: productId, quantity: 1 })
      showToast('Product added to cart successfully', 'success')
    } catch (error) {
      showToast('Failed to add product to cart', 'error')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Products</h1>
          
          {/* Search Bar */}
          <div className="mb-4">
            <SearchBar
              onSearch={handleSearch}
              initialValue={filters.search}
              placeholder="Search for organic products..."
            />
          </div>

          {/* Sort and Results Count */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {isLoading
                ? 'Loading...'
                : productsData
                ? `Showing ${products.length} of ${productsData.total} products`
                : 'No products'}
            </p>
            
            <div className="flex items-center space-x-2">
              <label htmlFor="sort" className="text-sm text-gray-600">
                Sort by:
              </label>
              <select
                id="sort"
                value={filters.sort_by || ''}
                onChange={handleSortChange}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Default</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="name_asc">Name: A to Z</option>
                <option value="name_desc">Name: Z to A</option>
                <option value="newest">Newest First</option>
              </select>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar - Hidden on mobile, shown on desktop */}
          <aside className="lg:w-64 flex-shrink-0">
            <div className="sticky top-4">
              <FilterSidebar
                categories={categories}
                filters={filters}
                onFilterChange={updateFilters}
              />
            </div>
          </aside>

          {/* Product Grid */}
          <main className="flex-1">
            {isLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
              </div>
            ) : isError ? (
              <div className="text-center py-12">
                <div className="text-red-600 mb-4">
                  <svg
                    className="mx-auto h-12 w-12"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading products</h3>
                <p className="text-sm text-gray-500 mb-4">
                  {error?.message || 'Something went wrong. Please try again.'}
                </p>
                <button
                  onClick={() => window.location.reload()}
                  className="text-green-600 hover:text-green-700 font-medium"
                >
                  Reload Page
                </button>
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No products found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try adjusting your search or filters to find what you're looking for.
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {products.map((product: any) => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      onAddToCart={handleAddToCart}
                    />
                  ))}
                </div>

                {/* Pagination */}
                <Pagination
                  currentPage={filters.page || 1}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}

export default ProductCatalogPage
