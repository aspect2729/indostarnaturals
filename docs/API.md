# API Documentation

This document provides comprehensive documentation for the IndoStar Naturals API.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.indostarnaturals.com`

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

1. Send OTP: `POST /api/v1/auth/send-otp`
2. Verify OTP: `POST /api/v1/auth/verify-otp` (returns JWT token)

## API Endpoints

### Authentication

#### Send OTP
```http
POST /api/v1/auth/send-otp
Content-Type: application/json

{
  "phone": "+919876543210",
  "email": "user@example.com"  // optional
}
```

**Response**:
```json
{
  "message": "OTP sent successfully",
  "expires_in": 600
}
```

#### Verify OTP
```http
POST /api/v1/auth/verify-otp
Content-Type: application/json

{
  "phone": "+919876543210",
  "otp": "123456"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "phone": "+919876543210",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "consumer"
  }
}
```

#### Google OAuth
```http
POST /api/v1/auth/google
Content-Type: application/json

{
  "token": "google_oauth_token"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Reset Password
```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

```http
PUT /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "reset_token",
  "new_password": "newpassword123"
}
```

### User Management

#### Get Current User
```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 1,
  "phone": "+919876543210",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "consumer",
  "is_email_verified": true,
  "is_phone_verified": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Update User Profile
```http
PUT /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Doe Updated",
  "email": "newemail@example.com"
}
```

#### Get User Addresses
```http
GET /api/v1/users/me/addresses
Authorization: Bearer <token>
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "phone": "+919876543210",
    "address_line1": "123 Main St",
    "address_line2": "Apt 4B",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "country": "India",
    "is_default": true
  }
]
```

#### Add Address
```http
POST /api/v1/users/me/addresses
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Doe",
  "phone": "+919876543210",
  "address_line1": "123 Main St",
  "address_line2": "Apt 4B",
  "city": "Mumbai",
  "state": "Maharashtra",
  "postal_code": "400001",
  "country": "India",
  "is_default": false
}
```

### Products

#### List Products
```http
GET /api/v1/products?page=1&limit=20&category_id=1&sort=price_asc
Authorization: Bearer <token>
```

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `category_id`: Filter by category
- `sort`: Sort order (price_asc, price_desc, name_asc, name_desc)
- `search`: Search query

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Organic Jaggery",
      "description": "Pure organic jaggery from sugarcane",
      "sku": "JAG-001",
      "unit_size": "1kg",
      "price": 150.00,
      "stock_quantity": 100,
      "is_subscription_available": false,
      "images": [
        {
          "id": 1,
          "url": "https://cdn.example.com/jaggery.jpg",
          "alt_text": "Organic Jaggery",
          "display_order": 1
        }
      ],
      "category": {
        "id": 1,
        "name": "Jaggery",
        "slug": "jaggery"
      }
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

#### Get Product Details
```http
GET /api/v1/products/1
Authorization: Bearer <token>
```

#### Search Products
```http
GET /api/v1/products/search?q=jaggery
Authorization: Bearer <token>
```

#### Get Categories
```http
GET /api/v1/categories
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "Jaggery",
    "slug": "jaggery",
    "parent_id": null,
    "display_order": 1
  },
  {
    "id": 2,
    "name": "Milk Products",
    "slug": "milk-products",
    "parent_id": null,
    "display_order": 2
  }
]
```

### Shopping Cart

#### Get Cart
```http
GET /api/v1/cart
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "title": "Organic Jaggery",
        "sku": "JAG-001",
        "images": [...]
      },
      "quantity": 2,
      "unit_price": 150.00,
      "total_price": 300.00
    }
  ],
  "subtotal": 300.00,
  "discount_amount": 30.00,
  "total": 270.00,
  "coupon_code": "SAVE10"
}
```

#### Add Item to Cart
```http
POST /api/v1/cart/items
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

#### Update Cart Item
```http
PUT /api/v1/cart/items/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "quantity": 3
}
```

#### Remove Cart Item
```http
DELETE /api/v1/cart/items/1
Authorization: Bearer <token>
```

#### Apply Coupon
```http
POST /api/v1/cart/coupon
Authorization: Bearer <token>
Content-Type: application/json

