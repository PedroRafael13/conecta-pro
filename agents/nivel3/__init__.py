"""
Nível 3 — Agentes Especializados Conecta PRO
11 agentes autônomos.
"""

from .business_agent import BusinessAgent
from .compliance_agent import ComplianceAgent
from .contract_agent import ContractAgent
from .coverage_agent import CoverageAgent
from .data_quality_agent import DataQualityAgent
from .data_validator_agent import DataValidatorAgent
from .load_agent import LoadAgent
from .log_monitor_agent import LogMonitorAgent
from .performance_agent import PerformanceAgent
from .security_agent import SecurityAgent
from .trend_agent import TrendAgent

__all__ = [
    "BusinessAgent",
    "ComplianceAgent",
    "ContractAgent",
    "CoverageAgent",
    "DataQualityAgent",
    "DataValidatorAgent",
    "LoadAgent",
    "LogMonitorAgent",
    "PerformanceAgent",
    "SecurityAgent",
    "TrendAgent",
]

AGENTES_NIVEL3 = {
    "business": BusinessAgent,
    "compliance": ComplianceAgent,
    "contract": ContractAgent,
    "coverage": CoverageAgent,
    "data_quality": DataQualityAgent,
    "data_validator": DataValidatorAgent,
    "load": LoadAgent,
    "log_monitor": LogMonitorAgent,
    "performance": PerformanceAgent,
    "security": SecurityAgent,
    "trend": TrendAgent,
}
