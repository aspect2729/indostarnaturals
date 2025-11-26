import React, { useState } from 'react'
import { Category, ProductFilters } from '../types/product'

interface FilterSidebarProps {
  categories: Category[]
  filters: ProductFilters
  onFilterChange: (filters: ProductFilters) => void
}

const FilterSidebar: React.FC<FilterSidebarProps> = ({
  categories,
  filters,
  onFilterChange,
}) => {
  const [minPrice, setMinPrice] = useState(filters.min_price?.toString() || '')
  const [maxPrice, setMaxPrice] = useState(filters.max_price?.toString() || '')

  const handleCategoryChange = (categoryId: number) => {
    onFilterChange({
      ...filters,
      category_id: filters.category_id === categoryId ? undefined : categoryId,
      page: 1, // Reset to first page when filter changes
    })
  }

  const handlePriceFilter = () => {
    onFilterChange({
      ...filters,
      min_price: minPrice ? parseFloat(minPrice) : undefined,
      max_price: maxPrice ? parseFloat(maxPrice) : undefined,
      page: 1,
    })
  }

  const handleSubscriptionFilter = (value: boolean | undefined) => {
    onFilterChange({
      ...filters,
      is_subscription_available: value,
      page: 1,
    })
  }

  const handleClearFilters = () => {
    setMinPrice('')
    setMaxPrice('')
    onFilterChange({
      page: 1,
      page_size: filters.page_size,
    })
  }

  const hasActiveFilters =
    filters.category_id ||
    filters.min_price ||
    filters.max_price ||
    filters.is_subscription_available !== undefined

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Filters</h2>
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-green-600 hover:text-green-700 font-medium"
          >
            Clear All
          </button>
        )}
      </div>

      {/* Categories */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Categories</h3>
        <div className="space-y-2">
          {categories.map((category) => (
            <label
              key={category.id}
              className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded"
            >
              <input
                type="checkbox"
                checked={filters.category_id === category.id}
                onChange={() => handleCategoryChange(category.id)}
                className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
              />
              <span className="ml-3 text-sm text-gray-700">{category.name}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Price Range */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Price Range</h3>
        <div className="space-y-3">
          <div>
            <label htmlFor="min-price" className="block text-xs text-gray-600 mb-1">
              Min Price (₹)
            </label>
            <input
              id="min-price"
              type="number"
              min="0"
              step="0.01"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              placeholder="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label htmlFor="max-price" className="block text-xs text-gray-600 mb-1">
              Max Price (₹)
            </label>
            <input
              id="max-price"
              type="number"
              min="0"
              step="0.01"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              placeholder="Any"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <button
            onClick={handlePriceFilter}
            className="w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
          >
            Apply Price Filter
          </button>
        </div>
      </div>

      {/* Subscription Available */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Availability</h3>
        <div className="space-y-2">
          <label className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded">
            <input
              type="radio"
              name="subscription"
              checked={filters.is_subscription_available === undefined}
              onChange={() => handleSubscriptionFilter(undefined)}
              className="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
            />
            <span className="ml-3 text-sm text-gray-700">All Products</span>
          </label>
          <label className="flex items-center cursor-pointer hover:bg-gray-50 p-2 rounded">
            <input
              type="radio"
              name="subscription"
              checked={filters.is_subscription_available === true}
              onChange={() => handleSubscriptionFilter(true)}
              className="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
            />
            <span className="ml-3 text-sm text-gray-700">Subscription Available</span>
          </label>
        </div>
      </div>
    </div>
  )
}

export default FilterSidebar
