"""
Controllers de Perfil Operacional.

Este modulo contem os endpoints REST para:
- Questionario de perfil
- Submissao e progresso
- Consulta de perfis
- Match funcionario-posto
- Dashboard e estatisticas
"""

from .profile_controller import router

__all__ = [
    "router",
]
