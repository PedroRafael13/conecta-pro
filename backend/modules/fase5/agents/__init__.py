"""
modules/fase5/agents/__init__.py - Multi-Agent System
=====================================================
Sistema multi-agente para automacao inteligente
"""

from .base import BaseAgent, AgentType, AgentStatus
from .email_agent import EmailAgent
from .cct_agent import CCTComplianceAgent
from .integration_agent import IntegrationHubAgent

__all__ = [
    "BaseAgent",
    "AgentType",
    "AgentStatus",
    "EmailAgent",
    "CCTComplianceAgent",
    "IntegrationHubAgent"
]
