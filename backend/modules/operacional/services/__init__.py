"""
Services do Modulo Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
"""

from .scale_generator import ScaleGenerator, scale_generator
from .substitution_service import SubstitutionService, substitution_service
from .time_bank_service import TimeBankService, time_bank_service
from .integration_service import IntegrationService, get_integration_service
from .geolocation_service import GeolocationService, GeoPoint, GeolocationValidation
from .biometric_service import BiometricService, FaceValidationResult, PhotoMetadata
from .check_in_validator import (
    CheckInValidator,
    CheckInData,
    ValidationConfig,
    ValidationResult,
)

__all__ = [
    # Scale Generator
    "ScaleGenerator",
    "scale_generator",
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
