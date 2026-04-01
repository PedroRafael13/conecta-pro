"""
modules/fase5/agents/__init__.py - Multi-Agent System
=====================================================
Sistema multi-agente para automacao inteligente
"""

from .base import AgentStatus, AgentType, BaseAgent
from .cct_agent import CCTComplianceAgent
from .email_agent import EmailAgent
from .integration_agent import IntegrationHubAgent

__all__ = ["BaseAgent", "AgentType", "AgentStatus", "EmailAgent", "CCTComplianceAgent", "IntegrationHubAgent"]
