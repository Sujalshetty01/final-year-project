from __future__ import annotations

import os
import sqlite3
import hashlib
import binascii
import time
from datetime import datetime

DB_PATH = os.getenv("DB_PATH") or os.path.join(os.path.dirname(__file__), '..', 'auth.db')


def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db() -> None:
    conn = _conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            salt TEXT,
            pw_hash TEXT,
            created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            jti TEXT PRIMARY KEY,
            username TEXT,
            expires_at INTEGER,
            revoked INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


def _hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    if salt_hex is None:
        salt = os.urandom(16)
    else:
        salt = binascii.unhexlify(salt_hex)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(salt).decode(), binascii.hexlify(dk).decode()


def create_user(username: str, password: str) -> None:
    conn = _conn()
    c = conn.cursor()
    salt, pw_hash = _hash_password(password)
    now = datetime.utcnow().isoformat()
    try:
        c.execute(
            "INSERT INTO users (username, salt, pw_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, salt, pw_hash, now),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def get_user(username: str) -> dict | None:
    conn = _conn()
    c = conn.cursor()
    c.execute('SELECT username, salt, pw_hash, created_at FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {'username': row[0], 'salt': row[1], 'pw_hash': row[2], 'created_at': row[3]}


def verify_password(username: str, password: str) -> bool:
    user = get_user(username)
    if not user:
        return False
    _, calc = _hash_password(password, salt_hex=user['salt'])
    return calc == user['pw_hash']


def store_refresh_token(jti: str, username: str, expires_at: int) -> None:
    conn = _conn()
    c = conn.cursor()
    c.execute(
        'INSERT OR REPLACE INTO refresh_tokens (jti, username, expires_at, revoked) VALUES (?, ?, ?, 0)',
        (jti, username, int(expires_at)),
    )
    conn.commit()
    conn.close()


def is_refresh_revoked(jti: str) -> bool:
    conn = _conn()
    c = conn.cursor()
    c.execute('SELECT revoked, expires_at FROM refresh_tokens WHERE jti = ?', (jti,))
    row = c.fetchone()
    conn.close()
    if not row:
        return True
    revoked, expires_at = row
    if revoked:
        return True
    if expires_at and int(time.time()) > int(expires_at):
        return True
    return False


def revoke_refresh(jti: str) -> None:
    conn = _conn()
    c = conn.cursor()
    c.execute('UPDATE refresh_tokens SET revoked = 1 WHERE jti = ?', (jti,))
    conn.commit()
    conn.close()
