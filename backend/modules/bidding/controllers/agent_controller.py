"""
Controller de Agentes IA - Licitacoes
======================================
Endpoints para interacao com os agentes de inteligencia artificial
do modulo de licitacoes: Scout, Analyst, Assessor, Pricer, Sentinel, Warrior.
"""

import logging

from fastapi import APIRouter, HTTPException, status

from modules.bidding.agents.analyst_agent import AnalystAgent
from modules.bidding.agents.assessor_agent import AssessorAgent
from modules.bidding.agents.base_agent import AgentStatus
from modules.bidding.agents.compiler_agent import CompilerAgent
from modules.bidding.agents.orchestrator import PipelineOrchestrator
from modules.bidding.agents.pricer_agent import PricerAgent
from modules.bidding.agents.scout_agent import ScoutAgent, ScoutSearchParams
from modules.bidding.agents.sentinel_agent import SentinelAgent
from modules.bidding.agents.warrior_agent import WarriorAgent
from modules.bidding.schemas.analysis import AnalystRequest
from modules.bidding.schemas.assessment import AssessorRequest
from modules.bidding.schemas.opportunity import ScoutRequest
from modules.bidding.schemas.pipeline import PipelineRequest
from modules.bidding.schemas.pricing import PricerRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Licitacoes - Agentes IA"])

# Instanciar agentes
scout_agent = ScoutAgent()
analyst_agent = AnalystAgent()
assessor_agent = AssessorAgent()
pricer_agent = PricerAgent()
sentinel_agent = SentinelAgent()
compiler_agent = CompilerAgent()
warrior_agent = WarriorAgent()
orchestrator = PipelineOrchestrator()

# ============================================================
# Registro de agentes e seus status de implementacao
# ============================================================
AGENTS_REGISTRY = [
    {
        "name": "scout",
        "description": "Busca automatizada de oportunidades em portais de licitacao",
        "status": scout_agent.AGENT_STATUS.value,
        "capabilities": ["busca_pncp", "busca_comprasnet", "busca_bec", "filtro_segmento"],
    },
    {
        "name": "analyst",
        "description": "Analise automatica de editais com extracao de requisitos e riscos",
        "status": analyst_agent.AGENT_STATUS.value,
        "capabilities": ["extracao_requisitos", "analise_riscos", "resumo_edital", "classificacao"],
    },
    {
        "name": "assessor",
        "description": "Avaliacao Go/No-Go com scoring multidimensional",
        "status": assessor_agent.AGENT_STATUS.value,
        "capabilities": ["scoring_financeiro", "scoring_tecnico", "scoring_estrategico", "analise_concorrencia"],
    },
    {
        "name": "pricer",
        "description": "Precificacao inteligente com composicao de custos e cenarios",
        "status": pricer_agent.AGENT_STATUS.value,
        "capabilities": ["composicao_custos", "calculo_bdi", "cenarios", "comparativo_mercado"],
    },
    {
        "name": "sentinel",
        "description": "Monitoramento de certidoes e documentos de habilitacao",
        "status": sentinel_agent.AGENT_STATUS.value,
        "capabilities": ["monitoramento_certidoes", "alertas_vencimento", "renovacao_automatica"],
    },
    {
        "name": "warrior",
        "description": "Robo de disputa para pregoes eletronicos",
        "status": warrior_agent.AGENT_STATUS.value,
        "capabilities": ["lances_automaticos", "estrategia_disputa", "monitoramento_sessao", "simulacao"],
    },
    {
        "name": "compiler",
        "description": "Geracao automatica de documentos de proposta",
        "status": compiler_agent.AGENT_STATUS.value,
        "capabilities": ["carta_proposta", "planilha_custos", "declaracoes", "checklist_habilitacao"],
    },
]

