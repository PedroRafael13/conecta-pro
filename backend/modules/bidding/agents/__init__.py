"""
Bidding AI Agents
==================
Sistema de agentes inteligentes para licitacoes governamentais.

Agentes disponiveis:
- SCOUT: Busca oportunidades no PNCP
- ANALYST: Analisa editais com Claude AI
- ASSESSOR: Avaliacao Go/No-Go
- PRICER: Precificacao com BDI
- COMPILER: Geracao de documentos de proposta
- WARRIOR: Robo de disputa para pregao eletronico (planned)
- SENTINEL: Monitoramento de certidoes/documentos

Pipeline: SCOUT -> ANALYST -> ASSESSOR -> PRICER -> COMPILER
"""

from modules.bidding.agents.analyst_agent import AnalysisResponse, AnalystAgent
from modules.bidding.agents.assessor_agent import AssessmentResponse, AssessorAgent, CompanyProfile, Recomendacao
from modules.bidding.agents.base_agent import (
    AgentConfig,
    AgentStatus,
    BaseAgent,
    ExecutionResult,
    ExecutionStatus,
)
from modules.bidding.agents.compiler_agent import CompilerAgent, CompilerInput, CompilerResponse
from modules.bidding.agents.orchestrator import PipelineOrchestrator, PipelineResult, PipelineStep
from modules.bidding.agents.pricer_agent import (
    PricerAgent,
    PricingInput,
    PricingResponse,
    RegimeTributario,
)
from modules.bidding.agents.scout_agent import OpportunityResponse, ScoutAgent, ScoutSearchParams
from modules.bidding.agents.sentinel_agent import SentinelAgent, SentinelResponse
from modules.bidding.agents.warrior_agent import WarriorAgent, WarriorConfig, WarriorResponse

__all__ = [
    # Base
    "BaseAgent",
    "AgentConfig",
    "AgentStatus",
    "ExecutionResult",
    "ExecutionStatus",
    # Agents
    "ScoutAgent",
    "AnalystAgent",
    "AssessorAgent",
    "PricerAgent",
    "CompilerAgent",
    "WarriorAgent",
    "SentinelAgent",
    # Orchestrator
    "PipelineOrchestrator",
    "PipelineResult",
    "PipelineStep",
    # DTOs
    "OpportunityResponse",
    "ScoutSearchParams",
    "AnalysisResponse",
    "AssessmentResponse",
    "CompanyProfile",
    "Recomendacao",
    "PricingInput",
    "PricingResponse",
    "RegimeTributario",
    "CompilerInput",
    "CompilerResponse",
    "WarriorConfig",
    "WarriorResponse",
    "SentinelResponse",
]
