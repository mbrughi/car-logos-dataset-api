import hmac, os
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings
from app.db import get_db
from app.models.api_key import ApiKey

def _constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())

def _is_admin_key(key: str) -> bool:
    raw = settings.ADMIN_API_KEYS or ""
    admin_keys = [k.strip() for k in raw.split(",") if k.strip()]
    return key in admin_keys

def require_api_key(db: Session = Depends(get_db)):
    if not settings.API_KEYS_ENABLED:
        return None
    header_name = settings.API_KEY_HEADER

    async def _dep(request: Request):
        provided = request.headers.get(header_name)
        if not provided:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
        row = db.execute(select(ApiKey).where(ApiKey.key == provided, ApiKey.is_active.is_(True))).scalar_one_or_none()
        if not row or not _constant_time_equal(row.key, provided):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
        request.state.api_key = row.key
        request.state.api_consumer = row.name
        request.state.is_admin = _is_admin_key(row.key)
        return row
    return _dep
