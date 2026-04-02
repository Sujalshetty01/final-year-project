from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
import os
import jwt
import time
from backend.app import auth_db
from datetime import datetime, timedelta
import uuid
import logging

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


@router.post('/login', response_model=TokenResponse)
async def login(req: LoginRequest):
    # Validate against the SQLite user store (created at startup)
    ok = auth_db.verify_password(req.username, req.password)
    if not ok:
        # fallback to env vars for first-time bootstrap compatibility
        user = os.environ.get('REVIEW_USER', 'admin')
        pwd = os.environ.get('REVIEW_PASS', 'admin')
        if req.username != user or req.password != pwd:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    secret = os.environ.get('JWT_SECRET', 'dev-secret')
    # Use time.time() to compute epoch seconds to avoid naive-datetime timezone issues
    now_ts = int(time.time())
    jti = str(uuid.uuid4())
    access_payload = {'sub': req.username, 'exp': now_ts + 30 * 60, 'jti': jti}
    refresh_payload = {'sub': req.username, 'exp': now_ts + 7 * 24 * 3600, 'jti': jti}
    access_token = jwt.encode(access_payload, secret, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, secret, algorithm='HS256')
    # persist refresh token jti
    try:
        auth_db.store_refresh_token(jti, req.username, refresh_payload.get('exp'))
    except Exception as e:
        logging.getLogger(__name__).exception('Failed to store refresh token jti')
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post('/refresh', response_model=TokenResponse)
async def refresh_token(req: RefreshRequest, request: Request):
    secret = os.environ.get('JWT_SECRET', 'dev-secret')
    try:
        payload = jwt.decode(req.refresh_token, secret, algorithms=['HS256'])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    old_jti = payload.get('jti')
    if auth_db.is_refresh_revoked(old_jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token revoked or expired')
    # rotate refresh token: issue new refresh jti and revoke old
    new_jti = str(uuid.uuid4())
    now_ts = int(time.time())
    access_payload = {'sub': payload.get('sub'), 'exp': now_ts + 30 * 60, 'jti': new_jti}
    refresh_payload = {'sub': payload.get('sub'), 'exp': now_ts + 7 * 24 * 3600, 'jti': new_jti}
    access_token = jwt.encode(access_payload, secret, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, secret, algorithm='HS256')
    try:
        auth_db.store_refresh_token(new_jti, payload.get('sub'), refresh_payload.get('exp'))
        auth_db.revoke_refresh(old_jti)
    except Exception as e:
        logging.getLogger(__name__).exception('Failed to rotate refresh token jti')
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


class LogoutRequest(BaseModel):
    token: str


@router.post('/logout')
async def logout(req: LogoutRequest, request: Request):
    secret = os.environ.get('JWT_SECRET', 'dev-secret')
    try:
        payload = jwt.decode(req.token, secret, algorithms=['HS256'])
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token')
    jti = payload.get('jti')
    if not jti:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Token missing jti')
    try:
        auth_db.revoke_refresh(jti)
    except Exception:
        # fallback to in-memory revocation set
        revoked = getattr(request.app.state, 'revoked_tokens', None)
        if revoked is None:
            request.app.state.revoked_tokens = set()
            revoked = request.app.state.revoked_tokens
        revoked.add(jti)
    return {'status': 'ok'}
