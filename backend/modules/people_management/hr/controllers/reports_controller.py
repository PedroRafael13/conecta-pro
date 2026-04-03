"""
Controller de Relatórios — Departamento Pessoal.

Endpoints de relatórios gerenciais: headcount, turnover, custo de benefícios.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["DP - Relatórios"])


@router.get(
    "/headcount",
    summary="Relatório de Headcount",
    description="Endpoint do módulo Departamento Pessoal — Reports.",
)
async def get_headcount(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna total de funcionários por status e por cargo CCT."""

    status_result = await db.execute(
        text("SELECT status, COUNT(*) as qtd FROM employees GROUP BY status ORDER BY qtd DESC")
    )
    por_status = [{"status": r[0], "total": r[1]} for r in status_result.fetchall()]

    cargo_result = await db.execute(
        text("""
            SELECT
                COALESCE(cargo, 'Sem cargo') AS cargo,
                COUNT(*)                      AS total,
                COUNT(*) FILTER (WHERE status = 'ativo') AS ativos
            FROM employees
            GROUP BY cargo
            ORDER BY ativos DESC
            LIMIT 30
        """)
    )
    por_cargo = [{"cargo": r[0], "total": r[1], "ativos": r[2]} for r in cargo_result.fetchall()]

    total_result = await db.execute(text("SELECT COUNT(*) FROM employees"))
    total_geral = total_result.scalar() or 0

    ativos_result = await db.execute(text("SELECT COUNT(*) FROM employees WHERE status = 'ativo'"))
    total_ativos = ativos_result.scalar() or 0

    return {
        "resumo": {
            "total_geral": total_geral,
            "total_ativos": total_ativos,
            "total_inativos": total_geral - total_ativos,
            "indice_atividade": round(total_ativos / total_geral * 100, 1) if total_geral > 0 else 0,
        },
        "por_status": por_status,
        "por_cargo": por_cargo,
    }
