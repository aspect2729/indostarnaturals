# Implementation Plan

- [x] 1. Project Setup and Infrastructure




- [x] 1.1 Initialize backend project structure


  - Create FastAPI project with Python 3.11+
  - Set up virtual environment and dependencies (FastAPI, SQLAlchemy, Alembic, Pydantic, python-jose, passlib, celery, redis)
  - Configure project structure: app/, models/, services/, api/, schemas/, core/
  - Set up environment variable management with python-dotenv
  - Create Docker and docker-compose.yml for local development
  - _Requirements: 19.1, 19.2_

- [x] 1.2 Initialize frontend project structure


  - Create React + TypeScript project with Vite
  - Install dependencies (React Router, Axios, React Query, Formik, Yup, Tailwind CSS)
  - Configure Tailwind CSS with custom theme
  - Set up project structure: components/, pages/, contexts/, hooks/, services/, utils/
  - Configure TypeScript strict mode
  - _Requirements: 13.1, 13.2_

- [x] 1.3 Set up database and migrations


  - Configure PostgreSQL connection with SQLAlchemy
  - Initialize Alembic for database migrations
  - Create initial migration with system roles table
  - Create migration for initial owner account
  - Set up Redis connection for caching and Celery
  - _Requirements: 3.6, 19.2_

- [x] 1.4 Configure CI/CD pipeline


  - Create GitHub Actions workflow for linting (flake8, black, eslint, prettier)
  - Add workflow steps for running tests
  - Add workflow for building Docker images
  - Configure deployment to staging on main branch
  - _Requirements: 19.3_


- [-] 2. Core Data Models and Database Schema


- [x] 2.1 Create User and Address models




  - Implement User model with role enum (consumer, distributor, owner)
  - Implement Address model with all required fields
  - Create database migration for users and addresses tables
  - Add indexes on user email and phone fields
  - _Requirements: 2.1, 6.2_

- [x] 2.2 Write property test for user role assignment



  - **Property 5: User creation assigns single role**
  - **Validates: Requirements 2.1**

- [x] 2.3 Create Product and Category models




  - Implement Category model with hierarchical support
  - Implement Product model with dual pricing (consumer and distributor)
  - Implement ProductImage model with display order
  - Create database migration for categories, products, and product_images tables
  - Add indexes on product category_id, sku, and is_active fields
  - Add full-text search index on product title and description
  - _Requirements: 3.1, 3.4, 4.2, 4.3_
-

- [x] 2.4 Write property test for dual pricing storage




  - **Property 14: Dual pricing stored and retrieved by role**
  - **Validates: Requirements 3.4**

- [x] 2.5 Create Cart models





  - Implement Cart model with coupon support
  - Implement CartItem model with locked unit price
  - Create database migration for carts and cart_items tables
  - Add indexes on cart user_id and cart_item cart_id
  - _Requirements: 5.1, 5.3_

- [x] 2.6 Write property test for cart persistence




  - **Property 21: Cart additions persist**
  - **Validates: Requirements 5.1**

- [x] 2.7 Create Order models





  - Implement Order model with status enums
  - Implement OrderItem model
  - Create database migration for orders and order_items tables
  - Add indexes on order user_id, order_status, and created_at
  - _Requirements: 6.1, 8.1, 8.2_
-

- [x] 2.8 Write property test for order initial status




  - **Property 40: New orders start as pending**
  - **Validates: Requirements 8.1**

- [x] 2.9 Create Subscription and Payment models







  - Implement Subscription model with frequency enum
  - Implement Payment model with Razorpay fields
  - Create database migration for subscriptions and payments tables
  - Add indexes on subscription user_id and status
  - _Requirements: 7.2, 7.3, 6.3_

- [x] 2.10 Create AuditLog model




  - Implement AuditLog model with JSON details field
  - Create database migration for audit_logs table
  - Add indexes on actor_id, action_type, and created_at
  - _Requirements: 15.1, 15.2, 15.3_


- [x] 3. Authentication and Authorization




- [x] 3.1 Implement JWT token service


  - Create functions for generating and verifying JWT tokens
  - Implement token refresh logic
  - Add token expiration handling (1 hour for access, 7 days for refresh)
  - _Requirements: 1.2, 1.4_

- [x] 3.2 Write property test for JWT token generation


  - **Property 1: OTP verification issues JWT**
  - **Validates: Requirements 1.2**

- [x] 3.3 Implement password hashing service


  - Create functions for hashing passwords with bcrypt (cost factor 12)
  - Create function for verifying passwords
  - _Requirements: 12.1_

- [x] 3.4 Write property test for password hashing



  - **Property 56: Passwords hashed with bcrypt**
  - **Validates: Requirements 12.1**

- [x] 3.5 Implement OTP service


  - Create function to generate 6-digit OTP codes
  - Store OTP in Redis with 10-minute expiration
  - Integrate with SMS provider (Twilio or MSG91) for sending OTP
  - Create function to verify OTP
  - _Requirements: 1.1, 1.2_

