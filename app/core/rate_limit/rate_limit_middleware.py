from typing import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.rate_limit.rate_limiter import RateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    AUTH_PATHS: tuple[str, ...] = (
        "/api/v1/auth/login",
        "/api/v1/auth/register",
    )

    EXCLUDED_PATHS: set[str] = {
        "/health",
        "/",
        "/favicon.ico",
        "/openapi.json",
        "/docs",
        "/redoc",
    }

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.auth_limiter = RateLimiter(capacity=5, refill_rate_per_minute=1)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        if any(request.url.path.startswith(p) for p in self.AUTH_PATHS):
            client_key = self._get_client_key(request)
            if not self.auth_limiter.is_allowed(client_key):
                return Response(
                    content='{"detail": "Demasiadas peticiones. Intenta de nuevo en 15 minutos.", "code": "RATE_LIMIT_EXCEEDED"}',
                    status_code=429,
                    media_type="application/json",
                    headers={"Retry-After": "900"},
                )

        return await call_next(request)

    @staticmethod
    def _get_client_key(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        if request.client:
            return f"ip:{request.client.host}"
        return "ip:unknown"