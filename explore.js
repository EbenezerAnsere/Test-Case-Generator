require('dotenv').config();
const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page    = await browser.newPage();

  // ── login ─────────────────────────────────────────────────────────────────
  console.log('Logging in as System Admin...');
  await page.goto('https://amap-staging.amalitech-dev.net', { waitUntil: 'load', timeout: 45000 });
  await page.waitForSelector('input[placeholder="Enter email"]', { timeout: 10000 });
  await page.fill('input[placeholder="Enter email"]', process.env.STAGING_SYSTEM_ADMIN_EMAIL);
  await page.fill('input[type="password"]', process.env.STAGING_SYSTEM_ADMIN_PASSWORD);
  await page.click('button[aria-label="Button"]');
  await page.waitForURL(/dashboard|home|overview/, { timeout: 15000 });
  console.log('Logged in. URL:', page.url());
  await page.screenshot({ path: 'after_login.png' });

  // ── find dark mode toggle ─────────────────────────────────────────────────
  // look in header/navbar area for toggle/switch/button related to theme
  await page.waitForTimeout(2000);

  const themeClues = await page.evaluate(() => {
    const candidates = [];
    document.querySelectorAll('button, [role="switch"], input[type="checkbox"], svg, [aria-label]').forEach(el => {
      const txt  = (el.innerText || '').trim().toLowerCase();
      const aria = (el.getAttribute('aria-label') || '').toLowerCase();
      const cls  = (typeof el.className === 'string' ? el.className : el.className.baseVal || '').toLowerCase();
      const id   = (el.id || '').toLowerCase();
      if (/dark|light|theme|mode|toggle/.test(txt + aria + cls + id)) {
        candidates.push({
          tag: el.tagName, txt, aria, cls: cls.slice(0,60), id, role: el.getAttribute('role')
        });
      }
    });
    return candidates;
  });
  console.log('\nDark mode candidates:', JSON.stringify(themeClues, null, 2));

  // ── check body/html for dark class ────────────────────────────────────────
  const bodyInfo = await page.evaluate(() => ({
    bodyClass:  document.body.className,
    htmlClass:  document.documentElement.className,
    colorScheme: getComputedStyle(document.documentElement).colorScheme,
  }));
  console.log('\nBody/HTML state:', bodyInfo);

  // ── grab header html for manual inspection ────────────────────────────────
  const headerHtml = await page.evaluate(() => {
    const h = document.querySelector('header, nav, [role="banner"]');
    return h ? h.outerHTML.slice(0, 2000) : 'no header found';
  });
  console.log('\nHeader HTML (truncated):\n', headerHtml);

  // ── navigate to Edit profile and scroll the content container ───────────
  const profileBtn = page.getByRole('button', { name: /open profile menu/i });
  await profileBtn.scrollIntoViewIfNeeded();
  await profileBtn.click();
  await page.waitForSelector('button:has-text("Edit profile")', { timeout: 5000 });
  await page.click('button:has-text("Edit profile")');
  await page.waitForTimeout(2000);
  // scroll the scrollable section (not window)
  await page.evaluate(() => {
    const el = document.querySelector('section, main, [class*="overflow-y-auto"]');
    if (el) el.scrollTop = el.scrollHeight;
  });
  await page.waitForTimeout(800);
  await page.screenshot({ path: 'edit_profile_bottom.png' });

  // dump all visible text on edit profile page
  const editProfileText = await page.evaluate(() => document.body.innerText);
  console.log('\nEdit Profile full text:\n', editProfileText);

  // ── now try ORG ADMIN account ─────────────────────────────────────────────
  console.log('\n\n=== Testing with ORG ADMIN account ===');
  await page.goto('https://amap-staging.amalitech-dev.net', { waitUntil: 'load', timeout: 30000 });
  // logout first, then login as org admin
  try {
    await page.waitForSelector('input[placeholder="Enter email"]', { timeout: 5000 });
  } catch {
    // already on dashboard, logout first
    const pb = page.getByRole('button', { name: /open profile menu/i });
    await pb.scrollIntoViewIfNeeded();
    await pb.click();
    await page.waitForSelector('button:has-text("Logout")', { timeout: 5000 });
    await page.click('button:has-text("Logout")');
    await page.waitForSelector('input[placeholder="Enter email"]', { timeout: 15000 });
  }
  await page.fill('input[placeholder="Enter email"]', 'woyel31259@merotx.com');
  await page.fill('input[type="password"]', 'SwiftTech.1');
  await page.click('button[aria-label="Button"]');
  await page.waitForURL(/dashboard|home|overview/, { timeout: 15000 });
  console.log('Org Admin logged in. URL:', page.url());
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'org_admin_dashboard.png' });

  const orgTheme = await page.evaluate(() => ({
    htmlClass: document.documentElement.className,
    colorScheme: getComputedStyle(document.documentElement).colorScheme,
  }));
  console.log('Org Admin theme state:', orgTheme);

  // look for dark mode elements on org admin dashboard
  const orgDarkCandidates = await page.evaluate(() => {
    const candidates = [];
    document.querySelectorAll('button, [role="switch"], input[type="checkbox"], svg, [aria-label], [data-test]').forEach(el => {
      const txt  = (el.innerText || '').trim().toLowerCase();
      const aria = (el.getAttribute('aria-label') || '').toLowerCase();
      const dt   = (el.getAttribute('data-test') || '').toLowerCase();
      const cls  = (typeof el.className === 'string' ? el.className : el.className.baseVal || '').toLowerCase();
      const id   = (el.id || '').toLowerCase();
      if (/dark|light|theme|mode|appear|color.?scheme|sun|moon/.test(txt + aria + cls + id + dt)) {
        candidates.push({ tag: el.tagName, txt: txt.slice(0,60), aria, dt, cls: cls.slice(0,60) });
      }
    });
    return candidates.filter(c => !/theme-icon|sidebar/.test(c.cls + c.aria));
  });
  console.log('\nOrg Admin dark mode candidates:', JSON.stringify(orgDarkCandidates, null, 2));

  await browser.close();
})();
