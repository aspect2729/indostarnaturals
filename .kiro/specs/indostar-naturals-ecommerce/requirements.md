# Requirements Document

## Introduction

IndoStar Naturals is a production-ready web application for selling organic jaggery, milk, and milk products. The system supports three distinct user roles (consumer, distributor, and owner) with role-based access control, product catalog management, shopping cart functionality, payment processing via Razorpay, and milk subscription services with recurring billing. The application emphasizes clean, responsive design with no hardcoded demo data—all product information must be uploaded and managed by the owner through the administrative interface.

## Glossary

- **System**: The IndoStar Naturals web application
- **Consumer**: An end-user who browses and purchases products for personal use
- **Distributor**: A business user who purchases products at wholesale prices for resale
- **Owner**: An administrative user with full system access for product, inventory, order, and user management
- **Product Catalog**: The collection of products available for purchase
- **Cart**: A temporary collection of products selected by a user for purchase
- **Subscription**: A recurring delivery and payment arrangement for milk products
- **OTP**: One-Time Password sent via SMS or email for authentication
- **Razorpay**: The payment gateway service used for processing payments and subscriptions
- **SKU**: Stock Keeping Unit, a unique identifier for each product
- **Webhook**: A server endpoint that receives automated notifications from external services
- **JWT**: JSON Web Token used for session authentication
- **ACL**: Access Control List defining user permissions

## Requirements

### Requirement 1: User Authentication

**User Story:** As a user, I want to authenticate using multiple methods, so that I can securely access the application with my preferred sign-in option.

#### Acceptance Criteria

1. WHEN a user requests OTP via SMS, THE System SHALL send a one-time password to the provided phone number within 30 seconds
2. WHEN a user submits a valid OTP, THE System SHALL verify the code and issue a JWT token for session authentication
3. WHEN a user requests email verification, THE System SHALL send a verification link to the provided email address
4. WHEN a user clicks a valid verification link, THE System SHALL mark the email as verified and authenticate the user
5. WHEN a user initiates Google OAuth sign-in, THE System SHALL redirect to Google authentication and create or authenticate the user account upon successful callback
6. WHEN a user requests password reset, THE System SHALL send a secure reset link via email that expires after 24 hours
7. WHEN authentication attempts exceed 5 failures within 15 minutes from the same IP address, THE System SHALL temporarily block further attempts for 30 minutes

### Requirement 2: Role-Based Access Control

**User Story:** As a system administrator, I want role-based access control, so that users can only access features and data appropriate to their role.

#### Acceptance Criteria

1. WHEN a user account is created, THE System SHALL assign exactly one role from the set: consumer, distributor, or owner
2. WHEN a consumer accesses product pricing, THE System SHALL display consumer prices
3. WHEN a distributor accesses product pricing, THE System SHALL display distributor wholesale prices
4. WHEN a distributor attempts to register, THE System SHALL require owner approval before granting distributor access
5. WHEN an owner accesses administrative functions, THE System SHALL grant full access to product management, inventory, orders, subscriptions, and user management
6. WHEN a non-owner user attempts to access owner-only endpoints, THE System SHALL return a 403 Forbidden response

### Requirement 3: Product Catalog Management

**User Story:** As an owner, I want to manage the complete product catalog, so that I can control all product information, pricing, and inventory without any hardcoded data.

#### Acceptance Criteria

1. WHEN an owner creates a product, THE System SHALL require title, description, category, SKU, unit size, consumer price, distributor price, and stock quantity
2. WHEN an owner uploads product images, THE System SHALL store images in S3-compatible storage and associate them with the product
3. WHEN an owner updates product stock quantity, THE System SHALL record the change in audit logs with timestamp and actor information
4. WHEN an owner sets different consumer and distributor prices for a product, THE System SHALL store both prices and display the appropriate price based on user role
5. WHEN an owner deletes a product, THE System SHALL soft-delete the product and prevent it from appearing in consumer or distributor catalogs
6. WHEN the System initializes the database, THE System SHALL create only system roles and an initial owner account with no product data

### Requirement 4: Product Browsing and Search

**User Story:** As a consumer or distributor, I want to browse and search products efficiently, so that I can quickly find items I want to purchase.

