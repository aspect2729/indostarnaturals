import React, { useState, useEffect } from 'react'
import { Product, Category } from '../types/product'
import productService from '../services/productService'
import ownerProductService, { ProductCreateData, ProductUpdateData } from '../services/ownerProductService'
import ProductForm from '../components/ProductForm'
import StockUpdateForm from '../components/StockUpdateForm'
import SearchBar from '../components/SearchBar'

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

const ProductManagementPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [stockUpdateProduct, setStockUpdateProduct] = useState<Product | null>(null)
  const [formLoading, setFormLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [searchQuery, selectedCategory])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [productsData, categoriesData] = await Promise.all([
        searchQuery
          ? productService.searchProducts(searchQuery, {
              category_id: selectedCategory || undefined,
              page_size: 100,
            })
          : productService.getProducts({
              category_id: selectedCategory || undefined,
              page_size: 100,
            }),
        productService.getCategories(),
      ])

      setProducts(productsData.items)
      setCategories(categoriesData)
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load products')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProduct = async (data: ProductCreateData | ProductUpdateData, images: ImageUploadItem[]) => {
    try {
      setFormLoading(true)
      setError(null)

      // Create product
      const newProduct = await ownerProductService.createProduct(data as ProductCreateData)

      // Upload images
      for (const image of images) {
        if (image.file) {
          await ownerProductService.uploadImage(
            newProduct.id,
            image.file,
            image.altText,
            image.displayOrder
          )
        }
      }

      setShowCreateForm(false)
      await loadData()
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to create product')
      throw err
    } finally {
      setFormLoading(false)
    }
  }

  const handleUpdateProduct = async (data: ProductCreateData | ProductUpdateData, images: ImageUploadItem[]) => {
    if (!editingProduct) return

    try {
      setFormLoading(true)
      setError(null)

      // Update product
      await ownerProductService.updateProduct(editingProduct.id, data as ProductUpdateData)

      // Handle images
      const existingImageIds = new Set(
        editingProduct.images.map((img) => img.id)
      )
      const newImageIds = new Set(
        images.filter((img) => img.id).map((img) => img.id!)
      )

      // Delete removed images
      for (const existingId of existingImageIds) {
        if (!newImageIds.has(existingId)) {
          await ownerProductService.deleteImage(editingProduct.id, existingId)
        }
      }

      // Upload new images
      for (const image of images) {
        if (image.file) {
          await ownerProductService.uploadImage(
            editingProduct.id,
            image.file,
            image.altText,
            image.displayOrder
          )
        }
      }

      setEditingProduct(null)
      await loadData()
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to update product')
      throw err
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteProduct = async (productId: number) => {
    if (!confirm('Are you sure you want to delete this product?')) {
      return
    }

    try {
      setError(null)
      await ownerProductService.deleteProduct(productId)
      await loadData()
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to delete product')
    }
  }

  const handleStockUpdate = async (quantityDelta: number) => {
    if (!stockUpdateProduct) return

    try {
      await ownerProductService.updateStock(stockUpdateProduct.id, quantityDelta)
      setStockUpdateProduct(null)
      await loadData()
    } catch (err: any) {
      throw err
    }
  }

  if (showCreateForm) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Create New Product</h1>
        </div>
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
        <div className="bg-white rounded-lg shadow p-6">
          <ProductForm
            categories={categories}
            onSubmit={handleCreateProduct}
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

  if (editingProduct) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Edit Product</h1>
        </div>
        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
        <div className="bg-white rounded-lg shadow p-6">
          <ProductForm
            product={editingProduct}
            categories={categories}
            onSubmit={handleUpdateProduct}
            onCancel={() => {
              setEditingProduct(null)
              setError(null)
            }}
            loading={formLoading}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Product Management</h1>
        
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Search and filters */}
          <div className="flex-1 flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <SearchBar
                onSearch={setSearchQuery}
                placeholder="Search products..."
                initialValue={searchQuery}
              />
            </div>
            
            <select
              value={selectedCategory || ''}
              onChange={(e) => setSelectedCategory(e.target.value ? parseInt(e.target.value) : null)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">All Categories</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          {/* Create button */}
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors font-medium"
          >
            + Create Product
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Products table */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        </div>
      ) : products.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500">No products found</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="mt-4 text-green-600 hover:text-green-700 font-medium"
          >
            Create your first product
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SKU
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {product.images[0] && (
                        <img
                          src={product.images[0].url}
                          alt={product.images[0].alt_text}
                          className="h-10 w-10 rounded object-cover mr-3"
                        />
                      )}
                      <div>
                        <div className="text-sm font-medium text-gray-900">{product.title}</div>
                        <div className="text-sm text-gray-500">{product.unit_size}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.sku}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.category.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">₹{product.consumer_price}</div>
                    <div className="text-xs text-gray-500">Dist: ₹{product.distributor_price}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span
                        className={`text-sm font-medium ${
                          product.stock_quantity === 0
                            ? 'text-red-600'
                            : product.stock_quantity < 10
                            ? 'text-yellow-600'
                            : 'text-gray-900'
                        }`}
                      >
                        {product.stock_quantity}
                      </span>
                      <button
                        onClick={() => setStockUpdateProduct(product)}
                        className="ml-2 text-blue-600 hover:text-blue-800 text-xs"
                      >
                        Update
                      </button>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        product.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {product.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => setEditingProduct(product)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteProduct(product.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Stock update modal */}
      {stockUpdateProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <StockUpdateForm
            currentStock={stockUpdateProduct.stock_quantity}
            onUpdate={handleStockUpdate}
            onCancel={() => setStockUpdateProduct(null)}
          />
        </div>
      )}
    </div>
  )
}

export default ProductManagementPage
