"""
Exceptions customizadas e handlers globais.
"""

from .handlers import (
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    ValidationError,
    setup_exception_handlers,
)

__all__ = [
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "BusinessRuleError",
    "setup_exception_handlers",
]
