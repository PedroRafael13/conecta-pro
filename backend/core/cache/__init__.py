"""Módulo de cache Redis."""

from .redis import cache_clear_pattern, cache_delete, cache_get, cache_set, close_redis, get_redis

__all__ = [
    "get_redis",
    "close_redis",
    "cache_get",
    "cache_set",
    "cache_delete",
    "cache_clear_pattern",
]
