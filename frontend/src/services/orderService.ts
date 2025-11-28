import api from './api'
import {
  Order,
  CreateOrderRequest,
  CreateOrderResponse,
  RazorpayPaymentResponse,
} from '../types/order'

export const orderService = {
  /**
   * Create a new order from the cart
   */
  createOrder: async (data: CreateOrderRequest): Promise<CreateOrderResponse> => {
    const response = await api.post<CreateOrderResponse>('/api/v1/orders', data)
    return response.data
  },

  /**
   * Get all orders for the current user
   */
  getOrders: async (): Promise<Order[]> => {
    const response = await api.get<{ orders: Order[] }>('/api/v1/orders')
    return response.data.orders || []
  },

  /**
   * Get a specific order by ID
   */
  getOrderById: async (orderId: number): Promise<Order> => {
    const response = await api.get<Order>(`/api/v1/orders/${orderId}`)
    return response.data
  },

  /**
   * Verify payment after Razorpay callback
   */
  verifyPayment: async (
    orderId: number,
    paymentData: RazorpayPaymentResponse
  ): Promise<Order> => {
    const response = await api.post<Order>(`/api/v1/orders/${orderId}/verify-payment`, paymentData)
    return response.data
  },
}
