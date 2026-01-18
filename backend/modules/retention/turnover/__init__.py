"""
Modulo de Predicao de Turnover com IA - Conecta PRO.

Este modulo implementa sistema completo de predicao de risco de turnover
usando algoritmo heuristico baseado em multiplas features comportamentais,
de engajamento, operacionais e contextuais.

Caracteristicas:
    - Calculo de score de risco 0-100
    - Classificacao em niveis: baixo, medio, alto, critico
    - Identificacao de fatores de risco
    - Geracao automatica de alertas
    - Dashboard de monitoramento
    - Historico e tendencias
    - Recomendacoes de acao

Seguranca:
    - Score NUNCA visivel para o funcionario
    - Logs de auditoria para todos os acessos
    - Threshold conservador para alertas (>= 70)

Uso:
    from modules.retention.turnover import (
        TurnoverPredictor,
        RiskAnalyzer,
        router,
    )

    # No main.py
    app.include_router(router, prefix="/api/v1")
"""

from modules.retention.turnover.models.turnover_models import (
    AuditLogTurnover,
    CategoriaFator,
    NivelRisco,
    RiskAlert,
    RiskFactor,
    TipoAlerta,
    TurnoverPrediction,
)

from modules.retention.turnover.schemas.turnover_schemas import (
    AlertAcaoRequest,
    AlertCreate,
    AlertFilter,
    AlertListResponse,
    AlertResponse,
    AlertSummary,
    AlertVisualizarRequest,
    DashboardDistribuicaoNivel,
    DashboardFatorFrequente,
    DashboardFiltro,
    DashboardResponse,
    DashboardTendencia,
    ExportRequest,
    ExportResponse,
    FatorAgregadoResponse,
    FatoresListResponse,
    FeatureConfig,
    FeaturesConfigResponse,
    HistoricoItemResponse,
    HistoricoResponse,
    PredictionCreate,
    PredictionFilter,
    PredictionListResponse,
    PredictionResponse,
    PredictionSummary,
    RecalcularBatchRequest,
    RecalcularBatchResponse,
    RecalcularRequest,
    RecalcularResponse,
    RiskFactorCreate,
    RiskFactorResponse,
    RiskFactorSummary,
)

from modules.retention.turnover.repositories.turnover_repository import (
    TurnoverRepository,
)

from modules.retention.turnover.services.turnover_predictor import (
    FEATURES_CONFIG,
    FeatureDefinition,
    TurnoverPredictor,
)

from modules.retention.turnover.services.risk_analyzer import (
    RiskAnalyzer,
)

from modules.retention.turnover.controllers.turnover_controller import (
    router,
)

__all__ = [
    # Models
    "TurnoverPrediction",
    "RiskFactor",
    "RiskAlert",
    "AuditLogTurnover",
    # Enums
    "NivelRisco",
    "TipoAlerta",
    "CategoriaFator",
    # Schemas - Prediction
    "PredictionCreate",
    "PredictionResponse",
    "PredictionSummary",
    "PredictionListResponse",
    "PredictionFilter",
    # Schemas - Risk Factor
    "RiskFactorCreate",
    "RiskFactorResponse",
    "RiskFactorSummary",
    # Schemas - Alert
    "AlertCreate",
    "AlertResponse",
    "AlertSummary",
    "AlertListResponse",
    "AlertFilter",
    "AlertVisualizarRequest",
    "AlertAcaoRequest",
    # Schemas - Dashboard
    "DashboardResponse",
    "DashboardDistribuicaoNivel",
    "DashboardFatorFrequente",
    "DashboardTendencia",
    "DashboardFiltro",
    # Schemas - Historico
    "HistoricoResponse",
    "HistoricoItemResponse",
    # Schemas - Fatores
    "FatorAgregadoResponse",
    "FatoresListResponse",
    # Schemas - Config
    "FeatureConfig",
    "FeaturesConfigResponse",
    # Schemas - Recalcular
    "RecalcularRequest",
    "RecalcularResponse",
    "RecalcularBatchRequest",
    "RecalcularBatchResponse",
    # Schemas - Export
    "ExportRequest",
    "ExportResponse",
    # Repository
    "TurnoverRepository",
    # Services
    "TurnoverPredictor",
    "RiskAnalyzer",
    "FeatureDefinition",
    "FEATURES_CONFIG",
    # Router
    "router",
]

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
