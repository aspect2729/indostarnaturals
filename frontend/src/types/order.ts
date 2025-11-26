export enum PaymentStatus {
  PENDING = 'pending',
  PAID = 'paid',
  FAILED = 'failed',
  REFUNDED = 'refunded',
}

export enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  PACKED = 'packed',
  OUT_FOR_DELIVERY = 'out_for_delivery',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled',
}

export interface OrderItem {
  id: number
  order_id: number
  product_id: number
  quantity: number
  unit_price: number
  total_price: number
  product: {
    id: number
    title: string
    sku: string
    unit_size: string
  }
}

export interface Order {
  id: number
  user_id: number
  order_number: string
  total_amount: number
  discount_amount: number
  final_amount: number
  payment_status: PaymentStatus
  order_status: OrderStatus
  delivery_address_id: number
  notes: string | null
  created_at: string
  updated_at: string
  items: OrderItem[]
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

export interface CreateOrderRequest {
  delivery_address_id: number
  notes?: string
}

export interface CreateOrderResponse {
  order: Order
  razorpay_order_id: string
  razorpay_key_id: string
  amount: number
  currency: string
}

export interface RazorpayPaymentResponse {
  razorpay_payment_id: string
  razorpay_order_id: string
  razorpay_signature: string
}