#### Acceptance Criteria

1. WHEN a user views the product catalog, THE System SHALL display products with pagination of 20 items per page
2. WHEN a user applies category filters, THE System SHALL return only products matching the selected categories
3. WHEN a user enters a search query, THE System SHALL return products matching the query in title, description, or tags using full-text search
4. WHEN a user sorts products by price, THE System SHALL order results by the price appropriate to the user's role (consumer or distributor price)
5. WHEN a user views a product detail page, THE System SHALL display multiple images, nutritional information, unit sizes, stock availability, and role-appropriate pricing

### Requirement 5: Shopping Cart Management

**User Story:** As a consumer or distributor, I want to manage items in my shopping cart, so that I can review and modify my selections before checkout.

#### Acceptance Criteria

1. WHEN a user adds a product to the cart, THE System SHALL persist the cart item in the database associated with the user account
2. WHEN a user modifies item quantity in the cart, THE System SHALL update the quantity and recalculate the cart total
3. WHEN a user applies a coupon code, THE System SHALL validate the code and apply the discount to the cart total
4. WHEN a user views the cart, THE System SHALL display all items with current prices based on the user's role
5. WHEN a user removes an item from the cart, THE System SHALL delete the cart item and update the cart total
6. WHEN a user's cart contains items exceeding available stock, THE System SHALL prevent checkout and display a stock availability warning

### Requirement 6: Checkout and Payment Processing

**User Story:** As a consumer or distributor, I want to complete purchases securely, so that I can receive my ordered products with confirmed payment.

#### Acceptance Criteria

1. WHEN a user initiates checkout, THE System SHALL validate cart items against current stock levels before proceeding
2. WHEN a user submits delivery address information, THE System SHALL validate all required fields including name, phone, address line, city, state, and postal code
3. WHEN a user confirms an order, THE System SHALL create a Razorpay order and return the order token to the frontend
4. WHEN Razorpay processes a successful payment, THE System SHALL verify the webhook signature and update the order status to confirmed
5. WHEN Razorpay reports a failed payment, THE System SHALL update the order status to failed and notify the user via email
6. WHEN an order is created, THE System SHALL reduce product stock quantities by the ordered amounts
7. WHEN the webhook endpoint receives requests, THE System SHALL verify the Razorpay signature before processing any payment status updates

### Requirement 7: Milk Subscription Management

**User Story:** As a consumer, I want to subscribe to recurring milk deliveries, so that I receive regular deliveries without manual reordering.

#### Acceptance Criteria

1. WHEN an owner marks a product as subscription-available, THE System SHALL display subscription options on the product detail page
2. WHEN a consumer creates a subscription, THE System SHALL require selection of frequency (daily, alternate days, or weekly), start date, and delivery schedule
3. WHEN a consumer confirms a subscription, THE System SHALL create a Razorpay subscription for recurring billing
4. WHEN a Razorpay subscription charges successfully, THE System SHALL create an order record and schedule delivery
5. WHEN a consumer pauses a subscription, THE System SHALL suspend billing and deliveries until resumed
6. WHEN a consumer cancels a subscription, THE System SHALL cancel the Razorpay subscription and prevent future charges
7. WHEN a subscription delivery date arrives, THE System SHALL create an order and process payment via Razorpay

### Requirement 8: Order Management and Tracking

**User Story:** As a consumer, distributor, or owner, I want to track order status, so that I can monitor order progress from placement to delivery.

#### Acceptance Criteria

1. WHEN an order is created, THE System SHALL set the initial status to pending
2. WHEN an owner updates order status, THE System SHALL transition through valid states: pending, confirmed, packed, out-for-delivery, delivered, cancelled, or refunded
3. WHEN an order status changes, THE System SHALL send email notifications to the customer
4. WHEN a consumer views order history, THE System SHALL display all orders with current status, items, and total amount
5. WHEN an owner views all orders, THE System SHALL display orders from all users with filtering by status, date range, and user role

### Requirement 9: Distributor-Specific Features

**User Story:** As a distributor, I want access to wholesale pricing and distributor-specific features, so that I can purchase products for resale at appropriate prices.

#### Acceptance Criteria

