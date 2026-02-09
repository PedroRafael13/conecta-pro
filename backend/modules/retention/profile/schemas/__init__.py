"""
Schemas Pydantic de Perfil Operacional.

Este modulo contem os schemas de validacao e serializacao para:
- Questionario e perguntas
- Respostas e progresso
- Perfil operacional
- Match funcionario-posto
- Dashboard e estatisticas
"""

from .profile_schemas import (
    BestFuncionariosResponse,
    BestMatchesResponse,
    BulkMatchRequest,
    CalculateMatchRequest,
    DashboardResponse,
    DashboardStats,
    # Perfil
    DimensionScore,
    # Tipos de posto
    IdealProfileByType,
    MatchFilter,
    MatchListResponse,
    MatchNivelEnum,
    OperationalProfileBase,
    OperationalProfileDetail,
    OperationalProfileHistory,
    OperationalProfileResponse,
    # Match
    PostMatchBase,
    PostMatchDetail,
    PostMatchResponse,
    PostTypeEnum,
    PostTypesResponse,
    # Enums
    ProfileDimensionEnum,
    # Dashboard
    ProfileDistribution,
    ProfileFilter,
    ProfileListResponse,
    # Perguntas
    ProfileQuestionBase,
    ProfileQuestionCreate,
    ProfileQuestionResponse,
    ProfileQuestionUpdate,
    ProgressResponse,
    QuestionnaireResponse,
    # Respostas
    RespostaItem,
    SaveProgressRequest,
    SubmitRespostasRequest,
)

__all__ = [
    # Enums
    "ProfileDimensionEnum",
    "PostTypeEnum",
    "MatchNivelEnum",
    # Perguntas
    "ProfileQuestionBase",
    "ProfileQuestionCreate",
    "ProfileQuestionUpdate",
    "ProfileQuestionResponse",
    "QuestionnaireResponse",
    # Respostas
    "RespostaItem",
    "SubmitRespostasRequest",
    "SaveProgressRequest",
    "ProgressResponse",
    # Perfil
    "DimensionScore",
    "OperationalProfileBase",
    "OperationalProfileResponse",
    "OperationalProfileDetail",
    "OperationalProfileHistory",
    "ProfileListResponse",
    "ProfileFilter",
    # Match
    "PostMatchBase",
    "PostMatchResponse",
    "PostMatchDetail",
    "CalculateMatchRequest",
    "BulkMatchRequest",
    "BestMatchesResponse",
    "BestFuncionariosResponse",
    "MatchListResponse",
    "MatchFilter",
    # Tipos de posto
    "IdealProfileByType",
    "PostTypesResponse",
    # Dashboard
    "ProfileDistribution",
    "DashboardStats",
    "DashboardResponse",
]
