"""
Rate Limiter Middleware - Conecta PRO.

Implementa rate limiting usando Redis para controle de requisicoes.
"""

import time
from typing import Callable, Optional

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.logging import logger


class RateLimiter:
    """Rate limiter usando Redis ou memoria."""

    def __init__(
        self,
        requests_limit: int = 100,
        window_seconds: int = 60,
    ):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self._cache: dict = {}  # Fallback para memoria se Redis indisponivel
        self._redis_client = None

    async def _get_redis(self):
        """Obtem cliente Redis."""
        if self._redis_client is None:
            try:
                from core.cache import get_redis
                self._redis_client = await get_redis()
            except Exception:
                self._redis_client = False  # Marca como indisponivel
        return self._redis_client if self._redis_client else None

    def _get_client_ip(self, request: Request) -> str:
        """Extrai IP do cliente."""
        # Verifica headers de proxy
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    async def _check_rate_limit_redis(
        self, key: str
    ) -> tuple[bool, int, int]:
        """Verifica rate limit usando Redis."""
        redis = await self._get_redis()
        if not redis:
            return await self._check_rate_limit_memory(key)

        try:
            current_time = int(time.time())
            window_start = current_time - self.window_seconds

            pipe = redis.pipeline()

            # Remove requests antigos
            pipe.zremrangebyscore(key, 0, window_start)

            # Adiciona request atual
            pipe.zadd(key, {str(current_time): current_time})

            # Conta requests na janela
            pipe.zcard(key)

            # Define TTL
            pipe.expire(key, self.window_seconds)

            results = await pipe.execute()
            request_count = results[2]

            remaining = max(0, self.requests_limit - request_count)
            reset_time = current_time + self.window_seconds

            is_allowed = request_count <= self.requests_limit

            return is_allowed, remaining, reset_time

        except Exception as e:
            logger.warning(f"Redis rate limit error: {e}, falling back to memory")
            return await self._check_rate_limit_memory(key)

    async def _check_rate_limit_memory(
        self, key: str
    ) -> tuple[bool, int, int]:
        """Verifica rate limit usando memoria (fallback)."""
        current_time = int(time.time())
        window_start = current_time - self.window_seconds

        # Limpa entradas antigas
        if key in self._cache:
            self._cache[key] = [
                ts for ts in self._cache[key] if ts > window_start
            ]
        else:
            self._cache[key] = []

        request_count = len(self._cache[key])

        if request_count < self.requests_limit:
            self._cache[key].append(current_time)
            remaining = self.requests_limit - request_count - 1
            return True, remaining, current_time + self.window_seconds

        return False, 0, current_time + self.window_seconds

    async def check(self, request: Request) -> tuple[bool, int, int]:
        """
        Verifica se request esta dentro do limite.

        Returns:
            tuple: (is_allowed, remaining, reset_time)
        """
        client_ip = self._get_client_ip(request)
        key = f"rate_limit:{client_ip}"

        return await self._check_rate_limit_redis(key)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting."""

    # Endpoints isentos de rate limiting
    EXEMPT_PATHS = {
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter(
            requests_limit=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )
        self.enabled = settings.rate_limit_enabled

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Processa request com rate limiting."""
        # Skip se desabilitado
        if not self.enabled:
            return await call_next(request)

        # Skip endpoints isentos
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Verifica rate limit
        is_allowed, remaining, reset_time = await self.rate_limiter.check(request)

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {request.client.host}: {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": "Muitas requisicoes. Tente novamente mais tarde.",
                    "retry_after": reset_time - int(time.time()),
                },
                headers={
                    "X-RateLimit-Limit": str(self.rate_limiter.requests_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time - int(time.time())),
                },
            )

        # Processa request
        response = await call_next(request)

        # Adiciona headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)

        return response


# Instancia global para uso direto
rate_limiter = RateLimiter(
    requests_limit=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)
