"""
Exceptions customizadas e handlers globais.
"""

from .handlers import (
    NotFoundError,
    ConflictError,
    ValidationError,
    BusinessRuleError,
    setup_exception_handlers,
)

__all__ = [
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "BusinessRuleError",
    "setup_exception_handlers",
]