- [x] 3.6 Implement email verification service


  - Create function to generate email verification tokens
  - Store tokens in database with 24-hour expiration
  - Integrate with email provider (SendGrid or AWS SES)
  - Create function to verify email tokens
  - _Requirements: 1.3, 1.4_

- [x] 3.7 Write property test for email verification


  - **Property 2: Email verification marks account verified**
  - **Validates: Requirements 1.4**

- [x] 3.8 Implement password reset service


  - Create function to generate password reset tokens
  - Store tokens with 24-hour expiration
  - Send reset email with secure link
  - Create function to verify and process password reset
  - _Requirements: 1.6_

- [x] 3.9 Write property test for password reset token expiration


  - **Property 3: Password reset tokens expire**
  - **Validates: Requirements 1.6**

- [x] 3.10 Implement rate limiting middleware


  - Create rate limiting decorator using Redis
  - Apply 5 attempts per 15 minutes limit on auth endpoints
  - Return 429 Too Many Requests when limit exceeded
  - _Requirements: 1.7, 12.6_

- [x] 3.11 Write property test for rate limiting


  - **Property 4: Rate limiting blocks excessive auth attempts**
  - **Validates: Requirements 1.7**

- [x] 3.12 Implement Google OAuth integration


  - Set up Google OAuth 2.0 client configuration
  - Create endpoint for Google OAuth callback
  - Implement user creation or authentication from Google profile
  - _Requirements: 1.5_

- [x] 3.13 Implement role-based access control middleware


  - Create dependency for extracting current user from JWT
  - Create role-checking decorators (require_owner, require_distributor_or_owner)
  - Return 403 Forbidden for unauthorized access
  - _Requirements: 2.5, 2.6_

- [x] 3.14 Write property test for owner access



  - **Property 9: Owner has full admin access**
  - **Validates: Requirements 2.5**

- [x] 3.15 Write property test for non-owner blocking


  - **Property 10: Non-owners blocked from admin endpoints**
  - **Validates: Requirements 2.6**


- [x] 4. User Management Service and APIs



- [x] 4.1 Implement UserService


  - Create create_user function with role assignment
  - Create authenticate_with_otp function
  - Create authenticate_with_google function
  - Create send_otp function
  - Create verify_email function
  - Create update_user_role function with audit logging
  - _Requirements: 2.1, 2.4, 10.5_

- [x] 4.2 Write property test for single role assignment


  - **Property 5: User creation assigns single role**
  - **Validates: Requirements 2.1**

- [x] 4.3 Create authentication API endpoints


  - POST /api/v1/auth/send-otp - Send OTP to phone/email
  - POST /api/v1/auth/verify-otp - Verify OTP and return JWT
  - POST /api/v1/auth/google - Google OAuth callback
  - POST /api/v1/auth/refresh - Refresh JWT token
  - POST /api/v1/auth/reset-password - Request password reset
  - PUT /api/v1/auth/reset-password - Complete password reset
  - Add input validation with Pydantic schemas
  - _Requirements: 1.1, 1.2, 1.5, 1.6_

- [x] 4.4 Create user profile API endpoints


  - GET /api/v1/users/me - Get current user profile
  - PUT /api/v1/users/me - Update user profile
  - GET /api/v1/users/me/addresses - Get user addresses
  - POST /api/v1/users/me/addresses - Add new address
  - PUT /api/v1/users/me/addresses/:id - Update address
  - DELETE /api/v1/users/me/addresses/:id - Delete address
  - _Requirements: 6.2_

- [x] 4.5 Write property test for address validation


  - **Property 28: Address validation requires all fields**
  - **Validates: Requirements 6.2**


- [-] 5. Product Management Service and APIs


- [x] 5.1 Implement ProductService


  - Create create_product function with validation
  - Create update_product function
  - Create get_products function with pagination, filtering, and role-based pricing
  - Create get_product_by_id function with role-based pricing
  - Create update_stock function with audit logging
  - Create search_products function with full-text search
  - Create soft delete function
  - _Requirements: 3.1, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4_

- [x] 5.2 Write property test for product creation validation


  - **Property 11: Product creation requires all fields**
  - **Validates: Requirements 3.1**

- [x] 5.3 Write property test for stock update audit logging


  - **Property 13: Stock updates create audit logs**
  - **Validates: Requirements 3.3**

- [x] 5.4 Write property test for consumer pricing


  - **Property 6: Consumer sees consumer prices**
  - **Validates: Requirements 2.2**

- [x] 5.5 Write property test for distributor pricing

  - **Property 7: Distributor sees distributor prices**
  - **Validates: Requirements 2.3**

- [x] 5.6 Write property test for soft delete



  - **Property 15: Soft delete hides products**
  - **Validates: Requirements 3.5**

- [x] 5.7 Implement S3 image upload service


  - Configure S3 client (boto3) with credentials
  - Create upload_image function with file type and size validation
  - Generate unique filenames and CDN URLs
  - Create delete_image function
  - _Requirements: 3.2, 20.1, 20.2_