# Tipos de certidoes monitoradas pelo Sentinel
CERTIFICATE_TYPES = [
    {"tipo": "CND_FEDERAL", "descricao": "Certidao Negativa de Debitos Federais (RFB/PGFN)", "validade_dias": 180},
    {"tipo": "CND_ESTADUAL", "descricao": "Certidao Negativa de Debitos Estaduais (SEFAZ)", "validade_dias": 90},
    {"tipo": "CND_MUNICIPAL", "descricao": "Certidao Negativa de Debitos Municipais", "validade_dias": 90},
    {"tipo": "CRF_FGTS", "descricao": "Certificado de Regularidade do FGTS", "validade_dias": 30},
    {"tipo": "CNDT_TRABALHISTA", "descricao": "Certidao Negativa de Debitos Trabalhistas (TST)", "validade_dias": 180},
    {"tipo": "SICAF", "descricao": "Registro no SICAF", "validade_dias": 360},
    {"tipo": "CEIS", "descricao": "Consulta ao Cadastro de Empresas Inidoneas e Suspensas", "validade_dias": 0},
    {"tipo": "CNEP", "descricao": "Cadastro Nacional de Empresas Punidas", "validade_dias": 0},
    {"tipo": "ATESTADO_CAPACIDADE", "descricao": "Atestado de Capacidade Tecnica", "validade_dias": 0},
    {"tipo": "BALANCO_PATRIMONIAL", "descricao": "Balanco Patrimonial e DRE", "validade_dias": 365},
]


def _planned_response(agent_name: str) -> dict:
    """Retorna resposta padrao para agentes em desenvolvimento."""
    return {
        "status": "planned",
        "agent": agent_name,
        "message": "Agent em desenvolvimento",
    }


# ============================================================
# Status geral dos agentes
# ============================================================
@router.get("/status")
async def list_agents_status():
    """Lista todos os agentes e seus status de implementacao."""
    return {
        "agents": AGENTS_REGISTRY,
        "total": len(AGENTS_REGISTRY),
        "operational": sum(1 for a in AGENTS_REGISTRY if a["status"] == AgentStatus.OPERATIONAL.value),
        "development": sum(1 for a in AGENTS_REGISTRY if a["status"] == AgentStatus.DEVELOPMENT.value),
        "planned": sum(1 for a in AGENTS_REGISTRY if a["status"] == AgentStatus.PLANNED.value),
    }


# ============================================================
# Scout - Busca de oportunidades
# ============================================================
@router.post("/scout/buscar")
async def scout_buscar(request: ScoutRequest):
    """Busca oportunidades de licitacao nos portais configurados."""
    try:
        search_params = ScoutSearchParams(
            keywords=request.keywords or ["vigilancia", "seguranca patrimonial", "portaria"],
            ufs=[request.uf] if request.uf else ["AM"],
            modalidades=[request.modalidade] if request.modalidade else None,
            valor_minimo=request.valor_min,
            valor_maximo=request.valor_max,
            portais=request.portais
            if hasattr(request, "portais") and request.portais
            else ["pncp", "comprasnet", "licitacoes_e", "ecompras_am"],
        )
        result = await scout_agent.run(search_params=search_params)
        if result.success:
            opportunities = result.data if isinstance(result.data, list) else result.data.get("opportunities", [])
            return {
                "status": "success",
                "agent": "scout",
                "opportunities": opportunities,
                "total": len(opportunities),
                "portal": request.portal or "todos",
            }
        return {
            "status": "error",
            "agent": "scout",
            "message": result.error or "Erro na busca",
        }
    except Exception as e:
        logger.error(f"Erro no agente Scout: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar agente Scout: {str(e)}",
        )


@router.get("/scout/portais")
async def scout_portais():
    """Lista portais de licitacao disponiveis para busca."""
    return {
        "portais": [
            {
                "id": "pncp",
                "nome": "Portal Nacional de Contratacoes Publicas",
                "url": "https://pncp.gov.br",
                "status": "disponivel",
                "tipo": "federal",
            },
            {
                "id": "comprasnet",
                "nome": "ComprasNet / Compras.gov.br",
                "url": "https://www.gov.br/compras",
                "status": "disponivel",
                "tipo": "federal",
            },
            {
                "id": "bec",
                "nome": "Bolsa Eletronica de Compras (SP)",
                "url": "https://www.bec.sp.gov.br",
                "status": "planejado",
                "tipo": "estadual",
            },
            {
                "id": "licitacoes_e",
                "nome": "Licitacoes-e (BB)",
                "url": "https://www.licitacoes-e.com.br",
                "status": "planejado",
                "tipo": "banco",
            },
            {
                "id": "e_compras_am",
                "nome": "e-Compras Amazonas",
                "url": "https://www.e-compras.am.gov.br",
                "status": "planejado",
                "tipo": "estadual",
            },
        ],
        "total": 5,
    }


