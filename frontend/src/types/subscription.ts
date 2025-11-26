export enum SubscriptionFrequency {
  DAILY = 'daily',
  ALTERNATE_DAYS = 'alternate_days',
  WEEKLY = 'weekly',
}

export enum SubscriptionStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  CANCELLED = 'cancelled',
}

export interface Subscription {
  id: number
  user_id: number
  product_id: number
  razorpay_subscription_id: string
  plan_frequency: SubscriptionFrequency
  start_date: string
  next_delivery_date: string
  delivery_address_id: number
  status: SubscriptionStatus
  created_at: string
  updated_at: string
  product: {
    id: number
    title: string
    sku: string
    unit_size: string
    consumer_price: number
    distributor_price: number
  }
  delivery_address: {
    id: number
    name: string
    phone: string
    address_line1: string
    address_line2: string | null
    city: string
    state: string
    postal_code: string
    country: string
  }
}

export interface CreateSubscriptionRequest {
  product_id: number
  plan_frequency: SubscriptionFrequency
  start_date: string
  delivery_address_id: number
}

export interface CreateSubscriptionResponse {
  subscription: Subscription
  razorpay_subscription_id: string
  razorpay_key_id: string
}
