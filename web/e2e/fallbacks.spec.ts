import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test('UI Fallbacks: Reader 503 fallback form, StatusStrip reader down, Desk message offline fallback, and Driver denied geolocation', async ({
  page,
  context,
}) => {
  await page.goto('/desk');
  const passcodeInput = page.locator('#passcode-input');
  if (await passcodeInput.isVisible({ timeout: 2000 }).catch(() => false)) {
    await passcodeInput.fill('change-me');
    await page.locator('#passcode-submit').click();
  }
  await expect(page.locator('#desk-page')).toBeVisible();

  // 1. Network failure on Desk message panel -> still renders fallback message with "Not sent: copy or call"
  await page.route('**/api/slots/*/message', (route) => route.abort('failed'));

  const demoRow = page.locator('#req-row-1');
  await demoRow.click();
  await expect(page.locator('#request-detail-panel')).toBeVisible();
  await page.locator('#btn-panel-message').click();

  const msgContainer = page.locator('#slot-message-container');
  await expect(msgContainer).toBeVisible();
  await expect(msgContainer).toContainText('Not sent: copy or call');
  await expect(msgContainer.locator('#btn-copy-msg')).toBeVisible();
  await expect(msgContainer.locator('#btn-call-farmer')).toBeVisible();

  await page.unroute('**/api/slots/*/message');
  await page.locator('.panel-close-btn').click();

  // 2. Reader 503 on /intake -> shows "Reader unavailable: type the rows" and opens manual form beside photo
  await page.route('**/api/intake/register-photo', (route) =>
    route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({
        error_code: 'READER_UNAVAILABLE',
        message: 'Reader unavailable: type the rows.',
        details: { intake_id: 999 },
      }),
    }),
  );

  // Also simulate health reporting reader: "down"
  await page.route('**/api/health', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'ok',
        database: 'connected',
        reader: 'down',
        messaging: 'screen+wa_link',
        satellite: 'disabled',
        today: '2026-10-25',
        demo_clock: false,
        version: '0.1',
      }),
    }),
  );

  await page.goto('/intake');
  await expect(page.locator('#intake-page')).toBeVisible();
  await expect(page.locator('#dep-pill-reader')).toContainText('down');

  const sampleImg = path.resolve(__dirname, '../../tests/fixtures/sample_field.jpg');
  await page.locator('#intake-file-input').setInputFiles(sampleImg);

  await expect(page.locator('#intake-error-banner')).toContainText(
    'Reader unavailable: type the rows',
  );
  await expect(page.locator('#intake-fallback-layout')).toBeVisible();
  await expect(page.locator('#new-request-form')).toBeVisible();

  await page.unroute('**/api/intake/register-photo');
  await page.unroute('**/api/health');

  // 3. Location permission denied on Driver page -> job still closes, badged "position self-reported"
  await context.clearPermissions(); // Deny geolocation

  await page.route('**/api/slots/*/start', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        slot_id: 1,
        status: 'in_progress',
        evidence: {
          kind: 'start',
          lat: null,
          lon: null,
          accuracy_m: null,
          distance_to_plot_m: null,
          plausible: false,
          position_state: 'not_given',
          photo: 'present',
          timestamp: new Date().toISOString(),
        },
        flags: [],
        needs_review: false,
        record_url: null,
      }),
    }),
  );

  await page.goto('/desk');
  await page.locator('#tab-machines').click();
  const driverLinkEl = page.locator('#machine-card-1 a[href^="/driver/"]');
  const driverPath = (await driverLinkEl.getAttribute('href'))!;

  await page.goto(driverPath);
  const scheduledJob = page.locator('.driver-job-card.card-status-scheduled').first();
  await scheduledJob.click();

  const startFixture = path.resolve(__dirname, '../../tests/fixtures/start_field.jpg');
  await page.locator('#driver-camera-input').setInputFiles(startFixture);
  await page.locator('#btn-start-job').click();

  await expect(page.locator('#evidence-summary-ticks')).toBeVisible({ timeout: 15000 });
  await expect(page.locator('#evidence-summary-ticks')).toContainText(
    'position self-reported',
  );

  await page.unroute('**/api/slots/*/start');
});
