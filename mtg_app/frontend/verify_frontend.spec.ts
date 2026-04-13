import { test, expect } from '@playwright/test';

test('basic UI check', async ({ page }) => {
  await page.goto('http://localhost:5173/');

  // Wait for the app to load
  await expect(page.locator('text=MTG Hub')).toBeVisible();

  // Add a card
  await page.fill('input[placeholder*="Add card by name"]', 'Grizzly Bears');
  await page.waitForTimeout(2000); // Wait for suggestions
  await page.click('button:has-text("Grizzly Bears")');

  // Verify it appears in collection
  await expect(page.locator('text=Quantity: 1')).toBeVisible();

  // Take screenshot
  await page.screenshot({ path: 'frontend-screenshot.png' });
});
