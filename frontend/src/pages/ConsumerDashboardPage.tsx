import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { orderService } from '../services/orderService'
import * as subscriptionService from '../services/subscriptionService'
import OrderHistoryList from '../components/OrderHistoryList'
import OrderDetailModal from '../components/OrderDetailModal'
import { Order } from '../types/order'
import { SubscriptionStatus } from '../types/subscription'

const ConsumerDashboardPage: React.FC = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)

  // Fetch orders
  const {
    data: ordersData = [],
    isLoading: ordersLoading,
    error: ordersError,
  } = useQuery({
    queryKey: ['orders'],
    queryFn: orderService.getOrders,
  })

  // Ensure orders is always an array
  const orders = Array.isArray(ordersData) ? ordersData : []

  // Fetch subscriptions
  const {
    data: subscriptions = [],
    isLoading: subscriptionsLoading,
  } = useQuery({
    queryKey: ['subscriptions'],
    queryFn: subscriptionService.getSubscriptions,
  })

  const activeSubscriptions = subscriptions.filter(
    (sub) => sub.status === SubscriptionStatus.ACTIVE
  )

  const handleViewOrderDetails = (order: Order) => {
    setSelectedOrder(order)
  }

  const handleCloseModal = () => {
    setSelectedOrder(null)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.name}!</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Orders */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Total Orders</p>
                <p className="text-3xl font-bold text-gray-900">
                  {ordersLoading ? '...' : orders.length}
                </p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <svg
                  className="w-8 h-8 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Active Subscriptions */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Active Subscriptions</p>
                <p className="text-3xl font-bold text-gray-900">
                  {subscriptionsLoading ? '...' : activeSubscriptions.length}
                </p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <svg
                  className="w-8 h-8 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Account Status */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Account Status</p>
                <p className="text-lg font-semibold text-green-600">Active</p>
              </div>
              <div className="bg-purple-100 rounded-full p-3">
                <svg
                  className="w-8 h-8 text-purple-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/products')}
              className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                />
              </svg>
              <span className="font-medium text-gray-700">Browse Products</span>
            </button>

            <button
              onClick={() => navigate('/subscriptions')}
              className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              <span className="font-medium text-gray-700">Manage Subscriptions</span>
            </button>

            <button
              onClick={() => navigate('/profile')}
              className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <span className="font-medium text-gray-700">Edit Profile</span>
            </button>

            <button
              onClick={() => navigate('/cart')}
              className="flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
              <span className="font-medium text-gray-700">View Cart</span>
            </button>
          </div>
        </div>

        {/* Active Subscriptions Summary */}
        {activeSubscriptions.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Active Subscriptions</h2>
              <button
                onClick={() => navigate('/subscriptions')}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                View All →
              </button>
            </div>
            <div className="space-y-3">
              {activeSubscriptions.slice(0, 3).map((subscription) => (
                <div
                  key={subscription.id}
                  className="flex justify-between items-center p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{subscription.product.title}</p>
                    <p className="text-sm text-gray-600">
                      Next delivery:{' '}
                      {new Date(subscription.next_delivery_date).toLocaleDateString('en-IN', {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </p>
                  </div>
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                    Active
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Order History */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Orders</h2>
          {ordersError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              Failed to load orders. Please try again.
            </div>
          )}
          <OrderHistoryList
            orders={orders.slice(0, 5)}
            onViewDetails={handleViewOrderDetails}
            isLoading={ordersLoading}
          />
          {orders.length > 5 && (
            <div className="mt-4 text-center">
              <button
                onClick={() => navigate('/orders')}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                View All Orders →
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Order Detail Modal */}
      {selectedOrder && <OrderDetailModal order={selectedOrder} onClose={handleCloseModal} />}
    </div>
  )
}

export default ConsumerDashboardPage
