import React from 'react'
import { OrderStatus } from '../types/order'

interface OrderStatusBadgeProps {
  status: OrderStatus
}

const OrderStatusBadge: React.FC<OrderStatusBadgeProps> = ({ status }) => {
  const getStatusConfig = (status: OrderStatus) => {
    const configs = {
      [OrderStatus.PENDING]: {
        label: 'Pending',
        className: 'bg-yellow-100 text-yellow-800',
      },
      [OrderStatus.CONFIRMED]: {
        label: 'Confirmed',
        className: 'bg-blue-100 text-blue-800',
      },
      [OrderStatus.PACKED]: {
        label: 'Packed',
        className: 'bg-purple-100 text-purple-800',
      },
      [OrderStatus.OUT_FOR_DELIVERY]: {
        label: 'Out for Delivery',
        className: 'bg-indigo-100 text-indigo-800',
      },
      [OrderStatus.DELIVERED]: {
        label: 'Delivered',
        className: 'bg-green-100 text-green-800',
      },
      [OrderStatus.CANCELLED]: {
        label: 'Cancelled',
        className: 'bg-red-100 text-red-800',
      },
    }
    return configs[status] || { label: status, className: 'bg-gray-100 text-gray-800' }
  }

  const config = getStatusConfig(status)

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.className}`}>
      {config.label}
    </span>
  )
}

export default OrderStatusBadge
