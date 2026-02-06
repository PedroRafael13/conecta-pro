"""
modules/fase5/__init__.py - FASE 5 GRAND FINALE
===============================================
Multi-Agent AI System + Email Intelligence + CCT Compliance
"""

from .core.orchestrator import (
    ConectaProOrchestrator,
    WorkflowOrchestrator,
    PhaseType,
    SystemComponent,
    CrossPhaseEvent
)
from .cct_compliance.service import CCTComplianceService
from .email_intelligence.service import EmailIntelligenceService
from .agents.base import BaseAgent, AgentType

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
    "AgentType"
]
