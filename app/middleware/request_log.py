# app/middleware/request_log.py
import json, time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import redis
from app.config import settings

_pool = None
def _get_redis():
    global _pool
    if _pool is None and settings.REDIS_URL:
        _pool = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _pool

class RequestLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_items:int=1000, ttl_seconds:int=60*60*24*30):
        super().__init__(app)
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        r = _get_redis()
        start = time.perf_counter()
        resp: Response = await call_next(request)
        if r:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            api_key = getattr(request.state, "api_key", None)
            who = api_key or request.client.host
            k = f"log:{who}"
            entry = {
                "ts": int(time.time()),
                "method": request.method,
                "path": request.url.path,
                "status": resp.status_code,
                "ms": elapsed_ms,
                "ip": request.client.host if request.client else None,
                "ua": request.headers.get("user-agent"),
            }
            # LPUSH + LTRIM + EXPIRE
            pipe = r.pipeline()
            pipe.lpush(k, json.dumps(entry))
            pipe.ltrim(k, 0, self.max_items - 1)
            pipe.expire(k, self.ttl_seconds)
            pipe.execute()
        return resp

