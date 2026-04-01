"""
Modulo de Pesquisa de Clima Operacional.

Este modulo implementa o sistema de pesquisa de clima organizacional
para o Conecta PRO, permitindo:

- Criacao e gestao de pesquisas de clima
- Coleta de respostas anonimizadas
- Calculo de scores normalizados (0-100)
- Agregacao por posto, equipe e empresa
- Deteccao de quedas e alertas automaticos
- Dashboards e analise de tendencias

Estrutura:
    models/: Modelos SQLAlchemy (ClimateSurvey, ClimateResponse, ClimateScore)
    schemas/: Schemas Pydantic v2 para validacao
    repositories/: Operacoes de banco de dados async
    services/: Logica de negocio
    controllers/: Endpoints FastAPI

Uso:
    # Registrar o router na aplicacao
    from modules.retention.climate import router
    app.include_router(router, prefix="/api/v1")

    # Usar o service diretamente
    from modules.retention.climate import ClimateService
    service = ClimateService(db)
    await service.criar_pesquisa(data)

Endpoints disponiveis:
    GET  /api/v1/retention/climate/surveys - Lista pesquisas
    POST /api/v1/retention/climate/surveys - Cria pesquisa
    GET  /api/v1/retention/climate/surveys/{id} - Obtem pesquisa
    GET  /api/v1/retention/climate/surveys/ativa - Pesquisa ativa
    POST /api/v1/retention/climate/respond - Responde pesquisa
    GET  /api/v1/retention/climate/results/posto/{id} - Resultados posto
    GET  /api/v1/retention/climate/results/equipe/{id} - Resultados equipe
    GET  /api/v1/retention/climate/results/empresa - Resultados empresa
    GET  /api/v1/retention/climate/trends/{tipo}/{id} - Tendencias
    GET  /api/v1/retention/climate/dashboard - Dashboard geral
    GET  /api/v1/retention/climate/alerts - Lista alertas
    POST /api/v1/retention/climate/calculate - Calcula scores

Escala de respostas (sem opcao neutra):
    1 = Discordo totalmente (0%)
    2 = Discordo parcialmente (33.33%)
    3 = Concordo parcialmente (66.67%)
    4 = Concordo totalmente (100%)

Score normalizado: 0-100

Classificacao:
    >= 80: Excelente
    >= 65: Bom
    >= 50: Regular
    >= 35: Atencao
    < 35: Critico

Alertas automaticos:
    - Queda > 20%: Gera alerta
    - Score < 35: Alerta critico
    - Dimensao < 35: Alerta de dimensao

Autor: Conecta PRO Team
Versao: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"

# Controllers (router)
from modules.retention.climate.controllers import router

# Models
from modules.retention.climate.models import (
    AlertSeverity,
    ClimateAlert,
    ClimateDimension,
    ClimateResponse,
    ClimateScore,
    ClimateSurvey,
    EntityType,
    QuestionType,
    SurveyFrequency,
)

# Repositories
from modules.retention.climate.repositories import (
    ClimateAlertRepository,
    ClimateResponseRepository,
    ClimateScoreRepository,
    ClimateSurveyRepository,
)

# Schemas
from modules.retention.climate.schemas import (
    AlertListResponse,
    AlertResolve,
    AlertResponse,
    CalculationRequest,
    CalculationResult,
    ClimateByEmpresa,
    ClimateByEquipe,
    ClimateByPosto,
    ClimateDashboard,
    ClimateFilter,
    ClimateScoreResponse,
    ClimateTrend,
    QuestionSchema,
    ResponseConfirmation,
    ResponseCreate,
    SurveyActiveResponse,
    SurveyCreate,
    SurveyListResponse,
    SurveyResponse,
    SurveyUpdate,
)

# Services
from modules.retention.climate.services import (
    PERGUNTAS_CLIMA_PADRAO,
    ClimateService,
    get_climate_service,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Router
    "router",
    # Enums
    "SurveyFrequency",
    "QuestionType",
    "ClimateDimension",
    "EntityType",
    "AlertSeverity",
    # Models
    "ClimateSurvey",
    "ClimateResponse",
    "ClimateScore",
    "ClimateAlert",
    # Repositories
    "ClimateSurveyRepository",
    "ClimateResponseRepository",
    "ClimateScoreRepository",
    "ClimateAlertRepository",
    # Services
    "ClimateService",
    "get_climate_service",
    "PERGUNTAS_CLIMA_PADRAO",
    # Schemas - Survey
    "QuestionSchema",
    "SurveyCreate",
    "SurveyUpdate",
    "SurveyResponse",
    "SurveyListResponse",
    "SurveyActiveResponse",
    # Schemas - Response
    "ResponseCreate",
    "ResponseConfirmation",
    # Schemas - Score
    "ClimateScoreResponse",
    # Schemas - Trend
    "ClimateTrend",
    # Schemas - Dashboard
    "ClimateDashboard",
    "ClimateByPosto",
    "ClimateByEquipe",
    "ClimateByEmpresa",
    # Schemas - Alert
    "AlertResponse",
    "AlertListResponse",
    "AlertResolve",
    # Schemas - Filter
    "ClimateFilter",
    # Schemas - Calculation
    "CalculationRequest",
    "CalculationResult",
]