# ============================================================
# Analyst - Analise de editais
# ============================================================
@router.post("/analyst/analisar")
async def analyst_analisar(request: AnalystRequest):
    """Analisa edital extraindo requisitos, prazos, riscos e oportunidades."""
    try:
        if not request.tender_id and not request.edital_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe tender_id ou edital_text para analise",
            )
        result = await analyst_agent.run(
            edital_text=request.edital_text or "",
        )
        if result.success:
            return {
                "status": "success",
                "agent": "analyst",
                "analysis": result.data,
            }
        return {
            "status": "error",
            "agent": "analyst",
            "message": result.error or "Erro na analise",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no agente Analyst: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar agente Analyst: {str(e)}",
        )


# ============================================================
# Assessor - Avaliacao Go/No-Go
# ============================================================
@router.post("/assessor/avaliar")
async def assessor_avaliar(request: AssessorRequest):
    """Avalia viabilidade de participacao (Go/No-Go) com scoring multidimensional."""
    try:
        if not request.tender_id and not request.analysis_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe tender_id ou analysis_id para avaliacao",
            )
        result = await assessor_agent.run(
            analysis={},
        )
        if result.success:
            return {
                "status": "success",
                "agent": "assessor",
                "assessment": result.data,
            }
        return {
            "status": "error",
            "agent": "assessor",
            "message": result.error or "Erro na avaliacao",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no agente Assessor: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar agente Assessor: {str(e)}",
        )


# ============================================================
# Pricer - Precificacao
# ============================================================
@router.post("/pricer/calcular")
async def pricer_calcular(request: PricerRequest):
    """Calcula precificacao com composicao de custos, BDI e cenarios."""
    try:
        pricing_input = {
            "regime_tributario": request.regime_tributario or "simples",
            "bdi_percentual": request.bdi_percentual,
            "cenario": request.cenario or "moderado",
        }
        result = await pricer_agent.run(pricing_input=pricing_input)
        if result.success:
            return {
                "status": "success",
                "agent": "pricer",
                "pricing": result.data,
            }
        return {
            "status": "error",
            "agent": "pricer",
            "message": result.error or "Erro na precificacao",
        }
    except Exception as e:
        logger.error(f"Erro no agente Pricer: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar agente Pricer: {str(e)}",
        )


