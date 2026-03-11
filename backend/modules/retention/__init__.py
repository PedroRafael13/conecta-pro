"""
Modulo de Retencao de Talentos - Conecta PRO.

DEPRECATED: Use 'modules.pessoas' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.
"""

import logging
import warnings

warnings.warn(
    "Importing from 'modules.retention' is deprecated. "
    "Use 'modules.pessoas' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

logger = logging.getLogger(__name__)

# Lista de exports
__all__ = []

# =============================================================================
# ONBOARDING - Modulo principal deste pacote
# =============================================================================
try:
    from .onboarding import (  # noqa: E402
        OnboardingChecklist,  # noqa: F401
        OnboardingError,  # noqa: F401
        OnboardingProgress,  # noqa: F401
        OnboardingRepository,  # noqa: F401
        OnboardingService,  # noqa: F401
        OnboardingStep,  # noqa: F401
        ProgressStatus,  # noqa: F401
        StepType,  # noqa: F401
        onboarding_router,  # noqa: F401
    )

    __all__.extend(
        [
            "OnboardingChecklist",
            "OnboardingStep",
            "OnboardingProgress",
            "OnboardingService",
            "OnboardingRepository",
            "OnboardingError",
            "onboarding_router",
            "StepType",
            "ProgressStatus",
        ]
    )
except ImportError as e:
    logger.warning(f"Falha ao importar modulo onboarding: {e}")

# =============================================================================
# PROFILE - Import opcional
# =============================================================================
try:
    from .profile import (  # noqa: E402
        OperationalProfile,  # noqa: F401
        PostMatch,  # noqa: F401
        ProfileMatcher,  # noqa: F401
        ProfileQuestion,  # noqa: F401
        ProfileRepository,  # noqa: F401
        ProfileService,  # noqa: F401
    )
    from .profile import (  # noqa: E402
        router as profile_router,  # noqa: F401
    )

    __all__.extend(
        [
            "OperationalProfile",
            "ProfileQuestion",
            "PostMatch",
            "ProfileService",
            "ProfileMatcher",
            "ProfileRepository",
            "profile_router",
        ]
    )
except (ImportError, Exception) as e:
    logger.debug(f"Modulo profile nao disponivel: {e}")

# =============================================================================
# CLIMATE - Import opcional
# =============================================================================
try:
    from .climate import (  # noqa: E402
        PERGUNTAS_CLIMA_PADRAO,  # noqa: F401
        ClimateAlert,  # noqa: F401
        ClimateAlertRepository,  # noqa: F401
        ClimateResponse,  # noqa: F401
        ClimateResponseRepository,  # noqa: F401
        ClimateScore,  # noqa: F401
        ClimateScoreRepository,  # noqa: F401
        ClimateService,  # noqa: F401
        ClimateSurvey,  # noqa: F401
        ClimateSurveyRepository,  # noqa: F401
        router,  # noqa: F401
    )

    climate_router = router
    __all__.extend(
        [
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
        ]
    )
except (ImportError, Exception) as e:
    logger.debug(f"Modulo climate nao disponivel: {e}")

# =============================================================================
# TURNOVER - Import opcional (pode ter dependencias externas)
# =============================================================================
try:
    from .turnover import (  # noqa: E402
        CategoriaFator,  # noqa: F401
        NivelRisco,  # noqa: F401
        RiskAlert,  # noqa: F401
        RiskAnalyzer,  # noqa: F401
        RiskFactor,  # noqa: F401
        TipoAlerta,  # noqa: F401
        TurnoverPrediction,  # noqa: F401
        TurnoverPredictor,  # noqa: F401
        TurnoverRepository,  # noqa: F401
        router,  # noqa: F401
    )

    turnover_router = router
    __all__.extend(
        [
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
        ]
    )
except (ImportError, Exception) as e:
    logger.debug(f"Modulo turnover nao disponivel: {e}")


__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
