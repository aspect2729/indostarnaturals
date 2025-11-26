/**
 * E2E test for subscription management
 */
import { test, expect } from '@playwright/test'

test.describe('Subscription Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as consumer
    await page.goto('/login')
    // ... login steps ...
  })

  test('create subscription for milk product', async ({ page }) => {
    // Navigate to subscription-available product
    await page.goto('/products?subscription=true')
    await page.locator('[data-testid="product-card"]').first().click()

    // Click subscribe button
    await page.click('button:has-text("Subscribe")')

    // Fill subscription details
    await page.selectOption('select[name="frequency"]', 'daily')
    await page.fill('input[name="start_date"]', '2024-01-20')
    await page.selectOption('select[name="address_id"]', '1')

    // Confirm subscription
    await page.click('button:has-text("Confirm Subscription")')

    // Verify subscription created
    await expect(page.locator('text=Subscription created successfully')).toBeVisible()
  })

  test('pause and resume subscription', async ({ page }) => {
    // Navigate to subscriptions
    await page.goto('/subscriptions')
    
    // Pause subscription
    await page.locator('[data-testid="subscription-card"]').first().locator('button:has-text("Pause")').click()
    await page.click('button:has-text("Confirm")')
    await expect(page.locator('text=Subscription paused')).toBeVisible()

    // Resume subscription
    await page.locator('[data-testid="subscription-card"]').first().locator('button:has-text("Resume")').click()
    await page.click('button:has-text("Confirm")')
    await expect(page.locator('text=Subscription resumed')).toBeVisible()
  })

  test('cancel subscription', async ({ page }) => {
    // Navigate to subscriptions
    await page.goto('/subscriptions')
    
    // Cancel subscription
    await page.locator('[data-testid="subscription-card"]').first().locator('button:has-text("Cancel")').click()
    await page.fill('textarea[name="reason"]', 'No longer needed')
    await page.click('button:has-text("Confirm Cancellation")')

    // Verify subscription cancelled
    await expect(page.locator('text=Subscription cancelled')).toBeVisible()
  })
})
