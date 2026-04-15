"""
Controller de Overview Financeiro — dados para a pagina /modulos/financeiro.

Endpoints que a pagina principal chama via hooks Orval:
- GET /bi-dashboard/bi/dashboards/stats → IFinancialOverview
- GET /payables/payables/stats → PayableStats
- GET /receivables/receivables/stats → ReceivableStats
- GET /cashflow/cashflow/dashboard → CashflowDashboard
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Financial Overview"])


@router.get("/bi-dashboard/bi/dashboards/stats")
async def financial_overview_stats(
    condominio_id: str | None = Query(None),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Overview financeiro: receita, despesa, saldo, inadimplencia."""
    # Receita: NFS-e emitidas (acumulado)
    r_nfse = (await db.execute(text("SELECT COALESCE(SUM(valor_servicos), 0) FROM nfses WHERE active = true"))).scalar()

    # Despesa: payable_accounts pagos
    r_desp = (
        await db.execute(
            text(
                "SELECT COALESCE(SUM(net_value), 0) FROM payable_accounts "
                "WHERE status IN ('pago','paga','paid','concluido')"
            )
        )
    ).scalar()

    # Saldo bancario
    r_saldo = (
        await db.execute(
            text("SELECT COALESCE(SUM(current_balance), 0) FROM bank_accounts WHERE status IN ('ativo','ativa')")
        )
    ).scalar()

    # Inadimplencia: receivables vencidos nao pagos
    r_inad = (
        await db.execute(
            text(
                "SELECT COALESCE(SUM(net_value), 0) FROM receivable_accounts "
                "WHERE status NOT IN ('paga','cancelada','baixada') AND due_date < CURRENT_DATE"
            )
        )
    ).scalar()

    return {
        "receita_total": round(float(r_nfse or 0), 2),
        "despesa_total": round(float(r_desp or 0), 2),
        "saldo": round(float(r_saldo or 0), 2),
        "inadimplencia": round(float(r_inad or 0), 2),
    }


@router.get("/payables/payables/stats")
async def payable_stats(
    condominio_id: str | None = Query(None),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Stats de contas a pagar."""
    r = await db.execute(
        text(
            "SELECT "
            "  COUNT(*) FILTER (WHERE status NOT IN ('pago','paga','cancelada')) as pendentes, "
            "  COALESCE(SUM(net_value) FILTER (WHERE status NOT IN ('pago','paga','cancelada')), 0) as total_pendente, "
            "  COUNT(*) FILTER (WHERE status NOT IN ('pago','paga','cancelada') AND due_date < CURRENT_DATE) as vencidas, "
            "  COALESCE(SUM(net_value) FILTER (WHERE status NOT IN ('pago','paga','cancelada') AND due_date < CURRENT_DATE), 0) as total_vencido, "
            "  COUNT(*) FILTER (WHERE status IN ('pago','paga')) as pagas, "
            "  COALESCE(SUM(net_value) FILTER (WHERE status IN ('pago','paga')), 0) as total_pago "
            "FROM payable_accounts"
        )
    )
    row = r.mappings().first()
    return {
        "pendentes": int(row["pendentes"]) if row else 0,
        "total_pendente": round(float(row["total_pendente"]), 2) if row else 0,
        "vencidas": int(row["vencidas"]) if row else 0,
        "total_vencido": round(float(row["total_vencido"]), 2) if row else 0,
        "pagas": int(row["pagas"]) if row else 0,
        "total_pago": round(float(row["total_pago"]), 2) if row else 0,
    }


@router.get("/receivables/receivables/stats")
async def receivable_stats(
    condominio_id: str | None = Query(None),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Stats de contas a receber."""
    r = await db.execute(
        text(
            "SELECT "
            "  COUNT(*) as total, "
            "  COUNT(*) FILTER (WHERE status NOT IN ('paga','cancelada','baixada')) as pendentes, "
            "  COALESCE(SUM(gross_value) FILTER (WHERE status NOT IN ('paga','cancelada','baixada')), 0) as total_pendente, "
            "  COUNT(*) FILTER (WHERE status NOT IN ('paga','cancelada','baixada') AND due_date < CURRENT_DATE) as vencidas, "
            "  COALESCE(SUM(gross_value) FILTER (WHERE status NOT IN ('paga','cancelada','baixada') AND due_date < CURRENT_DATE), 0) as total_vencido, "
            "  COUNT(*) FILTER (WHERE status IN ('paga')) as recebidas, "
            "  COALESCE(SUM(gross_value) FILTER (WHERE status IN ('paga')), 0) as total_recebido "
            "FROM receivable_accounts"
        )
    )
    row = r.mappings().first()
    return {
        "total": int(row["total"]) if row else 0,
        "pendentes": int(row["pendentes"]) if row else 0,
        "total_pendente": round(float(row["total_pendente"]), 2) if row else 0,
        "vencidas": int(row["vencidas"]) if row else 0,
        "total_vencido": round(float(row["total_vencido"]), 2) if row else 0,
        "recebidas": int(row["recebidas"]) if row else 0,
        "total_recebido": round(float(row["total_recebido"]), 2) if row else 0,
    }


@router.get("/cashflow/cashflow/dashboard")
async def cashflow_dashboard(
    condominio_id: str | None = Query(None),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dashboard de fluxo de caixa simplificado."""
    saldo = (
        await db.execute(
            text("SELECT COALESCE(SUM(current_balance), 0) FROM bank_accounts WHERE status IN ('ativo','ativa')")
        )
    ).scalar()

    entradas_7d = (
        await db.execute(
            text(
                "SELECT COALESCE(SUM(amount), 0) FROM bank_transactions "
                "WHERE transaction_type IN ('credito','credit','entrada') AND transaction_date >= CURRENT_DATE - 7"
            )
        )
    ).scalar()

    saidas_7d = (
        await db.execute(
            text(
                "SELECT COALESCE(SUM(amount), 0) FROM bank_transactions "
                "WHERE transaction_type IN ('debito','debit','saida') AND transaction_date >= CURRENT_DATE - 7"
            )
        )
    ).scalar()

    return {
        "saldo_atual": round(float(saldo or 0), 2),
        "entradas_7d": round(float(entradas_7d or 0), 2),
        "saidas_7d": round(float(saidas_7d or 0), 2),
        "projecao_30d": round(float(saldo or 0) + float(entradas_7d or 0) * 4 - float(saidas_7d or 0) * 4, 2),
    }
