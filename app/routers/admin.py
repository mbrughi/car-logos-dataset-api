from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
import time, redis
from app.db import get_db
from app.config import settings
from app.security.admin_only import admin_only
from app.models.api_key import ApiKey

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(admin_only)])

def _get_redis():
    if not settings.REDIS_URL:
        return None
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.get("/usage")
def get_usage(db: Session = Depends(get_db)):
    """
    Ritorna uso per chiave nell'attuale finestra di rate limit.
    """
    r = _get_redis()
    window = settings.RL_WINDOW_SECONDS
    limit = settings.RL_MAX_REQUESTS
    now = int(time.time())
    bucket = now // window
    resets_in = (bucket + 1) * window - now

    # leggi tutte le chiavi dal DB e chiedi i contatori correnti
    rows = db.execute(select(ApiKey).where(ApiKey.is_active.is_(True))).scalars().all()
    data = []
    for ak in rows:
        current = 0
        if r:
            k = f"rl:{ak.key}:{bucket}"
            val = r.get(k)
            current = int(val) if val and val.isdigit() else 0
        data.append({
            "name": ak.name,
            "key": ak.key,
            "current": current,
            "limit": limit,
            "remaining": max(0, limit - current),
            "window_seconds": window,
            "resets_in": resets_in
        })
    return {
        "window_bucket": bucket,
        "resets_in": resets_in,
        "items": data
    }
