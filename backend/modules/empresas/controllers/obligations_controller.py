"""Controller de Obrigações Multi-Empresa — Fase 7."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from core.auth import get_current_user
from modules.empresas.agents.obligations_monitor import ObligationsMonitorAgent

router = APIRouter(prefix="/obrigacoes", tags=["Obrigações Multi-Empresa"])
_agent = ObligationsMonitorAgent()


@router.get("/calendario/grupo")
async def calendario_grupo(
    mes: int = Query(default=date.today().month, ge=1, le=12),
    ano: int = Query(default=date.today().year, ge=2024, le=2030),
    current_user=Depends(get_current_user),
):
    """Calendário consolidado de obrigações de todas as empresas."""
    cal = _agent.gerar_calendario_grupo(mes, ano)
    return {
        "mes": cal.mes,
        "ano": cal.ano,
        "resumo": {
            "total": cal.total_obrigacoes,
            "criticas": cal.criticas,
            "atrasadas": cal.atrasadas,
            "pendentes": cal.pendentes,
            "concluidas": cal.concluidas,
        },
        "por_empresa": {
            slug: [
                {
                    "tipo": o.tipo,
                    "descricao": o.descricao,
                    "periodo": o.periodo_referencia,
                    "vencimento": o.data_vencimento.isoformat(),
                    "status": o.status,
                    "urgencia": o.urgencia,
                    "regime": o.regime,
                    "link": o.link_sistema,
                }
                for o in obs
            ]
            for slug, obs in cal.por_empresa.items()
        },
        "consolidado": [
            {
                "empresa": o.empresa_nome,
                "empresa_slug": o.empresa_slug,
                "tipo": o.tipo,
                "descricao": o.descricao,
                "vencimento": o.data_vencimento.isoformat(),
                "status": o.status,
                "urgencia": o.urgencia,
            }
            for o in cal.consolidado
        ],
    }


@router.get("/calendario/{empresa_slug}")
async def calendario_empresa(
    empresa_slug: str,
    mes: int = Query(default=date.today().month, ge=1, le=12),
    ano: int = Query(default=date.today().year, ge=2024, le=2030),
    current_user=Depends(get_current_user),
):
    """Calendário de obrigações de uma empresa específica."""
    regime_map = {
        "conecta_eletronica": "lucro_real",
        "conecta_patrimonial": "simples_nacional",
    }
    nome_map = {
        "conecta_eletronica": "Conecta Mais Eletrônica",
        "conecta_patrimonial": "Conecta Mais Patrimonial",
    }
    regime = regime_map.get(empresa_slug, "lucro_real")
    nome = nome_map.get(empresa_slug, empresa_slug)
    obs = _agent.gerar_calendario_empresa(empresa_slug, nome, regime, mes, ano)
    return {
        "empresa_slug": empresa_slug,
        "empresa_nome": nome,
        "regime": regime,
        "mes": mes,
        "ano": ano,
        "total": len(obs),
        "obrigacoes": [
            {
                "tipo": o.tipo,
                "descricao": o.descricao,
                "periodo": o.periodo_referencia,
                "vencimento": o.data_vencimento.isoformat(),
                "status": o.status,
                "urgencia": o.urgencia,
                "link": o.link_sistema,
            }
            for o in obs
        ],
    }


@router.get("/alertas")
async def alertas_vencimentos(
    dias: int = Query(default=10, ge=1, le=60),
    current_user=Depends(get_current_user),
):
    """Alerta sobre obrigações próximas de vencer em todas as empresas."""
    return {"alertas": _agent.alertar_vencimentos(dias), "dias_antecedencia": dias}


@router.get("/dispensadas-simples")
async def obrigacoes_dispensadas(current_user=Depends(get_current_user)):
    """Lista obrigações das quais o Simples Nacional é dispensado."""
    return {
        "regime": "Simples Nacional",
        "empresa": "Conecta Mais Patrimonial",
        "dispensadas": _agent.obrigacoes_dispensadas_simples(),
        "observacao": "Empresas do Simples Nacional são dispensadas dessas obrigações conforme LC 123/2006",
    }
