"""
Services de Perfil Operacional.

Este modulo contem os services de logica de negocio para:
- ProfileService: Gestao de perfis e questionarios
- ProfileMatcher: Calculo de match funcionario-posto
"""

from .profile_matcher import ProfileMatcher
from .profile_service import ProfileService

__all__ = [
    "ProfileService",
    "ProfileMatcher",
]
