"""
Circuit Breaker para proteção de serviços externos.
Previne cascata de falhas quando um serviço está indisponível.
"""

import asyncio
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional

from loguru import logger


class CircuitState(Enum):
    """Estados do circuit breaker."""

    CLOSED = "closed"  # Normal, requisições passam
    OPEN = "open"  # Falhas detectadas, requisições bloqueadas
    HALF_OPEN = "half_open"  # Testando se serviço voltou


class CircuitBreaker:
    """
    Implementação de Circuit Breaker pattern.

    Protege contra falhas em cascata quando serviços externos falham.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exceptions: tuple = (Exception,),
    ):
        """
        Inicializa o circuit breaker.

        Args:
            name: Nome do circuit (para logs)
            failure_threshold: Número de falhas para abrir o circuito
            recovery_timeout: Segundos para tentar recuperar
            expected_exceptions: Exceções que contam como falha
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Retorna estado atual do circuit."""
        return self._state

    @property
    def is_closed(self) -> bool:
        """Verifica se circuit está fechado (normal)."""
        return self._state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Verifica se circuit está aberto (bloqueado)."""
        return self._state == CircuitState.OPEN

    async def _check_state(self) -> None:
        """Verifica se deve transicionar de estado."""
        if self._state == CircuitState.OPEN:
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.recovery_timeout:
                    logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN (tentando recuperar)")
                    self._state = CircuitState.HALF_OPEN

    async def record_success(self) -> None:
        """Registra sucesso na operação."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                logger.info(f"Circuit {self.name}: HALF_OPEN -> CLOSED (recuperado)")
                self._state = CircuitState.CLOSED
            self._failure_count = 0

    async def record_failure(self) -> None:
        """Registra falha na operação."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                logger.warning(f"Circuit {self.name}: HALF_OPEN -> OPEN (falha na recuperacao)")
                self._state = CircuitState.OPEN
            elif self._failure_count >= self.failure_threshold:
                logger.error(
                    f"Circuit {self.name}: CLOSED -> OPEN "
                    f"(threshold {self.failure_threshold} atingido)"
                )
                self._state = CircuitState.OPEN

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Executa função protegida pelo circuit breaker.

        Args:
            func: Função a executar
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados

        Returns:
            Resultado da função

        Raises:
            CircuitOpenError: Se o circuit está aberto
            Exception: Exceção original da função
        """
        await self._check_state()

        if self._state == CircuitState.OPEN:
            raise CircuitOpenError(f"Circuit {self.name} está aberto")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            await self.record_success()
            return result
        except self.expected_exceptions as e:
            await self.record_failure()
            raise


class CircuitOpenError(Exception):
    """Exceção quando o circuit está aberto."""


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 30,
) -> Callable:
    """
    Decorator para proteger funções com circuit breaker.

    Args:
        name: Nome do circuit
        failure_threshold: Falhas para abrir
        recovery_timeout: Tempo de recuperação

    Example:
        @circuit_breaker("external_api", failure_threshold=3)
        async def call_external_api():
            ...
    """
    cb = CircuitBreaker(
        name=name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
    )

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await cb.call(func, *args, **kwargs)

        wrapper.circuit_breaker = cb  # type: ignore
        return wrapper

    return decorator


# Circuit breakers globais para serviços comuns
db_circuit = CircuitBreaker("database", failure_threshold=3, recovery_timeout=10)
redis_circuit = CircuitBreaker("redis", failure_threshold=5, recovery_timeout=15)
external_api_circuit = CircuitBreaker("external_api", failure_threshold=5, recovery_timeout=30)
