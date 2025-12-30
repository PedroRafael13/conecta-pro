"""Serviços do módulo CRM."""

from .lead_service import LeadScoringEngine, LeadService, lead_service
from .pipeline_service import PipelineService, pipeline_service

__all__ = [
    "LeadService",
    "LeadScoringEngine",
    "lead_service",
    "PipelineService",
    "pipeline_service",
]
