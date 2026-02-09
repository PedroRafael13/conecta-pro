"""
Rate Limiter para conectores de integração.
Sprint 33: Integration Framework
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuração de rate limiting."""

    requests_per_second: float | None = None
    requests_per_minute: float | None = None
    requests_per_hour: float | None = None
    burst_size: int = 1  # Quantas requisições podem ser feitas em burst


@dataclass
class RateLimitStats:
    """Estatísticas de rate limiting."""

    total_requests: int = 0
    total_waits: int = 0
    total_wait_time_ms: int = 0
    rate_limit_hits: int = 0


class RateLimiter:
    """
    Rate limiter baseado em token bucket algorithm.
    Thread-safe para uso com asyncio.
    """

    def __init__(
        self,
        requests_per_second: float | None = None,
        requests_per_minute: float | None = None,
        requests_per_hour: float | None = None,
        burst_size: int = 1,
        name: str | None = None,
    ):
        """
        Inicializa o rate limiter.

        Args:
            requests_per_second: Limite por segundo
            requests_per_minute: Limite por minuto
            requests_per_hour: Limite por hora
            burst_size: Tamanho do burst permitido
            name: Nome para logging
        """
        self.name = name or "RateLimiter"

        # Calcular o rate mais restritivo
        self.rate = self._calculate_rate(requests_per_second, requests_per_minute, requests_per_hour)
        self.burst_size = max(1, burst_size)

        # Token bucket
        self.tokens = float(burst_size)
        self.last_update = time.monotonic()

        # Lock para thread safety
        self._lock = asyncio.Lock()

        # Estatísticas
        self.stats = RateLimitStats()

        # Histórico de timestamps para rate tracking
        self._request_history: deque[float] = deque(maxlen=1000)

        logger.debug(f"[{self.name}] Inicializado: rate={self.rate}/s, burst={burst_size}")

    @staticmethod
    def _calculate_rate(per_second: float | None, per_minute: float | None, per_hour: float | None) -> float:
        """Calcula o rate mais restritivo em requisições por segundo."""
        rates = []
        if per_second:
            rates.append(per_second)
        if per_minute:
            rates.append(per_minute / 60)
        if per_hour:
            rates.append(per_hour / 3600)

        if not rates:
            # Default: 10 req/s
            return 10.0

        return min(rates)

    def _refill_tokens(self) -> None:
        """Reabastece tokens baseado no tempo decorrido."""
        now = time.monotonic()
        elapsed = now - self.last_update
        self.last_update = now

        # Adiciona tokens proporcionalmente ao tempo
        self.tokens = min(self.burst_size, self.tokens + (elapsed * self.rate))

    async def acquire(self, tokens: int = 1) -> float:
        """
        Adquire tokens, aguardando se necessário.

        Args:
            tokens: Número de tokens a adquirir

        Returns:
            Tempo de espera em segundos (0 se não precisou esperar)
        """
        async with self._lock:
            self._refill_tokens()

            wait_time = 0.0

            if self.tokens < tokens:
                # Calcular tempo de espera
                needed = tokens - self.tokens
                wait_time = needed / self.rate

                logger.debug(f"[{self.name}] Rate limit: aguardando {wait_time:.2f}s")

                # Aguardar
                await asyncio.sleep(wait_time)

                # Refill após espera
                self._refill_tokens()

                # Estatísticas
                self.stats.total_waits += 1
                self.stats.total_wait_time_ms += int(wait_time * 1000)
                self.stats.rate_limit_hits += 1

            # Consumir tokens
            self.tokens -= tokens
            self.stats.total_requests += 1

            # Registrar timestamp
            self._request_history.append(time.monotonic())

            return wait_time

    async def try_acquire(self, tokens: int = 1) -> bool:
        """
        Tenta adquirir tokens sem esperar.

        Args:
            tokens: Número de tokens a adquirir

        Returns:
            True se conseguiu adquirir, False se não há tokens
        """
        async with self._lock:
            self._refill_tokens()

            if self.tokens >= tokens:
                self.tokens -= tokens
                self.stats.total_requests += 1
                self._request_history.append(time.monotonic())
                return True

            return False

    def get_wait_time(self) -> float:
        """Retorna tempo estimado de espera para próxima requisição."""
        self._refill_tokens()

        if self.tokens >= 1:
            return 0.0

        needed = 1 - self.tokens
        return needed / self.rate

    def get_current_rate(self, window_seconds: float = 60.0) -> float:
        """
        Calcula a taxa atual de requisições.

        Args:
            window_seconds: Janela de tempo para cálculo

        Returns:
            Requisições por segundo na janela
        """
        now = time.monotonic()
        cutoff = now - window_seconds

        # Contar requisições na janela
        recent = sum(1 for ts in self._request_history if ts > cutoff)

        return recent / window_seconds

    def reset(self) -> None:
        """Reseta o rate limiter."""
        self.tokens = float(self.burst_size)
        self.last_update = time.monotonic()
        self._request_history.clear()
        logger.debug(f"[{self.name}] Reset")

    def get_stats(self) -> dict:
        """Retorna estatísticas do rate limiter."""
        return {
            "total_requests": self.stats.total_requests,
            "total_waits": self.stats.total_waits,
            "total_wait_time_ms": self.stats.total_wait_time_ms,
            "rate_limit_hits": self.stats.rate_limit_hits,
            "current_tokens": self.tokens,
            "max_tokens": self.burst_size,
            "rate_per_second": self.rate,
            "current_rate": self.get_current_rate(),
        }


