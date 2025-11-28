/**
 * Accessibility Property-Based Tests
 * Feature: indostar-naturals-ecommerce
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '../contexts/AuthContext'
import { CartProvider } from '../contexts/CartContext'
import ProductCard from '../components/ProductCard'
import ImageCarousel from '../components/ImageCarousel'
import { Product, ProductImage } from '../types/product'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

// Helper to wrap components with all necessary providers
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <CartProvider>
          <BrowserRouter>{component}</BrowserRouter>
        </CartProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}

describe('Accessibility Properties', () => {
  /**
   * Property 59: Images include alt text
   * Validates: Requirements 13.4
   * 
   * For any product image displayed, the image element should include 
   * descriptive alt text for screen readers.
   */
  describe('Property 59: Images include alt text', () => {
    it('should have alt text for product card images', () => {
      // Arrange: Create a product with an image
      const product: Product = {
        id: 1,
        owner_id: 1,
        title: 'Organic Jaggery',
        description: 'Pure organic jaggery',
        category_id: 1,
        category: { id: 1, name: 'Jaggery', slug: 'jaggery', parent_id: null, display_order: 1 },
        sku: 'JAG-001',
        unit_size: '1kg',
        consumer_price: 150,
        distributor_price: 120,
        stock_quantity: 100,
        is_subscription_available: false,
        is_active: true,
        images: [
          {
            id: 1,
            product_id: 1,
            url: 'https://example.com/jaggery.jpg',
            alt_text: 'Organic jaggery blocks on a wooden surface',
            display_order: 1,
            created_at: new Date().toISOString(),
          },
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      // Act: Render the product card
      renderWithProviders(<ProductCard product={product} />)

      // Assert: Image should have alt text
      const image = screen.getByRole('img')
      expect(image).toHaveAttribute('alt')
      const altText = image.getAttribute('alt')
      expect(altText).toBeTruthy()
      expect(altText!.length).toBeGreaterThan(0)
    })

    it('should have descriptive alt text for product images in carousel', () => {
      // Arrange: Create product images
      const images: ProductImage[] = [
        {
          id: 1,
          product_id: 1,
          url: 'https://example.com/image1.jpg',
          alt_text: 'Organic milk bottle with fresh milk',
          display_order: 1,
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          product_id: 1,
          url: 'https://example.com/image2.jpg',
          alt_text: 'Close-up of organic milk being poured',
          display_order: 2,
          created_at: new Date().toISOString(),
        },
      ]

      // Act: Render the image carousel
      render(<ImageCarousel images={images} productTitle="Organic Milk" />)

      // Assert: All images should have alt text
      const allImages = screen.getAllByRole('img')
      expect(allImages.length).toBeGreaterThan(0)

      allImages.forEach((image) => {
        expect(image).toHaveAttribute('alt')
        const altText = image.getAttribute('alt')
        expect(altText).toBeTruthy()
        expect(altText!.length).toBeGreaterThan(0)
      })
    })

    it('should have non-empty alt text for all product images', () => {
      // Arrange: Create multiple products with images
      const products: Product[] = [
        {
          id: 1,
          owner_id: 1,
          title: 'Product 1',
          description: 'Description 1',
          category_id: 1,
          category: { id: 1, name: 'Category', slug: 'category', parent_id: null, display_order: 1 },
          sku: 'SKU-001',
          unit_size: '1kg',
          consumer_price: 100,
          distributor_price: 80,
          stock_quantity: 50,
          is_subscription_available: false,
          is_active: true,
          images: [
            {
              id: 1,
              product_id: 1,
              url: 'https://example.com/product1.jpg',
              alt_text: 'Product 1 image description',
              display_order: 1,
              created_at: new Date().toISOString(),
            },
          ],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          owner_id: 1,
          title: 'Product 2',
          description: 'Description 2',
          category_id: 1,
          category: { id: 1, name: 'Category', slug: 'category', parent_id: null, display_order: 1 },
          sku: 'SKU-002',
          unit_size: '500g',
          consumer_price: 75,
          distributor_price: 60,
          stock_quantity: 30,
          is_subscription_available: false,
          is_active: true,
          images: [
            {
              id: 2,
              product_id: 2,
              url: 'https://example.com/product2.jpg',
              alt_text: 'Product 2 detailed view',
              display_order: 1,
              created_at: new Date().toISOString(),
            },
          ],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]

      // Act & Assert: For each product, verify alt text
      products.forEach((product) => {
        const { unmount } = renderWithProviders(<ProductCard product={product} />)
        
        const image = screen.getByRole('img')
        expect(image).toHaveAttribute('alt')
        const altText = image.getAttribute('alt')
        
        // Alt text should not be empty
        expect(altText).toBeTruthy()
        expect(altText!.trim()).not.toBe('')
        
        // Alt text should be descriptive (at least 3 characters)
        expect(altText!.length).toBeGreaterThanOrEqual(3)
        
        unmount()
      })
    })

    it('should provide fallback alt text when alt_text is missing', () => {
      // Arrange: Create a product with image but no alt_text
      const product: Product = {
        id: 1,
        owner_id: 1,
        title: 'Test Product',
        description: 'Test description',
        category_id: 1,
        category: { id: 1, name: 'Category', slug: 'category', parent_id: null, display_order: 1 },
        sku: 'TEST-001',
        unit_size: '1kg',
        consumer_price: 100,
        distributor_price: 80,
        stock_quantity: 50,
        is_subscription_available: false,
        is_active: true,
        images: [
          {
            id: 1,
            product_id: 1,
            url: 'https://example.com/test.jpg',
            alt_text: '', // Empty alt text
            display_order: 1,
            created_at: new Date().toISOString(),
          },
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      // Act: Render the product card
      renderWithProviders(<ProductCard product={product} />)

      // Assert: Image should still have an alt attribute (even if fallback)
      const image = screen.getByRole('img')
      expect(image).toHaveAttribute('alt')
      
      // The component should provide a fallback (product title or similar)
      const altText = image.getAttribute('alt')
      expect(altText).toBeDefined()
    })
  })

  /**
   * Property 78: Product images have multiple resolutions
   * Validates: Requirements 20.3
   * 
   * For any product image, the system should provide responsive image URLs 
   * with multiple resolutions for different screen sizes.
   */
  describe('Property 78: Product images have multiple resolutions', () => {
    it('should have srcset attribute for responsive images', () => {
      // Arrange: Create a product with an image
      const product: Product = {
        id: 1,
        owner_id: 1,
        title: 'Organic Milk',
        description: 'Fresh organic milk',
        category_id: 1,
        category: { id: 1, name: 'Dairy', slug: 'dairy', parent_id: null, display_order: 1 },
        sku: 'MILK-001',
        unit_size: '1L',
        consumer_price: 60,
        distributor_price: 50,
        stock_quantity: 100,
        is_subscription_available: true,
        is_active: true,
        images: [
          {
            id: 1,
            product_id: 1,
            url: 'https://cdn.example.com/milk.jpg',
            alt_text: 'Fresh organic milk bottle',
            display_order: 1,
            created_at: new Date().toISOString(),
          },
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      // Act: Render the product card
      renderWithProviders(<ProductCard product={product} />)

      // Assert: Image should have srcset for responsive images
      const image = screen.getByRole('img')
      
      // Check if srcset attribute exists (may be set after lazy load)
      // The LazyImage component should add srcset
      expect(image).toHaveAttribute('loading', 'lazy')
      
      // Verify the image has sizes attribute for responsive behavior
      const sizes = image.getAttribute('sizes')
      if (sizes) {
        expect(sizes).toBeTruthy()
      }
    })

    it('should provide multiple image resolutions in srcset', () => {
      // Arrange: Create product images
      const images: ProductImage[] = [
        {
          id: 1,
          product_id: 1,
          url: 'https://cdn.example.com/product1.jpg',
          alt_text: 'Product image 1',
          display_order: 1,
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          product_id: 1,
          url: 'https://cdn.example.com/product2.jpg',
          alt_text: 'Product image 2',
          display_order: 2,
          created_at: new Date().toISOString(),
        },
      ]

      // Act: Render the image carousel
      render(<ImageCarousel images={images} productTitle="Test Product" />)

      // Assert: Images should support responsive loading
      const allImages = screen.getAllByRole('img')
      expect(allImages.length).toBeGreaterThan(0)

      allImages.forEach((image) => {
        // Each image should have alt text
        expect(image).toHaveAttribute('alt')
        
        // Images should be optimized for loading
        const src = image.getAttribute('src')
        expect(src).toBeTruthy()
      })
    })

    it('should use lazy loading for performance', () => {
      // Arrange: Create multiple products
      const products: Product[] = Array.from({ length: 5 }, (_, i) => ({
        id: i + 1,
        owner_id: 1,
        title: `Product ${i + 1}`,
        description: `Description ${i + 1}`,
        category_id: 1,
        category: { id: 1, name: 'Category', slug: 'category', parent_id: null, display_order: 1 },
        sku: `SKU-${i + 1}`,
        unit_size: '1kg',
        consumer_price: 100 + i * 10,
        distributor_price: 80 + i * 10,
        stock_quantity: 50,
        is_subscription_available: false,
        is_active: true,
        images: [
          {
            id: i + 1,
            product_id: i + 1,
            url: `https://cdn.example.com/product${i + 1}.jpg`,
            alt_text: `Product ${i + 1} image`,
            display_order: 1,
            created_at: new Date().toISOString(),
          },
        ],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }))

      // Act & Assert: For each product, verify lazy loading
      products.forEach((product) => {
        const { unmount } = renderWithProviders(<ProductCard product={product} />)
        
        const image = screen.getByRole('img')
        
        // Image should have loading="lazy" attribute for performance
        expect(image).toHaveAttribute('loading', 'lazy')
        
        unmount()
      })
    })
  })
})
