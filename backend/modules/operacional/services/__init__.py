"""
Services do Modulo Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
"""

from .biometric_service import BiometricService, FaceValidationResult, PhotoMetadata
from .check_in_validator import (
    CheckInData,
    CheckInValidator,
    ValidationConfig,
    ValidationResult,
)
from .geolocation_service import GeolocationService, GeolocationValidation, GeoPoint
from .integration_service import IntegrationService, get_integration_service
from .scale_generator import ScaleGenerator, scale_generator
from .scale_template_service import ScaleTemplateService
from .substitution_service import SubstitutionService, substitution_service
from .time_bank_service import TimeBankService, time_bank_service

__all__ = [
    # Scale Generator
    "ScaleGenerator",
    "scale_generator",
    # Scale Template Service
    "ScaleTemplateService",
    # Substitution Service
    "SubstitutionService",
    "substitution_service",
    # Time Bank Service
    "TimeBankService",
    "time_bank_service",
    # Integration Service
    "IntegrationService",
    "get_integration_service",
    # Geolocation
    "GeolocationService",
    "GeoPoint",
    "GeolocationValidation",
    # Biometric
    "BiometricService",
    "FaceValidationResult",
    "PhotoMetadata",
    # Check-in Validator
    "CheckInValidator",
    "CheckInData",
    "ValidationConfig",
    "ValidationResult",
]
