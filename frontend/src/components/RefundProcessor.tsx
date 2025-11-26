import React, { useState } from 'react'
import { OrderWithUser, ownerOrderService } from '../services/ownerOrderService'

interface RefundProcessorProps {
  order: OrderWithUser
  onClose: () => void
  onUpdate: () => void
}

const RefundProcessor: React.FC<RefundProcessorProps> = ({ order, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [confirmed, setConfirmed] = useState(false)

  const handleRefund = async () => {
    if (!confirmed) {
      setError('Please confirm that you want to process this refund')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      await ownerOrderService.processRefund(order.id)
      onUpdate()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process refund')
      console.error('Error processing refund:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-900">Process Refund</h3>
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
        <div className="p-6">
          <div className="mb-6">
            <p className="text-sm text-gray-600 mb-2">
              Order: <span className="font-medium text-gray-900">{order.order_number}</span>
            </p>
            <p className="text-sm text-gray-600 mb-2">
              Customer: <span className="font-medium text-gray-900">{order.user_name}</span>
            </p>
            <p className="text-sm text-gray-600 mb-4">
              Amount: <span className="font-medium text-gray-900">₹{order.final_amount.toFixed(2)}</span>
            </p>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <svg className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <h4 className="text-sm font-medium text-yellow-800 mb-1">Warning</h4>
                <p className="text-sm text-yellow-700">
                  Processing a refund will:
                </p>
                <ul className="text-sm text-yellow-700 list-disc list-inside mt-2 space-y-1">
                  <li>Update order status to REFUNDED</li>
                  <li>Update payment status to REFUNDED</li>
                  <li>Restore product stock quantities</li>
                  <li>Create an audit log entry</li>
                </ul>
                <p className="text-sm text-yellow-700 mt-2 font-medium">
                  This action cannot be undone.
                </p>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => {
                  setConfirmed(e.target.checked)
                  setError(null)
                }}
                className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
              />
              <span className="ml-2 text-sm text-gray-700">
                I confirm that I want to process this refund
              </span>
            </label>
          </div>

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
              onClick={handleRefund}
              disabled={loading || !confirmed}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Processing...' : 'Process Refund'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RefundProcessor
