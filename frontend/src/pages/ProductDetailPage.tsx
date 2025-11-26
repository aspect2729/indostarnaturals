import React, { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import ImageCarousel from '../components/ImageCarousel'
import PriceDisplay from '../components/PriceDisplay'
import SubscriptionForm from '../components/SubscriptionForm'
import { useProduct } from '../hooks/useProducts'
import { useCart } from '../hooks/useCart'
import { useAuth } from '../hooks/useAuth'
import * as subscriptionService from '../services/subscriptionService'
import { CreateSubscriptionRequest } from '../types/subscription'
import userService from '../services/userService'

const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const productId = id ? parseInt(id) : 0
  const navigate = useNavigate()
  const [quantity, setQuantity] = useState(1)
  const [isAddingToCart, setIsAddingToCart] = useState(false)
  const [addToCartMessage, setAddToCartMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [showSubscriptionForm, setShowSubscriptionForm] = useState(false)
  const [isCreatingSubscription, setIsCreatingSubscription] = useState(false)
  const [addresses, setAddresses] = useState<any[]>([])
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null)

  // Fetch product using React Query
  const { data: product, isLoading, isError, error } = useProduct(productId)
  const { addToCart } = useCart()
  const { isAuthenticated } = useAuth()

  // Fetch user addresses when subscription form is shown
  React.useEffect(() => {
    if (showSubscriptionForm && isAuthenticated) {
      fetchAddresses()
    }
  }, [showSubscriptionForm, isAuthenticated])

  const fetchAddresses = async () => {
    try {
      const userAddresses = await userService.getAddresses()
      setAddresses(userAddresses)
      if (userAddresses.length > 0) {
        const defaultAddress = userAddresses.find((addr: any) => addr.is_default)
        setSelectedAddressId(defaultAddress?.id || userAddresses[0].id)
      }
    } catch (err) {
      console.error('Failed to fetch addresses:', err)
    }
  }

  const handleQuantityChange = (delta: number) => {
    setQuantity((prev) => Math.max(1, Math.min(prev + delta, product?.stock_quantity || 1)))
  }

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate(`/login?redirect=/products/${id}`)
      return
    }

    try {
      setIsAddingToCart(true)
      setAddToCartMessage(null)
      await addToCart({ product_id: productId, quantity })
      setAddToCartMessage({ type: 'success', text: 'Added to cart successfully!' })
      setQuantity(1) // Reset quantity
      
      // Clear success message after 3 seconds
      setTimeout(() => setAddToCartMessage(null), 3000)
    } catch (err: any) {
      console.error('Failed to add to cart:', err)
      setAddToCartMessage({
        type: 'error',
        text: err.response?.data?.error?.message || 'Failed to add to cart',
      })
    } finally {
      setIsAddingToCart(false)
    }
  }

  const handleSubscribe = () => {
    if (!isAuthenticated) {
      navigate(`/login?redirect=/products/${id}`)
      return
    }
    setShowSubscriptionForm(true)
  }

  const handleSubscriptionSubmit = async (data: CreateSubscriptionRequest) => {
    try {
      setIsCreatingSubscription(true)
      const response = await subscriptionService.createSubscription(data)
      
      // Initialize Razorpay subscription checkout
      subscriptionService.initializeRazorpaySubscription(
        response,
        async (razorpayResponse: any) => {
          // Payment successful
          try {
            await subscriptionService.handleRazorpaySubscription(
              response.subscription.id,
              razorpayResponse.razorpay_payment_id,
              razorpayResponse.razorpay_subscription_id,
              razorpayResponse.razorpay_signature
            )
            // Navigate to subscriptions page
            navigate('/subscriptions')
          } catch (err) {
            console.error('Failed to verify subscription payment:', err)
            alert('Subscription created but payment verification failed. Please contact support.')
          }
        },
        (error: any) => {
          // Payment failed or cancelled
          console.error('Subscription payment failed:', error)
          alert('Subscription payment was cancelled or failed. Please try again.')
          setShowSubscriptionForm(false)
        }
      )
    } catch (err: any) {
      console.error('Failed to create subscription:', err)
      alert(err.response?.data?.error?.message || 'Failed to create subscription. Please try again.')
    } finally {
      setIsCreatingSubscription(false)
    }
  }

  const handleCancelSubscription = () => {
    setShowSubscriptionForm(false)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error loading product</h2>
          <p className="text-gray-600 mb-4">
            {error?.message || 'Something went wrong. Please try again.'}
          </p>
          <Link
            to="/products"
            className="text-green-600 hover:text-green-700 font-medium"
          >
            Back to Products
          </Link>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Product not found</h2>
          <p className="text-gray-600 mb-4">The product you're looking for doesn't exist.</p>
          <Link
            to="/products"
            className="text-green-600 hover:text-green-700 font-medium"
          >
            Back to Products
          </Link>
        </div>
      </div>
    )
  }

  const isOutOfStock = product.stock_quantity === 0
  const isLowStock = product.stock_quantity > 0 && product.stock_quantity <= 10

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm">
          <ol className="flex items-center space-x-2 text-gray-600">
            <li>
              <Link to="/" className="hover:text-green-600">
                Home
              </Link>
            </li>
            <li>/</li>
            <li>
              <Link to="/products" className="hover:text-green-600">
                Products
              </Link>
            </li>
            <li>/</li>
            <li>
              <Link
                to={`/products?category_id=${product.category_id}`}
                className="hover:text-green-600"
              >
                {product.category.name}
              </Link>
            </li>
            <li>/</li>
            <li className="text-gray-900 font-medium">{product.title}</li>
          </ol>
        </nav>

        {/* Product Details */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-6 lg:p-8">
            {/* Left Column - Images */}
            <div>
              <ImageCarousel images={product.images} productTitle={product.title} />
            </div>

            {/* Right Column - Product Info */}
            <div className="space-y-6">
              {/* Title and Category */}
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.title}</h1>
                <p className="text-sm text-gray-600">
                  Category:{' '}
                  <Link
                    to={`/products?category_id=${product.category_id}`}
                    className="text-green-600 hover:text-green-700"
                  >
                    {product.category.name}
                  </Link>
                </p>
              </div>

              {/* Price */}
              <div className="border-t border-b border-gray-200 py-4">
                <PriceDisplay
                  consumerPrice={product.consumer_price}
                  distributorPrice={product.distributor_price}
                  className="text-2xl"
                  showLabel
                />
                <p className="text-sm text-gray-600 mt-1">Unit Size: {product.unit_size}</p>
              </div>

              {/* Stock Status */}
              <div>
                {isOutOfStock ? (
                  <p className="text-red-600 font-semibold">Out of Stock</p>
                ) : isLowStock ? (
                  <p className="text-orange-600 font-medium">
                    Only {product.stock_quantity} left in stock!
                  </p>
                ) : (
                  <p className="text-green-600 font-medium">In Stock</p>
                )}
              </div>

              {/* Description */}
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Description</h2>
                <p className="text-gray-700 whitespace-pre-line">{product.description}</p>
              </div>

              {/* Quantity Selector and Add to Cart */}
              {!isOutOfStock && (
                <div className="space-y-4">
                  <div>
                    <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-2">
                      Quantity
                    </label>
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleQuantityChange(-1)}
                        disabled={quantity <= 1}
                        className="w-10 h-10 rounded-md border border-gray-300 flex items-center justify-center hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label="Decrease quantity"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M20 12H4"
                          />
                        </svg>
                      </button>
                      <input
                        id="quantity"
                        type="number"
                        min="1"
                        max={product.stock_quantity}
                        value={quantity}
                        onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                        className="w-20 text-center border border-gray-300 rounded-md py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                      <button
                        onClick={() => handleQuantityChange(1)}
                        disabled={quantity >= product.stock_quantity}
                        className="w-10 h-10 rounded-md border border-gray-300 flex items-center justify-center hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label="Increase quantity"
                      >
                        <svg
                          className="w-4 h-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 4v16m8-8H4"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <button
                    onClick={handleAddToCart}
                    disabled={isAddingToCart}
                    className="w-full py-3 px-6 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 active:bg-green-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isAddingToCart ? 'Adding...' : 'Add to Cart'}
                  </button>

                  {/* Add to Cart Message */}
                  {addToCartMessage && (
                    <div
                      className={`p-3 rounded-md ${
                        addToCartMessage.type === 'success'
                          ? 'bg-green-50 text-green-800 border border-green-200'
                          : 'bg-red-50 text-red-800 border border-red-200'
                      }`}
                    >
                      <p className="text-sm font-medium">{addToCartMessage.text}</p>
                      {addToCartMessage.type === 'success' && (
                        <button
                          onClick={() => navigate('/cart')}
                          className="text-sm text-green-600 hover:text-green-700 underline mt-1"
                        >
                          View Cart
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Subscription Options */}
              {product.is_subscription_available && !isOutOfStock && (
                <div className="border-t border-gray-200 pt-6">
                  <h2 className="text-lg font-semibold text-gray-900 mb-3">
                    Subscribe & Save
                  </h2>
                  <p className="text-sm text-gray-600 mb-4">
                    Get regular deliveries and never run out!
                  </p>

                  <button
                    onClick={handleSubscribe}
                    className="w-full py-3 px-6 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 active:bg-blue-800 transition-colors"
                  >
                    Start Subscription
                  </button>
                </div>
              )}

              {/* Product Details */}
              <div className="border-t border-gray-200 pt-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-3">Product Details</h2>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-gray-600">SKU:</dt>
                    <dd className="text-gray-900 font-medium">{product.sku}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Unit Size:</dt>
                    <dd className="text-gray-900 font-medium">{product.unit_size}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600">Category:</dt>
                    <dd className="text-gray-900 font-medium">{product.category.name}</dd>
                  </div>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Subscription Form Modal */}
      {showSubscriptionForm && product && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            {addresses.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">
                  You need to add a delivery address before creating a subscription.
                </p>
                <button
                  onClick={() => navigate('/profile')}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Add Address
                </button>
                <button
                  onClick={handleCancelSubscription}
                  className="ml-4 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <>
                {/* Address Selector */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Delivery Address
                  </label>
                  <select
                    value={selectedAddressId || ''}
                    onChange={(e) => setSelectedAddressId(parseInt(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    {addresses.map((addr: any) => (
                      <option key={addr.id} value={addr.id}>
                        {addr.name} - {addr.address_line1}, {addr.city}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedAddressId && (
                  <SubscriptionForm
                    product={product}
                    addressId={selectedAddressId}
                    onSubmit={handleSubscriptionSubmit}
                    onCancel={handleCancelSubscription}
                    isLoading={isCreatingSubscription}
                  />
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ProductDetailPage
