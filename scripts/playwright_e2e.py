from playwright.sync_api import sync_playwright
import os
import time

FRONTEND = os.environ.get('FRONTEND_URL', 'http://localhost:8082')
SAMPLE = os.path.join(os.path.dirname(__file__), '..', 'sample_flows.json')

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(FRONTEND)

        # Wait for the file input element to be present (it may be hidden)
        page.wait_for_selector('#fileInput', state='attached', timeout=10000)

        # Wait for Analyze button to be visible
        page.wait_for_selector('#analyzeButton', state='visible', timeout=10000)

        # Attach sample file (this should trigger change event)
        input_handle = page.query_selector('#fileInput')
        if not input_handle:
            raise SystemExit('file input not found')
        input_handle.set_input_files(SAMPLE)

        # Give UI a moment to process the file input
        page.wait_for_timeout(500)

        # Click analyze
        page.click('#analyzeButton')

        # Wait for either the classification badge OR an alert message (success/error)
        # This makes the E2E more robust to timing and to the UI showing alerts on failure.
        try:
            page.wait_for_selector('#results-section .classification-badge', state='visible', timeout=30000)
            found_badge = True
        except Exception:
            # If badge not found, check for alerts
            found_badge = False

        # Also wait briefly for any alert elements to appear
        try:
            page.wait_for_selector('#alerts .alert', state='visible', timeout=2000)
            found_alert = True
        except Exception:
            found_alert = False

        # Simple check: ensure we observed either a badge or an alert
        content = page.content()
        if not found_badge and not found_alert:
            # Dump page content for debugging
            print('--- PAGE CONTENT START ---')
            print(content)
            print('--- PAGE CONTENT END ---')
            # Also take a screenshot for inspection
            try:
                screenshot_path = os.path.join(os.path.dirname(__file__), 'playwright_failure.png')
                page.screenshot(path=screenshot_path, full_page=True)
                print(f'Screenshot saved to {screenshot_path}')
            except Exception as e:
                print('Failed to save screenshot:', e)
            raise SystemExit('Result not found in page (no badge or alert)')
        if found_alert and not found_badge:
            # If an error alert is present, fail the test and include alert text
            # Prefer to read the first alert text
            alert_el = page.query_selector('#alerts .alert')
            alert_text = alert_el.inner_text() if alert_el else 'unknown alert'
            print('--- PAGE CONTENT START ---')
            print(content)
            print('--- PAGE CONTENT END ---')
            raise SystemExit(f'E2E failed: alert shown: {alert_text}')

        print('E2E: success')
        browser.close()

if __name__ == '__main__':
    run()