- [x] 5.8 Write property test for image upload validation


  - **Property 76: Image upload validates file type and size**
  - **Validates: Requirements 20.1**

- [x] 5.9 Write property test for image association


  - **Property 12: Product image upload associates with product**
  - **Validates: Requirements 3.2**

- [x] 5.10 Create product API endpoints


  - GET /api/v1/products - List products (paginated, filtered, role-based pricing)
  - GET /api/v1/products/:id - Get product details
  - GET /api/v1/categories - List categories
  - GET /api/v1/products/search - Search products
  - Add query parameter validation for filters and pagination
  - _Requirements: 4.1, 4.2, 4.3, 4.5_

- [x] 5.11 Write property test for pagination







  - **Property 16: Catalog pagination returns 20 items**
  - **Validates: Requirements 4.1**

- [x] 5.12 Write property test for category filtering





  - **Property 17: Category filter returns matching products**
  - **Validates: Requirements 4.2**

- [x] 5.13 Write property test for search




  - **Property 18: Search returns matching products**
  - **Validates: Requirements 4.3**

- [x] 5.14 Create owner product management API endpoints


  - POST /api/v1/owner/products - Create product (owner only)
  - PUT /api/v1/owner/products/:id - Update product (owner only)
  - DELETE /api/v1/owner/products/:id - Delete product (owner only)
  - POST /api/v1/owner/products/:id/images - Upload product images (owner only)
  - DELETE /api/v1/owner/products/:id/images/:imageId - Delete image (owner only)
  - PUT /api/v1/owner/products/:id/stock - Update stock quantity (owner only)
  - Apply role-based access control middleware
  - _Requirements: 3.1, 3.2, 3.3, 3.5_


- [-] 6. Shopping Cart Service and APIs


- [x] 6.1 Implement CartService


  - Create get_cart function that returns cart with role-based pricing
  - Create add_item function with stock validation
  - Create update_item_quantity function with total recalculation
  - Create remove_item function with total recalculation
  - Create apply_coupon function with validation
  - Create validate_cart function for stock availability check
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 6.2 Write property test for cart total recalculation









  - **Property 22: Quantity updates recalculate total**
  - **Validates: Requirements 5.2**

- [x] 6.3 Write property test for coupon application














  - **Property 23: Valid coupon reduces cart total**
  - **Validates: Requirements 5.3**

- [x] 6.4 Write property test for role-based cart pricing




  - **Property 24: Cart displays role-appropriate prices**
  - **Validates: Requirements 5.4**

- [x] 6.5 Write property test for item removal





  - **Property 25: Item removal updates cart**
  - **Validates: Requirements 5.5**

- [x] 6.6 Write property test for stock validation



  - **Property 26: Insufficient stock blocks checkout**
  - **Validates: Requirements 5.6**

- [x] 6.7 Create cart API endpoints





  - GET /api/v1/cart - Get user's cart
  - POST /api/v1/cart/items - Add item to cart
  - PUT /api/v1/cart/items/:id - Update cart item quantity
  - DELETE /api/v1/cart/items/:id - Remove item from cart
  - POST /api/v1/cart/coupon - Apply coupon code
  - DELETE /api/v1/cart/coupon - Remove coupon
  - Require authentication for all cart endpoints
  - _Requirements: 5.1, 5.2, 5.3, 5.5_


- [x] 7. Payment Integration with Razorpay




- [x] 7.1 Implement PaymentService


  - Configure Razorpay client with API keys
  - Create create_razorpay_order function
  - Create create_razorpay_subscription function
  - Create verify_payment_signature function
  - Create handle_payment_success function with order status update
  - Create handle_payment_failure function with order status update
  - Create handle_subscription_charged function
  - _Requirements: 6.3, 6.4, 6.5, 7.3, 7.4_

- [x] 7.2 Write property test for Razorpay order creation


  - **Property 29: Order confirmation creates Razorpay order**
  - **Validates: Requirements 6.3**

- [x] 7.3 Write property test for payment success handling

  - **Property 30: Payment success updates order status**
  - **Validates: Requirements 6.4**

- [x] 7.4 Write property test for payment failure handling

  - **Property 31: Payment failure updates order status**
  - **Validates: Requirements 6.5**

- [x] 7.5 Write property test for webhook signature verification

  - **Property 33: Webhook signature verification required**
  - **Validates: Requirements 6.7**

- [x] 7.6 Create payment webhook endpoint


  - POST /api/v1/webhooks/razorpay - Handle Razorpay webhooks
  - Verify webhook signature before processing
  - Handle payment.captured event
  - Handle payment.failed event
  - Handle subscription.charged event
  - Handle subscription.cancelled event
  - Implement idempotency to prevent duplicate processing
  - Log all webhook events
  - _Requirements: 6.4, 6.5, 6.7, 7.4, 15.5_

- [x] 7.7 Write property test for payment logging


  - **Property 64: Payment attempts are logged**
  - **Validates: Requirements 15.5**

- [-] 8. Order Management Service and APIs

