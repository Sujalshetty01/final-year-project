#!/usr/bin/env python3
"""Headless browser tester: loads demo, injects sample flows, clicks Analyze,
captures console logs and screenshot, and writes results to out/logs/frontend_console.json
and out/screenshots/frontend_result.png
"""
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_LOG = Path('out/logs')
OUT_SCREEN = Path('out/screenshots')
OUT_LOG.mkdir(parents=True, exist_ok=True)
OUT_SCREEN.mkdir(parents=True, exist_ok=True)

sample_flows = [
    {"src_ip":"10.0.0.1","dst_ip":"8.8.8.8","protocol":"TCP","src_port":12345,"dst_port":80,"bytes_sent":1024,"bytes_received":2048,"duration":1.2},
    {"src_ip":"10.0.0.2","dst_ip":"1.1.1.1","protocol":"TCP","src_port":23456,"dst_port":443,"bytes_sent":4096,"bytes_received":1024,"duration":0.8},
    {"src_ip":"10.0.0.3","dst_ip":"9.9.9.9","protocol":"UDP","src_port":34567,"dst_port":53,"bytes_sent":128,"bytes_received":64,"duration":0.2}
]

def run():
    results = {'console': [], 'errors': []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # capture console messages
        def on_console(msg):
            try:
                results['console'].append({'type': msg.type, 'text': msg.text})
            except Exception:
                results['console'].append({'type': 'unknown', 'text': str(msg)})

        page.on('console', on_console)

        url = os.environ.get('DEMO_URL', 'http://localhost:3000')
        page.goto(url, wait_until='networkidle')

        # inject sample flows into textarea
        try:
            page.fill('#flowDataInput', JSON := json.dumps(sample_flows, indent=2))
        except Exception:
            # fallback: set value via evaluate
            page.evaluate("(data) => { const el = document.getElementById('flowDataInput'); if(el) el.value = data; }", json.dumps(sample_flows))

        # ensure analyze button exists and click
        try:
            page.click('#analyzeButton')
        except Exception as e:
            results['errors'].append(f'click failed: {e}')

        # wait for results-section to appear or a network response
        try:
            page.wait_for_selector('#results-section.active, .classification-badge', timeout=8000)
        except Exception:
            # continue anyway
            pass

        # take screenshot
        shot_path = OUT_SCREEN / 'frontend_result.png'
        page.screenshot(path=str(shot_path), full_page=True)

        # try read visible result JSON if present
        try:
            # attempt to read text of results container
            txt = page.inner_text('#results-section')
            results['rendered_results'] = txt
        except Exception:
            results['rendered_results'] = None

        browser.close()

    out_file = OUT_LOG / 'frontend_console.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(json.dumps({'console_log': str(out_file), 'screenshot': str(shot_path)}))


if __name__ == '__main__':
    run()
