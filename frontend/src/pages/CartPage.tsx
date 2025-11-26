import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCart } from '../hooks/useCart'
import { useAuth } from '../hooks/useAuth'
import CartItem from '../components/CartItem'
import CouponInput from '../components/CouponInput'

const CartPage: React.FC = () => {
  const { cart, isLoading, error, itemCount } = useCart()
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  // Redirect to login if not authenticated
  React.useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/cart')
    }
  }, [isAuthenticated, navigate])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading cart...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Link to="/products" className="text-green-600 hover:text-green-700">
            Continue Shopping
          </Link>
        </div>
      </div>
    )
  }

  if (!cart || itemCount === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
          <p className="text-gray-600 mb-6">Add some products to get started</p>
          <Link
            to="/products"
            className="inline-block px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Browse Products
          </Link>
        </div>
      </div>
    )
  }

  // Check if any items are out of stock
  const hasStockIssues = cart.items.some(
    (item) => item.quantity > item.product.stock_quantity
  )

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          <p className="text-gray-600 mt-2">
            {itemCount} {itemCount === 1 ? 'item' : 'items'} in your cart
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {cart.items.map((item) => (
              <CartItem key={item.id} item={item} />
            ))}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-4">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Order Summary</h2>

              {/* Subtotal */}
              <div className="flex justify-between py-2">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium">₹{cart.total_amount.toFixed(2)}</span>
              </div>

              {/* Discount */}
              {cart.discount_amount > 0 && (
                <div className="flex justify-between py-2 text-green-600">
                  <span>Discount</span>
                  <span className="font-medium">-₹{cart.discount_amount.toFixed(2)}</span>
                </div>
              )}

              {/* Divider */}
              <div className="border-t border-gray-200 my-4"></div>

              {/* Total */}
              <div className="flex justify-between py-2 text-lg font-bold">
                <span>Total</span>
                <span>₹{cart.final_amount.toFixed(2)}</span>
              </div>

              {/* Stock Warning */}
              {hasStockIssues && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                  <p className="text-sm text-red-800">
                    ⚠️ Some items in your cart exceed available stock. Please adjust quantities
                    before checkout.
                  </p>
                </div>
              )}

              {/* Coupon Input */}
              <div className="mt-6">
                <CouponInput />
              </div>

              {/* Checkout Button */}
              <button
                onClick={() => navigate('/checkout')}
                disabled={hasStockIssues}
                className="w-full mt-6 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Proceed to Checkout
              </button>

              {/* Continue Shopping */}
              <Link
                to="/products"
                className="block text-center mt-4 text-green-600 hover:text-green-700"
              >
                Continue Shopping
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CartPage
