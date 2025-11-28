import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import SubscriptionCard from '../components/SubscriptionCard'
import { Subscription, SubscriptionStatus } from '../types/subscription'
import * as subscriptionService from '../services/subscriptionService'
import { useAuth } from '../hooks/useAuth'

const SubscriptionManagementPage: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [filter, setFilter] = useState<'all' | SubscriptionStatus>('all')

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }
    fetchSubscriptions()
  }, [user, navigate])

  const fetchSubscriptions = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await subscriptionService.getSubscriptions()
      setSubscriptions(Array.isArray(data) ? data : [])
    } catch (err) {
      setError('Failed to load subscriptions. Please try again.')
      console.error('Error fetching subscriptions:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handlePause = async (id: number) => {
    try {
      setActionLoading(id)
      await subscriptionService.pauseSubscription(id)
      // Update local state
      setSubscriptions((prev) =>
        prev.map((sub) =>
          sub.id === id ? { ...sub, status: SubscriptionStatus.PAUSED } : sub
        )
      )
    } catch (err) {
      alert('Failed to pause subscription. Please try again.')
      console.error('Error pausing subscription:', err)
    } finally {
      setActionLoading(null)
    }
  }

  const handleResume = async (id: number) => {
    try {
      setActionLoading(id)
      await subscriptionService.resumeSubscription(id)
      // Update local state
      setSubscriptions((prev) =>
        prev.map((sub) =>
          sub.id === id ? { ...sub, status: SubscriptionStatus.ACTIVE } : sub
        )
      )
    } catch (err) {
      alert('Failed to resume subscription. Please try again.')
      console.error('Error resuming subscription:', err)
    } finally {
      setActionLoading(null)
    }
  }

  const handleCancel = async (id: number) => {
    try {
      setActionLoading(id)
      await subscriptionService.cancelSubscription(id)
      // Update local state
      setSubscriptions((prev) =>
        prev.map((sub) =>
          sub.id === id ? { ...sub, status: SubscriptionStatus.CANCELLED } : sub
        )
      )
    } catch (err) {
      alert('Failed to cancel subscription. Please try again.')
      console.error('Error cancelling subscription:', err)
    } finally {
      setActionLoading(null)
    }
  }

  const filteredSubscriptions = (subscriptions || []).filter((sub) => {
    if (filter === 'all') return true
    return sub.status === filter
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading subscriptions...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Subscriptions</h1>
          <p className="text-gray-600">Manage your recurring deliveries</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Filter tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setFilter('all')}
              className={`px-6 py-3 text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              All ({subscriptions.length})
            </button>
            <button
              onClick={() => setFilter(SubscriptionStatus.ACTIVE)}
              className={`px-6 py-3 text-sm font-medium transition-colors ${
                filter === SubscriptionStatus.ACTIVE
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Active (
              {subscriptions.filter((s) => s.status === SubscriptionStatus.ACTIVE).length})
            </button>
            <button
              onClick={() => setFilter(SubscriptionStatus.PAUSED)}
              className={`px-6 py-3 text-sm font-medium transition-colors ${
                filter === SubscriptionStatus.PAUSED
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Paused (
              {subscriptions.filter((s) => s.status === SubscriptionStatus.PAUSED).length})
            </button>
            <button
              onClick={() => setFilter(SubscriptionStatus.CANCELLED)}
              className={`px-6 py-3 text-sm font-medium transition-colors ${
                filter === SubscriptionStatus.CANCELLED
                  ? 'border-b-2 border-green-600 text-green-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Cancelled (
              {subscriptions.filter((s) => s.status === SubscriptionStatus.CANCELLED).length}
              )
            </button>
          </div>
        </div>

        {/* Subscriptions list */}
        {filteredSubscriptions.length === 0 ? (
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
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filter === 'all' ? 'No subscriptions yet' : `No ${filter} subscriptions`}
            </h3>
            <p className="text-gray-600 mb-6">
              {filter === 'all'
                ? 'Start a subscription to get regular deliveries of your favorite products.'
                : `You don't have any ${filter} subscriptions.`}
            </p>
            {filter === 'all' && (
              <button
                onClick={() => navigate('/products')}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Browse Products
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredSubscriptions.map((subscription) => (
              <SubscriptionCard
                key={subscription.id}
                subscription={subscription}
                onPause={handlePause}
                onResume={handleResume}
                onCancel={handleCancel}
                isLoading={actionLoading === subscription.id}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default SubscriptionManagementPage
