import React, { useState, useEffect } from 'react'
import { analyticsService, DeliveryCalendarResponse } from '../services/analyticsService'

const SubscriptionCalendar: React.FC = () => {
  const [calendar, setCalendar] = useState<DeliveryCalendarResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const fetchCalendar = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Default to next 30 days if no dates specified
      let start = startDate
      let end = endDate
      
      if (!start || !end) {
        const today = new Date()
        const futureDate = new Date(today)
        futureDate.setDate(today.getDate() + 30)
        start = today.toISOString().split('T')[0]
        end = futureDate.toISOString().split('T')[0]
      }
      
      const data = await analyticsService.getDeliveryCalendar(start, end)
      setCalendar(data)
    } catch (err) {
      setError('Failed to load delivery calendar')
      console.error('Error fetching delivery calendar:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCalendar()
  }, [startDate, endDate])

  // Group deliveries by date
  const deliveriesByDate = calendar?.deliveries.reduce((acc, delivery) => {
    const date = delivery.delivery_date
    if (!acc[date]) {
      acc[date] = []
    }
    acc[date].push(delivery)
    return acc
  }, {} as Record<string, typeof calendar.deliveries>) || {}

  const sortedDates = Object.keys(deliveriesByDate).sort()

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <p className="mt-2 text-sm text-gray-600">Loading calendar...</p>
        </div>
      </div>
    )
  }

  if (error || !calendar) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error || 'No data available'}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">Subscription Delivery Calendar</h2>
        
        {/* Date Range Selector */}
        <div className="flex gap-4 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        <div className="text-sm text-gray-600">
          Showing deliveries for: <span className="font-medium">{calendar.date_range}</span>
        </div>
        <div className="text-sm text-gray-600">
          Total scheduled deliveries: <span className="font-medium">{calendar.total}</span>
        </div>
      </div>

      {/* Calendar View */}
      {sortedDates.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No scheduled deliveries for the selected period
        </div>
      ) : (
        <div className="space-y-6">
          {sortedDates.map((date) => {
            const deliveries = deliveriesByDate[date]
            const dateObj = new Date(date)
            const isToday = dateObj.toDateString() === new Date().toDateString()
            
            return (
              <div key={date} className={`border rounded-lg overflow-hidden ${
                isToday ? 'border-green-500 bg-green-50' : 'border-gray-200'
              }`}>
                <div className={`px-4 py-3 font-semibold ${
                  isToday ? 'bg-green-100 text-green-900' : 'bg-gray-50 text-gray-900'
                }`}>
                  <div className="flex items-center justify-between">
                    <span>
                      {dateObj.toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                      {isToday && <span className="ml-2 text-sm">(Today)</span>}
                    </span>
                    <span className="text-sm font-normal">
                      {deliveries.length} delivery{deliveries.length !== 1 ? 'ies' : ''}
                    </span>
                  </div>
                </div>
                <div className="divide-y divide-gray-200">
                  {deliveries.map((delivery) => (
                    <div key={delivery.subscription_id} className="px-4 py-3 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-gray-900">{delivery.product_title}</span>
                            <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                              {delivery.status}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600">
                            <p>Customer: {delivery.user_name}</p>
                            <p>Address: {delivery.delivery_address}</p>
                          </div>
                        </div>
                        <div className="text-right text-sm text-gray-500">
                          <p>Sub ID: {delivery.subscription_id}</p>
                          <p>User ID: {delivery.user_id}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default SubscriptionCalendar
