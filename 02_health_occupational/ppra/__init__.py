"""
Package: ppra
Description: Modulo PPRA/PGR - Programa de Prevencao de Riscos Ambientais (NR-9)
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: NR-9 (Portaria MTb 3.214/78)
"""

from .risk_mapping import (
    RiskMappingManager,
    OccupationalRisk,
    RiskAgent,
    RiskMeasurement,
    ControlMeasure,
    WorkLocation,
    RiskCategory,
    RiskLevel,
    ExposureFrequency,
    ControlType,
    RiskMappingError,
    PPRAConfig,
    OccupationalRiskModel,
    RiskAgentModel,
    get_risk_manager,
    init_risk_manager,
)

__all__ = [
    "RiskMappingManager",
    "OccupationalRisk",
    "RiskAgent",
    "RiskMeasurement",
    "ControlMeasure",
    "WorkLocation",
    "RiskCategory",
    "RiskLevel",
    "ExposureFrequency",
    "ControlType",
    "RiskMappingError",
    "PPRAConfig",
    "OccupationalRiskModel",
    "RiskAgentModel",
    "get_risk_manager",
    "init_risk_manager",
]

__version__ = "1.0.0"
