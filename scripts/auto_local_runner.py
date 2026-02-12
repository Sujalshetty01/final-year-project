#!/usr/bin/env python3
"""
Cross-platform local test/fix automation script.

Behaviors:
- Ensures project `.venv` Python is used (re-execs into it if found).
- Installs `backend/requirements.txt` with pip.
- Kills any process listening on the target port.
- Starts uvicorn serving the backend and logs to `backend_uvicorn.log`.
- Polls `/api/v1/health` then `/api/v1/ready` every 2s (timeout 60s).
- On healthy: runs `scripts/local_test_fix_runner.py` and captures output.
- If tests pass: commits and pushes with message `fix(auth): auto-runner verification`.
- If tests fail: prints failing lines and runner output.

Usage: run from repo root (works on Windows and Linux):
    python scripts/auto_local_runner.py

"""
from __future__ import annotations
import os
import sys
import time
import subprocess
import shutil
import socket
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

PORT = int(os.environ.get('BACKEND_PORT', '8001'))
BASE_URL = os.environ.get('BACKEND_BASE_URL', f'http://127.0.0.1:{PORT}/api/v1')
UVICORN_LOG = ROOT / 'backend_uvicorn.log'


def ensure_venv_and_reexec():
    # If running inside .venv, continue. Otherwise, if .venv exists, re-exec
    if os.environ.get('VIRTUAL_ENV'):
        return
    venv_dir = ROOT / '.venv'
    if not venv_dir.exists():
        print('No active virtualenv found and .venv missing; continuing with current python')
        return
    if sys.platform.startswith('win'):
        venv_py = venv_dir / 'Scripts' / 'python.exe'
    else:
        venv_py = venv_dir / 'bin' / 'python'
    if not venv_py.exists():
        print('Detected .venv but python executable not found; continuing with current python')
        return
    # Re-exec under venv python
    if Path(sys.executable).resolve() == venv_py.resolve():
        return
    print(f'Re-execing under venv python: {venv_py}')
    os.execv(str(venv_py), [str(venv_py)] + sys.argv)


def run_cmd(cmd, **kwargs):
    print('> ', ' '.join(cmd))
    return subprocess.run(cmd, **kwargs)


def install_requirements(strict: bool = True):
    req = ROOT / 'backend' / 'requirements.txt'
    if not req.exists():
        print('No backend/requirements.txt found; skipping pip install')
        return True
    print("Installing backend requirements...")
    pip_log = str(ROOT / 'scripts' / 'pip_install_output.log')
    with open(pip_log, 'w', encoding='utf-8') as f:
        r = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], stdout=f, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        print(f"pip install failed (see {pip_log})")
        # Attempt targeted installs for missing distributions parsed from pip log
        missing = parse_missing_packages_from_pip_log(pip_log)
        if missing:
            print(f"Detected missing packages: {missing}. Attempting targeted installs...")
            success = try_targeted_install(missing, pip_log)
            if success:
                print("Some targeted installs succeeded; re-running full requirements install...")
                with open(pip_log, 'a', encoding='utf-8') as f:
                    r2 = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], stdout=f, stderr=subprocess.STDOUT)
                    if r2.returncode == 0:
                        print("Re-run pip install succeeded after targeted installs.")
                    else:
                        print(f"Re-run pip install still failed (see {pip_log}). Continuing to tests anyway\n")
            else:
                print("Targeted installs did not help. Continuing to tests anyway\n")
        else:
            print("No specific missing packages detected; continuing to tests anyway\n")
        if strict:
            return False
        else:
            print('Continuing despite pip install failure (non-strict mode)')
    return r.returncode == 0


