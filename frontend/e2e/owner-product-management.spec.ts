/**
 * E2E test for owner product management
 */
import { test, expect } from '@playwright/test'

test.describe('Owner Product Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as owner
    await page.goto('/login')
    await page.fill('input[name="email"]', 'owner@example.com')
    await page.fill('input[name="password"]', 'password')
    await page.click('button:has-text("Sign In")')
    await expect(page.locator('text=Owner Dashboard')).toBeVisible()
  })

  test('create new product with images and pricing', async ({ page }) => {
    // Navigate to product management
    await page.click('text=Products')
    await page.click('button:has-text("Add Product")')

    // Fill product details
    await page.fill('input[name="title"]', 'New Test Product')
    await page.fill('textarea[name="description"]', 'This is a test product')
    await page.selectOption('select[name="category_id"]', '1')
    await page.fill('input[name="sku"]', 'TEST-001')
    await page.fill('input[name="unit_size"]', '1 Unit')
    await page.fill('input[name="consumer_price"]', '100')
    await page.fill('input[name="distributor_price"]', '80')
    await page.fill('input[name="stock_quantity"]', '50')

    // Upload image
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles('test-image.jpg')

    // Save product
    await page.click('button:has-text("Save Product")')

    // Verify product created
    await expect(page.locator('text=Product created successfully')).toBeVisible()
    await expect(page.locator('text=New Test Product')).toBeVisible()
  })

  test('update product stock quantity', async ({ page }) => {
    // Navigate to products
    await page.click('text=Products')
    
    // Click on first product
    await page.locator('[data-testid="product-row"]').first().click()

    // Update stock
    await page.click('button:has-text("Update Stock")')
    await page.fill('input[name="quantity_delta"]', '10')
    await page.click('button:has-text("Confirm")')

    // Verify stock updated
    await expect(page.locator('text=Stock updated successfully')).toBeVisible()
  })

  test('delete product (soft delete)', async ({ page }) => {
    // Navigate to products
    await page.click('text=Products')
    
    // Delete first product
    await page.locator('[data-testid="product-row"]').first().locator('button:has-text("Delete")').click()
    await page.click('button:has-text("Confirm Delete")')

    // Verify product deleted
    await expect(page.locator('text=Product deleted successfully')).toBeVisible()
  })
})
