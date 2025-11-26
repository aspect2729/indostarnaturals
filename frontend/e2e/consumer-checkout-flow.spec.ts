/**
 * E2E test for consumer checkout flow
 */
import { test, expect } from '@playwright/test'

test.describe('Consumer Checkout Flow', () => {
  test('complete checkout flow from signup to payment', async ({ page }) => {
    // Step 1: Navigate to homepage
    await page.goto('/')
    expect(await page.title()).toContain('IndoStar Naturals')

    // Step 2: Sign up
    await page.click('text=Sign In')
    await page.click('text=Sign Up')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="phone"]', '+919876543210')
    await page.fill('input[name="name"]', 'Test User')
    await page.click('button:has-text("Send OTP")')
    
    // Mock OTP verification
    await page.fill('input[name="otp"]', '123456')
    await page.click('button:has-text("Verify")')
    
    // Wait for successful login
    await expect(page.locator('text=Welcome')).toBeVisible()

    // Step 3: Browse products
    await page.click('text=Products')
    await expect(page.locator('[data-testid="product-card"]').first()).toBeVisible()

    // Step 4: Add product to cart
    await page.locator('[data-testid="product-card"]').first().click()
    await page.click('button:has-text("Add to Cart")')
    await expect(page.locator('text=Added to cart')).toBeVisible()

    // Step 5: Go to cart
    await page.click('[data-testid="cart-icon"]')
    await expect(page.locator('[data-testid="cart-item"]')).toBeVisible()

    // Step 6: Proceed to checkout
    await page.click('button:has-text("Proceed to Checkout")')
    
    // Step 7: Fill delivery address
    await page.fill('input[name="address_line1"]', '123 Test Street')
    await page.fill('input[name="city"]', 'Test City')
    await page.fill('input[name="state"]', 'Test State')
    await page.fill('input[name="postal_code"]', '123456')
    await page.click('button:has-text("Continue")')

    // Step 8: Confirm order
    await page.click('button:has-text("Place Order")')
    
    // Wait for Razorpay modal (in real test, would interact with it)
    await expect(page.locator('text=Order Confirmed')).toBeVisible({ timeout: 10000 })
  })

  test('cart validation prevents checkout with insufficient stock', async ({ page }) => {
    // Login
    await page.goto('/login')
    // ... login steps ...

    // Add product with high quantity
    await page.goto('/products/1')
    await page.fill('input[name="quantity"]', '1000')
    await page.click('button:has-text("Add to Cart")')

    // Try to checkout
    await page.goto('/cart')
    await page.click('button:has-text("Proceed to Checkout")')

    // Should show error
    await expect(page.locator('text=Insufficient stock')).toBeVisible()
  })
})
