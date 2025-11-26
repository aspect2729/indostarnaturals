import React from 'react'
import { Link } from 'react-router-dom'
import { Product } from '../types/product'
import PriceDisplay from './PriceDisplay'
import LazyImage from './LazyImage'

interface ProductCardProps {
  product: Product
  onAddToCart?: (productId: number) => void
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onAddToCart }) => {
  const primaryImage = product.images.find((img) => img.display_order === 0) || product.images[0]
  const imageUrl = primaryImage?.url || '/placeholder-product.png'
  const imageAlt = primaryImage?.alt_text || product.title

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (onAddToCart) {
      onAddToCart(product.id)
    }
  }

  const isOutOfStock = product.stock_quantity === 0

  return (
    <Link
      to={`/products/${product.id}`}
      className="group block bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden"
    >
      {/* Product Image */}
      <div className="relative aspect-square overflow-hidden bg-gray-100">
        <LazyImage
          src={imageUrl}
          alt={imageAlt}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
        />
        {isOutOfStock && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <span className="text-white font-semibold text-lg">Out of Stock</span>
          </div>
        )}
        {product.is_subscription_available && !isOutOfStock && (
          <div className="absolute top-2 right-2 bg-green-600 text-white text-xs font-semibold px-2 py-1 rounded">
            Subscription Available
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2 group-hover:text-green-700 transition-colors">
          {product.title}
        </h3>
        
        <p className="text-sm text-gray-600 mb-2">{product.unit_size}</p>
        
        <div className="flex items-center justify-between mb-3">
          <PriceDisplay
            consumerPrice={product.consumer_price}
            distributorPrice={product.distributor_price}
          />
          {product.stock_quantity > 0 && product.stock_quantity <= 10 && (
            <span className="text-xs text-orange-600 font-medium">
              Only {product.stock_quantity} left
            </span>
          )}
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={handleAddToCart}
          disabled={isOutOfStock}
          className={`w-full py-2 px-4 rounded-md font-medium transition-colors ${
            isOutOfStock
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700 active:bg-green-800'
          }`}
        >
          {isOutOfStock ? 'Out of Stock' : 'Add to Cart'}
        </button>
      </div>
    </Link>
  )
}

export default ProductCard
