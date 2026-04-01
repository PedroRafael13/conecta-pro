"""
Nível 3 — Agentes Especializados Conecta PRO
Time completo de agentes autônomos.
"""
from .business_agent import BusinessAgent
from .compliance_agent import ComplianceAgent
from .contract_agent import ContractAgent
from .coverage_agent import CoverageAgent
from .data_quality_agent import DataQualityAgent
from .performance_agent import PerformanceAgent
from .security_agent import SecurityAgent

__all__ = [
    "CoverageAgent",
    "ContractAgent",
    "ComplianceAgent",
    "DataQualityAgent",
    "PerformanceAgent",
    "SecurityAgent",
    "BusinessAgent",
]

AGENTES_NIVEL3 = {
    "coverage": CoverageAgent,
    "contract": ContractAgent,
    "compliance": ComplianceAgent,
    "data_quality": DataQualityAgent,
    "performance": PerformanceAgent,
    "security": SecurityAgent,
    "business": BusinessAgent,
}
