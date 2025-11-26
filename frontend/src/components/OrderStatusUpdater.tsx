import React, { useState } from 'react'
import { OrderWithUser, ownerOrderService } from '../services/ownerOrderService'
import { OrderStatus } from '../types/order'

interface OrderStatusUpdaterProps {
  order: OrderWithUser
  onClose: () => void
  onUpdate: () => void
}

const OrderStatusUpdater: React.FC<OrderStatusUpdaterProps> = ({ order, onClose, onUpdate }) => {
  const [selectedStatus, setSelectedStatus] = useState<OrderStatus>(order.order_status)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Define valid status transitions
  const getAvailableStatuses = (currentStatus: OrderStatus): OrderStatus[] => {
    switch (currentStatus) {
      case OrderStatus.PENDING:
        return [OrderStatus.CONFIRMED, OrderStatus.CANCELLED]
      case OrderStatus.CONFIRMED:
        return [OrderStatus.PACKED, OrderStatus.CANCELLED]
      case OrderStatus.PACKED:
        return [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.CANCELLED]
      case OrderStatus.OUT_FOR_DELIVERY:
        return [OrderStatus.DELIVERED, OrderStatus.CANCELLED]
      case OrderStatus.DELIVERED:
        return [] // No transitions from delivered
      case OrderStatus.CANCELLED:
        return [] // No transitions from cancelled
      default:
        return []
    }
  }

  const availableStatuses = getAvailableStatuses(order.order_status)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (selectedStatus === order.order_status) {
      setError('Please select a different status')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      await ownerOrderService.updateOrderStatus(order.id, { status: selectedStatus })
      onUpdate()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update order status')
      console.error('Error updating order status:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusLabel = (status: OrderStatus): string => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-900">Update Order Status</h3>
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

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">
              Order: <span className="font-medium text-gray-900">{order.order_number}</span>
            </p>
            <p className="text-sm text-gray-600 mb-4">
              Current Status: <span className="font-medium text-gray-900">{getStatusLabel(order.order_status)}</span>
            </p>
          </div>

          {availableStatuses.length === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-yellow-800">
                No status transitions available for this order.
              </p>
            </div>
          ) : (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Status
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as OrderStatus)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                required
              >
                <option value={order.order_status}>Select new status...</option>
                {availableStatuses.map((status) => (
                  <option key={status} value={status}>
                    {getStatusLabel(status)}
                  </option>
                ))}
              </select>
            </div>
          )}

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 font-medium"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || availableStatuses.length === 0 || selectedStatus === order.order_status}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Updating...' : 'Update Status'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default OrderStatusUpdater
