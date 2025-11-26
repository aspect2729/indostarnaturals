import React, { useState, useEffect } from 'react'
import { Product, Category } from '../types/product'
import { ProductCreateData, ProductUpdateData } from '../services/ownerProductService'
import ImageUploader from './ImageUploader'

interface ImageUploadItem {
  id?: number
  file?: File
  url: string
  altText: string
  displayOrder: number
  uploading?: boolean
  progress?: number
  error?: string
}

interface ProductFormProps {
  product?: Product | null
  categories: Category[]
  onSubmit: (data: ProductCreateData | ProductUpdateData, images: ImageUploadItem[]) => Promise<void>
  onCancel: () => void
  loading?: boolean
}

const ProductForm: React.FC<ProductFormProps> = ({
  product,
  categories,
  onSubmit,
  onCancel,
  loading = false,
}) => {
  const [formData, setFormData] = useState({
    title: product?.title || '',
    description: product?.description || '',
    category_id: product?.category_id || 0,
    sku: product?.sku || '',
    unit_size: product?.unit_size || '',
    consumer_price: product?.consumer_price?.toString() || '',
    distributor_price: product?.distributor_price?.toString() || '',
    stock_quantity: product?.stock_quantity?.toString() || '',
    is_subscription_available: product?.is_subscription_available || false,
    is_active: product?.is_active ?? true,
  })

  const [images, setImages] = useState<ImageUploadItem[]>([])
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Initialize images from existing product
  useEffect(() => {
    if (product?.images) {
      setImages(
        product.images.map((img) => ({
          id: img.id,
          url: img.url,
          altText: img.alt_text,
          displayOrder: img.display_order,
        }))
      )
    }
  }, [product])

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target
    const checked = (e.target as HTMLInputElement).checked

    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))

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

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required'
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required'
    }

    if (!formData.category_id || formData.category_id === 0) {
      newErrors.category_id = 'Category is required'
    }

    if (!formData.sku.trim()) {
      newErrors.sku = 'SKU is required'
    }

    if (!formData.unit_size.trim()) {
      newErrors.unit_size = 'Unit size is required'
    }

    const consumerPrice = parseFloat(formData.consumer_price)
    if (isNaN(consumerPrice) || consumerPrice <= 0) {
      newErrors.consumer_price = 'Consumer price must be a positive number'
    } else if (!/^\d+(\.\d{1,2})?$/.test(formData.consumer_price)) {
      newErrors.consumer_price = 'Price must have at most 2 decimal places'
    }

    const distributorPrice = parseFloat(formData.distributor_price)
    if (isNaN(distributorPrice) || distributorPrice <= 0) {
      newErrors.distributor_price = 'Distributor price must be a positive number'
    } else if (!/^\d+(\.\d{1,2})?$/.test(formData.distributor_price)) {
      newErrors.distributor_price = 'Price must have at most 2 decimal places'
    }

    const stockQuantity = parseInt(formData.stock_quantity, 10)
    if (isNaN(stockQuantity) || stockQuantity < 0) {
      newErrors.stock_quantity = 'Stock quantity must be a non-negative integer'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    const data: ProductCreateData | ProductUpdateData = {
      title: formData.title.trim(),
      description: formData.description.trim(),
      category_id: parseInt(formData.category_id.toString(), 10),
      sku: formData.sku.trim(),
      unit_size: formData.unit_size.trim(),
      consumer_price: parseFloat(formData.consumer_price),
      distributor_price: parseFloat(formData.distributor_price),
      stock_quantity: parseInt(formData.stock_quantity, 10),
      is_subscription_available: formData.is_subscription_available,
    }

    if (product) {
      ;(data as ProductUpdateData).is_active = formData.is_active
    }

    await onSubmit(data, images)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Product Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
            errors.title ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="e.g., Organic Jaggery Powder"
        />
        {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description <span className="text-red-500">*</span>
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={4}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
            errors.description ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Detailed product description..."
        />
        {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
      </div>

      {/* Category and SKU */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="category_id" className="block text-sm font-medium text-gray-700 mb-1">
            Category <span className="text-red-500">*</span>
          </label>
          <select
            id="category_id"
            name="category_id"
            value={formData.category_id}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
              errors.category_id ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value={0}>Select a category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          {errors.category_id && <p className="mt-1 text-sm text-red-600">{errors.category_id}</p>}
        </div>

        <div>
          <label htmlFor="sku" className="block text-sm font-medium text-gray-700 mb-1">
            SKU <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="sku"
            name="sku"
            value={formData.sku}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
              errors.sku ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="e.g., JAG-PWD-500"
          />
          {errors.sku && <p className="mt-1 text-sm text-red-600">{errors.sku}</p>}
        </div>
      </div>

      {/* Unit Size */}
      <div>
        <label htmlFor="unit_size" className="block text-sm font-medium text-gray-700 mb-1">
          Unit Size <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="unit_size"
          name="unit_size"
          value={formData.unit_size}
          onChange={handleChange}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
            errors.unit_size ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="e.g., 500g, 1L, 1kg"
        />
        {errors.unit_size && <p className="mt-1 text-sm text-red-600">{errors.unit_size}</p>}
      </div>

      {/* Pricing */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="consumer_price" className="block text-sm font-medium text-gray-700 mb-1">
            Consumer Price (₹) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="consumer_price"
            name="consumer_price"
            value={formData.consumer_price}
            onChange={handleChange}
            step="0.01"
            min="0"
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
              errors.consumer_price ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="0.00"
          />
          {errors.consumer_price && (
            <p className="mt-1 text-sm text-red-600">{errors.consumer_price}</p>
          )}
        </div>

        <div>
          <label
            htmlFor="distributor_price"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Distributor Price (₹) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="distributor_price"
            name="distributor_price"
            value={formData.distributor_price}
            onChange={handleChange}
            step="0.01"
            min="0"
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
              errors.distributor_price ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="0.00"
          />
          {errors.distributor_price && (
            <p className="mt-1 text-sm text-red-600">{errors.distributor_price}</p>
          )}
        </div>
      </div>

      {/* Stock Quantity */}
      <div>
        <label htmlFor="stock_quantity" className="block text-sm font-medium text-gray-700 mb-1">
          Stock Quantity <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          id="stock_quantity"
          name="stock_quantity"
          value={formData.stock_quantity}
          onChange={handleChange}
          min="0"
          step="1"
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 ${
            errors.stock_quantity ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="0"
        />
        {errors.stock_quantity && (
          <p className="mt-1 text-sm text-red-600">{errors.stock_quantity}</p>
        )}
      </div>

      {/* Checkboxes */}
      <div className="space-y-3">
        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_subscription_available"
            name="is_subscription_available"
            checked={formData.is_subscription_available}
            onChange={handleChange}
            className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
          />
          <label htmlFor="is_subscription_available" className="ml-2 text-sm text-gray-700">
            Available for subscription
          </label>
        </div>

        {product && (
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            />
            <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
              Product is active
            </label>
          </div>
        )}
      </div>

      {/* Images */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Product Images</label>
        <ImageUploader images={images} onImagesChange={setImages} />
      </div>

      {/* Action buttons */}
      <div className="flex space-x-3 pt-4 border-t">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {loading ? 'Saving...' : product ? 'Update Product' : 'Create Product'}
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

export default ProductForm