- [ ] 8. Order Management Service and APIs

- [x] 8.1 Implement OrderService


  - Create create_order function with stock validation and reduction
  - Create get_user_orders function with pagination
  - Create get_order_by_id function with ownership validation
  - Create update_order_status function with state validation and audit logging
  - Create process_refund function
  - Implement database transactions for order creation
  - _Requirements: 6.1, 6.6, 8.1, 8.2, 8.4, 8.5_

- [x] 8.2 Write property test for checkout stock validation


  - **Property 27: Checkout validates stock**
  - **Validates: Requirements 6.1**

- [x] 8.3 Write property test for stock reduction


  - **Property 32: Order creation reduces stock**
  - **Validates: Requirements 6.6**

- [x] 8.4 Write property test for order status transitions


  - **Property 41: Order status transitions are valid**
  - **Validates: Requirements 8.2**

- [ ] 8.5 Implement notification service




  - Create send_email function with template support
  - Create send_sms function
  - Integrate with email provider (SendGrid or AWS SES)
  - Integrate with SMS provider (Twilio or MSG91)
  - Create notification templates for order confirmation, shipping, payment failure
  - Implement retry logic with exponential backoff
  - _Requirements: 8.3, 11.2, 11.3, 11.4, 17.5_

- [x] 8.6 Write property test for order status notifications




- [ ] 8.6 Write property test for order status notifications
  - **Property 42: Status changes trigger notifications**
  - **Validates: Requirements 8.3**
-

- [x] 8.7 Write property test for external service retry




  - **Property 75: External service failures retry with backoff**
  - **Validates: Requirements 17.5**



- [x] 8.8 Create order API endpoints





  - POST /api/v1/orders - Create order (initiate checkout)
  - GET /api/v1/orders - Get user's orders
  - GET /api/v1/orders/:id - Get order details
  - Validate cart before order creation
  - Integrate with PaymentService to create Razorpay order
  - _Requirements: 6.1, 8.4_

- [x] 8.9 Write property test for consumer order visibility


  - **Property 43: Consumer sees own orders**
  - **Validates: Requirements 8.4**


- [x] 8.10 Create owner order management API endpoints



  - GET /api/v1/owner/orders - List all orders (filtered)
  - PUT /api/v1/owner/orders/:id/status - Update order status
  - POST /api/v1/owner/orders/:id/refund - Process refund
  - Apply owner-only access control
  - _Requirements: 8.2, 8.5_

- [x] 8.11 Write property test for owner order visibility



  - **Property 44: Owner sees all orders**
  - **Validates: Requirements 8.5**


- [x] 9. Subscription Management Service and APIs

















- [x] 9.1 Implement SubscriptionService




  - Create create_subscription function with Razorpay integration
  - Create get_user_subscriptions function
  - Create pause_subscription function with Razorpay API call
  - Create resume_subscription function with Razorpay API call
  - Create cancel_subscription function with Razorpay API call
  - Create process_subscription_charge function (called from webhook)
  - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 9.2 Write property test for subscription creation validation


  - **Property 35: Subscription creation requires all fields**
  - **Validates: Requirements 7.2**

- [x] 9.3 Write property test for Razorpay subscription creation

  - **Property 36: Subscription confirmation creates Razorpay subscription**
  - **Validates: Requirements 7.3**

- [x] 9.4 Write property test for subscription charge handling


  - **Property 37: Subscription charge creates order**
  - **Validates: Requirements 7.4**

- [x] 9.5 Write property test for paused subscription

  - **Property 38: Paused subscriptions suspend billing**
  - **Validates: Requirements 7.5**

- [x] 9.6 Write property test for cancelled subscription

  - **Property 39: Cancelled subscriptions prevent charges**
  - **Validates: Requirements 7.6**

- [x] 9.7 Create subscription API endpoints


  - POST /api/v1/subscriptions - Create subscription
  - GET /api/v1/subscriptions - Get user's subscriptions
  - GET /api/v1/subscriptions/:id - Get subscription details
  - PUT /api/v1/subscriptions/:id/pause - Pause subscription
  - PUT /api/v1/subscriptions/:id/resume - Resume subscription
  - DELETE /api/v1/subscriptions/:id - Cancel subscription
  - Validate product is subscription-available
  - _Requirements: 7.1, 7.2, 7.5, 7.6_

- [x] 9.8 Write property test for subscription product display


  - **Property 34: Subscription products show options**
  - **Validates: Requirements 7.1**

- [x] 9.9 Create owner subscription management API endpoints


  - GET /api/v1/owner/subscriptions - List all subscriptions
  - GET /api/v1/owner/subscriptions/calendar - Delivery calendar view
  - Apply owner-only access control
  - _Requirements: 10.3_

- [x] 9.10 Write property test for subscription calendar


  - **Property 51: Subscription calendar shows scheduled deliveries**
  - **Validates: Requirements 10.3**




- [ ] 10. Distributor Features


