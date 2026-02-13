from playwright.sync_api import sync_playwright
import os
import time

FRONTEND = os.environ.get('FRONTEND_URL', 'http://localhost:8083')
SAMPLE = os.path.join(os.path.dirname(__file__), '..', 'sample_flows.json')

def run():
    with sync_playwright() as p:
        # Run headed so we can observe the demo when debugging locally
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        # Capture console messages and failed requests for diagnostics
        def on_console(msg):
            try:
                print(f"BROWSER CONSOLE: {msg.type}: {msg.text}")
            except Exception:
                print("BROWSER CONSOLE: <unprintable message>")

        def on_request_failed(request):
            print(f"REQUEST FAILED: {request.method} {request.url} -> {request.failure}")

        page.on('console', on_console)
        page.on('requestfailed', on_request_failed)
        page.goto(FRONTEND)

        # Wait for the file input element to be attached to the DOM (may be hidden)
        page.wait_for_selector('#fileInput', state='attached', timeout=20000)

        # Attach sample file even if the input is hidden
        input_handle = page.query_selector('#fileInput')
        if not input_handle:
            # save diagnostics
            page.screenshot(path='playwright_failure_page.png')
            with open('playwright_failure_page.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            raise SystemExit('file input not found')

        input_handle.set_input_files(SAMPLE)

        # Wait for analyze button to be visible and click it
        try:
            page.wait_for_selector('#analyzeButton', state='visible', timeout=20000)
            page.click('#analyzeButton')
        except Exception:
            # attempt clicking even if hidden
            btn = page.query_selector('#analyzeButton')
            if btn:
                btn.click()
            else:
                page.screenshot(path='playwright_failure_no_analyze.png')
                raise

        # Wait for either a classification badge or results-section active class
        try:
            page.wait_for_selector('#results-section.active, #results-section .classification-badge', timeout=30000)
        except Exception:
            # Save diagnostics on failure
            page.screenshot(path='playwright_failure_results.png')
            with open('playwright_failure_page_after_click.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            raise SystemExit('Result not found within timeout')

        # Simple check: ensure Analysis Results header or badge present
        content = page.content()
        if 'Analysis Results' not in content and 'classification-badge' not in content:
            raise SystemExit('Result not found in page')

        print('E2E: success')
        browser.close()

if __name__ == '__main__':
    run()
