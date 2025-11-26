/**
 * Unit tests for CartItem component
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '../utils/test-utils'
import CartItem from '../../components/CartItem'

describe('CartItem', () => {
  const mockCartItem = {
    id: 1,
    product: {
      id: 1,
      title: 'Test Product',
      images: [],
    },
    quantity: 2,
    unit_price: 100.0,
  }

  it('renders cart item information', () => {
    render(<CartItem item={mockCartItem} onUpdateQuantity={() => {}} onRemove={() => {}} />)
    
    expect(screen.getByText(mockCartItem.product.title)).toBeInTheDocument()
    expect(screen.getByText(`₹${mockCartItem.unit_price}`)).toBeInTheDocument()
  })

  it('displays correct quantity', () => {
    render(<CartItem item={mockCartItem} onUpdateQuantity={() => {}} onRemove={() => {}} />)
    
    const quantityInput = screen.getByRole('spinbutton')
    expect(quantityInput).toHaveValue(mockCartItem.quantity)
  })

  it('calls onUpdateQuantity when quantity is changed', () => {
    const onUpdateQuantity = vi.fn()
    
    render(<CartItem item={mockCartItem} onUpdateQuantity={onUpdateQuantity} onRemove={() => {}} />)
    
    const quantityInput = screen.getByRole('spinbutton')
    fireEvent.change(quantityInput, { target: { value: '3' } })
    
    expect(onUpdateQuantity).toHaveBeenCalledWith(mockCartItem.id, 3)
  })

  it('calls onRemove when remove button is clicked', () => {
    const onRemove = vi.fn()
    
    render(<CartItem item={mockCartItem} onUpdateQuantity={() => {}} onRemove={onRemove} />)
    
    const removeButton = screen.getByRole('button', { name: /remove/i })
    fireEvent.click(removeButton)
    
    expect(onRemove).toHaveBeenCalledWith(mockCartItem.id)
  })

  it('calculates and displays item total correctly', () => {
    render(<CartItem item={mockCartItem} onUpdateQuantity={() => {}} onRemove={() => {}} />)
    
    const expectedTotal = mockCartItem.quantity * mockCartItem.unit_price
    expect(screen.getByText(`₹${expectedTotal}`)).toBeInTheDocument()
  })
})
