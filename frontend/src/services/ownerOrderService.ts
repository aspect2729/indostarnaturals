import api from './api'
import { OrderStatus, PaymentStatus } from '../types/order'
import { UserRole } from '../types/user'

export interface OrderItemResponse {
  id: number
  order_id: number
  product_id: number
  quantity: number
  unit_price: number
  total_price: number
  product_title: string
  product_sku: string
}

export interface AddressResponse {
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

export interface OrderWithUser {
  id: number
  user_id: number
  user_name: string
  user_email: string | null
  user_phone: string
  user_role: string
  order_number: string
  total_amount: number
  discount_amount: number
  final_amount: number
  payment_status: PaymentStatus
  order_status: OrderStatus
  delivery_address: AddressResponse
  items: OrderItemResponse[]
  notes: string | null
  created_at: string
  updated_at: string
}

export interface OwnerOrderListResponse {
  orders: OrderWithUser[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface OrderFilters {
  page?: number
  page_size?: number
  status_filter?: OrderStatus
  user_role_filter?: UserRole
  start_date?: string
  end_date?: string
}

export interface OrderStatusUpdate {
  status: OrderStatus
}

export const ownerOrderService = {
  /**
   * Get all orders with filtering (owner only)
   */
  getAllOrders: async (filters?: OrderFilters): Promise<OwnerOrderListResponse> => {
    const params = new URLSearchParams()
    
    if (filters?.page) params.append('page', filters.page.toString())
    if (filters?.page_size) params.append('page_size', filters.page_size.toString())
    if (filters?.status_filter) params.append('status_filter', filters.status_filter)
    if (filters?.user_role_filter) params.append('user_role_filter', filters.user_role_filter)
    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)
    
    const response = await api.get<OwnerOrderListResponse>(
      `/api/v1/owner/orders?${params.toString()}`
    )
    return response.data
  },

  /**
   * Update order status (owner only)
   */
  updateOrderStatus: async (
    orderId: number,
    statusUpdate: OrderStatusUpdate
  ): Promise<OrderWithUser> => {
    const response = await api.put<OrderWithUser>(
      `/api/v1/owner/orders/${orderId}/status`,
      statusUpdate
    )
    return response.data
  },

  /**
   * Process refund for an order (owner only)
   */
  processRefund: async (orderId: number): Promise<OrderWithUser> => {
    const response = await api.post<OrderWithUser>(
      `/api/v1/owner/orders/${orderId}/refund`
    )
    return response.data
  },
}
