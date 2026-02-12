#!/usr/bin/env python3
import json
from pathlib import Path
import re

ROOT = Path('.').resolve()

def iter_json_files(root):
    for p in root.rglob('*.json'):
        if any(part in p.parts for part in ('node_modules', '.git', '.venv', 'venv', '__pycache__')):
            continue
        if 'Lib\\site-packages' in str(p) or 'Lib/site-packages' in str(p):
            continue
        yield p

latex_re = re.compile(r"\\[A-Za-z]+")
windows_path_re = re.compile(r"[A-Za-z]:\\")

results = {}

for f in iter_json_files(ROOT):
    try:
        text = f.read_text(encoding='utf-8')
        data = json.loads(text)
    except Exception:
        # skip files that can't be parsed
        continue
    matches = []
    def walk(obj, path):
        if isinstance(obj, dict):
            for k,v in obj.items():
                walk(v, path + [str(k)])
        elif isinstance(obj, list):
            for i,v in enumerate(obj):
                walk(v, path + [f"[{i}]"])
        elif isinstance(obj, str):
            s = obj
            # find LaTeX-like commands
            la = latex_re.findall(s)
            wp = windows_path_re.findall(s)
            # find any backslash characters
            if '\\' in s:
                backslash_present = True
            elif '\\' not in s and '\\' in s:
                backslash_present = True
            else:
                backslash_present = '\\' in s or '\\' in s
            # Actually just check for backslash char
            if '\\' in s:
                pass
            # In Python string from JSON, backslashes appear as '\\' literal only if escape sequences present.
            # Simpler: check for backslash char
            if '\\' in s or '\\' in s:
                pass
            if '\\' in s:
                pass
            # Check for backslash char
            if '\\' in s:
                pass
            # Use direct check for backslash
            if '\\' in s or '\\' in s:
                pass
            # Real check
            if '\\' in s:
                pass
            # The above is noisy due to escaping; do final checks using raw content matchers on original text
            # We'll instead search within the JSON-encoded substring
            enc = json.dumps(s)
            # enc starts and ends with quotes
            # look for backslash sequences in enc
            backslash_seq = re.search(r'(?<!\\)\\(?!["\\/bfnrtu])', enc)
            if la or wp or backslash_seq:
                matches.append({
                    'path': '.'.join(path),
                    'value_preview': s[:200],
                    'latex': la,
                    'windows_paths': wp,
                    'raw_has_unescaped_backslash': bool(backslash_seq)
                })
    walk(data, [])
    if matches:
        results[str(f)] = matches

# print concise report
if not results:
    print('No LaTeX/backslash issues found in project JSON files.')
else:
    for fname, matches in results.items():
        print(f'File: {fname}')
        for m in matches:
            print('  Path:', m['path'])
            print('   Preview:', m['value_preview'])
            if m['latex']:
                print('   LaTeX cmds:', m['latex'])
            if m['windows_paths']:
                print('   Windows paths:', m['windows_paths'])
            if m['raw_has_unescaped_backslash']:
                print('   Contains potentially unescaped backslash sequences in JSON encoding')
        print()
