import React, { useState } from 'react'
import { SubscriptionFrequency, CreateSubscriptionRequest } from '../types/subscription'
import { Product } from '../types/product'

interface SubscriptionFormProps {
  product: Product
  addressId: number
  onSubmit: (data: CreateSubscriptionRequest) => void
  onCancel: () => void
  isLoading?: boolean
}

const SubscriptionForm: React.FC<SubscriptionFormProps> = ({
  product,
  addressId,
  onSubmit,
  onCancel,
  isLoading = false,
}) => {
  const [frequency, setFrequency] = useState<SubscriptionFrequency>(
    SubscriptionFrequency.DAILY
  )
  const [startDate, setStartDate] = useState<string>(() => {
    // Default to tomorrow
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toISOString().split('T')[0]
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      product_id: product.id,
      plan_frequency: frequency,
      start_date: startDate,
      delivery_address_id: addressId,
    })
  }

  const getMinDate = () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toISOString().split('T')[0]
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Subscribe to {product.title}</h3>
        <p className="text-gray-600 mb-4">
          Get regular deliveries of {product.title} at your doorstep
        </p>
      </div>

      <div>
        <label htmlFor="frequency" className="block text-sm font-medium text-gray-700 mb-2">
          Delivery Frequency
        </label>
        <select
          id="frequency"
          value={frequency}
          onChange={(e) => setFrequency(e.target.value as SubscriptionFrequency)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          required
        >
          <option value={SubscriptionFrequency.DAILY}>Daily</option>
          <option value={SubscriptionFrequency.ALTERNATE_DAYS}>Alternate Days</option>
          <option value={SubscriptionFrequency.WEEKLY}>Weekly</option>
        </select>
      </div>

      <div>
        <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-2">
          Start Date
        </label>
        <input
          type="date"
          id="startDate"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          min={getMinDate()}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          required
        />
        <p className="text-sm text-gray-500 mt-1">
          Your first delivery will be on this date
        </p>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-700">Product:</span>
          <span className="font-semibold">{product.title}</span>
        </div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-700">Unit Size:</span>
          <span className="font-semibold">{product.unit_size}</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-700">Price per delivery:</span>
          <span className="font-semibold text-green-600">
            ₹{product.consumer_price.toFixed(2)}
          </span>
        </div>
      </div>

      <div className="flex gap-4">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          disabled={isLoading}
        >
          {isLoading ? 'Creating...' : 'Create Subscription'}
        </button>
      </div>
    </form>
  )
}

export default SubscriptionForm
