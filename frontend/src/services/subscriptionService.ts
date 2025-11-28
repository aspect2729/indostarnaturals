import api from './api'
import {
  Subscription,
  CreateSubscriptionRequest,
  CreateSubscriptionResponse,
} from '../types/subscription'

/**
 * Create a new subscription
 */
export const createSubscription = async (
  data: CreateSubscriptionRequest
): Promise<CreateSubscriptionResponse> => {
  const response = await api.post<CreateSubscriptionResponse>('/api/v1/subscriptions', data)
  return response.data
}

/**
 * Get all subscriptions for the current user
 */
export const getSubscriptions = async (): Promise<Subscription[]> => {
  const response = await api.get<{ subscriptions: Subscription[] }>('/api/v1/subscriptions')
  return response.data.subscriptions || []
}

/**
 * Get a specific subscription by ID
 */
export const getSubscriptionById = async (id: number): Promise<Subscription> => {
  const response = await api.get<Subscription>(`/api/v1/subscriptions/${id}`)
  return response.data
}

/**
 * Pause a subscription
 */
export const pauseSubscription = async (id: number): Promise<Subscription> => {
  const response = await api.put<Subscription>(`/api/v1/subscriptions/${id}/pause`)
  return response.data
}

/**
 * Resume a paused subscription
 */
export const resumeSubscription = async (id: number): Promise<Subscription> => {
  const response = await api.put<Subscription>(`/api/v1/subscriptions/${id}/resume`)
  return response.data
}

/**
 * Cancel a subscription
 */
export const cancelSubscription = async (id: number): Promise<void> => {
  await api.delete(`/api/v1/subscriptions/${id}`)
}

/**
 * Handle Razorpay subscription payment
 * This is called after Razorpay checkout completes
 */
export const handleRazorpaySubscription = async (
  subscriptionId: number,
  razorpayPaymentId: string,
  razorpaySubscriptionId: string,
  razorpaySignature: string
): Promise<void> => {
  await api.post(`/api/v1/subscriptions/${subscriptionId}/verify-payment`, {
    razorpay_payment_id: razorpayPaymentId,
    razorpay_subscription_id: razorpaySubscriptionId,
    razorpay_signature: razorpaySignature,
  })
}

/**
 * Initialize Razorpay subscription checkout
 */
export const initializeRazorpaySubscription = (
  subscriptionData: CreateSubscriptionResponse,
  onSuccess: (response: any) => void,
  onFailure: (error: any) => void
): void => {
  const options = {
    key: subscriptionData.razorpay_key_id,
    subscription_id: subscriptionData.razorpay_subscription_id,
    name: 'IndoStar Naturals',
    description: 'Subscription Payment',
    handler: function (response: any) {
      onSuccess(response)
    },
    prefill: {
      name: '',
      email: '',
      contact: '',
    },
    theme: {
      color: '#16a34a', // green-600
    },
    modal: {
      ondismiss: function () {
        onFailure(new Error('Payment cancelled by user'))
      },
    },
  }

  // @ts-ignore - Razorpay is loaded via script tag
  const razorpay = new window.Razorpay(options)
  razorpay.open()
}

const subscriptionService = {
  createSubscription,
  getSubscriptions,
  getSubscriptionById,
  pauseSubscription,
  resumeSubscription,
  cancelSubscription,
  handleRazorpaySubscription,
}

export default subscriptionService
