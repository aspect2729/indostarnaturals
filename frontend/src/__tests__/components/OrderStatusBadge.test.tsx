/**
 * Unit tests for OrderStatusBadge component
 */
import { describe, it, expect } from 'vitest'
import { render, screen } from '../utils/test-utils'
import OrderStatusBadge from '../../components/OrderStatusBadge'
import { OrderStatus } from '../../types/order'

describe('OrderStatusBadge', () => {
  it('renders pending status correctly', () => {
    render(<OrderStatusBadge status={OrderStatus.PENDING} />)
    
    expect(screen.getByText(/pending/i)).toBeInTheDocument()
    expect(screen.getByText(/pending/i)).toHaveClass('bg-yellow-100')
  })

  it('renders confirmed status correctly', () => {
    render(<OrderStatusBadge status={OrderStatus.CONFIRMED} />)
    
    expect(screen.getByText(/confirmed/i)).toBeInTheDocument()
    expect(screen.getByText(/confirmed/i)).toHaveClass('bg-blue-100')
  })

  it('renders delivered status correctly', () => {
    render(<OrderStatusBadge status={OrderStatus.DELIVERED} />)
    
    expect(screen.getByText(/delivered/i)).toBeInTheDocument()
    expect(screen.getByText(/delivered/i)).toHaveClass('bg-green-100')
  })

  it('renders cancelled status correctly', () => {
    render(<OrderStatusBadge status={OrderStatus.CANCELLED} />)
    
    expect(screen.getByText(/cancelled/i)).toBeInTheDocument()
    expect(screen.getByText(/cancelled/i)).toHaveClass('bg-red-100')
  })
})
