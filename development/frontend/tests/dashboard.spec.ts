import { test, expect } from '@playwright/test';

test.describe('Cash Flow Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the dashboard
    await page.goto('/');
  });

  test('should display dashboard title and description', async ({ page }) => {
    // Check main title
    await expect(page.locator('h1')).toContainText('Cash Flow Dashboard');
    
    // Check description
    await expect(page.locator('p')).toContainText('Monitor and forecast your organization\'s cash flow');
  });

  test('should display all metric cards', async ({ page }) => {
    // Wait for metrics cards to load
    await page.waitForSelector('[data-testid="metrics-cards"]', { timeout: 10000 });
    
    // Check that all 4 metric cards are present
    const metricCards = page.locator('[data-testid="metric-card"]');
    await expect(metricCards).toHaveCount(4);
    
    // Check specific metrics
    await expect(page.locator('text=Current Balance')).toBeVisible();
    await expect(page.locator('text=Monthly Inflow')).toBeVisible();
    await expect(page.locator('text=Monthly Outflow')).toBeVisible();
    await expect(page.locator('text=30-Day Forecast')).toBeVisible();
  });

  test('should display cash flow chart section', async ({ page }) => {
    // Check chart section title
    await expect(page.locator('h2').filter({ hasText: 'Cash Flow Trends' })).toBeVisible();
    
    // Check chart container exists
    await expect(page.locator('[data-testid="cash-flow-chart"]')).toBeVisible();
  });

  test('should display recent transactions section', async ({ page }) => {
    // Check transactions section title
    await expect(page.locator('h2').filter({ hasText: 'Recent Transactions' })).toBeVisible();
    
    // Check transactions container exists
    await expect(page.locator('[data-testid="transaction-list"]')).toBeVisible();
  });

  test('should display AI forecast panel', async ({ page }) => {
    // Check forecast section title
    await expect(page.locator('h2').filter({ hasText: 'AI Forecast' })).toBeVisible();
    
    // Check forecast panel exists
    await expect(page.locator('[data-testid="forecast-panel"]')).toBeVisible();
  });

  test('should handle loading states properly', async ({ page }) => {
    // Check that loading states are handled
    // This test might need adjustment based on actual loading implementation
    await page.reload();
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
    
    // Ensure no loading indicators remain visible
    await expect(page.locator('.animate-pulse')).toHaveCount(0);
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that the dashboard is still functional
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('[data-testid="metrics-cards"]')).toBeVisible();
  });
});
