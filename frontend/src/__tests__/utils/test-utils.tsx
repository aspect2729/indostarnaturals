/**
 * Test utilities for rendering components with providers
 */
import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '../../contexts/AuthContext'
import { CartProvider } from '../../contexts/CartContext'

// Create a new QueryClient for each test
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

interface AllTheProvidersProps {
  children: React.ReactNode
}

const AllTheProviders = ({ children }: AllTheProvidersProps) => {
  const queryClient = createTestQueryClient()

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <CartProvider>{children}</CartProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

const customRender = (ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) =>
  render(ui, { wrapper: AllTheProviders, ...options })

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }

// Mock user for testing
export const mockUser = {
  id: 1,
  email: 'test@example.com',
  phone: '+919876543210',
  name: 'Test User',
  role: 'consumer' as const,
  is_active: true,
  is_email_verified: true,
  is_phone_verified: true,
}

// Mock product for testing
export const mockProduct = {
  id: 1,
  title: 'Test Product',
  description: 'Test Description',
  consumer_price: 100.0,
  distributor_price: 80.0,
  stock_quantity: 50,
  sku: 'TEST-001',
  unit_size: '1 Unit',
  is_active: true,
  is_subscription_available: false,
  images: [],
  category: {
    id: 1,
    name: 'Test Category',
    slug: 'test-category',
  },
}

// Mock cart for testing
export const mockCart = {
  id: 1,
  items: [],
  discount_amount: 0,
  total_amount: 0,
}

// Mock order for testing
export const mockOrder = {
  id: 1,
  order_number: 'ORD-20240115-001',
  total_amount: 100.0,
  discount_amount: 0,
  final_amount: 100.0,
  order_status: 'pending' as const,
  payment_status: 'pending' as const,
  created_at: new Date().toISOString(),
  items: [],
}

// Helper to wait for async updates
export const waitForLoadingToFinish = () =>
  new Promise((resolve) => setTimeout(resolve, 0))
