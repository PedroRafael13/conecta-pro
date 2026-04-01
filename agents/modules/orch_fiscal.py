"""Orquestrador Fiscal & Contábil."""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from fin_fiscal_agentes import (
    AgenteNFe, AgenteNFSe, AgenteCertidoes,
    AgenteESocialFiscal, AgenteSPED,
    AgenteDCTFWeb, AgenteEFDReinf
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "fiscal_contabil"
    DESCRICAO = (
        "NFS-e, impostos, SPED, "
        "multi-empresa e demonstrativos"
    )
    AGENTES = [
        AgenteNFe,
        AgenteNFSe,
        AgenteCertidoes,
        AgenteESocialFiscal,
        AgenteSPED,
        AgenteDCTFWeb,
        AgenteEFDReinf,
    ]
