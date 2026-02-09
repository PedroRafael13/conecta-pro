"""
modules/fase5/__init__.py - FASE 5 GRAND FINALE
===============================================
Multi-Agent AI System + Email Intelligence + CCT Compliance
"""

from .agents.base import AgentType, BaseAgent
from .cct_compliance.service import CCTComplianceService
from .core.orchestrator import ConectaProOrchestrator, CrossPhaseEvent, PhaseType, SystemComponent, WorkflowOrchestrator
from .email_intelligence.service import EmailIntelligenceService

__all__ = [
    # Orchestrator
    "ConectaProOrchestrator",
    "WorkflowOrchestrator",
    "PhaseType",
    "SystemComponent",
    "CrossPhaseEvent",
    # Services
    "CCTComplianceService",
    "EmailIntelligenceService",
    # Agents
    "BaseAgent",
    "AgentType",
]
