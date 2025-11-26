import api from './api'

export interface DashboardMetrics {
  total_revenue: number
  order_count: number
  active_subscriptions: number
  low_stock_alerts: Array<{
    id: number
    title: string
    sku: string
    stock_quantity: number
  }>
}

export interface RevenueReport {
  start_date: string
  end_date: string
  total_revenue: number
  total_orders: number
  daily_data: Array<{
    date: string
    revenue: number
    order_count: number
  }>
}

export interface InventoryProduct {
  product_id: number
  title: string
  sku: string
  category_id: number
  stock_quantity: number
  consumer_price: number
  distributor_price: number
  is_low_stock: boolean
}

export interface InventoryStatus {
  products: InventoryProduct[]
}

export interface DeliveryCalendarItem {
  subscription_id: number
  user_id: number
  user_name: string
  product_id: number
  product_title: string
  delivery_date: string
  delivery_address: string
  status: string
}

export interface DeliveryCalendarResponse {
  deliveries: DeliveryCalendarItem[]
  total: number
  date_range: string
}

export interface AuditLogEntry {
  id: number
  actor_id: number | null
  action_type: string
  object_type: string
  object_id: number
  details: Record<string, any>
  ip_address: string | null
  created_at: string
}

export interface AuditLogsResponse {
  logs: AuditLogEntry[]
}

export const analyticsService = {
  /**
   * Get dashboard metrics
   */
  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    const response = await api.get<DashboardMetrics>('/api/v1/owner/analytics/dashboard')
    return response.data
  },

  /**
   * Get revenue report with optional date range
   */
  getRevenueReport: async (
    startDate?: string,
    endDate?: string
  ): Promise<RevenueReport> => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    
    const response = await api.get<RevenueReport>(
      `/api/v1/owner/analytics/revenue?${params.toString()}`
    )
    return response.data
  },

  /**
   * Get inventory status with optional category filter
   */
  getInventoryStatus: async (categoryId?: number): Promise<InventoryStatus> => {
    const params = categoryId ? `?category_id=${categoryId}` : ''
    const response = await api.get<InventoryStatus>(`/api/v1/owner/inventory${params}`)
    return response.data
  },

  /**
   * Get subscription delivery calendar
   */
  getDeliveryCalendar: async (
    startDate?: string,
    endDate?: string
  ): Promise<DeliveryCalendarResponse> => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    
    const response = await api.get<DeliveryCalendarResponse>(
      `/api/v1/owner/subscriptions/calendar?${params.toString()}`
    )
    return response.data
  },

  /**
   * Get audit logs with filtering
   */
  getAuditLogs: async (
    actionType?: string,
    startDate?: string,
    endDate?: string,
    actorId?: number,
    limit?: number
  ): Promise<AuditLogsResponse> => {
    const params = new URLSearchParams()
    if (actionType) params.append('action_type', actionType)
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    if (actorId) params.append('actor_id', actorId.toString())
    if (limit) params.append('limit', limit.toString())
    
    const response = await api.get<AuditLogsResponse>(
      `/api/v1/owner/analytics/audit-logs?${params.toString()}`
    )
    return response.data
  },
}