1. WHEN a distributor views the product catalog, THE System SHALL display distributor prices instead of consumer prices
2. WHEN a distributor adds items to cart, THE System SHALL calculate totals using distributor pricing
3. WHEN a distributor completes checkout, THE System SHALL process payment at distributor prices
4. WHEN an owner creates bulk discount rules for distributors, THE System SHALL apply additional discounts to distributor orders meeting quantity thresholds
5. WHEN a distributor views order history, THE System SHALL display orders with distributor pricing and any applied bulk discounts

### Requirement 10: Owner Dashboard and Analytics

**User Story:** As an owner, I want comprehensive dashboards and analytics, so that I can monitor business performance and manage operations effectively.

#### Acceptance Criteria

1. WHEN an owner views the dashboard, THE System SHALL display total revenue, order count, active subscriptions, and low-stock alerts
2. WHEN an owner views inventory reports, THE System SHALL display current stock levels for all products with filtering by category
3. WHEN an owner views the subscription calendar, THE System SHALL display scheduled deliveries organized by date
4. WHEN an owner views user management, THE System SHALL display all users with filtering by role and account status
5. WHEN an owner approves a distributor application, THE System SHALL change the user role to distributor and send confirmation email

### Requirement 11: Notification System

**User Story:** As a user, I want to receive timely notifications, so that I stay informed about authentication, orders, and deliveries.

#### Acceptance Criteria

1. WHEN a user receives an OTP, THE System SHALL send the code via SMS within 30 seconds
2. WHEN an order is confirmed, THE System SHALL send an email notification with order details
3. WHEN an order ships, THE System SHALL send an SMS notification with tracking information
4. WHEN a payment fails, THE System SHALL send an email notification with retry instructions
5. WHEN a subscription is about to renew, THE System SHALL send an email notification 24 hours before the charge

### Requirement 12: Security and Data Protection

**User Story:** As a system administrator, I want robust security measures, so that user data and transactions are protected from unauthorized access and attacks.

#### Acceptance Criteria

1. WHEN the System stores passwords, THE System SHALL hash passwords using bcrypt with a minimum cost factor of 12
2. WHEN the System receives API requests, THE System SHALL validate and sanitize all input parameters to prevent injection attacks
3. WHEN the System handles webhook requests, THE System SHALL verify cryptographic signatures before processing
4. WHEN the System stores sensitive configuration, THE System SHALL retrieve values from environment variables or secret management services
5. WHEN the System serves content in production, THE System SHALL enforce HTTPS for all endpoints
6. WHEN the System receives requests to rate-limited endpoints, THE System SHALL enforce maximum request limits per IP address per time window

### Requirement 13: Responsive Design and Accessibility

**User Story:** As a user on any device, I want a responsive and accessible interface, so that I can use the application effectively regardless of device or ability.

#### Acceptance Criteria

1. WHEN a user accesses the application on mobile devices, THE System SHALL display a mobile-optimized layout with touch-friendly controls
2. WHEN a user accesses the application on desktop, THE System SHALL display a layout matching the reference design aesthetic
3. WHEN a user navigates using keyboard only, THE System SHALL provide visible focus indicators and logical tab order
4. WHEN the System displays images, THE System SHALL include descriptive alt text for screen readers
5. WHEN the System displays forms, THE System SHALL associate labels with inputs and provide clear validation error messages

### Requirement 14: Performance and Scalability

**User Story:** As a user, I want fast page loads and responsive interactions, so that I can complete tasks efficiently without delays.

#### Acceptance Criteria

1. WHEN a user loads the product catalog page, THE System SHALL return the initial page within 2 seconds under normal load
2. WHEN the System serves product images, THE System SHALL deliver optimized images via CDN with lazy loading
3. WHEN the System queries products, THE System SHALL use database indexes on frequently queried fields (category, SKU, price)
4. WHEN the System processes search queries, THE System SHALL return results within 1 second for catalogs up to 10,000 products
5. WHEN the System handles concurrent checkout requests, THE System SHALL prevent race conditions in stock quantity updates using database transactions

### Requirement 15: Audit Logging and Compliance

**User Story:** As an owner, I want comprehensive audit logs, so that I can track all significant system changes and maintain compliance.