- [x] 10.1 Implement distributor approval workflow


  - Create distributor registration endpoint with pending status
  - Create owner endpoint to approve distributor applications
  - Send confirmation email on approval
  - Update user role to distributor on approval
  - Create audit log entry for role change
  - _Requirements: 2.4, 10.5, 15.3_

- [x] 10.2 Write property test for distributor approval


  - **Property 8: Distributor requires approval**
  - **Validates: Requirements 2.4**

- [x] 10.3 Write property test for approval notification

  - **Property 53: Distributor approval updates role and notifies**
  - **Validates: Requirements 10.5**

- [x] 10.4 Implement bulk discount rules


  - Create BulkDiscountRule model with quantity thresholds
  - Create database migration for bulk_discount_rules table
  - Implement apply_bulk_discounts function in OrderService
  - Create owner endpoints to manage bulk discount rules
  - _Requirements: 9.4_

- [x] 10.5 Write property test for bulk discounts


  - **Property 47: Bulk discounts apply to qualifying orders**
  - **Validates: Requirements 9.4**

- [x] 10.6 Write property test for distributor cart pricing

  - **Property 45: Distributor cart uses distributor pricing**
  - **Validates: Requirements 9.2**

- [x] 10.7 Write property test for distributor checkout pricing

  - **Property 46: Distributor checkout uses distributor pricing**
  - **Validates: Requirements 9.3**

- [x] 10.8 Write property test for distributor order history


  - **Property 48: Distributor order history shows distributor pricing**
  - **Validates: Requirements 9.5**


- [-] 11. Owner Dashboard and Analytics


- [x] 11.1 Implement analytics service


  - Create get_dashboard_metrics function (revenue, order count, active subscriptions, low stock)
  - Create get_revenue_report function with date range filtering
  - Create get_inventory_status function with category filtering
  - Create get_low_stock_alerts function
  - _Requirements: 10.1, 10.2_



- [ ] 11.2 Write property test for dashboard metrics
  - **Property 49: Dashboard displays all metrics**
  - **Validates: Requirements 10.1**


- [ ] 11.3 Write property test for inventory reports
  - **Property 50: Inventory reports show accurate stock**
  - **Validates: Requirements 10.2**



- [ ] 11.4 Create owner analytics API endpoints
  - GET /api/v1/owner/analytics/dashboard - Dashboard metrics
  - GET /api/v1/owner/analytics/revenue - Revenue reports
  - GET /api/v1/owner/inventory - Inventory status

  - Apply owner-only access control
  - _Requirements: 10.1, 10.2_

- [x] 11.5 Implement user management for owner

  - Create get_all_users function with role and status filtering
  - Create update_user_role function with audit logging
  - _Requirements: 10.4, 15.3_


- [x] 11.6 Write property test for user management filtering

  - **Property 52: User management supports filtering**
  - **Validates: Requirements 10.4**



- [ ] 11.7 Write property test for role change audit logging
  - **Property 62: Role changes create audit logs**
  - **Validates: Requirements 15.3**

- [x] 11.8 Create owner user management API endpoints


  - GET /api/v1/owner/users - User management with filtering
  - PUT /api/v1/owner/users/:id/role - Update user role
  - Apply owner-only access control
  - _Requirements: 10.4, 10.5_


- [x] 11.9 Implement audit log viewer

  - Create get_audit_logs function with filtering by action type, date range, and actor
  - _Requirements: 15.4_


- [x] 11.10 Write property test for audit log filtering

  - **Property 63: Audit logs support filtering**
  - **Validates: Requirements 15.4**


- [x] 11.11 Create audit log API endpoint

  - GET /api/v1/owner/audit-logs - Audit log viewer
  - Apply owner-only access control
  - _Requirements: 15.4_


- [x] 11.12 Write property test for price change audit logging


  - **Property 61: Price changes create audit logs**
  - **Validates: Requirements 15.1**


- [x] 12. Input Validation and Security






- [x] 12.1 Implement comprehensive input validation


  - Create Pydantic schemas for all API request bodies
  - Add email format validation (RFC 5322)
  - Add phone number format validation with country code
  - Add price validation (positive, max 2 decimal places)
  - Add required field validation for all forms
  - _Requirements: 16.1, 16.2, 16.3, 16.4_

- [x] 12.2 Write property test for form validation


  - **Property 65: Required form fields validated**
  - **Validates: Requirements 16.1**

- [x] 12.3 Write property test for email validation

  - **Property 66: Email format validated**
  - **Validates: Requirements 16.2**

- [x] 12.4 Write property test for phone validation

  - **Property 67: Phone format validated**
  - **Validates: Requirements 16.3**

- [x] 12.5 Write property test for price validation

  - **Property 68: Price values validated**
  - **Validates: Requirements 16.4**

- [x] 12.6 Implement SQL injection and XSS prevention

  - Use parameterized queries (SQLAlchemy ORM)
  - Add input sanitization middleware
  - Implement output encoding for user-generated content
  - Add security headers (CSP, X-Frame-Options, etc.)
  - _Requirements: 12.2_

