"""
Orquestrador Departamento Pessoal.
Coordena 14 agentes: colaboradores, admissão, rescisão, contratos,
folha, ponto, banco de horas, férias, benefícios, licenças,
reembolsos, eSocial, disciplina, CCT e documentos.
"""
import sys
sys.path.insert(0, '/opt/conecta-pro/agents/core')
sys.path.insert(0, '/opt/conecta-pro/agents/modules')
from base_orchestrator import BaseOrchestrator
from dp_agentes import (
    AgenteColaboradores,
    AgenteAdmissao,
    AgenteRescisao,
    AgenteContratos,
    AgenteFolhaSalarial,
    AgentePontoEletronico,
    AgenteBancoHoras,
    AgenteFeriasDP,
    AgenteBeneficios,
    AgenteLicencas,
    AgenteReembolsos,
    AgenteESocialDP,
    AgenteDocumentosDP,
    AgenteDisciplina,
    AgenteCCT,
    AgenteSST,
    AgenteCommandCenter,
)


class OrchestratorClass(BaseOrchestrator):
    MODULO = "departamento_pessoal"
    DESCRICAO = (
        "Gestão completa de colaboradores, folha, ponto, "
        "benefícios, eSocial e SST"
    )
    AGENTES = [
        AgenteColaboradores,
        AgenteAdmissao,
        AgenteRescisao,
        AgenteContratos,
        AgenteFolhaSalarial,
        AgentePontoEletronico,
        AgenteBancoHoras,
        AgenteFeriasDP,
        AgenteBeneficios,
        AgenteLicencas,
        AgenteReembolsos,
        AgenteESocialDP,
        AgenteDocumentosDP,
        AgenteDisciplina,
        AgenteCCT,
        AgenteSST,
        AgenteCommandCenter,
    ]
