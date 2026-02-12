#!/usr/bin/env python3
import json
import re
from pathlib import Path

# Smart fixer for common JSON escape problems

def fix_text(text: str) -> str:
    orig = text
    # 1) Fix \u followed by 1-3 hex digits -> pad with leading zeros to 4 digits
    def pad_u(m):
        hexpart = m.group(1)
        return "\\u" + hexpart.zfill(4)
    text = re.sub(r"(?<!\\)\\u([0-9A-Fa-f]{1,3})(?![0-9A-Fa-f])", pad_u, text)

    # 2) If \u is followed by a non-hex (invalid), escape the backslash so it's literal
    text = re.sub(r"(?<!\\)\\u(?=[^0-9A-Fa-f])", r"\\\\u", text)

    # 3) Fix Windows drive letter paths like C:\Users\ -> C:\\Users\\ (double backslashes)
    text = re.sub(r"([A-Za-z]:)\\(?![\\/])", r"\1\\\\", text)

    # 4) Escape LaTeX/other single backslashes in strings not part of valid JSON escapes
    # We'll double backslashes that are not already escaped and not part of known JSON escapes
    text = re.sub(r"(?<!\\)\\(?![\"\\/bfnrtu])", r"\\\\", text)

    return text


def validate_and_format(path: Path) -> bool:
    # Read using utf-8-sig to tolerate files that include a BOM
    try:
        text = path.read_text(encoding="utf-8-sig")
    except Exception:
        text = path.read_text(encoding="utf-8")
    try:
        obj = json.loads(text)
        # Already valid JSON; write formatted version
        path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return True
    except Exception as e:
        # Try to apply fixes
        fixed = fix_text(text)
        try:
            obj = json.loads(fixed)
            path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return True
        except Exception as e2:
            # As a last resort, attempt to escape all backslashes inside quotes
            # This brute-force step targets remaining bad escapes
            def escape_in_quotes(s):
                out = []
                i = 0
                in_str = False
                while i < len(s):
                    ch = s[i]
                    if ch == '"':
                        # detect if quote is escaped
                        back = 0
                        j = i-1
                        while j >=0 and s[j] == '\\':
                            back += 1
                            j -= 1
                        if back %2 == 0:
                            in_str = not in_str
                        out.append(ch)
                        i += 1
                    else:
                        if in_str and ch == '\\':
                            # double it
                            out.append('\\\\')
                            i += 1
                        else:
                            out.append(ch)
                            i += 1
                return ''.join(out)
            brute = escape_in_quotes(text)
            try:
                obj = json.loads(brute)
                path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                return True
            except Exception as e3:
                print(f"Failed to fix {path}: {e3}")
                return False


if __name__ == '__main__':
    import sys
    root = Path('.').resolve()
    # find JSON files recursively
    files = list(root.rglob('*.json'))
    if len(sys.argv) > 1:
        files = [Path(p) for p in sys.argv[1:]]
    changed = []
    failed = []
    for f in files:
        # skip node_modules, .git, virtual envs and cache directories
        if any(p in f.parts for p in ('node_modules', '.git', '.venv', 'venv', '__pycache__')):
            continue
        # also skip site-packages inside a venv discovered by rglob
        if '\\Lib\\site-packages\\' in str(f) or '/Lib/site-packages/' in str(f):
            continue
        ok = validate_and_format(f)
        if ok:
            changed.append(str(f))
        else:
            failed.append(str(f))
    print('Processed files:', len(files))
    if changed:
        print('Fixed/validated:', '\n'.join(changed))
    if failed:
        print('Failed to fix:', '\n'.join(failed))
    if failed:
        sys.exit(2)
    sys.exit(0)
