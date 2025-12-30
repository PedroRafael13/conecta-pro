"""Serviços do módulo CRM."""

from .commission_service import CommissionService
from .contract_service import ContractService
from .dashboard_service import DashboardService, dashboard_service
from .lead_service import LeadScoringEngine, LeadService, lead_service
from .pipeline_service import PipelineService, pipeline_service

# Instâncias singleton
commission_service = CommissionService()
contract_service = ContractService()

__all__ = [
    "LeadService",
    "LeadScoringEngine",
    "lead_service",
    "PipelineService",
    "pipeline_service",
    "CommissionService",
    "commission_service",
    "DashboardService",
    "dashboard_service",
    "ContractService",
    "contract_service",
]
