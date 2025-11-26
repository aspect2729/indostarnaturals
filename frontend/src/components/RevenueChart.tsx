import React, { useState, useEffect } from 'react'
import { analyticsService, RevenueReport } from '../services/analyticsService'

const RevenueChart: React.FC = () => {
  const [report, setReport] = useState<RevenueReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dateRange, setDateRange] = useState<'7days' | '30days' | 'custom'>('30days')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const fetchReport = async () => {
    try {
      setLoading(true)
      setError(null)
      
      let start: string | undefined
      let end: string | undefined
      
      if (dateRange === 'custom') {
        start = startDate
        end = endDate
      } else {
        const today = new Date()
        const daysAgo = dateRange === '7days' ? 7 : 30
        const startDateObj = new Date(today)
        startDateObj.setDate(today.getDate() - daysAgo)
        start = startDateObj.toISOString().split('T')[0]
        end = today.toISOString().split('T')[0]
      }
      
      const data = await analyticsService.getRevenueReport(start, end)
      setReport(data)
    } catch (err) {
      setError('Failed to load revenue report')
      console.error('Error fetching revenue report:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (dateRange !== 'custom' || (startDate && endDate)) {
      fetchReport()
    }
  }, [dateRange, startDate, endDate])

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <p className="mt-2 text-sm text-gray-600">Loading revenue data...</p>
        </div>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error || 'No data available'}
        </div>
      </div>
    )
  }

  // Calculate max revenue for scaling
  const maxRevenue = Math.max(...report.daily_data.map((d) => d.revenue), 1)

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Revenue Report</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setDateRange('7days')}
            className={`px-3 py-1 text-sm rounded-md ${
              dateRange === '7days'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            7 Days
          </button>
          <button
            onClick={() => setDateRange('30days')}
            className={`px-3 py-1 text-sm rounded-md ${
              dateRange === '30days'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            30 Days
          </button>
          <button
            onClick={() => setDateRange('custom')}
            className={`px-3 py-1 text-sm rounded-md ${
              dateRange === 'custom'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Custom
          </button>
        </div>
      </div>

      {dateRange === 'custom' && (
        <div className="mb-6 flex gap-4">
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
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-sm text-green-600 font-medium">Total Revenue</p>
          <p className="text-2xl font-bold text-green-900">₹{report.total_revenue.toFixed(2)}</p>
        </div>
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-sm text-blue-600 font-medium">Total Orders</p>
          <p className="text-2xl font-bold text-blue-900">{report.total_orders}</p>
        </div>
      </div>

      {/* Simple Bar Chart */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-700 mb-3">Daily Revenue</p>
        {report.daily_data.map((day) => {
          const percentage = (day.revenue / maxRevenue) * 100
          return (
            <div key={day.date} className="flex items-center gap-3">
              <div className="w-24 text-xs text-gray-600">
                {new Date(day.date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                })}
              </div>
              <div className="flex-1 bg-gray-100 rounded-full h-8 relative overflow-hidden">
                <div
                  className="bg-green-500 h-full rounded-full transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                />
                <div className="absolute inset-0 flex items-center px-3">
                  <span className="text-xs font-medium text-gray-700">
                    ₹{day.revenue.toFixed(2)} ({day.order_count} orders)
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {report.daily_data.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No revenue data available for the selected period
        </div>
      )}
    </div>
  )
}

export default RevenueChart
