const { test, expect } = require('@playwright/test');
require('dotenv').config();

const ADMIN_EMAIL = process.env.STAGING_SYSTEM_ADMIN_EMAIL;
const ADMIN_PASS  = process.env.STAGING_SYSTEM_ADMIN_PASSWORD;
const ORG_EMAIL   = process.env.STAGING_ORG_ADMIN_EMAIL;
const ORG_PASS    = process.env.STAGING_ORG_ADMIN_PASSWORD;
const BASE_URL    = process.env.STAGING_BASE_URL;

// Selector candidates for the dark mode toggle
const TOGGLE_SELECTORS = [
  '[aria-label*="dark mode" i]',
  '[aria-label*="light mode" i]',
  '[aria-label*="toggle theme" i]',
  '[data-test*="theme-toggle"]',
  '[data-test*="dark-mode"]',
  'button:has([src*="moon"])',
  'button:has([src*="sun"])',
];

async function login(page, email, password) {
  await page.goto(BASE_URL, { waitUntil: 'load', timeout: 30000 });
  await page.waitForSelector('input[placeholder="Enter email"]', { timeout: 10000 });
  await page.fill('input[placeholder="Enter email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[aria-label="Button"]');
  await page.waitForURL(/dashboard|home|overview/, { timeout: 15000 });
  await page.waitForTimeout(1000);
}

async function getTheme(page) {
  return page.evaluate(() => document.documentElement.className);
}

// Finds the toggle on the page; opens profile menu first if not immediately visible
async function findThemeToggle(page) {
  for (const sel of TOGGLE_SELECTORS) {
    if (await page.locator(sel).first().isVisible({ timeout: 500 }).catch(() => false)) {
      return page.locator(sel).first();
    }
  }
  const profileBtn = page.getByRole('button', { name: /open profile menu/i });
  if (await profileBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
    await profileBtn.click();
    await page.waitForTimeout(800);
    for (const sel of TOGGLE_SELECTORS) {
      if (await page.locator(sel).first().isVisible({ timeout: 500 }).catch(() => false)) {
        return page.locator(sel).first();
      }
    }
  }
  return null;
}

test.describe('DK26-139 — Dark Mode (System Admin)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ADMIN_EMAIL, ADMIN_PASS);
  });

  test('TC-DM-001: Dark mode toggle is visible in profile or header', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(
      toggle,
      'TC-DM-001 FAIL: Dark mode toggle not found — feature may not be deployed to staging yet'
    ).not.toBeNull();
    await expect(toggle).toBeVisible();
  });

  test('TC-DM-002: Activating dark mode — UI switches instantly without page reload', async ({ page }) => {
    expect(await getTheme(page), 'Precondition: default theme should be light-theme').toContain('light-theme');

    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-002 FAIL: Dark mode toggle not found').not.toBeNull();

    const urlBefore = page.url();
    await toggle.click();
    await page.waitForTimeout(500);

    expect(page.url()).toBe(urlBefore);  // no navigation occurred
    expect(await getTheme(page), 'html class should switch to dark-theme').toContain('dark-theme');
  });

  test('TC-DM-003: Dark mode applies to Dashboard', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-003 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();
    await page.waitForTimeout(500);

    await page.goto(BASE_URL + '/dashboard/home', { waitUntil: 'load' });
    await page.waitForTimeout(1000);

    expect(await getTheme(page), 'Dashboard should be in dark-theme').toContain('dark-theme');
    await expect(page.locator('[data-test="page-title"], h1').first()).toBeVisible();
  });

  test('TC-DM-004: Dark mode applies to Admin pages (User Management)', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-004 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();
    await page.waitForTimeout(500);

    await page.goto(BASE_URL + '/dashboard/user-management', { waitUntil: 'load' });
    await page.waitForTimeout(1000);

    expect(await getTheme(page), 'User Management page should be in dark-theme').toContain('dark-theme');
    await expect(page.locator('[data-test="page-title"], h1').first()).toBeVisible();
  });

  test('TC-DM-005: Dark mode applies to modals and dialogs', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-005 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();
    await page.waitForTimeout(500);
    expect(await getTheme(page)).toContain('dark-theme');

    // Open the Invite New User modal
    const inviteBtn = page.getByRole('button', { name: /invite new user/i });
    await inviteBtn.click();
    await page.waitForTimeout(1000);

    const modal = page.locator('[role="dialog"], mat-dialog-container, [class*="modal"]').first();
    await expect(modal, 'Modal should open in dark mode').toBeVisible();

    const bgColor = await modal.evaluate(el => getComputedStyle(el).backgroundColor);
    console.log('  Modal background in dark mode:', bgColor);
    expect(await getTheme(page)).toContain('dark-theme');
  });

  test('TC-DM-006: Dark mode contrast — heading text visible (spot check)', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-006 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();
    await page.waitForTimeout(500);

    const heading = page.locator('[data-test="page-title"], h1').first();
    await expect(heading).toBeVisible();
    const color = await heading.evaluate(el => getComputedStyle(el).color);
    console.log('  Heading color in dark mode:', color);
    // Fail if text is invisible (black text on dark background)
    expect(color, 'Heading should not be black on dark background').not.toBe('rgba(0, 0, 0, 1)');
  });

  test('TC-DM-007: Dark mode persists after page refresh', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-007 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();
    await page.waitForTimeout(500);
    expect(await getTheme(page)).toContain('dark-theme');

    await page.reload({ waitUntil: 'load' });
    await page.waitForTimeout(1500);

    expect(await getTheme(page), 'Dark mode should persist after page refresh').toContain('dark-theme');
  });

  test('TC-DM-008: Dark mode persists across logout and re-login', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-008 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();
    await page.waitForTimeout(500);

    // Logout
    const profileBtn = page.getByRole('button', { name: /open profile menu/i });
    await profileBtn.click();
    await page.waitForSelector('button:has-text("Logout")', { timeout: 5000 });
    await page.click('button:has-text("Logout")');
    await page.waitForSelector('input[placeholder="Enter email"]', { timeout: 15000 });

    // Re-login
    await login(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.waitForTimeout(1500);

    expect(await getTheme(page), 'Dark mode should persist after re-login').toContain('dark-theme');
  });

  test('TC-DM-009: Disable dark mode — UI returns to light theme', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-009 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();  // Enable
    await page.waitForTimeout(500);
    expect(await getTheme(page)).toContain('dark-theme');

    await toggle.click();  // Disable
    await page.waitForTimeout(500);

    expect(await getTheme(page), 'UI should return to light-theme after disabling').toContain('light-theme');
  });
});

test.describe('DK26-139 — Dark Mode (Org Admin)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, ORG_EMAIL, ORG_PASS);
  });

  test('TC-DM-001 (Org Admin): Dark mode toggle is visible', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-001 FAIL: Dark mode toggle not found for Org Admin').not.toBeNull();
    await expect(toggle).toBeVisible();
  });

  test('TC-DM-002 (Org Admin): Toggle activates dark mode', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-002 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();
    await page.waitForTimeout(500);
    expect(await getTheme(page), 'Org Admin dark mode should activate').toContain('dark-theme');
  });

  test('TC-DM-007 (Org Admin): Dark mode persists after page refresh', async ({ page }) => {
    const toggle = await findThemeToggle(page);
    expect(toggle, 'TC-DM-007 FAIL: Dark mode toggle not found').not.toBeNull();
    await toggle.click();
    await page.waitForTimeout(500);

    await page.reload({ waitUntil: 'load' });
    await page.waitForTimeout(1500);

    expect(await getTheme(page), 'Org Admin dark mode should persist after refresh').toContain('dark-theme');
  });
});
