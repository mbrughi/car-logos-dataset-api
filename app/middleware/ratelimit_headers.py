from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        limit = getattr(request.state, "rl_limit", None)
        remaining = getattr(request.state, "rl_remaining", None)
        reset = getattr(request.state, "rl_reset", None)
        if limit is not None and remaining is not None and reset is not None:
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset)  # secondi al reset
        return response