- [x] 12.7 Write property test for malicious input rejection

  - **Property 57: Malicious input rejected**
  - **Validates: Requirements 12.2**

- [x] 12.8 Implement stock quantity constraints


  - Add database constraint for non-negative stock
  - Add validation in update_stock function
  - Add transaction-level stock verification in order creation
  - _Requirements: 16.5, 16.6_

- [x] 12.9 Write property test for non-negative stock

  - **Property 69: Stock cannot be negative**
  - **Validates: Requirements 16.5**

- [x] 12.10 Write property test for atomic stock verification


  - **Property 70: Order creation verifies stock atomically**
  - **Validates: Requirements 16.6**

- [x] 12.11 Write property test for concurrent stock updates

  - **Property 60: Concurrent stock updates are consistent**
  - **Validates: Requirements 14.5**-


- [x] 13. Error Handling and Logging




- [x] 13.1 Implement standardized error responses


  - Create custom exception classes for different error types
  - 
   Create FastAPI exception handlers for consistent error format
  - Return 400 for validation errors with field-level details
  - Return 401 for authentication errors
  - Return 403 for authorization errors
  - Return 500 for server errors with sanitized messages
  - Include request_id in all error responses
  - _Requirements: 17.1, 17.2, 17.3, 17.4_

- [x] 13.2 Write property test for validation error responses


  - **Property 71: Validation errors return 400**
  - **Validates: Requirements 17.1**

- [x] 13.3 Write property test for authentication error responses

  - **Property 72: Authentication errors return 401**
  - **Validates: Requirements 17.2**

- [x] 13.4 Write property test for authorization error responses

  - **Property 73: Authorization errors return 403**
  - **Validates: Requirements 17.3**

- [x] 13.5 Write property test for server error responses

  - **Property 74: Server errors return 500 and log**
  - **Validates: Requirements 17.4**

- [x] 13.6 Implement structured logging


  - Configure Python logging with JSON formatter
  - Add request_id to all log entries
  - Log all API requests with method, path, status code, duration
  - Log all errors with full stack traces
  - Integrate with Sentry for error tracking
  - _Requirements: 19.5_

- [x] 13.7 Implement monitoring and alerting


  - Configure Sentry DSN
  - Add custom metrics for order count, revenue, active subscriptions
  - Set up alerts for high error rates, slow response times, external service failures
  - _Requirements: 19.4_


- [x] 14. Frontend - Authentication and User Management


- [x] 14.1 Create authentication context and hooks


  - Implement AuthContext with user state and auth functions
  - Create useAuth hook for accessing auth context
  - Implement JWT token storage in localStorage
  - Create axios interceptor for adding JWT to requests
  - Implement token refresh logic
  - _Requirements: 1.2, 1.4_

- [x] 14.2 Create authentication components





  - Create AuthModal component with tabs for login/signup
  - Create OTPForm component for phone/email OTP
  - Create GoogleSignInButton component
  - Create PasswordResetForm component
  - Add form validation with Formik and Yup
  - _Requirements: 1.1, 1.2, 1.5, 1.6_


- [x] 14.3 Create user profile components

  - Create UserProfilePage component
  - Create AddressForm component with validation
  - Create AddressList component with edit/delete actions
  - _Requirements: 6.2_

- [x] 14.4 Implement protected routes
  - Create ProtectedRoute component that checks authentication
  - Create RoleBasedRoute component that checks user role
  - Redirect to login if not authenticated
  - Show 403 error if insufficient permissions
  - _Requirements: 2.5, 2.6_


- [x] 15. Frontend - Product Catalog and Search




- [x] 15.1 Create product browsing components


  - Create ProductCatalogPage with grid layout
  - Create ProductCard component showing image, title, price, add-to-cart
  - Create FilterSidebar component with category, price range filters
  - Create SearchBar component with debounced search
  - Create PriceDisplay component that shows role-appropriate pricing
  - Implement pagination controls
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 15.2 Create product detail components


  - Create ProductDetailPage component
  - Create ImageCarousel component for product images
  - Display product information, pricing, stock availability
  - Add AddToCart button with quantity selector
  - Show subscription options if product is subscription-available
  - _Requirements: 4.5, 7.1_

- [x] 15.3 Implement product API integration


  - Create productService with API calls (getProducts, getProductById, searchProducts)
  - Use React Query for caching and state management
  - Implement loading and error states
  - _Requirements: 4.1, 4.2, 4.3, 4.5_


- [-] 16. Frontend - Shopping Cart and Checkout


- [x] 16.1 Create cart context and hooks


  - Implement CartContext with cart state
  - Create useCart hook for cart operations
  - Implement optimistic updates for cart actions
  - _Requirements: 5.1, 5.2, 5.5_

- [x] 16.2 Create cart components


  - Create CartPage component with item list
  - Create CartItem component with quantity controls and remove button
  - Create CouponInput component
  - Display cart total with role-appropriate pricing
  - Show stock availability warnings
  - _Requirements: 5.2, 5.3, 5.4, 5.6_

