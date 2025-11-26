/**
 * Unit tests for ProductCard component
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '../utils/test-utils'
import ProductCard from '../../components/ProductCard'
import { mockProduct } from '../utils/test-utils'

describe('ProductCard', () => {
  it('renders product information correctly', () => {
    render(<ProductCard product={mockProduct} />)
    
    expect(screen.getByText(mockProduct.title)).toBeInTheDocument()
    expect(screen.getByText(mockProduct.description)).toBeInTheDocument()
    expect(screen.getByText(`₹${mockProduct.consumer_price}`)).toBeInTheDocument()
  })

  it('displays product image', () => {
    const productWithImage = {
      ...mockProduct,
      images: [{ id: 1, url: 'https://example.com/image.jpg', alt_text: 'Product image' }]
    }
    
    render(<ProductCard product={productWithImage} />)
    
    const image = screen.getByRole('img')
    expect(image).toHaveAttribute('src', productWithImage.images[0].url)
  })

  it('shows out of stock message when stock is 0', () => {
    const outOfStockProduct = { ...mockProduct, stock_quantity: 0 }
    
    render(<ProductCard product={outOfStockProduct} />)
    
    expect(screen.getByText(/out of stock/i)).toBeInTheDocument()
  })

  it('calls onAddToCart when add to cart button is clicked', () => {
    const onAddToCart = vi.fn()
    
    render(<ProductCard product={mockProduct} onAddToCart={onAddToCart} />)
    
    const addButton = screen.getByRole('button', { name: /add to cart/i })
    fireEvent.click(addButton)
    
    expect(onAddToCart).toHaveBeenCalledWith(mockProduct.id)
  })

  it('navigates to product detail when card is clicked', () => {
    render(<ProductCard product={mockProduct} />)
    
    const card = screen.getByTestId('product-card')
    fireEvent.click(card)
    
    // Check if navigation occurred (would need router mock)
    expect(window.location.pathname).toContain(`/products/${mockProduct.id}`)
  })
})