class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter adaptativo que ajusta o rate baseado em respostas 429.
    """

    def __init__(
        self,
        initial_rate: float = 10.0,
        min_rate: float = 0.5,
        max_rate: float = 100.0,
        backoff_factor: float = 0.5,
        recovery_factor: float = 1.1,
        name: str | None = None,
    ):
        """
        Inicializa o rate limiter adaptativo.

        Args:
            initial_rate: Rate inicial em req/s
            min_rate: Rate mínimo
            max_rate: Rate máximo
            backoff_factor: Fator de redução ao receber 429
            recovery_factor: Fator de aumento gradual
            name: Nome para logging
        """
        super().__init__(
            requests_per_second=initial_rate, burst_size=max(1, int(initial_rate)), name=name or "AdaptiveRateLimiter"
        )

        self.initial_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.backoff_factor = backoff_factor
        self.recovery_factor = recovery_factor

        self._consecutive_success = 0
        self._recovery_threshold = 10  # Sucessos antes de aumentar rate

    async def report_rate_limit(self, retry_after: int | None = None) -> None:
        """
        Reporta que recebeu rate limit (429).
        Reduz o rate automaticamente.

        Args:
            retry_after: Segundos sugeridos pelo servidor para esperar
        """
        async with self._lock:
            old_rate = self.rate
            self.rate = max(self.min_rate, self.rate * self.backoff_factor)
            self.burst_size = max(1, int(self.rate))
            self._consecutive_success = 0

            logger.warning(f"[{self.name}] Rate limit detectado. Rate reduzido: {old_rate:.2f} -> {self.rate:.2f}/s")

            if retry_after:
                logger.info(f"[{self.name}] Retry-After: {retry_after}s")
                await asyncio.sleep(retry_after)

    async def report_success(self) -> None:
        """
        Reporta requisição bem-sucedida.
        Aumenta rate gradualmente após vários sucessos.
        """
        async with self._lock:
            self._consecutive_success += 1

            if self._consecutive_success >= self._recovery_threshold:
                old_rate = self.rate
                self.rate = min(self.max_rate, self.rate * self.recovery_factor)
                self.burst_size = max(1, int(self.rate))
                self._consecutive_success = 0

                if self.rate != old_rate:
                    logger.debug(f"[{self.name}] Rate aumentado: {old_rate:.2f} -> {self.rate:.2f}/s")

    def reset_to_initial(self) -> None:
        """Reseta para o rate inicial."""
        self.rate = self.initial_rate
        self.burst_size = max(1, int(self.initial_rate))
        self._consecutive_success = 0
        self.reset()
        logger.info(f"[{self.name}] Reset para rate inicial: {self.initial_rate}/s")