- [x] 16.3 Create checkout components


  - Create CheckoutPage component with multi-step flow
  - Create DeliveryAddressSelector component
  - Create OrderSummary component
  - Integrate Razorpay Checkout SDK
  - Handle payment success/failure callbacks
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 16.4 Implement cart and order API integration



  - Create cartService with API calls (getCart, addItem, updateItem, removeItem, applyCoupon)
  - Create orderService with API calls (createOrder, getOrders, getOrderById)
  - Handle Razorpay payment flow
  - _Requirements: 5.1, 5.2, 5.3, 5.5, 6.1_


- [x] 17. Frontend - Subscriptions






- [x] 17.1 Create subscription components

  - Create SubscriptionForm component with frequency selector and date picker
  - Create SubscriptionCard component showing subscription details
  - Create SubscriptionManagementPage with list of active subscriptions
  - Add pause/resume/cancel buttons with confirmation dialogs
  - _Requirements: 7.2, 7.5, 7.6_

- [x] 17.2 Implement subscription API integration


  - Create subscriptionService with API calls (createSubscription, getSubscriptions, pauseSubscription, resumeSubscription, cancelSubscription)
  - Handle Razorpay subscription flow
  - _Requirements: 7.2, 7.5, 7.6_


- [x] 18. Frontend - User Dashboards




- [x] 18.1 Create consumer dashboard


  - Create ConsumerDashboardPage component
  - Create OrderHistoryList component with status badges
  - Create OrderDetailModal component
  - Display active subscriptions summary
  - Link to profile and address management
  - _Requirements: 8.4_

- [x] 18.2 Create distributor dashboard


  - Create DistributorDashboardPage component
  - Display orders with distributor pricing
  - Show account status and approval state
  - Display bulk discount information
  - _Requirements: 9.5_

- [x] 18.3 Create owner dashboard


  - Create OwnerDashboardPage component
  - Display dashboard metrics (revenue, order count, subscriptions, low stock)
  - Create charts for revenue trends
  - Show recent orders and alerts
  - _Requirements: 10.1_


- [x] 19. Frontend - Owner Product Management




- [x] 19.1 Create product management components


  - Create ProductManagementPage with product list and search
  - Create ProductForm component for create/edit
  - Create ImageUploader component with drag-and-drop
  - Create StockUpdateForm component
  - Add validation for all product fields
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 19.2 Create category management components


  - Create CategoryManagementPage component
  - Create CategoryForm component
  - _Requirements: 4.2_

- [x] 19.3 Implement owner product API integration

  - Create ownerProductService with API calls (createProduct, updateProduct, deleteProduct, uploadImage, updateStock)
  - Handle image upload with progress indicator
  - _Requirements: 3.1, 3.2, 3.3_


- [x] 20. Frontend - Owner Order and User Management




- [x] 20.1 Create order management components


  - Create OrderManagementPage with filters (status, date range, user role)
  - Create OrderDetailView component
  - Create OrderStatusUpdater component with status dropdown
  - Create RefundProcessor component
  - _Requirements: 8.2, 8.5_

- [x] 20.2 Create user management components


  - Create UserManagementPage with filters (role, status)
  - Create UserDetailView component
  - Create RoleUpdater component
  - Create DistributorApprovalList component
  - _Requirements: 10.4, 10.5_

- [x] 20.3 Create inventory and analytics components


  - Create InventoryPage with stock levels and category filters
  - Create LowStockAlerts component
  - Create RevenueChart component
  - Create SubscriptionCalendar component
  - _Requirements: 10.1, 10.2, 10.3_

- [x] 20.4 Create audit log viewer component


  - Create AuditLogPage with filters (action type, date range, actor)
  - Display audit log entries in table format
  - _Requirements: 15.4_


- [x] 21. Frontend - Layout and Navigation



- [x] 21.1 Create layout components


  - Create Header component with navigation, search, cart icon, user menu
  - Create Footer component with links and contact info
  - Create Sidebar component for filters
  - Create responsive navigation with mobile menu
  - _Requirements: 13.1, 13.2_

- [x] 21.2 Create shared UI components


  - Create LoadingSpinner component
  - Create ErrorBoundary component
  - Create Toast notification component
  - Create Modal component
  - Create Button component with variants
  - Create Input component with validation display
  - Create OrderStatusBadge component
  - _Requirements: 17.1_

- [x] 21.3 Implement routing


  - Set up React Router with all routes
  - Create HomePage route
  - Create product catalog and detail routes
  - Create cart and checkout routes
  - Create dashboard routes (consumer, distributor, owner)
  - Create authentication routes
  - Implement 404 page
  - _Requirements: 13.1, 13.2_

- [x] 21.4 Create homepage


  - Create HomePage component with hero banner
  - Display featured products
  - Display category cards
  - Add subscription CTA section
  - Implement responsive design matching reference site
  - _Requirements: 13.1, 13.2_


- [x] 22. Frontend - Accessibility and Optimization




