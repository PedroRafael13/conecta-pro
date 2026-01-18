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
    # Enums
    ProfileDimensionEnum,
    PostTypeEnum,
    MatchNivelEnum,
    # Perguntas
    ProfileQuestionBase,
    ProfileQuestionCreate,
    ProfileQuestionUpdate,
    ProfileQuestionResponse,
    QuestionnaireResponse,
    # Respostas
    RespostaItem,
    SubmitRespostasRequest,
    SaveProgressRequest,
    ProgressResponse,
    # Perfil
    DimensionScore,
    OperationalProfileBase,
    OperationalProfileResponse,
    OperationalProfileDetail,
    OperationalProfileHistory,
    ProfileListResponse,
    ProfileFilter,
    # Match
    PostMatchBase,
    PostMatchResponse,
    PostMatchDetail,
    CalculateMatchRequest,
    BulkMatchRequest,
    BestMatchesResponse,
    BestFuncionariosResponse,
    MatchListResponse,
    MatchFilter,
    # Tipos de posto
    IdealProfileByType,
    PostTypesResponse,
    # Dashboard
    ProfileDistribution,
    DashboardStats,
    DashboardResponse,
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