#### Acceptance Criteria

1. WHEN an owner modifies product pricing, THE System SHALL record the change in audit logs with actor ID, timestamp, old value, and new value
2. WHEN an owner updates inventory quantities, THE System SHALL record the change in audit logs with actor ID, timestamp, and quantity delta
3. WHEN an owner changes user roles or permissions, THE System SHALL record the change in audit logs with actor ID, timestamp, and affected user
4. WHEN an owner views audit logs, THE System SHALL display logs with filtering by action type, date range, and actor
5. WHEN the System processes payments, THE System SHALL log all payment attempts, successes, and failures with transaction IDs

### Requirement 16: Data Integrity and Validation

**User Story:** As a system administrator, I want strict data validation, so that the database maintains integrity and prevents invalid states.

#### Acceptance Criteria

1. WHEN a user submits a form, THE System SHALL validate all required fields before processing
2. WHEN a user enters an email address, THE System SHALL validate the format using RFC 5322 standards
3. WHEN a user enters a phone number, THE System SHALL validate the format and require country code
4. WHEN an owner sets product prices, THE System SHALL require positive decimal values with maximum two decimal places
5. WHEN the System updates stock quantities, THE System SHALL prevent negative stock values
6. WHEN a user creates an order, THE System SHALL verify cart items still exist and have sufficient stock within a database transaction

### Requirement 17: Error Handling and Recovery

**User Story:** As a user, I want clear error messages and graceful failure handling, so that I understand issues and can take corrective action.

#### Acceptance Criteria

1. WHEN the System encounters a validation error, THE System SHALL return a 400 Bad Request response with specific field-level error messages
2. WHEN the System encounters an authentication error, THE System SHALL return a 401 Unauthorized response with a clear message
3. WHEN the System encounters an authorization error, THE System SHALL return a 403 Forbidden response without exposing sensitive information
4. WHEN the System encounters a server error, THE System SHALL return a 500 Internal Server Error response and log the full error details to the monitoring service
5. WHEN external services (Razorpay, SMS provider) fail, THE System SHALL retry failed requests up to 3 times with exponential backoff before reporting failure to the user

### Requirement 18: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive test coverage, so that I can confidently deploy changes without introducing regressions.

#### Acceptance Criteria

1. WHEN the test suite runs, THE System SHALL execute unit tests for all API endpoints with mocked external dependencies
2. WHEN the test suite runs, THE System SHALL execute integration tests for payment webhook processing
3. WHEN the test suite runs, THE System SHALL execute end-to-end tests for critical user flows: signup, add to cart, checkout, and subscription creation
4. WHEN code is committed, THE System SHALL run automated tests via CI pipeline and block merges if tests fail
5. WHEN the test suite completes, THE System SHALL generate a coverage report showing minimum 80% code coverage for backend services

### Requirement 19: Deployment and DevOps

**User Story:** As a developer, I want streamlined deployment processes, so that I can release updates safely and efficiently.

#### Acceptance Criteria

1. WHEN the application is deployed, THE System SHALL run as containerized services using Docker
2. WHEN database schema changes are needed, THE System SHALL apply migrations using version-controlled migration scripts
3. WHEN code is pushed to the main branch, THE System SHALL trigger automated CI/CD pipeline that runs tests, builds containers, and deploys to staging
4. WHEN the System runs in production, THE System SHALL send error reports to Sentry or equivalent monitoring service
5. WHEN the System runs in production, THE System SHALL output structured JSON logs for centralized log aggregation

### Requirement 20: Content Management and Media Handling

**User Story:** As an owner, I want to upload and manage product images and media, so that products are presented attractively to customers.

#### Acceptance Criteria

1. WHEN an owner uploads a product image, THE System SHALL validate file type (JPEG, PNG, WebP) and maximum size (5MB)
2. WHEN an owner uploads a product image, THE System SHALL store the image in S3-compatible storage and generate a CDN URL
3. WHEN the System serves product images, THE System SHALL provide responsive image URLs with multiple resolutions for different screen sizes
4. WHEN an owner deletes a product image, THE System SHALL remove the image from storage and update the product record
5. WHEN the System displays product images, THE System SHALL implement lazy loading to improve page load performance
