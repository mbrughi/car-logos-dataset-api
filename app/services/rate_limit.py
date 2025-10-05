import time
from typing import Callable
import redis
from fastapi import Request, HTTPException, status
from app.config import settings

_pool = None
def _get_redis():
    global _pool
    if _pool is None:
        if not settings.REDIS_URL:
            return None
        _pool = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _pool

def rate_limit_dep() -> Callable:
    r = _get_redis()
    window = settings.RL_WINDOW_SECONDS
    limit = settings.RL_MAX_REQUESTS

    async def _dep(request: Request):
        if not r or not settings.API_KEYS_ENABLED:
            return
        key = getattr(request.state, "api_key", None) or request.client.host
        now = int(time.time())
        bucket = now // window
        resets_in = (bucket + 1) * window - now
        rk = f"rl:{key}:{bucket}"

        pipe = r.pipeline()
        pipe.incr(rk, 1)
        pipe.expire(rk, window + 5)
        count, _ = pipe.execute()
        remaining = max(0, limit - int(count))

        # Salva su request.state per il middleware headers
        request.state.rl_limit = limit
        request.state.rl_remaining = remaining
        request.state.rl_reset = resets_in

        if int(count) > limit:
            # comunque esponiamo headers via middleware
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try later."
            )
    return _dep
