"""
Modulo de Retencao de Talentos - Conecta PRO.

Este modulo gerencia estrategias e processos de retencao de funcionarios,
incluindo onboarding digital, perfil operacional, acompanhamento de novos
colaboradores e metricas de engajamento.

Submodulos:
    - onboarding: Gerenciamento do processo de integracao de novos funcionarios
    - profile: Perfil operacional e match com postos de trabalho
    - climate: Pesquisa de clima organizacional
    - turnover: Analise e previsao de turnover
"""

import logging

logger = logging.getLogger(__name__)

# Lista de exports
__all__ = []

# =============================================================================
# ONBOARDING - Modulo principal deste pacote
# =============================================================================
try:
    from .onboarding import (
        OnboardingChecklist,
        OnboardingStep,
        OnboardingProgress,
        OnboardingService,
        OnboardingRepository,
        OnboardingException,
        onboarding_router,
        StepType,
        ProgressStatus,
    )
    __all__.extend([
        "OnboardingChecklist",
        "OnboardingStep",
        "OnboardingProgress",
        "OnboardingService",
        "OnboardingRepository",
        "OnboardingException",
        "onboarding_router",
        "StepType",
        "ProgressStatus",
    ])
except ImportError as e:
    logger.warning(f"Falha ao importar modulo onboarding: {e}")

# =============================================================================
# PROFILE - Import opcional
# =============================================================================
try:
    from .profile import (
        OperationalProfile,
        ProfileQuestion,
        PostMatch,
        ProfileService,
        ProfileMatcher,
        ProfileRepository,
        router as profile_router,
    )
    __all__.extend([
        "OperationalProfile",
        "ProfileQuestion",
        "PostMatch",
        "ProfileService",
        "ProfileMatcher",
        "ProfileRepository",
        "profile_router",
    ])
except (ImportError, Exception) as e:
    logger.debug(f"Modulo profile nao disponivel: {e}")

# =============================================================================
# CLIMATE - Import opcional
# =============================================================================
try:
    from .climate import (
        ClimateSurvey,
        ClimateResponse,
        ClimateScore,
        ClimateAlert,
        ClimateService,
        ClimateSurveyRepository,
        ClimateResponseRepository,
        ClimateScoreRepository,
        ClimateAlertRepository,
        router,
        PERGUNTAS_CLIMA_PADRAO,
    )
    climate_router = router
    __all__.extend([
        "ClimateSurvey",
        "ClimateResponse",
        "ClimateScore",
        "ClimateAlert",
        "ClimateService",
        "ClimateSurveyRepository",
        "ClimateResponseRepository",
        "ClimateScoreRepository",
        "ClimateAlertRepository",
        "climate_router",
        "PERGUNTAS_CLIMA_PADRAO",
    ])
except (ImportError, Exception) as e:
    logger.debug(f"Modulo climate nao disponivel: {e}")

# =============================================================================
# TURNOVER - Import opcional (pode ter dependencias externas)
# =============================================================================
try:
    from .turnover import (
        TurnoverPrediction,
        RiskFactor,
        RiskAlert,
        NivelRisco,
        TipoAlerta,
        CategoriaFator,
        TurnoverPredictor,
        RiskAnalyzer,
        TurnoverRepository,
        router,
    )
    turnover_router = router
    __all__.extend([
        "TurnoverPrediction",
        "RiskFactor",
        "RiskAlert",
        "NivelRisco",
        "TipoAlerta",
        "CategoriaFator",
        "TurnoverPredictor",
        "RiskAnalyzer",
        "TurnoverRepository",
        "turnover_router",
    ])
except (ImportError, Exception) as e:
    logger.debug(f"Modulo turnover nao disponivel: {e}")


__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
