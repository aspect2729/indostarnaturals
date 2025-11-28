import React from 'react'
import { Order } from '../types/order'
import OrderStatusBadge from './OrderStatusBadge'

interface OrderHistoryListProps {
  orders: Order[]
  onViewDetails: (order: Order) => void
  isLoading?: boolean
}

const OrderHistoryList: React.FC<OrderHistoryListProps> = ({
  orders,
  onViewDetails,
  isLoading = false,
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading orders...</p>
      </div>
    )
  }

  if (orders.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-12 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400 mb-4"
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
        <h3 className="text-lg font-medium text-gray-900 mb-2">No orders yet</h3>
        <p className="text-gray-600">Start shopping to see your orders here.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {orders.map((order) => (
        <div
          key={order.id}
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Order #{order.order_number}
              </h3>
              <p className="text-sm text-gray-600">Placed on {formatDate(order.created_at)}</p>
            </div>
            <OrderStatusBadge status={order.order_status} />
          </div>

          <div className="border-t border-gray-200 pt-4 mb-4">
            <div className="space-y-2">
              {order.items.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span className="text-gray-700">
                    {item.product.title} x {item.quantity}
                  </span>
                  <span className="font-medium text-gray-900">
                    ₹{Number(item.total_price).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-gray-200">
            <div>
              <p className="text-sm text-gray-600">Total Amount</p>
              <p className="text-xl font-bold text-gray-900">₹{order.final_amount.toFixed(2)}</p>
            </div>
            <button
              onClick={() => onViewDetails(order)}
              className="px-4 py-2 border border-primary-600 text-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
            >
              View Details
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default OrderHistoryList
