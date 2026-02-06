"""
Models de Perfil Operacional.

Este modulo contem os models SQLAlchemy para:
- OperationalProfile: Perfil operacional do funcionario
- ProfileQuestion: Perguntas do questionario
- PostMatch: Match entre funcionario e posto
"""

from .profile_models import (
    # Models
    OperationalProfile,
    ProfileQuestion,
    PostMatch,
    # Enums
    ProfileDimension,
    PostTypeProfile,
    # Constants
    QUESTIONARIO_PERFIL,
    PERFIL_IDEAL_POR_TIPO,
)

__all__ = [
    # Models
    "OperationalProfile",
    "ProfileQuestion",
    "PostMatch",
    # Enums
    "ProfileDimension",
    "PostTypeProfile",
    # Constants
    "QUESTIONARIO_PERFIL",
    "PERFIL_IDEAL_POR_TIPO",
]
