from __future__ import annotations

from fastapi import APIRouter
import os
import sqlite3
from backend.app.auth_db import DB_PATH, get_user

router = APIRouter()


@router.get('/debug/auth')
async def auth_debug():
    admin = os.environ.get('REVIEW_USER', 'admin')
    try:
        user = get_user(admin) is not None
    except Exception:
        user = False
    info = {}
    try:
        cn = sqlite3.connect(DB_PATH)
        cur = cn.cursor()
        cur.execute("SELECT COUNT(*) FROM refresh_tokens")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM refresh_tokens WHERE revoked=1")
        revoked = cur.fetchone()[0]
        cn.close()
        info.update({'refresh_tokens_total': int(total), 'refresh_tokens_revoked': int(revoked)})
    except Exception as e:
        info.update({'refresh_tokens_total': None, 'refresh_tokens_revoked': None, 'error': str(e)})

    return {'admin_exists': user, **info}
