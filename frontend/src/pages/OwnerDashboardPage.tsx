import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { analyticsService } from '../services/analyticsService'
import { orderService } from '../services/orderService'
import OrderStatusBadge from '../components/OrderStatusBadge'
import { OrderStatus } from '../types/order'

const OwnerDashboardPage: React.FC = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [revenueTimeRange, setRevenueTimeRange] = useState<'7d' | '30d' | '90d'>('30d')

  // Fetch dashboard metrics
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: analyticsService.getDashboardMetrics,
  })

  // Fetch recent orders
  const {
    data: orders = [],
    isLoading: ordersLoading,
  } = useQuery({
    queryKey: ['recent-orders'],
    queryFn: orderService.getOrders,
  })

  // Get date range for revenue report
  const getDateRange = (range: '7d' | '30d' | '90d') => {
    const endDate = new Date()
    const startDate = new Date()
    
    switch (range) {
      case '7d':
        startDate.setDate(endDate.getDate() - 7)
        break
      case '30d':
        startDate.setDate(endDate.getDate() - 30)
        break
      case '90d':
        startDate.setDate(endDate.getDate() - 90)
        break
    }
    
    return {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0],
    }
  }

  // Fetch revenue report
  const { start, end } = getDateRange(revenueTimeRange)
  const {
    data: revenueReport,
    isLoading: revenueLoading,
  } = useQuery({
    queryKey: ['revenue-report', start, end],
    queryFn: () => analyticsService.getRevenueReport(start, end),
  })

  // Get recent orders (last 5)
  const recentOrders = orders.slice(0, 5)

  // Get pending orders count
  const pendingOrdersCount = orders.filter(
    (order) => order.order_status === OrderStatus.PENDING
  ).length

  const formatCurrency = (amount: number) => {
    return `₹${amount.toFixed(2)}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Owner Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.name}! Here's your business overview.</p>
        </div>

        {/* Error Alert */}
        {metricsError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            Failed to load dashboard metrics. Please try again.
          </div>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Revenue */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-600">Total Revenue</p>
              <div className="bg-green-100 rounded-full p-2">
                <svg
                  className="w-5 h-5 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {metricsLoading ? '...' : formatCurrency(metrics?.total_revenue || 0)}
            </p>
          </div>

          {/* Total Orders */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-600">Total Orders</p>
              <div className="bg-blue-100 rounded-full p-2">
                <svg
                  className="w-5 h-5 text-blue-600"
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
            <p className="text-3xl font-bold text-gray-900">
              {metricsLoading ? '...' : metrics?.order_count || 0}
            </p>
          </div>

          {/* Active Subscriptions */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-600">Active Subscriptions</p>
              <div className="bg-purple-100 rounded-full p-2">
                <svg
                  className="w-5 h-5 text-purple-600"
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
            <p className="text-3xl font-bold text-gray-900">
              {metricsLoading ? '...' : metrics?.active_subscriptions || 0}
            </p>
          </div>

          {/* Pending Orders */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-600">Pending Orders</p>
              <div className="bg-yellow-100 rounded-full p-2">
                <svg
                  className="w-5 h-5 text-yellow-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {ordersLoading ? '...' : pendingOrdersCount}
            </p>
          </div>
        </div>

        {/* Low Stock Alerts */}
        {metrics && metrics.low_stock_alerts.length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg
                  className="w-6 h-6 text-yellow-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-yellow-800 mb-2">
                  Low Stock Alerts ({metrics.low_stock_alerts.length})
                </h3>
                <div className="space-y-2">
                  {metrics.low_stock_alerts.slice(0, 3).map((product) => (
                    <div
                      key={product.id}
                      className="flex justify-between items-center text-sm text-yellow-700"
                    >
                      <span>
                        {product.title} (SKU: {product.sku})
                      </span>
                      <span className="font-semibold">
                        {product.stock_quantity} units remaining
                      </span>
                    </div>
                  ))}
                </div>
                {metrics.low_stock_alerts.length > 3 && (
                  <button
                    onClick={() => navigate('/owner/inventory')}
                    className="mt-3 text-sm text-yellow-800 font-medium hover:text-yellow-900"
                  >
                    View all {metrics.low_stock_alerts.length} alerts →
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Revenue Trends */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Revenue Trends</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setRevenueTimeRange('7d')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  revenueTimeRange === '7d'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                7 Days
              </button>
              <button
                onClick={() => setRevenueTimeRange('30d')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  revenueTimeRange === '30d'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                30 Days
              </button>
              <button
                onClick={() => setRevenueTimeRange('90d')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  revenueTimeRange === '90d'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                90 Days
              </button>
            </div>
          </div>

          {revenueLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading revenue data...</p>
            </div>
          ) : revenueReport ? (
            <div>
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Revenue</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(revenueReport.total_revenue)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Orders</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {revenueReport.total_orders}
                  </p>
                </div>
              </div>

              {/* Simple bar chart visualization */}
              <div className="space-y-2">
                {revenueReport.daily_data.slice(-10).map((day) => {
                  const maxRevenue = Math.max(
                    ...revenueReport.daily_data.map((d) => d.revenue)
                  )
                  const widthPercent = maxRevenue > 0 ? (day.revenue / maxRevenue) * 100 : 0

                  return (
                    <div key={day.date} className="flex items-center gap-3">
                      <span className="text-xs text-gray-600 w-16">{formatDate(day.date)}</span>
                      <div className="flex-1 bg-gray-100 rounded-full h-8 relative">
                        <div
                          className="bg-primary-600 h-8 rounded-full flex items-center justify-end pr-3"
                          style={{ width: `${widthPercent}%` }}
                        >
                          {day.revenue > 0 && (
                            <span className="text-xs font-medium text-white">
                              {formatCurrency(day.revenue)}
                            </span>
                          )}
                        </div>
                      </div>
                      <span className="text-xs text-gray-600 w-12 text-right">
                        {day.order_count} orders
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          ) : (
            <p className="text-center text-gray-600 py-12">No revenue data available</p>
          )}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/owner/products')}
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
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              <span className="font-medium text-gray-700">Add Product</span>
            </button>

            <button
              onClick={() => navigate('/owner/orders')}
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
              <span className="font-medium text-gray-700">Manage Orders</span>
            </button>

            <button
              onClick={() => navigate('/owner/inventory')}
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
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
                />
              </svg>
              <span className="font-medium text-gray-700">View Inventory</span>
            </button>

            <button
              onClick={() => navigate('/owner/users')}
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
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
              <span className="font-medium text-gray-700">Manage Users</span>
            </button>
          </div>
        </div>

        {/* Recent Orders */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Recent Orders</h2>
            <button
              onClick={() => navigate('/owner/orders')}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              View All →
            </button>
          </div>

          {ordersLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-2"></div>
              <p className="text-sm text-gray-600">Loading orders...</p>
            </div>
          ) : recentOrders.length === 0 ? (
            <p className="text-center text-gray-600 py-8">No orders yet</p>
          ) : (
            <div className="space-y-3">
              {recentOrders.map((order) => (
                <div
                  key={order.id}
                  className="flex justify-between items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  onClick={() => navigate(`/owner/orders/${order.id}`)}
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Order #{order.order_number}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(order.created_at).toLocaleDateString('en-IN', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <p className="font-semibold text-gray-900">
                      {formatCurrency(order.final_amount)}
                    </p>
                    <OrderStatusBadge status={order.order_status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default OwnerDashboardPage
