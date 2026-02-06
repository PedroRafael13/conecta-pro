"""
Repository de Perfil Operacional.

Este modulo contem o repository para acesso a dados de:
- Perfis operacionais
- Perguntas do questionario
- Matches funcionario-posto
- Estatisticas e metricas
"""

from .profile_repository import ProfileRepository

__all__ = [
    "ProfileRepository",
]