def find_pids_on_port(port: int):
    pids = set()
    try:
        if sys.platform.startswith('win'):
            out = subprocess.check_output(['netstat', '-ano'], text=True, stderr=subprocess.DEVNULL)
            import re
            # Robustly find lines that include :port and end with a numeric PID
            pattern = re.compile(rf"^(?:TCP|UDP)\s+\S+:{port}\b.*?\s(\d+)$", re.IGNORECASE)
            for line in out.splitlines():
                m = pattern.search(line)
                if m:
                    pid = m.group(1)
                    if pid.isdigit() and pid != '0':
                        pids.add(int(pid))
        else:
            # Linux / macOS: use lsof
            out = subprocess.check_output(['lsof', '-i', f':{port}', '-t'], text=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                line = line.strip()
                if line.isdigit():
                    pids.add(int(line))
    except subprocess.CalledProcessError:
        pass
    except FileNotFoundError:
        # lsof not installed on some systems
        pass
    return list(pids)


def parse_missing_packages_from_pip_log(logpath: str) -> list:
    """Parse pip install log for missing distribution/package errors.

    Returns a list of package specifiers that pip reported as missing.
    """
    missing = []
    import re
    if not os.path.exists(logpath):
        return missing
    with open(logpath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    # Common pip error patterns
    patterns = [
        r"Could not find a version that satisfies the requirement\s+([^\s,]+)",
        r"No matching distribution found for\s+([^\s,]+)",
        r"ERROR: Could not find a version that satisfies the requirement\s+([^\s,]+)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            pkg = m.group(1).strip()
            # normalize common extras like pkg==1.2.3,pkg>=1 etc — keep full spec
            if pkg and pkg not in missing:
                missing.append(pkg)
    return missing


def try_targeted_install(packages: list, pip_log: str) -> bool:
    """Attempt to pip install each package individually. Append output to pip_log.

    Returns True if at least one install succeeded (best-effort), False otherwise.
    """
    if not packages:
        return False
    any_success = False
    with open(pip_log, 'a', encoding='utf-8', errors='ignore') as f:
        for pkg in packages:
            print(f"Attempting targeted install: {pkg}")
            f.write(f"\n--- Attempting targeted install: {pkg} ---\n")
            try:
                r = subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], stdout=f, stderr=subprocess.STDOUT)
                if r.returncode == 0:
                    any_success = True
                else:
                    f.write(f"Targeted install returned {r.returncode} for {pkg}\n")
            except Exception as e:
                f.write(f"Exception during targeted install {pkg}: {e}\n")
    return any_success


def kill_pids(pids):
    for pid in pids:
        try:
            if sys.platform.startswith('win'):
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
            else:
                os.kill(pid, 9)
            print(f'SUCCESS: Terminated PID {pid}')
        except Exception as e:
            print(f'ERROR: Failed to terminate PID {pid}: {e}')


def start_uvicorn_background():
    # Start uvicorn and redirect output to UVICORN_LOG
    # Run uvicorn from the backend package cwd so imports like `from app.routes` resolve
    cmd = [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(PORT), '--log-level', 'warning']
    f = open(UVICORN_LOG, 'ab')
    kwargs = dict(stdout=f, stderr=subprocess.STDOUT, cwd=str(ROOT / 'backend'))
    if sys.platform.startswith('win'):
        # create new process group on Windows
        kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs['preexec_fn'] = os.setsid
    proc = subprocess.Popen(cmd, **kwargs)
    print(f'Started uvicorn pid={proc.pid}; logging to {UVICORN_LOG}')
    # give process a short moment
    time.sleep(0.5)
    return proc


def tail_log(path: Path, lines: int = 50):
    if not path.exists():
        return ''
    with open(path, 'rb') as f:
        try:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            size = 1024
            data = b''
            while end > 0 and data.count(b'\n') <= lines:
                read_size = min(size, end)
                f.seek(end - read_size)
                chunk = f.read(read_size)
                data = chunk + data
                end -= read_size
            return '\n'.join(line.decode(errors='replace') for line in data.splitlines()[-lines:])
        except Exception:
            f.seek(0)
            return f.read().decode(errors='replace')[-10000:]


def wait_for_healthy(timeout=60):
    deadline = time.time() + timeout
    endpoints = [f'{BASE_URL}/health', f'{BASE_URL}/ready', f'{ROOT}/api/v1/health']
    # Try health then ready
    while time.time() < deadline:
        for path in (f'{BASE_URL}/health', f'{BASE_URL}/ready'):
            try:
                import urllib.request, urllib.error
                with urllib.request.urlopen(path, timeout=3) as r:
                    if r.status == 200:
                        print('Backend healthy at', path)
                        return True
            except Exception:
                continue
        time.sleep(2)
    print('Backend not healthy after timeout')
    return False


def run_runner_and_capture():
    cmd = [sys.executable, str(ROOT / 'scripts' / 'local_test_fix_runner.py')]
    env = os.environ.copy()
    env['BACKEND_PORT'] = str(PORT)
    env['BACKEND_BASE_URL'] = BASE_URL
    print('Running local_test_fix_runner...')
    runner_log = ROOT / 'scripts' / 'runner_output.log'
    with open(runner_log, 'w', encoding='utf-8') as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env, text=True, cwd=str(ROOT))
        proc.wait()
    with open(runner_log, 'r', encoding='utf-8') as f:
        out = f.read()
    print(f'--- Runner Output (saved to {runner_log}) ---')
    print(out)
    success = proc.returncode == 0
    return success, out


def git_commit_and_push():
    # commit any changes and push
    try:
        rc = run_cmd(['git', 'add', '-A'])
        status = subprocess.check_output(['git', 'status', '--porcelain'], text=True).strip()
        if not status:
            print('No git changes to commit')
            return True
        rc = run_cmd(['git', 'commit', '-m', 'fix(auth): auto-runner verification'])
        if rc.returncode != 0:
            print('git commit failed')
            return False
        rc2 = run_cmd(['git', 'push'])
        if rc2.returncode != 0:
            print('git push failed')
            return False
        return True
    except Exception as e:
        print('Git failure', e)
        return False


def main():
    ensure_venv_and_reexec()
    install_requirements()
    pids = find_pids_on_port(PORT)
    if pids:
        print('Found processes on port', PORT, pids)
        kill_pids(pids)

    # remove old log
    try:
        if UVICORN_LOG.exists():
            UVICORN_LOG.unlink()
    except Exception:
        pass

    proc = start_uvicorn_background()
    healthy = wait_for_healthy(timeout=60)
    if not healthy:
        print('Last 50 lines of', UVICORN_LOG)
        print(tail_log(UVICORN_LOG, 50))
        print('Exiting with error')
        sys.exit(2)

    success, out = run_runner_and_capture()
    if success:
        print('All tests passed — committing and pushing changes')
        ok = git_commit_and_push()
        if not ok:
            print('Commit/push failed — please inspect git status')
            sys.exit(3)
        print('Done — tests passed and changes pushed')
        sys.exit(0)
    else:
        print('\nTests failed. Summary:')
        # print failing lines
        for line in out.splitlines():
            if line.startswith('FAIL:') or 'FINAL SUMMARY' in line or 'FAIL' in line:
                print(line)
        print('\nFull runner output above.')
        sys.exit(4)


if __name__ == '__main__':
    main()
