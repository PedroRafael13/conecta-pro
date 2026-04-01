"""
Operations Services — Re-export dos services do modulo operacional + Scale Optimizer.
"""

import contextlib

from .scale_optimizer_service import ScaleOptimizerService

with contextlib.suppress(ImportError):
    from modules.operacional.services import (
        BiometricService,
        CheckInData,
        CheckInValidator,
        GeolocationService,
        IntegrationService,
        ScaleGenerator,
        ScaleTemplateService,
        SubstitutionService,
        TimeBankService,
        get_integration_service,
        scale_generator,
        substitution_service,
        time_bank_service,
    )

__all__ = [
    "ScaleGenerator",
    "scale_generator",
    "ScaleTemplateService",
    "SubstitutionService",
    "substitution_service",
    "TimeBankService",
    "time_bank_service",
    "IntegrationService",
    "get_integration_service",
    "GeolocationService",
    "BiometricService",
    "CheckInValidator",
    "CheckInData",
    "ScaleOptimizerService",
]