# ============================================================
# Pipeline - Execucao completa
# ============================================================
@router.post("/pipeline")
async def run_pipeline(request: PipelineRequest):
    """Executa pipeline completo: analise -> avaliacao -> precificacao."""
    try:
        if not request.tender_id and not request.edital_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Informe tender_id ou edital_text para o pipeline",
            )
        if request.edital_text:
            # Analise de edital direto (ANALYST + ASSESSOR)
            pipeline_result = await orchestrator.run_analysis_only(
                edital_text=request.edital_text,
            )
        else:
            # Pipeline completo com busca (SCOUT → ANALYST → ASSESSOR → PRICER)
            pipeline_result = await orchestrator.run_full_pipeline()
        return {
            "status": pipeline_result.status_geral,
            "agent": "pipeline",
            "pipeline": {
                "pipeline_id": pipeline_result.pipeline_id,
                "status": pipeline_result.status_geral,
                "etapas": [
                    {"nome": e.step.value, "status": e.status, "duracao_ms": e.duration_ms}
                    for e in pipeline_result.steps_executados
                ],
                "analise": pipeline_result.analise,
                "avaliacao": pipeline_result.avaliacao,
                "precificacao": pipeline_result.precificacao,
                "score_final": pipeline_result.score_final,
                "recomendacao": pipeline_result.recomendacao_final,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no pipeline de agentes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar pipeline: {str(e)}",
        )


# ============================================================
# Sentinel - Monitoramento de certidoes
# ============================================================
@router.get("/sentinel/tipos")
async def sentinel_tipos():
    """Lista tipos de certidoes monitoradas pelo agente Sentinel."""
    return {
        "tipos": CERTIFICATE_TYPES,
        "total": len(CERTIFICATE_TYPES),
    }


@router.post("/sentinel/verificar")
async def sentinel_verificar():
    """Verifica status atual de todas as certidoes da empresa."""
    try:
        result = await sentinel_agent.run()
        if result.success:
            return {
                "status": "success",
                "agent": "sentinel",
                "verificacao": result.data,
            }
        return {
            "status": "error",
            "agent": "sentinel",
            "message": result.error or "Erro na verificacao",
        }
    except Exception as e:
        logger.error(f"Erro no agente Sentinel: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar agente Sentinel: {str(e)}",
        )


@router.get("/sentinel/alertas")
async def sentinel_alertas():
    """Retorna certidoes proximas do vencimento ou vencidas."""
    try:
        result = await sentinel_agent.run()
        if result.success:
            documentos = result.data.get("documentos", [])
            alertas = [d for d in documentos if d.get("nivel_alerta") in ("urgente", "critico", "atencao")]
            return {
                "status": "success",
                "agent": "sentinel",
                "alertas": alertas,
                "total": len(alertas),
                "apto_licitar": result.data.get("apto_licitar", False),
            }
        return {
            "status": "error",
            "agent": "sentinel",
            "message": result.error or "Erro ao consultar alertas",
        }
    except Exception as e:
        logger.error(f"Erro ao consultar alertas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar alertas: {str(e)}",
        )


# ============================================================
# Warrior - Robo de disputa
# ============================================================
@router.get("/warrior/status")
async def warrior_status():
    """Retorna status do robo de disputa (Warrior)."""
    return {
        "status": warrior_agent.AGENT_STATUS.value,
        "agent": "warrior",
        "message": "Warrior disponivel para simulacao de disputas",
        "modos": ["simulacao"],
        "portais_reais": [],
    }


@router.post("/warrior/simular")
async def warrior_simular(
    valor_referencia: float = 100000.0,
    estrategia: str = "moderado",
    piso_minimo: float | None = None,
    num_rodadas: int = 10,
    concorrentes: int = 3,
):
    """Simula uma disputa de pregao eletronico."""
    try:
        result = await warrior_agent.run(
            valor_referencia=valor_referencia,
            estrategia=estrategia,
            piso_minimo=piso_minimo or valor_referencia * 0.7,
            num_rodadas=num_rodadas,
            concorrentes=concorrentes,
        )
        if result.success:
            return {"status": "success", "agent": "warrior", "simulacao": result.data}
        return {"status": "error", "agent": "warrior", "message": result.error or "Erro na simulacao"}
    except Exception as e:
        logger.error(f"Erro no Warrior: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro na simulacao: {str(e)}")


# ============================================================
# Compiler - Geracao de documentos
# ============================================================
@router.post("/compiler/gerar")
async def compiler_gerar(
    edital_numero: str = "001/2026",
    objeto: str = "Contratacao de servicos de vigilancia patrimonial",
    valor_total: float = 100000.0,
    regime_tributario: str = "simples",
):
    """Gera documentos de proposta (carta, planilha, declaracoes)."""
    try:
        result = await compiler_agent.run(
            analysis_data={"numero_edital": edital_numero, "objeto": objeto, "modalidade": "Pregao Eletronico"},
            pricing_data={"valor_total": valor_total, "regime_tributario": regime_tributario},
        )
        if result.success:
            return {"status": "success", "agent": "compiler", "documentos": result.data}
        return {"status": "error", "agent": "compiler", "message": result.error or "Erro na geracao"}
    except Exception as e:
        logger.error(f"Erro no Compiler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro na geracao: {str(e)}")
