import React from 'react'
import { Order, PaymentStatus } from '../types/order'
import OrderStatusBadge from './OrderStatusBadge'

interface OrderDetailModalProps {
  order: Order
  onClose: () => void
}

const OrderDetailModal: React.FC<OrderDetailModalProps> = ({ order, onClose }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getPaymentStatusBadge = (status: PaymentStatus) => {
    const configs = {
      [PaymentStatus.PENDING]: {
        label: 'Pending',
        className: 'bg-yellow-100 text-yellow-800',
      },
      [PaymentStatus.PAID]: {
        label: 'Paid',
        className: 'bg-green-100 text-green-800',
      },
      [PaymentStatus.FAILED]: {
        label: 'Failed',
        className: 'bg-red-100 text-red-800',
      },
      [PaymentStatus.REFUNDED]: {
        label: 'Refunded',
        className: 'bg-purple-100 text-purple-800',
      },
    }
    const config = configs[status] || { label: status, className: 'bg-gray-100 text-gray-800' }
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.className}`}>
        {config.label}
      </span>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Order Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Order Info */}
          <div>
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  Order #{order.order_number}
                </h3>
                <p className="text-sm text-gray-600">Placed on {formatDate(order.created_at)}</p>
              </div>
              <div className="flex gap-2">
                <OrderStatusBadge status={order.order_status} />
                {getPaymentStatusBadge(order.payment_status)}
              </div>
            </div>
          </div>

          {/* Order Items */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3">Order Items</h4>
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              {order.items.map((item) => (
                <div key={item.id} className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{item.product.title}</p>
                    <p className="text-sm text-gray-600">
                      {item.product.unit_size} • SKU: {item.product.sku}
                    </p>
                    <p className="text-sm text-gray-600">
                      ₹{Number(item.unit_price).toFixed(2)} × {item.quantity}
                    </p>
                  </div>
                  <p className="font-semibold text-gray-900">₹{Number(item.total_price).toFixed(2)}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Price Breakdown */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3">Price Breakdown</h4>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium text-gray-900">
                  ₹{order.total_amount.toFixed(2)}
                </span>
              </div>
              {order.discount_amount > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Discount</span>
                  <span className="font-medium text-green-600">
                    -₹{order.discount_amount.toFixed(2)}
                  </span>
                </div>
              )}
              <div className="border-t border-gray-300 pt-2 flex justify-between">
                <span className="font-semibold text-gray-900">Total</span>
                <span className="font-bold text-xl text-gray-900">
                  ₹{order.final_amount.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Delivery Address */}
          <div>
            <h4 className="text-md font-semibold text-gray-900 mb-3">Delivery Address</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="font-medium text-gray-900">{order.delivery_address.name}</p>
              <p className="text-sm text-gray-700 mt-1">{order.delivery_address.address_line1}</p>
              {order.delivery_address.address_line2 && (
                <p className="text-sm text-gray-700">{order.delivery_address.address_line2}</p>
              )}
              <p className="text-sm text-gray-700">
                {order.delivery_address.city}, {order.delivery_address.state}{' '}
                {order.delivery_address.postal_code}
              </p>
              <p className="text-sm text-gray-700 mt-2">
                Phone: {order.delivery_address.phone}
              </p>
            </div>
          </div>

          {/* Notes */}
          {order.notes && (
            <div>
              <h4 className="text-md font-semibold text-gray-900 mb-3">Order Notes</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-700">{order.notes}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4">
          <button
            onClick={onClose}
            className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default OrderDetailModal
