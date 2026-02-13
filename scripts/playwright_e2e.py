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

        # Wait for the file input to be created
        page.wait_for_selector('#fileInput', timeout=10000)

        # Attach sample file
        input_handle = page.query_selector('#fileInput')
        if not input_handle:
            raise SystemExit('file input not found')

        input_handle.set_input_files(SAMPLE)

        # Click analyze
        page.click('#analyzeButton')

        # Wait for results-section to become active
        page.wait_for_selector('#results-section.active, #results-section .classification-badge', timeout=20000)

        # Simple check: ensure Analysis Results header present
        content = page.content()
        if 'Analysis Results' not in content and 'classification-badge' not in content:
            raise SystemExit('Result not found in page')

        print('E2E: success')
        browser.close()

if __name__ == '__main__':
    run()
