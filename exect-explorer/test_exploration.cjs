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
  
  // Go to the local dev server
  console.log('Navigating to http://127.0.0.1:5173/...');
  await page.goto('http://127.0.0.1:5173/');
  await page.waitForTimeout(3000); // Wait for loading screen to complete

  // 1. Initial view: ExECT, Reader View, Annotator Lens
  await page.screenshot({ path: path.join(screenshotDir, '01_exect_reader_annotator.png') });
  console.log('Saved 01_exect_reader_annotator.png');

  // 2. Click Oracle Lens
  console.log('Clicking Oracle Lens...');
  await page.getByRole('button', { name: 'Oracle', exact: true }).click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(screenshotDir, '02_exect_reader_oracle.png') });

  // 3. Click Clinician Lens
  console.log('Clicking Clinician Lens...');
  await page.getByRole('button', { name: 'Clinician', exact: true }).click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(screenshotDir, '03_exect_reader_clinician.png') });

  // 4. Click Model Lens
  console.log('Clicking Model Lens...');
  await page.getByRole('button', { name: 'Model', exact: true }).click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(screenshotDir, '04_exect_reader_model.png') });

  // Reset to Annotator lens for testing other views
  await page.getByRole('button', { name: 'Annotator', exact: true }).click();
  await page.waitForTimeout(500);

  // 5. Click Timeline View
  console.log('Clicking Timeline View...');
  await page.getByRole('button', { name: 'Timeline', exact: true }).click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(screenshotDir, '05_exect_timeline.png') });

  // 6. Click Annotate View
  console.log('Clicking Annotate View...');
  await page.getByRole('button', { name: 'Annotate', exact: true }).click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(screenshotDir, '06_exect_annotate.png') });

  // 7. Click Landscape View
  console.log('Clicking Landscape View...');
  await page.getByRole('button', { name: 'Landscape', exact: true }).click();
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(screenshotDir, '07_exect_landscape.png') });

  // Reset to Reader View
  await page.getByRole('button', { name: 'Reader', exact: true }).click();
  await page.waitForTimeout(500);

  // 8. Click Gan 2026 Dataset button
  console.log('Switching to Gan 2026...');
  await page.getByRole('button', { name: 'Gan 2026', exact: true }).click();
  await page.waitForTimeout(3000); // Wait for load
  await page.screenshot({ path: path.join(screenshotDir, '08_gan_reader_annotator.png') });

  // 9. Click Next navigation button
  console.log('Clicking next letter button...');
  const nextBtn = page.locator('.nav-arrows button').last();
  await nextBtn.click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(screenshotDir, '09_gan_next_letter.png') });

  // 10. Open help modal
  console.log('Pressing ? to open shortcuts...');
  await page.keyboard.press('?');
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(screenshotDir, '10_shortcuts_modal.png') });

  await browser.close();
  console.log('All tests finished successfully.');
})();
