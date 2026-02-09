"""Módulo de cache Redis."""

from .redis import (
    cache_clear_pattern,
    cache_delete,
    cache_get,
    cache_response,
    cache_set,
    close_redis,
    get_redis,
)
from .reference_data import ReferenceDataCache, reference_cache
from .utils import (
    CacheManager,
    invalidate_on_create,
    invalidate_on_delete,
    invalidate_on_update,
)

__all__ = [
    "get_redis",
    "close_redis",
    "cache_get",
    "cache_set",
    "cache_delete",
    "cache_clear_pattern",
    "cache_response",
    # Reference data cache
    "ReferenceDataCache",
    "reference_cache",
    # Cache management
    "CacheManager",
    "invalidate_on_create",
    "invalidate_on_update",
    "invalidate_on_delete",
]
