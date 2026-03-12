"""
Modulo Operations — Re-export do modulo operacional existente.

Parte da categoria People Management.
Fornece acesso ao modulo operacional sob o namespace people_management.operations.
"""

try:
    from modules.operacional import (
        operacional_router,
        operations_router,
        router,
    )
except ImportError:
    operacional_router = None
    operations_router = None
    router = None

__all__ = [
    "operacional_router",
    "operations_router",
    "router",
]
