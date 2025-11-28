import React, { useState } from 'react'
import { Subscription, SubscriptionStatus, SubscriptionFrequency } from '../types/subscription'

interface SubscriptionCardProps {
  subscription: Subscription
  onPause: (id: number) => void
  onResume: (id: number) => void
  onCancel: (id: number) => void
  isLoading?: boolean
}

const SubscriptionCard: React.FC<SubscriptionCardProps> = ({
  subscription,
  onPause,
  onResume,
  onCancel,
  isLoading = false,
}) => {
  const [showCancelConfirm, setShowCancelConfirm] = useState(false)

  const getStatusBadge = (status: SubscriptionStatus) => {
    const badges = {
      [SubscriptionStatus.ACTIVE]: 'bg-green-100 text-green-800',
      [SubscriptionStatus.PAUSED]: 'bg-yellow-100 text-yellow-800',
      [SubscriptionStatus.CANCELLED]: 'bg-red-100 text-red-800',
    }
    return badges[status] || 'bg-gray-100 text-gray-800'
  }

  const getFrequencyLabel = (frequency: SubscriptionFrequency) => {
    const labels = {
      [SubscriptionFrequency.DAILY]: 'Daily',
      [SubscriptionFrequency.ALTERNATE_DAYS]: 'Alternate Days',
      [SubscriptionFrequency.WEEKLY]: 'Weekly',
    }
    return labels[frequency]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const handleCancelClick = () => {
    setShowCancelConfirm(true)
  }

  const handleConfirmCancel = () => {
    onCancel(subscription.id)
    setShowCancelConfirm(false)
  }

  const handleCancelConfirmDialog = () => {
    setShowCancelConfirm(false)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {subscription.product.title}
          </h3>
          <p className="text-sm text-gray-600">{subscription.product.unit_size}</p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(
            subscription.status
          )}`}
        >
          {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
        </span>
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Frequency:</span>
          <span className="font-medium text-gray-900">
            {getFrequencyLabel(subscription.plan_frequency)}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Next Delivery:</span>
          <span className="font-medium text-gray-900">
            {formatDate(subscription.next_delivery_date)}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Price per delivery:</span>
          <span className="font-semibold text-green-600">
            ₹{Number(subscription.product.consumer_price).toFixed(2)}
          </span>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-4">
        <div className="text-sm text-gray-600 mb-3">
          <p className="font-medium mb-1">Delivery Address:</p>
          <p>{subscription.delivery_address.name}</p>
          <p>{subscription.delivery_address.address_line1}</p>
          {subscription.delivery_address.address_line2 && (
            <p>{subscription.delivery_address.address_line2}</p>
          )}
          <p>
            {subscription.delivery_address.city}, {subscription.delivery_address.state}{' '}
            {subscription.delivery_address.postal_code}
          </p>
          <p>{subscription.delivery_address.phone}</p>
        </div>
      </div>

      {subscription.status !== SubscriptionStatus.CANCELLED && (
        <div className="flex gap-2 mt-4">
          {subscription.status === SubscriptionStatus.ACTIVE && (
            <button
              onClick={() => onPause(subscription.id)}
              disabled={isLoading}
              className="flex-1 px-4 py-2 border border-yellow-500 text-yellow-700 rounded-lg hover:bg-yellow-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Pause
            </button>
          )}
          {subscription.status === SubscriptionStatus.PAUSED && (
            <button
              onClick={() => onResume(subscription.id)}
              disabled={isLoading}
              className="flex-1 px-4 py-2 border border-green-500 text-green-700 rounded-lg hover:bg-green-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Resume
            </button>
          )}
          <button
            onClick={handleCancelClick}
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-red-500 text-red-700 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel Subscription
          </button>
        </div>
      )}

      {showCancelConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Cancel Subscription?</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to cancel this subscription? This action cannot be undone.
              You will no longer receive deliveries for {subscription.product.title}.
            </p>
            <div className="flex gap-4">
              <button
                onClick={handleCancelConfirmDialog}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Keep Subscription
              </button>
              <button
                onClick={handleConfirmCancel}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Yes, Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SubscriptionCard
