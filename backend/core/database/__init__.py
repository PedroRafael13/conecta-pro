"""Módulo de banco de dados."""

# Importar Base do core.models para re-exportar
from core.models.base import Base, BaseModel

from .circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    circuit_breaker,
    db_circuit,
    external_api_circuit,
    redis_circuit,
)
from .session import async_session_factory, close_db, engine, get_db, init_db

# Alias para compatibilidade
get_session = get_db
get_async_session = get_db

__all__ = [
    # Session
    "engine",
    "async_session_factory",
    "get_db",
    "get_session",
    "get_async_session",
    "init_db",
    "close_db",
    # Base
    "Base",
    "BaseModel",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitOpenError",
    "circuit_breaker",
    "db_circuit",
    "redis_circuit",
    "external_api_circuit",
]
