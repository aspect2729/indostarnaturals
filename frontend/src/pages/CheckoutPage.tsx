import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../hooks/useCart'
import { useAuth } from '../hooks/useAuth'
import { orderService } from '../services/orderService'
import { cartService } from '../services/cartService'
import DeliveryAddressSelector from '../components/DeliveryAddressSelector'
import OrderSummary from '../components/OrderSummary'
import { RazorpayPaymentResponse } from '../types/order'

// Extend Window interface for Razorpay
declare global {
  interface Window {
    Razorpay: any
  }
}

const CheckoutPage: React.FC = () => {
  const { cart, isLoading: cartLoading, refreshCart } = useCart()
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null)
  const [notes, setNotes] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/checkout')
    }
  }, [isAuthenticated, navigate])

  // Validate cart on mount
  useEffect(() => {
    const validateCart = async () => {
      if (!cart) return

      try {
        const validation = await cartService.validateCart()
        if (!validation.is_valid) {
          const errorMessages = validation.errors.map((err) => err.message).join(', ')
          setValidationError(errorMessages)
        } else {
          setValidationError(null)
        }
      } catch (err) {
        console.error('Failed to validate cart:', err)
      }
    }

    validateCart()
  }, [cart])

  // Load Razorpay script
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.async = true
    document.body.appendChild(script)

    return () => {
      document.body.removeChild(script)
    }
  }, [])

  const handlePayment = async () => {
    if (!selectedAddressId) {
      setError('Please select a delivery address')
      return
    }

    if (validationError) {
      setError('Please fix cart issues before proceeding')
      return
    }

    try {
      setIsProcessing(true)
      setError(null)

      // Create order
      const orderResponse = await orderService.createOrder({
        delivery_address_id: selectedAddressId,
        notes: notes || undefined,
      })

      // Initialize Razorpay
      const options = {
        key: orderResponse.razorpay_key_id,
        amount: orderResponse.amount,
        currency: orderResponse.currency,
        name: 'IndoStar Naturals',
        description: `Order #${orderResponse.order.order_number}`,
        order_id: orderResponse.razorpay_order_id,
        handler: async (response: RazorpayPaymentResponse) => {
          try {
            // Verify payment
            await orderService.verifyPayment(orderResponse.order.id, response)
            
            // Refresh cart (should be empty now)
            await refreshCart()
            
            // Redirect to success page
            navigate(`/orders/${orderResponse.order.id}?payment=success`)
          } catch (err: any) {
            console.error('Payment verification failed:', err)
            setError('Payment verification failed. Please contact support.')
            setIsProcessing(false)
          }
        },
        prefill: {
          name: user?.name || '',
          email: user?.email || '',
          contact: user?.phone || '',
        },
        theme: {
          color: '#16a34a', // green-600
        },
        modal: {
          ondismiss: () => {
            setIsProcessing(false)
            setError('Payment cancelled')
          },
        },
      }

      const razorpay = new window.Razorpay(options)
      razorpay.open()
    } catch (err: any) {
      console.error('Failed to initiate payment:', err)
      setError(err.response?.data?.error?.message || 'Failed to initiate payment')
      setIsProcessing(false)
    }
  }

  if (cartLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Your cart is empty</h2>
          <p className="text-gray-600 mb-6">Add some products to checkout</p>
          <button
            onClick={() => navigate('/products')}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Browse Products
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
          <p className="text-gray-600 mt-2">Complete your order</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Checkout Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Delivery Address */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <DeliveryAddressSelector
                selectedAddressId={selectedAddressId}
                onSelectAddress={setSelectedAddressId}
              />
            </div>

            {/* Order Notes */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Order Notes (Optional)</h2>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Any special instructions for delivery?"
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Validation Errors */}
            {validationError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 font-medium">⚠️ Cart Validation Error</p>
                <p className="text-red-600 text-sm mt-1">{validationError}</p>
                <button
                  onClick={() => navigate('/cart')}
                  className="mt-3 text-sm text-red-600 hover:text-red-800 underline"
                >
                  Go back to cart
                </button>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">{error}</p>
              </div>
            )}
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="sticky top-4">
              <OrderSummary cart={cart} showItems={true} />

              {/* Place Order Button */}
              <button
                onClick={handlePayment}
                disabled={isProcessing || !selectedAddressId || !!validationError}
                className="w-full mt-6 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {isProcessing ? 'Processing...' : 'Proceed to Payment'}
              </button>

              {/* Security Note */}
              <p className="text-xs text-gray-500 text-center mt-4">
                🔒 Secure payment powered by Razorpay
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CheckoutPage
