"""Testes para o sistema de banco de dados."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.database.circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    circuit_breaker,
    db_circuit,
    redis_circuit,
)


class TestCircuitState:
    """Testes para enum CircuitState."""

    def test_closed_state(self):
        """Testa estado CLOSED."""
        assert CircuitState.CLOSED.value == "closed"

    def test_open_state(self):
        """Testa estado OPEN."""
        assert CircuitState.OPEN.value == "open"

    def test_half_open_state(self):
        """Testa estado HALF_OPEN."""
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestCircuitOpenError:
    """Testes para exceção CircuitOpenError."""

    def test_error_message(self):
        """Testa mensagem de erro."""
        error = CircuitOpenError("Circuit is open")
        assert str(error) == "Circuit is open"

    def test_error_inheritance(self):
        """Testa que CircuitOpenError herda de Exception."""
        error = CircuitOpenError("test")
        assert isinstance(error, Exception)


class TestCircuitBreaker:
    """Testes para CircuitBreaker."""

    def test_initial_state(self):
        """Testa estado inicial."""
        cb = CircuitBreaker(name="test")

        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0
        assert cb.is_closed is True
        assert cb.is_open is False

    def test_custom_thresholds(self):
        """Testa thresholds customizados."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=3,
            recovery_timeout=30,
        )

        assert cb.failure_threshold == 3
        assert cb.recovery_timeout == 30

    def test_properties(self):
        """Testa propriedades do circuit breaker."""
        cb = CircuitBreaker(name="test")

        # Estado inicial
        assert cb.is_closed is True
        assert cb.is_open is False

        # Após abrir
        cb._state = CircuitState.OPEN
        assert cb.is_closed is False
        assert cb.is_open is True

    @pytest.mark.asyncio
    async def test_record_success_resets_failure_count(self):
        """Testa que sucesso reseta contador de falhas."""
        cb = CircuitBreaker(name="test")
        cb._failure_count = 2

        await cb.record_success()

        assert cb._failure_count == 0

    @pytest.mark.asyncio
    async def test_record_success_closes_half_open(self):
        """Testa que sucesso em half-open fecha circuit."""
        cb = CircuitBreaker(name="test")
        cb._state = CircuitState.HALF_OPEN

        await cb.record_success()

        assert cb.state == CircuitState.CLOSED
        assert cb._failure_count == 0

    @pytest.mark.asyncio
    async def test_record_failure_increments_count(self):
        """Testa incremento do contador de falhas."""
        cb = CircuitBreaker(name="test", failure_threshold=5)

        await cb.record_failure()

        assert cb._failure_count == 1
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_record_failure_opens_circuit(self):
        """Testa que falhas suficientes abrem o circuit."""
        cb = CircuitBreaker(name="test", failure_threshold=3)

        await cb.record_failure()
        await cb.record_failure()
        await cb.record_failure()

        assert cb.state == CircuitState.OPEN
        assert cb._failure_count == 3
        assert cb._last_failure_time is not None

    @pytest.mark.asyncio
    async def test_half_open_failure_opens_circuit(self):
        """Testa que falha em half-open abre circuit."""
        cb = CircuitBreaker(name="test")
        cb._state = CircuitState.HALF_OPEN

        await cb.record_failure()

        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_check_state_transitions_to_half_open(self):
        """Testa transição de OPEN para HALF_OPEN após timeout."""
        cb = CircuitBreaker(name="test", recovery_timeout=1)
        cb._state = CircuitState.OPEN
        cb._last_failure_time = time.time() - 2  # 2 segundos atrás

        await cb._check_state()

        assert cb.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_check_state_stays_open_before_timeout(self):
        """Testa que circuit permanece OPEN antes do timeout."""
        cb = CircuitBreaker(name="test", recovery_timeout=60)
        cb._state = CircuitState.OPEN
        cb._last_failure_time = time.time()  # Agora

        await cb._check_state()

        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_call_success(self):
        """Testa execução com sucesso."""
        cb = CircuitBreaker(name="test")

        async def success_func():
            return "result"

        result = await cb.call(success_func)

        assert result == "result"
        assert cb._failure_count == 0

    @pytest.mark.asyncio
    async def test_call_sync_function(self):
        """Testa execução de função síncrona."""
        cb = CircuitBreaker(name="test")

        def sync_func():
            return "sync_result"

        result = await cb.call(sync_func)

        assert result == "sync_result"

    @pytest.mark.asyncio
    async def test_call_failure(self):
        """Testa execução com falha."""
        cb = CircuitBreaker(name="test")

        async def fail_func():
            raise ValueError("error")

        with pytest.raises(ValueError):
            await cb.call(fail_func)

        assert cb._failure_count == 1

    @pytest.mark.asyncio
    async def test_call_when_open_raises_error(self):
        """Testa que call quando circuit está aberto lança erro."""
        cb = CircuitBreaker(name="test", recovery_timeout=60)
        cb._state = CircuitState.OPEN
        cb._last_failure_time = time.time()

        async def func():
            return "result"

        with pytest.raises(CircuitOpenError) as exc_info:
            await cb.call(func)

        assert "test" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_call_with_args_and_kwargs(self):
        """Testa execução com argumentos."""
        cb = CircuitBreaker(name="test")

        async def func_with_args(a, b, c=None):
            return f"{a}-{b}-{c}"

        result = await cb.call(func_with_args, 1, 2, c=3)

        assert result == "1-2-3"


class TestCircuitBreakerDecorator:
    """Testes para decorator circuit_breaker."""

    @pytest.mark.asyncio
    async def test_decorator_success(self):
        """Testa decorator com sucesso."""
        @circuit_breaker(name="test_decorator", failure_threshold=3)
        async def my_func():
            return "decorated_result"

        result = await my_func()

        assert result == "decorated_result"

    @pytest.mark.asyncio
    async def test_decorator_exposes_circuit(self):
        """Testa que decorator expõe circuit breaker."""
        @circuit_breaker(name="exposed_circuit")
        async def my_func():
            return "result"

        assert hasattr(my_func, "circuit_breaker")
        assert isinstance(my_func.circuit_breaker, CircuitBreaker)

    @pytest.mark.asyncio
    async def test_decorator_failure_tracking(self):
        """Testa que decorator rastreia falhas."""
        @circuit_breaker(name="track_failures", failure_threshold=3)
        async def failing_func():
            raise ValueError("error")

        for _ in range(2):
            try:
                await failing_func()
            except ValueError:
                pass

        assert failing_func.circuit_breaker._failure_count == 2


class TestGlobalCircuits:
    """Testes para circuits globais."""

    def test_db_circuit_exists(self):
        """Testa que db_circuit existe."""
        assert db_circuit is not None
        assert isinstance(db_circuit, CircuitBreaker)
        assert db_circuit.name == "database"

    def test_redis_circuit_exists(self):
        """Testa que redis_circuit existe."""
        assert redis_circuit is not None
        assert isinstance(redis_circuit, CircuitBreaker)
        assert redis_circuit.name == "redis"


class TestDatabaseSession:
    """Testes para sessão do banco."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Testa que get_db retorna sessão."""
        with patch("core.database.session.async_session_factory") as mock_factory:
            mock_session_instance = AsyncMock()
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session_instance
            mock_context.__aexit__.return_value = None
            mock_factory.return_value = mock_context

            from core.database.session import get_db

            async for session in get_db():
                assert session == mock_session_instance


class TestDatabaseInit:
    """Testes para inicialização do banco."""

    def test_imports(self):
        """Testa que imports funcionam."""
        from core.database import get_db, close_db

        assert get_db is not None
        assert close_db is not None
