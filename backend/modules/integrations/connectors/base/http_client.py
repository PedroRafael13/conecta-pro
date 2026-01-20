"""
Cliente HTTP para integrações com retry, circuit breaker e rate limiting.
Sprint 33: Integration Framework
"""

import asyncio
import httpx
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Callable, TypeVar
from uuid import uuid4

from modules.integrations.connectors.base.auth import AuthStrategy
from modules.integrations.connectors.base.rate_limiter import RateLimiter, AdaptiveRateLimiter
from modules.integrations.connectors.base.exceptions import (
    ConnectorError,
    APIError,
    RateLimitError,
    ConnectionError,
    TimeoutError,
    AuthenticationError,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(str, Enum):
    """Estados do circuit breaker."""
    CLOSED = "closed"  # Normal, requisições passam
    OPEN = "open"  # Falhas, requisições bloqueadas
    HALF_OPEN = "half_open"  # Testando recovery


@dataclass
class CircuitBreakerConfig:
    """Configuração do circuit breaker."""
    failure_threshold: int = 5  # Falhas para abrir
    success_threshold: int = 2  # Sucessos para fechar
    timeout_seconds: int = 60  # Tempo para tentar novamente


@dataclass
class HTTPClientConfig:
    """Configuração do cliente HTTP."""
    base_url: str
    timeout_connect: float = 5.0
    timeout_read: float = 30.0
    timeout_write: float = 10.0
    max_retries: int = 3
    retry_backoff_base: float = 1.0
    retry_backoff_max: float = 60.0
    retry_on_status: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class RequestMetrics:
    """Métricas de uma requisição."""
    request_id: str
    method: str
    url: str
    status_code: Optional[int] = None
    duration_ms: int = 0
    retries: int = 0
    rate_limited: bool = False
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class CircuitBreaker:
    """
    Circuit breaker para proteger contra falhas em cascata.
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None, name: str = "default"):
        self.config = config or CircuitBreakerConfig()
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()

    async def can_execute(self) -> bool:
        """Verifica se pode executar requisição."""
        async with self._lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                # Verificar se já passou timeout
                if self.last_failure_time:
                    elapsed = time.monotonic() - self.last_failure_time
                    if elapsed >= self.config.timeout_seconds:
                        self.state = CircuitState.HALF_OPEN
                        self.success_count = 0
                        logger.info(f"[{self.name}] Circuit breaker: OPEN -> HALF_OPEN")
                        return True
                return False

            # HALF_OPEN - permite tentativas
            return True

    async def record_success(self) -> None:
        """Registra sucesso."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info(f"[{self.name}] Circuit breaker: HALF_OPEN -> CLOSED")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    async def record_failure(self) -> None:
        """Registra falha."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning(f"[{self.name}] Circuit breaker: HALF_OPEN -> OPEN")
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning(f"[{self.name}] Circuit breaker: CLOSED -> OPEN")

    def reset(self) -> None:
        """Reseta o circuit breaker."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None


class IntegrationHTTPClient:
    """
    Cliente HTTP otimizado para integrações.
    Inclui: retry, circuit breaker, rate limiting, métricas.
    """

    def __init__(
        self,
        config: HTTPClientConfig,
        auth: Optional[AuthStrategy] = None,
        rate_limiter: Optional[RateLimiter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        connector_name: str = "unknown"
    ):
        self.config = config
        self.auth = auth
        self.rate_limiter = rate_limiter or RateLimiter(
            requests_per_second=10,
            name=connector_name
        )
        self.circuit_breaker = circuit_breaker or CircuitBreaker(name=connector_name)
        self.connector_name = connector_name

        # Cliente httpx
        self._client: Optional[httpx.AsyncClient] = None

        # Métricas
        self._metrics: List[RequestMetrics] = []
        self._total_requests = 0
        self._total_errors = 0

    async def __aenter__(self) -> "IntegrationHTTPClient":
        """Context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.close()

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Garante que o cliente está criado."""
        if self._client is None:
            timeout = httpx.Timeout(
                connect=self.config.timeout_connect,
                read=self.config.timeout_read,
                write=self.config.timeout_write,
                pool=5.0
            )

            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=timeout,
                headers=self.config.headers,
                follow_redirects=True
            )

            # Aplicar autenticação
            if self.auth:
                await self.auth.authenticate(self._client)

        return self._client

    async def close(self) -> None:
        """Fecha o cliente."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        skip_rate_limit: bool = False,
        correlation_id: Optional[str] = None
    ) -> httpx.Response:
        """
        Executa requisição HTTP com retry e rate limiting.

        Args:
            method: Método HTTP
            path: Caminho relativo
            params: Query parameters
            json: Body JSON
            data: Form data
            headers: Headers adicionais
            timeout: Timeout customizado
            skip_rate_limit: Pular rate limiting
            correlation_id: ID para correlação de logs

        Returns:
            Response HTTP

        Raises:
            ConnectorError: Em caso de falha após retries
        """
        request_id = correlation_id or str(uuid4())[:8]
        metrics = RequestMetrics(
            request_id=request_id,
            method=method,
            url=f"{self.config.base_url}{path}"
        )

        start_time = time.monotonic()
        last_error: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                # Verificar circuit breaker
                if not await self.circuit_breaker.can_execute():
                    raise ConnectorError(
                        "Circuit breaker aberto",
                        connector=self.connector_name,
                        error_code="CIRCUIT_OPEN",
                        recoverable=True,
                        retry_after=self.circuit_breaker.config.timeout_seconds
                    )

                # Rate limiting
                if not skip_rate_limit:
                    wait_time = await self.rate_limiter.acquire()
                    if wait_time > 0:
                        metrics.rate_limited = True
                        logger.debug(
                            f"[{self.connector_name}] Rate limit wait: {wait_time:.2f}s"
                        )

                # Refresh auth se necessário
                client = await self._ensure_client()
                if self.auth:
                    await self.auth.refresh_if_needed(client)

                # Executar requisição
                response = await client.request(
                    method=method,
                    url=path,
                    params=params,
                    json=json,
                    data=data,
                    headers=headers,
                    timeout=timeout
                )

                # Verificar status
                if response.status_code == 429:
                    # Rate limit do servidor
                    retry_after = int(response.headers.get("Retry-After", 60))
                    metrics.rate_limited = True

                    if isinstance(self.rate_limiter, AdaptiveRateLimiter):
                        await self.rate_limiter.report_rate_limit(retry_after)

                    raise RateLimitError(
                        connector=self.connector_name,
                        retry_after=retry_after
                    )

                if response.status_code >= 500:
                    # Erro do servidor
                    raise APIError(
                        f"Erro do servidor: {response.status_code}",
                        connector=self.connector_name,
                        status_code=response.status_code,
                        response_body=response.text[:500]
                    )

                if response.status_code == 401:
                    # Não autorizado
                    raise AuthenticationError(
                        "Requisição não autorizada",
                        connector=self.connector_name
                    )

                if response.status_code == 404:
                    # Not found - não fazer retry
                    raise APIError(
                        "Recurso não encontrado",
                        connector=self.connector_name,
                        status_code=404
                    )

                # Sucesso
                await self.circuit_breaker.record_success()

                if isinstance(self.rate_limiter, AdaptiveRateLimiter):
                    await self.rate_limiter.report_success()

                # Métricas
                metrics.status_code = response.status_code
                metrics.duration_ms = int((time.monotonic() - start_time) * 1000)
                metrics.retries = attempt
                self._metrics.append(metrics)
                self._total_requests += 1

                logger.debug(
                    f"[{self.connector_name}] {method} {path} -> "
                    f"{response.status_code} ({metrics.duration_ms}ms, {attempt} retries)"
                )

                return response

            except (httpx.ConnectError, httpx.ConnectTimeout) as e:
                last_error = ConnectionError(
                    f"Erro de conexão: {str(e)}",
                    connector=self.connector_name,
                    original_error=e
                )
                await self.circuit_breaker.record_failure()

            except httpx.ReadTimeout as e:
                last_error = TimeoutError(
                    f"Timeout de leitura",
                    connector=self.connector_name,
                    timeout_seconds=int(self.config.timeout_read)
                )
                await self.circuit_breaker.record_failure()

            except RateLimitError as e:
                last_error = e
                # Aguardar retry_after
                if attempt < self.config.max_retries:
                    await asyncio.sleep(e.retry_after or 60)
                continue

            except APIError as e:
                if e.status_code and e.status_code < 500:
                    # Erros 4xx (exceto 429) não são recuperáveis
                    metrics.status_code = e.status_code
                    metrics.error = str(e)
                    metrics.duration_ms = int((time.monotonic() - start_time) * 1000)
                    self._metrics.append(metrics)
                    self._total_errors += 1
                    raise

                last_error = e
                await self.circuit_breaker.record_failure()

            except AuthenticationError:
                # Não fazer retry em erros de auth
                raise

            except Exception as e:
                last_error = ConnectorError(
                    f"Erro inesperado: {str(e)}",
                    connector=self.connector_name,
                    details={"error_type": type(e).__name__}
                )
                await self.circuit_breaker.record_failure()

            # Backoff exponencial para retry
            if attempt < self.config.max_retries:
                delay = min(
                    self.config.retry_backoff_base * (2 ** attempt),
                    self.config.retry_backoff_max
                )
                logger.warning(
                    f"[{self.connector_name}] Tentativa {attempt + 1} falhou. "
                    f"Retry em {delay:.1f}s"
                )
                await asyncio.sleep(delay)

        # Todas as tentativas falharam
        metrics.error = str(last_error) if last_error else "Unknown error"
        metrics.duration_ms = int((time.monotonic() - start_time) * 1000)
        metrics.retries = self.config.max_retries
        self._metrics.append(metrics)
        self._total_errors += 1

        raise last_error or ConnectorError(
            "Falha após máximo de tentativas",
            connector=self.connector_name
        )

    # Métodos de conveniência
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """GET request."""
        return await self.request("GET", path, params=params, **kwargs)

    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """POST request."""
        return await self.request("POST", path, json=json, data=data, **kwargs)

    async def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """PUT request."""
        return await self.request("PUT", path, json=json, **kwargs)

    async def patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """PATCH request."""
        return await self.request("PATCH", path, json=json, **kwargs)

    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """DELETE request."""
        return await self.request("DELETE", path, **kwargs)

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do cliente."""
        recent_metrics = self._metrics[-100:]  # Últimas 100

        success_count = sum(1 for m in recent_metrics if m.status_code and m.status_code < 400)
        error_count = sum(1 for m in recent_metrics if m.error)
        rate_limited_count = sum(1 for m in recent_metrics if m.rate_limited)

        durations = [m.duration_ms for m in recent_metrics if m.duration_ms > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "connector": self.connector_name,
            "total_requests": self._total_requests,
            "total_errors": self._total_errors,
            "recent_success": success_count,
            "recent_errors": error_count,
            "recent_rate_limited": rate_limited_count,
            "avg_duration_ms": avg_duration,
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "rate_limiter_stats": self.rate_limiter.get_stats(),
        }
