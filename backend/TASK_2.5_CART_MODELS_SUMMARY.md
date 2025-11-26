# Task 2.5: Create Cart Models - Implementation Summary

## Task Requirements
- Implement Cart model with coupon support
- Implement CartItem model with locked unit price
- Create database migration for carts and cart_items tables
- Add indexes on cart user_id and cart_item cart_id
- Requirements: 5.1, 5.3

## Implementation Details

### 1. Cart Model (`backend/app/models/cart.py`)
✅ Created Cart model with the following features:
- `id`: Primary key
- `user_id`: Foreign key to users table with unique constraint (one cart per user)
- `coupon_code`: Optional string field for coupon support
- `discount_amount`: Numeric field for storing discount amount
- `created_at` and `updated_at`: Timestamp fields
- Relationship to User model
- Relationship to CartItem model with cascade delete

### 2. CartItem Model (`backend/app/models/cart_item.py`)
✅ Created CartItem model with the following features:
- `id`: Primary key
- `cart_id`: Foreign key to carts table
- `product_id`: Foreign key to products table
- `quantity`: Integer field for item quantity
- `unit_price`: Numeric field for locked price at time of adding
- `created_at`: Timestamp field
- Relationship to Cart model
- Relationship to Product model

### 3. Database Migration (`backend/alembic/versions/2024_01_15_1205-006_create_cart_tables.py`)
✅ Created migration with:
- `carts` table creation with all required columns
- `cart_items` table creation with all required columns
- Foreign key constraints with CASCADE delete
- Indexes on:
  - `carts.id` (primary key index)
  - `carts.user_id` (unique index) ✅
  - `cart_items.id` (primary key index)
  - `cart_items.cart_id` (index) ✅
  - `cart_items.product_id` (index)
- Proper upgrade and downgrade functions

### 4. Model Registration
✅ Updated `backend/app/models/__init__.py` to export Cart and CartItem models

### 5. Tests
✅ Added unit tests in `backend/tests/test_models.py`:
- `test_cart_model_creation`: Verifies Cart model instantiation
- `test_cart_model_with_coupon`: Verifies coupon support
- `test_cart_item_model_creation`: Verifies CartItem model instantiation
- `test_cart_item_locked_price`: Verifies unit price locking feature

## Test Results
All tests passed successfully:
```
tests/test_models.py::test_cart_model_creation PASSED
tests/test_models.py::test_cart_model_with_coupon PASSED
tests/test_models.py::test_cart_item_model_creation PASSED
tests/test_models.py::test_cart_item_locked_price PASSED
```

## Requirements Validation

### Requirement 5.1: Cart Persistence
✅ Cart model persists cart items in database associated with user account
- One-to-one relationship between User and Cart (unique constraint on user_id)
- One-to-many relationship between Cart and CartItem
- Cascade delete ensures cart items are removed when cart is deleted

### Requirement 5.3: Coupon Support
✅ Cart model includes coupon_code and discount_amount fields
- `coupon_code`: String field to store applied coupon code
- `discount_amount`: Numeric field to store discount amount

## Design Document Alignment

### Cart Model (from design.md)
```python
class Cart:
    id: int
    user_id: int
    coupon_code: str | None
    discount_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: list[CartItem]
```
✅ Implementation matches design specification

### CartItem Model (from design.md)
```python
class CartItem:
    id: int
    cart_id: int
    product_id: int
    quantity: int
    unit_price: Decimal  # Locked price at time of adding
    created_at: datetime
    product: Product
```
✅ Implementation matches design specification

## Database Schema
```sql
-- Carts table
CREATE TABLE carts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    coupon_code VARCHAR(100),
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX ix_carts_user_id ON carts(user_id);

-- Cart Items table
CREATE TABLE cart_items (
    id INTEGER PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX ix_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX ix_cart_items_product_id ON cart_items(product_id);
```

## Key Features Implemented

1. **Coupon Support**: Cart model includes fields for storing coupon codes and discount amounts
2. **Locked Unit Price**: CartItem stores the price at the time of adding to cart, preventing price changes from affecting existing cart items
3. **User Association**: Each cart is uniquely associated with a user (one cart per user)
4. **Cascade Deletion**: Cart items are automatically deleted when the cart is deleted
5. **Proper Indexing**: Indexes added on foreign keys for efficient queries
6. **Timestamps**: Created and updated timestamps for audit trail

## Migration Status
⚠️ Migration file created and validated but not yet applied to database
- Migration file syntax verified with py_compile
- Database connection requires Docker services to be running
- Migration can be applied with: `alembic upgrade head`

## Next Steps
The Cart models are fully implemented and tested. The next task (2.6) is to write property tests for cart persistence.