- [x] 22.1 Implement accessibility features


  - Add alt text to all images
  - Ensure proper heading hierarchy
  - Add ARIA labels where needed
  - Implement keyboard navigation
  - Add focus indicators
  - Associate labels with form inputs
  - _Requirements: 13.3, 13.4, 13.5_

- [x] 22.2 Write property test for image alt text


  - **Property 59: Images include alt text**
  - **Validates: Requirements 13.4**

- [x] 22.3 Implement performance optimizations


  - Add code splitting by route
  - Implement lazy loading for images
  - Add debouncing for search input
  - Optimize bundle size
  - Add service worker for caching
  - Implement responsive images with srcset
  - _Requirements: 14.1, 14.2, 20.5_

- [x] 22.4 Write property test for responsive images


  - **Property 78: Product images have multiple resolutions**
  - **Validates: Requirements 20.3**


- [x] 23. Background Tasks and Scheduled Jobs




- [x] 23.1 Set up Celery for background tasks


  - Configure Celery with Redis broker
  - Create Celery app instance
  - Set up task queues (default, notifications, subscriptions)
  - Configure task retry policies
  - _Requirements: 17.5_

- [x] 23.2 Implement notification tasks


  - Create send_email_task for async email sending
  - Create send_sms_task for async SMS sending
  - Implement retry logic with exponential backoff
  - _Requirements: 8.3, 11.2, 11.3, 11.4, 17.5_

- [x] 23.3 Implement subscription processing tasks


  - Create process_due_subscriptions task (runs daily)
  - Check for subscriptions with next_delivery_date = today
  - Create orders for due subscriptions
  - Process Razorpay charges
  - Update next_delivery_date based on frequency
  - _Requirements: 7.7_

- [x] 23.4 Implement cleanup tasks


  - Create cleanup_expired_carts task (runs daily)
  - Create cleanup_expired_tokens task (runs daily)
  - _Requirements: 1.6_


- [x] 24. Testing and Quality Assurance




- [x] 24.1 Set up testing infrastructure


  - Configure pytest with pytest-asyncio for backend
  - Configure Jest and React Testing Library for frontend
  - Set up test database with fixtures
  - Configure Hypothesis for property-based testing
  - Create test data factories with Factory Boy
  - _Requirements: 18.1, 18.2_

- [x] 24.2 Write unit tests for backend services


  - Test UserService methods
  - Test ProductService methods
  - Test CartService methods
  - Test OrderService methods
  - Test SubscriptionService methods
  - Test PaymentService methods
  - Mock external dependencies (Razorpay, SMS, email, S3)
  - Target 80%+ code coverage

- [x] 24.3 Write unit tests for frontend components


  - Test authentication components
  - Test product catalog components
  - Test cart and checkout components
  - Test dashboard components
  - Mock API calls with MSW
  - Target 70%+ code coverage

- [x] 24.4 Write integration tests


  - Test complete API flows with test database
  - Test webhook processing with simulated webhooks
  - Test authentication flows
  - Test cart-to-order flow
  - Test subscription creation and management

- [x] 24.5 Write end-to-end tests


  - Set up Playwright for E2E testing
  - Test consumer signup → browse → cart → checkout → payment
  - Test distributor signup → approval → checkout
  - Test owner product creation → pricing → inventory
  - Test subscription creation → pause → resume → cancel
  - Run E2E tests in CI pipeline

- [x] 25. Deployment and Documentation



- [ ] 25. Deployment and Documentation

- [x] 25.1 Create deployment configurations


  - Write production Dockerfile for backend
  - Write production Dockerfile for frontend (with Nginx)
  - Write docker-compose for production
  - Create Kubernetes manifests (optional)
  - Configure environment variables for production
  - _Requirements: 19.1_

- [x] 25.2 Set up production infrastructure


  - Configure PostgreSQL RDS with Multi-AZ
  - Configure ElastiCache Redis cluster
  - Set up S3 bucket with CloudFront CDN
  - Configure Application Load Balancer
  - Set up auto-scaling groups
  - Configure Route 53 DNS
  - _Requirements: 19.1_

- [x] 25.3 Configure monitoring and logging


  - Set up Sentry for error tracking
  - Configure CloudWatch for infrastructure metrics
  - Set up log aggregation
  - Create alerts for critical issues
  - _Requirements: 19.4, 19.5_

- [x] 25.4 Write documentation


  - Create README with setup instructions
  - Document environment variables
  - Document API endpoints (OpenAPI/Swagger)
  - Create owner admin guide for product upload and management
  - Document deployment process
  - Create runbook for common issues
  - _Requirements: 19.1_

- [x] 25.5 Create database backup and recovery plan


  - Configure automated daily backups
  - Enable point-in-time recovery
  - Document restore process
  - Test disaster recovery
  - _Requirements: 19.2_

- [x] 26. Final Checkpoint - Ensure all tests pass




  - Run all unit tests (backend and frontend)
  - Run all property-based tests
  - Run all integration tests
  - Run E2E tests
  - Verify code coverage meets targets
  - Fix any failing tests
  - Ensure all tests pass, ask the user if questions arise.
