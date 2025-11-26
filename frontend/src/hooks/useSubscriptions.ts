import { useState, useEffect } from 'react'
import { Subscription } from '../types/subscription'
import * as subscriptionService from '../services/subscriptionService'

export const useSubscriptions = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSubscriptions = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await subscriptionService.getSubscriptions()
      setSubscriptions(data)
    } catch (err) {
      setError('Failed to load subscriptions')
      console.error('Error fetching subscriptions:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSubscriptions()
  }, [])

  const pauseSubscription = async (id: number) => {
    try {
      const updated = await subscriptionService.pauseSubscription(id)
      setSubscriptions((prev) => prev.map((sub) => (sub.id === id ? updated : sub)))
      return updated
    } catch (err) {
      console.error('Error pausing subscription:', err)
      throw err
    }
  }

  const resumeSubscription = async (id: number) => {
    try {
      const updated = await subscriptionService.resumeSubscription(id)
      setSubscriptions((prev) => prev.map((sub) => (sub.id === id ? updated : sub)))
      return updated
    } catch (err) {
      console.error('Error resuming subscription:', err)
      throw err
    }
  }

  const cancelSubscription = async (id: number) => {
    try {
      await subscriptionService.cancelSubscription(id)
      // Refresh subscriptions after cancellation
      await fetchSubscriptions()
    } catch (err) {
      console.error('Error cancelling subscription:', err)
      throw err
    }
  }

  return {
    subscriptions,
    isLoading,
    error,
    refetch: fetchSubscriptions,
    pauseSubscription,
    resumeSubscription,
    cancelSubscription,
  }
}

export default useSubscriptions
