"""
Modulo Employee Portal — Portal do Funcionario.

Parte da categoria People Management.
Permite que funcionarios acessem contracheques, escalas, documentos
e assinem documentos digitalmente via portal self-service.
"""

try:
    from .aggregator import router as portal_router
except ImportError:
    portal_router = None

__all__ = [
    "portal_router",
]
