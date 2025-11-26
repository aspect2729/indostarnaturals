import React, { useState } from 'react'
import { OrderWithUser } from '../services/ownerOrderService'
import OrderStatusUpdater from './OrderStatusUpdater'
import RefundProcessor from './RefundProcessor'
import OrderStatusBadge from './OrderStatusBadge'
import { OrderStatus, PaymentStatus } from '../types/order'

interface OrderDetailViewProps {
  order: OrderWithUser
  onClose: () => void
  onUpdate: () => void
}

const OrderDetailView: React.FC<OrderDetailViewProps> = ({ order, onClose, onUpdate }) => {
  const [showStatusUpdater, setShowStatusUpdater] = useState(false)
  const [showRefundProcessor, setShowRefundProcessor] = useState(false)

  const canRefund = order.payment_status === PaymentStatus.PAID && 
                    order.order_status !== OrderStatus.CANCELLED

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            Order Details - {order.order_number}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6">
          {/* Customer Information */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Customer Information</h3>
            <div className="bg-gray-50 rounded-lg p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-medium">{order.user_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium">{order.user_phone}</p>
              </div>
              {order.user_email && (
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-medium">{order.user_email}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-600">Role</p>
                <span className="inline-block px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 capitalize">
                  {order.user_role}
                </span>
              </div>
            </div>
          </div>

          {/* Order Status */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Order Status</h3>
            <div className="bg-gray-50 rounded-lg p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Order Status</p>
                <div className="mt-1">
                  <OrderStatusBadge status={order.order_status} />
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600">Payment Status</p>
                <div className="mt-1">
                  <span className={`inline-block px-3 py-1 text-sm font-medium rounded-full ${
                    order.payment_status === PaymentStatus.PAID
                      ? 'bg-green-100 text-green-800'
                      : order.payment_status === PaymentStatus.FAILED
                      ? 'bg-red-100 text-red-800'
                      : order.payment_status === PaymentStatus.REFUNDED
                      ? 'bg-purple-100 text-purple-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {order.payment_status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600">Order Date</p>
                <p className="font-medium">{new Date(order.created_at).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Last Updated</p>
                <p className="font-medium">{new Date(order.updated_at).toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Delivery Address */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Delivery Address</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="font-medium">{order.delivery_address.name}</p>
              <p className="text-gray-700">{order.delivery_address.phone}</p>
              <p className="text-gray-700 mt-2">
                {order.delivery_address.address_line1}
                {order.delivery_address.address_line2 && `, ${order.delivery_address.address_line2}`}
              </p>
              <p className="text-gray-700">
                {order.delivery_address.city}, {order.delivery_address.state} {order.delivery_address.postal_code}
              </p>
              <p className="text-gray-700">{order.delivery_address.country}</p>
            </div>
          </div>

          {/* Order Items */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Order Items</h3>
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {order.items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-4 py-3 text-sm text-gray-900">{item.product_title}</td>
                      <td className="px-4 py-3 text-sm text-gray-500">{item.product_sku}</td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">{item.quantity}</td>
                      <td className="px-4 py-3 text-sm text-gray-900 text-right">₹{item.unit_price.toFixed(2)}</td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900 text-right">
                        ₹{item.total_price.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Order Summary */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Order Summary</h3>
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-700">Subtotal</span>
                <span className="font-medium">₹{order.total_amount.toFixed(2)}</span>
              </div>
              {order.discount_amount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Discount</span>
                  <span className="font-medium">-₹{order.discount_amount.toFixed(2)}</span>
                </div>
              )}
              <div className="border-t border-gray-300 pt-2 flex justify-between text-lg font-bold">
                <span>Total</span>
                <span>₹{order.final_amount.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Notes */}
          {order.notes && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Notes</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700">{order.notes}</p>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => setShowStatusUpdater(true)}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
            >
              Update Status
            </button>
            {canRefund && (
              <button
                onClick={() => setShowRefundProcessor(true)}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium"
              >
                Process Refund
              </button>
            )}
          </div>
        </div>

        {/* Status Updater Modal */}
        {showStatusUpdater && (
          <OrderStatusUpdater
            order={order}
            onClose={() => setShowStatusUpdater(false)}
            onUpdate={() => {
              setShowStatusUpdater(false)
              onUpdate()
            }}
          />
        )}

        {/* Refund Processor Modal */}
        {showRefundProcessor && (
          <RefundProcessor
            order={order}
            onClose={() => setShowRefundProcessor(false)}
            onUpdate={() => {
              setShowRefundProcessor(false)
              onUpdate()
            }}
          />
        )}
      </div>
    </div>
  )
}

export default OrderDetailView
