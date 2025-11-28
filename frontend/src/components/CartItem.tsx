import React, { useState } from 'react'
import { CartItem as CartItemType } from '../types/cart'
import { useCart } from '../hooks/useCart'

interface CartItemProps {
  item: CartItemType
}

const CartItem: React.FC<CartItemProps> = ({ item }) => {
  const { updateItemQuantity, removeItem } = useCart()
  const [isUpdating, setIsUpdating] = useState(false)
  const [isRemoving, setIsRemoving] = useState(false)

  const handleQuantityChange = async (newQuantity: number) => {
    if (newQuantity < 1) return
    if (newQuantity > item.product_stock_quantity) {
      alert(`Only ${item.product_stock_quantity} items available in stock`)
      return
    }

    try {
      setIsUpdating(true)
      await updateItemQuantity(item.id, newQuantity)
    } catch (error) {
      console.error('Failed to update quantity:', error)
    } finally {
      setIsUpdating(false)
    }
  }

  const handleRemove = async () => {
    if (!confirm('Remove this item from cart?')) return

    try {
      setIsRemoving(true)
      await removeItem(item.id)
    } catch (error) {
      console.error('Failed to remove item:', error)
      setIsRemoving(false)
    }
  }

  const itemTotal = item.subtotal
  const imageUrl = item.product_image_url || '/placeholder-product.png'
  const imageAlt = item.product_title || 'Product'

  const isOutOfStock = item.quantity > item.product_stock_quantity

  return (
    <div
      className={`flex gap-4 p-4 border rounded-lg ${
        isRemoving ? 'opacity-50' : ''
      } ${isOutOfStock ? 'border-red-300 bg-red-50' : 'border-gray-200'}`}
    >
      {/* Product Image */}
      <div className="flex-shrink-0 w-24 h-24">
        <img
          src={imageUrl}
          alt={imageAlt}
          className="w-full h-full object-cover rounded"
        />
      </div>

      {/* Product Details */}
      <div className="flex-1">
        <h3 className="font-semibold text-gray-900">{item.product_title || 'Product'}</h3>
        <p className="text-sm text-gray-600 mt-1">
          SKU: {item.product_sku || 'N/A'}
        </p>
        <p className="text-sm font-medium text-gray-900 mt-2">
          ₹{Number(item.unit_price ?? 0).toFixed(2)} each
        </p>

        {/* Stock Warning */}
        {isOutOfStock && (
          <p className="text-sm text-red-600 mt-2 font-medium">
            ⚠️ Only {item.product_stock_quantity} items available
          </p>
        )}
      </div>

      {/* Quantity Controls */}
      <div className="flex flex-col items-end justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleQuantityChange(item.quantity - 1)}
            disabled={isUpdating || item.quantity <= 1}
            className="w-8 h-8 flex items-center justify-center border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Decrease quantity"
          >
            −
          </button>
          <span className="w-12 text-center font-medium">{item.quantity}</span>
          <button
            onClick={() => handleQuantityChange(item.quantity + 1)}
            disabled={isUpdating || item.quantity >= (item.product?.stock_quantity ?? 0)}
            className="w-8 h-8 flex items-center justify-center border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Increase quantity"
          >
            +
          </button>
        </div>

        {/* Item Total */}
        <p className="text-lg font-bold text-gray-900">
          ₹{Number(itemTotal ?? 0).toFixed(2)}
        </p>

        {/* Remove Button */}
        <button
          onClick={handleRemove}
          disabled={isRemoving}
          className="text-sm text-red-600 hover:text-red-800 disabled:opacity-50"
        >
          {isRemoving ? 'Removing...' : 'Remove'}
        </button>
      </div>
    </div>
  )
}

export default CartItem
