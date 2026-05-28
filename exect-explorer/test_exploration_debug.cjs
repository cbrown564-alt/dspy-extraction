const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const screenshotDir = path.join(__dirname, 'test_screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir);
  }

  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  
  page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
  page.on('pageerror', err => console.error('BROWSER ERROR:', err.message));

  try {
    console.log('Navigating to http://127.0.0.1:5173/...');
    await page.goto('http://127.0.0.1:5173/');
    await page.waitForTimeout(3000);

    console.log('Taking screenshot 01 (Annotator)...');
    await page.screenshot({ path: path.join(screenshotDir, '01_exect_reader_annotator.png') });

    console.log('Clicking Oracle Lens (tab)...');
    await page.getByRole('tab', { name: 'Oracle' }).click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(screenshotDir, '02_exect_reader_oracle.png') });

    console.log('Clicking Clinician Lens (tab)...');
    await page.getByRole('tab', { name: 'Clinician' }).click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(screenshotDir, '03_exect_reader_clinician.png') });

    console.log('Clicking Model Lens (tab)...');
    await page.getByRole('tab', { name: 'Model' }).click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(screenshotDir, '04_exect_reader_model.png') });

    console.log('Resetting to Annotator (tab)...');
    await page.getByRole('tab', { name: 'Annotator' }).click();
    await page.waitForTimeout(500);

    console.log('Clicking Timeline View (button)...');
    await page.getByRole('button', { name: 'Timeline', exact: true }).click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(screenshotDir, '05_exect_timeline.png') });

    console.log('Clicking Annotate View (button)...');
    await page.getByRole('button', { name: 'Annotate', exact: true }).click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(screenshotDir, '06_exect_annotate.png') });

    console.log('Clicking Runs View (button)...');
    await page.getByRole('button', { name: 'Runs', exact: true }).click();
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(screenshotDir, '07_exect_runs.png') });

    console.log('Clicking Landscape View (button)...');
    await page.getByRole('button', { name: 'Landscape', exact: true }).click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(screenshotDir, '08_exect_landscape.png') });

    console.log('Resetting to Reader View (button)...');
    await page.getByRole('button', { name: 'Reader', exact: true }).click();
    await page.waitForTimeout(500);

    console.log('Switching to Gan 2026 (button)...');
    await page.getByRole('button', { name: 'Gan 2026', exact: true }).click();
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(screenshotDir, '09_gan_reader_annotator.png') });

    console.log('Clicking next letter button...');
    const nextBtn = page.locator('.nav-arrows button').last();
    await nextBtn.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(screenshotDir, '10_gan_next_letter.png') });

    console.log('Opening shortcuts modal...');
    await page.keyboard.press('?');
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(screenshotDir, '11_shortcuts_modal.png') });

    console.log('Done!');
  } catch (error) {
    console.error('ERROR OCCURRED:', error);
  } finally {
    await browser.close();
  }
})();