{
  "coupon_code": "SAVE10"
}
```

#### Remove Coupon
```http
DELETE /api/v1/cart/coupon
Authorization: Bearer <token>
```

### Orders

#### Create Order
```http
POST /api/v1/orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "delivery_address_id": 1,
  "notes": "Please deliver in the morning"
}
```

**Response**:
```json
{
  "order": {
    "id": 1,
    "order_number": "ORD-2024-0001",
    "total_amount": 300.00,
    "discount_amount": 30.00,
    "final_amount": 270.00,
    "payment_status": "pending",
    "order_status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "razorpay_order": {
    "id": "order_xyz123",
    "amount": 27000,
    "currency": "INR"
  }
}
```

#### Get User Orders
```http
GET /api/v1/orders?page=1&limit=10
Authorization: Bearer <token>
```

#### Get Order Details
```http
GET /api/v1/orders/1
Authorization: Bearer <token>
```

**Response**:
```json
{
  "id": 1,
  "order_number": "ORD-2024-0001",
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "title": "Organic Jaggery",
        "sku": "JAG-001"
      },
      "quantity": 2,
      "unit_price": 150.00,
      "total_price": 300.00
    }
  ],
  "total_amount": 300.00,
  "discount_amount": 30.00,
  "final_amount": 270.00,
  "payment_status": "paid",
  "order_status": "confirmed",
  "delivery_address": {
    "name": "John Doe",
    "phone": "+919876543210",
    "address_line1": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### Subscriptions

#### Create Subscription
```http
POST /api/v1/subscriptions
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": 2,
  "plan_frequency": "daily",
  "start_date": "2024-01-20",
  "delivery_address_id": 1
}
```

**Response**:
```json
{
  "subscription": {
    "id": 1,
    "product": {
      "id": 2,
      "title": "Fresh Milk",
      "unit_size": "1L"
    },
    "plan_frequency": "daily",
    "start_date": "2024-01-20",
    "next_delivery_date": "2024-01-20",
    "status": "active",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "razorpay_subscription": {
    "id": "sub_xyz123",
    "status": "active"
  }
}
```

#### Get User Subscriptions
```http
GET /api/v1/subscriptions
Authorization: Bearer <token>
```

#### Get Subscription Details
```http
GET /api/v1/subscriptions/1
Authorization: Bearer <token>
```

#### Pause Subscription
```http
PUT /api/v1/subscriptions/1/pause
Authorization: Bearer <token>
```

#### Resume Subscription
```http
PUT /api/v1/subscriptions/1/resume
Authorization: Bearer <token>
```

#### Cancel Subscription
```http
DELETE /api/v1/subscriptions/1
Authorization: Bearer <token>
```

### Owner Endpoints

All owner endpoints require the user to have the "owner" role.

#### Product Management

##### Create Product
```http
POST /api/v1/owner/products
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Organic Jaggery",
  "description": "Pure organic jaggery from sugarcane",
  "category_id": 1,
  "sku": "JAG-001",
  "unit_size": "1kg",
  "consumer_price": 150.00,
  "distributor_price": 120.00,
  "stock_quantity": 100,
  "is_subscription_available": false
}
```

##### Update Product
```http
PUT /api/v1/owner/products/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Organic Jaggery Updated",
  "consumer_price": 160.00
}
```

##### Delete Product
```http
DELETE /api/v1/owner/products/1
Authorization: Bearer <token>
```

##### Upload Product Image
```http
POST /api/v1/owner/products/1/images
Authorization: Bearer <token>
Content-Type: multipart/form-data

image: <file>
alt_text: "Organic Jaggery"
display_order: 1
```

##### Update Stock
```http
PUT /api/v1/owner/products/1/stock
Authorization: Bearer <token>
Content-Type: application/json

{
  "quantity_delta": -10  // Reduce by 10 or +10 to add
}
```

#### Order Management

##### List All Orders
```http
GET /api/v1/owner/orders?status=pending&page=1&limit=20
Authorization: Bearer <token>
```

##### Update Order Status
```http
PUT /api/v1/owner/orders/1/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "confirmed"
}
```

**Valid statuses**: pending, confirmed, packed, out_for_delivery, delivered, cancelled, refunded

##### Process Refund
```http
POST /api/v1/owner/orders/1/refund
Authorization: Bearer <token>
Content-Type: application/json

{
  "reason": "Customer requested refund"
}
```

#### User Management

##### List Users
```http
GET /api/v1/owner/users?role=distributor&page=1&limit=20
Authorization: Bearer <token>
```

##### Update User Role
```http
PUT /api/v1/owner/users/1/role
Authorization: Bearer <token>
Content-Type: application/json

{
  "role": "distributor"
}
```

#### Analytics

##### Dashboard Metrics
```http
GET /api/v1/owner/analytics/dashboard
Authorization: Bearer <token>
```

**Response**:
```json
{
  "total_revenue": 150000.00,
  "order_count": 250,
  "active_subscriptions": 45,
  "low_stock_products": 5,
  "revenue_trend": [
    {"date": "2024-01-01", "revenue": 5000.00},
    {"date": "2024-01-02", "revenue": 6000.00}
  ]
}
```

##### Revenue Report
```http
GET /api/v1/owner/analytics/revenue?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

##### Inventory Status
```http
GET /api/v1/owner/inventory?category_id=1
Authorization: Bearer <token>
```

#### Audit Logs

##### View Audit Logs
```http
GET /api/v1/owner/audit-logs?action_type=PRICE_UPDATED&page=1&limit=20
Authorization: Bearer <token>
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "request_id": "abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

## Rate Limiting

Authentication endpoints are rate-limited to 5 attempts per 15 minutes per IP address.

## Webhooks

### Razorpay Webhook

```http
POST /api/v1/webhooks/razorpay
X-Razorpay-Signature: <signature>
Content-Type: application/json

{
  "event": "payment.captured",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_xyz123",
        "order_id": "order_abc456",
        "amount": 27000,
        "status": "captured"
      }
    }
  }
}
```

## Pagination

All list endpoints support pagination:

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response Format**:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5
}
```

## Filtering and Sorting

Many endpoints support filtering and sorting:

**Example**:
```http
GET /api/v1/products?category_id=1&sort=price_asc&min_price=100&max_price=500
```

## Interactive API Documentation

Visit the following URLs when the backend is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.
