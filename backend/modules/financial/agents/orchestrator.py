"""Orchestrator — Coordena os agentes financeiros de IA em paralelo."""

import asyncio
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.agents.cashflow_predictor import CashflowPredictorAgent
from modules.financial.agents.collection_negotiator import CollectionNegotiatorAgent
from modules.financial.agents.risk_monitor import RiskMonitorAgent

logger = logging.getLogger("agents.orchestrator")


async def run_command_center(session: AsyncSession) -> dict:
    """
    Executa CashflowPredictorAgent e RiskMonitorAgent em paralelo e
    consolida o resultado do Command Center financeiro.
    """
    cashflow_agent = CashflowPredictorAgent(session)
    risk_agent = RiskMonitorAgent(session)

    # Executar predict e scan em paralelo
    cashflow_result, alerts_raw = await asyncio.gather(
        cashflow_agent.predict(days=90),
        risk_agent.scan(),
        return_exceptions=True,
    )

    # Tratar exceções inesperadas do gather
    if isinstance(cashflow_result, Exception):
        logger.warning("Erro no cashflow_predictor: %s", cashflow_result)
        cashflow_result = await cashflow_agent._fallback(days=90)

    if isinstance(alerts_raw, Exception):
        logger.warning("Erro no risk_monitor scan: %s", alerts_raw)
        alerts_raw = []

    # Health check (usa os alertas já calculados)
    health_data = await risk_agent.health_check()

    # Enriquecer health com dados do cashflow
    cashflow_trend = cashflow_result.get("trend", "estavel") if cashflow_result else "estavel"
    if cashflow_trend != "negativo":
        health_data["revenue_trend"] = cashflow_trend

    # ----------------------------------------------------------------
    # Gerar insights com base nos resultados combinados
    # ----------------------------------------------------------------
    insights: list[dict] = []

    # Insight de gap de caixa previsto
    gaps = cashflow_result.get("gaps", []) if cashflow_result else []
    if gaps:
        first_gap = gaps[0]
        insights.append(
            {
                "type": "risco",
                "icon": "⚠️",
                "title": f"Gap de caixa previsto em {first_gap['date']}",
                "description": (
                    f"Saldo projetado de R$ {first_gap['projected_balance']:,.2f} no cenário pessimista. "
                    "Tome medidas preventivas para evitar falta de liquidez."
                ),
                "priority": 5,
            }
        )

    # Insight de alertas críticos
    critical_alerts = [a for a in alerts_raw if isinstance(a, dict) and a.get("level") == "critico"]
    if critical_alerts:
        insights.append(
            {
                "type": "alerta",
                "icon": "🚨",
                "title": f"{len(critical_alerts)} alerta(s) crítico(s) detectado(s)",
                "description": (
                    "Existem contas com mais de 60 dias de atraso. Ação imediata é necessária para minimizar perdas."
                ),
                "priority": 5,
            }
        )

    # Insight de tendência positiva
    if cashflow_trend == "positivo" and not gaps:
        insights.append(
            {
                "type": "oportunidade",
                "icon": "📈",
                "title": "Fluxo de caixa em tendência positiva",
                "description": (
                    "A projeção de 90 dias indica crescimento consistente. "
                    "Considere reinvestir o excedente em expansão ou reservas."
                ),
                "priority": 2,
            }
        )

    # Insight de margem
    margin = health_data.get("margin_avg", 0.0)
    if margin > 20:
        insights.append(
            {
                "type": "oportunidade",
                "icon": "✅",
                "title": f"Margem operacional saudável: {margin:.1f}%",
                "description": (
                    "Operação com boa rentabilidade. Mantenha o controle de custos para sustentar o resultado."
                ),
                "priority": 1,
            }
        )
    elif margin > 0 and margin <= 10:
        insights.append(
            {
                "type": "risco",
                "icon": "📉",
                "title": f"Margem operacional baixa: {margin:.1f}%",
                "description": ("Receitas e despesas estão muito próximas. Revise contratos de baixa margem."),
                "priority": 4,
            }
        )

    # Insight de inadimplência controlada
    default_rate = health_data.get("default_rate", 0.0)
    if default_rate < 2 and not critical_alerts:
        insights.append(
            {
                "type": "oportunidade",
                "icon": "💚",
                "title": "Inadimplência sob controle",
                "description": (
                    f"Taxa de {default_rate:.1f}% está excelente. "
                    "Considere oferecer condições diferenciadas para bons pagadores."
                ),
                "priority": 1,
            }
        )

    # Ordenar insights por prioridade (maior primeiro)
    insights.sort(key=lambda x: x["priority"], reverse=True)

    # Buscar dados de cobrança para enriquecer os insights
    try:
        collection_agent = CollectionNegotiatorAgent(session)
        collection_data = await collection_agent.analisar()
        qtd_inadimplentes = collection_data.get("qtd_inadimplentes", 0)
        total_em_atraso = collection_data.get("total_em_atraso", 0.0)
        if qtd_inadimplentes > 0:
            insights.append(
                {
                    "type": "alerta",
                    "icon": "📋",
                    "title": f"{qtd_inadimplentes} cliente(s) inadimplente(s) — ação necessária",
                    "description": (
                        f"Total de R$ {total_em_atraso:,.2f} em atraso. "
                        "Acione a régua de cobrança para maximizar a recuperação."
                    ),
                    "priority": 4,
                }
            )
    except Exception as exc:
        logger.debug("CollectionNegotiatorAgent indisponível: %s", exc)

    # Ordenar insights por prioridade (maior primeiro)
    insights.sort(key=lambda x: x["priority"], reverse=True)

    return {
        "health": health_data,
        "alerts": alerts_raw,
        "insights": insights,
        "cashflow": cashflow_result,
        "updated_at": datetime.now().isoformat(),
    }
