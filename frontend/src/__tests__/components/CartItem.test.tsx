/**
 * Unit tests for CartItem component
 */
import { describe, it, expect } from 'vitest'
import { render, screen } from '../utils/test-utils'
import CartItem from '../../components/CartItem'

describe('CartItem', () => {
  const mockCartItem = {
    id: 1,
    cart_id: 1,
    product_id: 1,
    product: {
      id: 1,
      title: 'Test Product',
      sku: 'TEST-001',
      unit_size: '1 Unit',
      stock_quantity: 50,
      images: [],
    },
    quantity: 2,
    unit_price: 100.0,
    created_at: new Date().toISOString(),
  }

  it('renders cart item information', () => {
    render(<CartItem item={mockCartItem} />)
    
    expect(screen.getByText(mockCartItem.product.title)).toBeInTheDocument()
    expect(screen.getByText(/₹100\.00 each/i)).toBeInTheDocument()
  })

  it('displays correct quantity', () => {
    render(<CartItem item={mockCartItem} />)
    
    expect(screen.getByText(mockCartItem.quantity.toString())).toBeInTheDocument()
  })

  it('displays quantity controls', () => {
    render(<CartItem item={mockCartItem} />)
    
    expect(screen.getByLabelText('Decrease quantity')).toBeInTheDocument()
    expect(screen.getByLabelText('Increase quantity')).toBeInTheDocument()
  })

  it('displays remove button', () => {
    render(<CartItem item={mockCartItem} />)
    
    const removeButton = screen.getByRole('button', { name: /remove/i })
    expect(removeButton).toBeInTheDocument()
  })

  it('calculates and displays item total correctly', () => {
    render(<CartItem item={mockCartItem} />)
    
    const expectedTotal = (mockCartItem.quantity * mockCartItem.unit_price).toFixed(2)
    expect(screen.getByText(`₹${expectedTotal}`)).toBeInTheDocument()
  })

  it('displays out of stock warning when quantity exceeds stock', () => {
    const outOfStockItem = {
      ...mockCartItem,
      quantity: 100,
      product: {
        ...mockCartItem.product,
        stock_quantity: 5,
      },
    }
    
    render(<CartItem item={outOfStockItem} />)
    
    expect(screen.getByText(/only 5 items available/i)).toBeInTheDocument()
  })
})
