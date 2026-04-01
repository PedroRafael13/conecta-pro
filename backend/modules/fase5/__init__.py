"""
DEPRECATED: fase5 module — experimental AI orchestration, not in production.
Candidates for future extraction: CCT Compliance → Fiscal, Email Intelligence → Inteligência.
Deprecation date: 2026-03-11

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
