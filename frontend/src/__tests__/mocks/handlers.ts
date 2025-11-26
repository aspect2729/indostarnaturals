/**
 * MSW (Mock Service Worker) handlers for API mocking in tests
 */
import { http, HttpResponse } from 'msw'

const API_BASE_URL = 'http://localhost:8000/api/v1'

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE_URL}/auth/send-otp`, () => {
    return HttpResponse.json({ message: 'OTP sent successfully' })
  }),

  http.post(`${API_BASE_URL}/auth/verify-otp`, () => {
    return HttpResponse.json({
      access_token: 'mock_access_token',
      refresh_token: 'mock_refresh_token',
      token_type: 'bearer',
      user: {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        role: 'consumer',
      },
    })
  }),

  http.post(`${API_BASE_URL}/auth/refresh`, () => {
    return HttpResponse.json({
      access_token: 'new_mock_access_token',
      token_type: 'bearer',
    })
  }),

  // User endpoints
  http.get(`${API_BASE_URL}/users/me`, () => {
    return HttpResponse.json({
      id: 1,
      email: 'test@example.com',
      phone: '+919876543210',
      name: 'Test User',
      role: 'consumer',
      is_active: true,
    })
  }),

  http.get(`${API_BASE_URL}/users/me/addresses`, () => {
    return HttpResponse.json([
      {
        id: 1,
        name: 'Test User',
        phone: '+919876543210',
        address_line1: '123 Test Street',
        city: 'Test City',
        state: 'Test State',
        postal_code: '123456',
        country: 'India',
        is_default: true,
      },
    ])
  }),

  // Product endpoints
  http.get(`${API_BASE_URL}/products`, () => {
    return HttpResponse.json({
      items: [
        {
          id: 1,
          title: 'Test Product',
          description: 'Test Description',
          consumer_price: 100.0,
          distributor_price: 80.0,
          stock_quantity: 50,
          images: [],
        },
      ],
      total: 1,
      page: 1,
      size: 20,
      pages: 1,
    })
  }),

  http.get(`${API_BASE_URL}/products/:id`, ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      title: 'Test Product',
      description: 'Test Description',
      consumer_price: 100.0,
      distributor_price: 80.0,
      stock_quantity: 50,
      images: [],
      category: {
        id: 1,
        name: 'Test Category',
      },
    })
  }),

  // Cart endpoints
  http.get(`${API_BASE_URL}/cart`, () => {
    return HttpResponse.json({
      id: 1,
      items: [],
      discount_amount: 0,
      total_amount: 0,
    })
  }),

  http.post(`${API_BASE_URL}/cart/items`, () => {
    return HttpResponse.json({
      id: 1,
      items: [
        {
          id: 1,
          product_id: 1,
          quantity: 1,
          unit_price: 100.0,
        },
      ],
      discount_amount: 0,
      total_amount: 100.0,
    })
  }),

  // Order endpoints
  http.get(`${API_BASE_URL}/orders`, () => {
    return HttpResponse.json({
      items: [
        {
          id: 1,
          order_number: 'ORD-20240115-001',
          total_amount: 100.0,
          order_status: 'pending',
          payment_status: 'pending',
          created_at: new Date().toISOString(),
        },
      ],
      total: 1,
      page: 1,
      size: 20,
      pages: 1,
    })
  }),

  http.post(`${API_BASE_URL}/orders`, () => {
    return HttpResponse.json({
      id: 1,
      order_number: 'ORD-20240115-001',
      razorpay_order_id: 'order_test123',
      amount: 100.0,
    })
  }),

  // Subscription endpoints
  http.get(`${API_BASE_URL}/subscriptions`, () => {
    return HttpResponse.json([
      {
        id: 1,
        product: {
          id: 1,
          title: 'Test Product',
        },
        plan_frequency: 'daily',
        status: 'active',
        next_delivery_date: new Date().toISOString(),
      },
    ])
  }),

  // Error responses
  http.get(`${API_BASE_URL}/error/400`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Validation failed',
          details: [{ field: 'email', message: 'Invalid email format' }],
        },
      },
      { status: 400 }
    )
  }),

  http.get(`${API_BASE_URL}/error/401`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'UNAUTHORIZED',
          message: 'Authentication required',
        },
      },
      { status: 401 }
    )
  }),

  http.get(`${API_BASE_URL}/error/403`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'FORBIDDEN',
          message: 'Insufficient permissions',
        },
      },
      { status: 403 }
    )
  }),

  http.get(`${API_BASE_URL}/error/500`, () => {
    return HttpResponse.json(
      {
        error: {
          code: 'INTERNAL_SERVER_ERROR',
          message: 'An unexpected error occurred',
        },
      },
      { status: 500 }
    )
  }),
]
