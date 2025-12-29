"""Módulo de banco de dados."""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    circuit_breaker,
    db_circuit,
    external_api_circuit,
    redis_circuit,
)
from .session import async_session_factory, close_db, engine, get_db, init_db

__all__ = [
    # Session
    "engine",
    "async_session_factory",
    "get_db",
    "init_db",
    "close_db",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitOpenError",
    "circuit_breaker",
    "db_circuit",
    "redis_circuit",
    "external_api_circuit",
]
