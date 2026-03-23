"""
Controller de NFS-e e Dashboard Financeiro.

Endpoints para consulta de notas fiscais de servico emitidas
e metricas de faturamento.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["NFS-e"])


@router.get("/nfse")
async def list_nfse(
    competencia: str | None = Query(None, description="YYYY-MM (ex: 2026-01)"),
    cliente: str | None = Query(None, description="Filtro por razao social (parcial)"),
    status: str | None = Query(None, description="autorizada, cancelada, etc."),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista NFS-e emitidas com filtros."""
    conditions = ["active = true"]
    params: dict[str, Any] = {"limit": limit}

    if competencia:
        conditions.append("to_char(data_competencia, 'YYYY-MM') = :competencia")
        params["competencia"] = competencia
    if cliente:
        conditions.append("tomador_razao_social ILIKE :cliente")
        params["cliente"] = f"%{cliente}%"
    if status:
        conditions.append("status = :status")
        params["status"] = status

    where = " AND ".join(conditions)
    result = await db.execute(
        text(f"SELECT * FROM nfses WHERE {where} ORDER BY data_competencia DESC, numero_rps LIMIT :limit"),
        params,
    )
    rows = result.mappings().all()

    return {
        "total": len(rows),
        "items": [
            {
                "id": str(r["id"]),
                "numero_nfse": r["numero_nfse"],
                "numero_rps": r["numero_rps"],
                "status": r["status"],
                "data_emissao": r["data_emissao"].isoformat() if r["data_emissao"] else None,
                "data_competencia": r["data_competencia"].isoformat() if r["data_competencia"] else None,
                "tomador_razao_social": r["tomador_razao_social"],
                "tomador_cpf_cnpj": r["tomador_cpf_cnpj"],
                "descricao_servico": r["descricao_servico"],
                "valor_servicos": float(r["valor_servicos"]),
                "iss_aliquota": float(r["iss_aliquota"]),
                "iss_valor": float(r["iss_valor"]) if r["iss_valor"] else 0,
                "iss_retido": r["iss_retido"],
                "discriminacao": r["discriminacao"],
            }
            for r in rows
        ],
    }


@router.get("/nfse/dashboard")
async def nfse_dashboard(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dashboard de faturamento com metricas consolidadas."""
    # Faturamento por competencia
    por_mes = await db.execute(
        text("""
        SELECT
            to_char(data_competencia, 'YYYY-MM') as competencia,
            count(*) as nfse_emitidas,
            sum(valor_servicos) as faturamento_bruto,
            sum(iss_valor) as iss_total,
            sum(valor_servicos) - COALESCE(sum(iss_valor), 0) as faturamento_liquido
        FROM nfses
        WHERE active = true
        GROUP BY data_competencia
        ORDER BY data_competencia DESC
        LIMIT 12
    """)
    )
    meses = por_mes.mappings().all()

    # Faturamento por cliente (acumulado)
    por_cliente = await db.execute(
        text("""
        SELECT
            tomador_razao_social as cliente,
            tomador_cpf_cnpj as cnpj,
            count(*) as nfse_emitidas,
            sum(valor_servicos) as total_bruto,
            sum(iss_valor) as total_iss
        FROM nfses
        WHERE active = true
        GROUP BY tomador_razao_social, tomador_cpf_cnpj
        ORDER BY sum(valor_servicos) DESC
    """)
    )
    clientes = por_cliente.mappings().all()

    # Faturamento por tipo de servico
    por_servico = await db.execute(
        text("""
        SELECT
            descricao_servico as servico,
            count(*) as quantidade,
            sum(valor_servicos) as total
        FROM nfses
        WHERE active = true
        GROUP BY descricao_servico
        ORDER BY sum(valor_servicos) DESC
    """)
    )
    servicos = por_servico.mappings().all()

    # Totais gerais
    totais = await db.execute(
        text("""
        SELECT
            count(*) as total_nfse,
            count(DISTINCT tomador_cpf_cnpj) as total_clientes,
            sum(valor_servicos) as faturamento_total,
            sum(iss_valor) as iss_total,
            avg(valor_servicos) as ticket_medio
        FROM nfses
        WHERE active = true
    """)
    )
    t = totais.mappings().first()

    return {
        "totais": {
            "nfse_emitidas": t["total_nfse"] if t else 0,
            "clientes_ativos": t["total_clientes"] if t else 0,
            "faturamento_bruto": round(float(t["faturamento_total"]), 2) if t and t["faturamento_total"] else 0,
            "iss_total": round(float(t["iss_total"]), 2) if t and t["iss_total"] else 0,
            "ticket_medio": round(float(t["ticket_medio"]), 2) if t and t["ticket_medio"] else 0,
        },
        "por_mes": [
            {
                "competencia": m["competencia"],
                "nfse_emitidas": m["nfse_emitidas"],
                "faturamento_bruto": round(float(m["faturamento_bruto"]), 2),
                "iss_total": round(float(m["iss_total"]), 2) if m["iss_total"] else 0,
                "faturamento_liquido": round(float(m["faturamento_liquido"]), 2) if m["faturamento_liquido"] else 0,
            }
            for m in meses
        ],
        "por_cliente": [
            {
                "cliente": c["cliente"],
                "cnpj": c["cnpj"],
                "nfse_emitidas": c["nfse_emitidas"],
                "total_bruto": round(float(c["total_bruto"]), 2),
                "total_iss": round(float(c["total_iss"]), 2) if c["total_iss"] else 0,
            }
            for c in clientes
        ],
        "por_servico": [
            {
                "servico": s["servico"],
                "quantidade": s["quantidade"],
                "total": round(float(s["total"]), 2),
            }
            for s in servicos
        ],
    }


@router.get("/headcount")
async def headcount_by_client(
    current_user: CurrentActiveUser = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Headcount por cliente com folha bruta e valor do contrato."""
    result = await db.execute(
        text("""
        SELECT
            g.id as client_id,
            g.name as cliente,
            (SELECT n2.tomador_cpf_cnpj FROM nfses n2 WHERE n2.condominio_id = g.id LIMIT 1) as cnpj,
            count(DISTINCT a.employee_id) as headcount,
            (SELECT sum(e2.salario_base)
             FROM employees e2
             WHERE e2.id IN (
                SELECT DISTINCT a2.employee_id
                FROM allocations a2
                JOIN posts p2 ON a2.post_id = p2.id
                WHERE p2.client_id::text = g.id::text
                AND a2.status = 'active' AND p2.is_active = true
                AND e2.is_active = true
             )
            ) as folha_bruta,
            COALESCE((
                SELECT sum(valor_servicos)
                FROM nfses
                WHERE condominio_id = g.id
                AND data_competencia = (
                    SELECT MAX(data_competencia) FROM nfses
                    WHERE condominio_id = g.id AND active = true
                )
            ), 0) as contrato_mensal
        FROM ged_clients g
        JOIN posts p ON p.client_id::text = g.id::text AND p.is_active = true
        JOIN allocations a ON a.post_id = p.id AND a.status = 'active'
        JOIN employees e ON e.id = a.employee_id AND e.is_active = true
        GROUP BY g.id, g.name
        ORDER BY count(DISTINCT a.employee_id) DESC
    """)
    )
    rows = result.mappings().all()

    total_headcount = sum(r["headcount"] for r in rows)
    total_folha = sum(float(r["folha_bruta"]) for r in rows)

    return {
        "total_headcount": total_headcount,
        "total_folha_bruta": round(total_folha, 2),
        "por_cliente": [
            {
                "client_id": str(r["client_id"]),
                "cliente": r["cliente"],
                "cnpj": r["cnpj"],
                "headcount": r["headcount"],
                "folha_bruta": round(float(r["folha_bruta"]), 2),
                "contrato_mensal": round(float(r["contrato_mensal"]), 2),
            }
            for r in rows
        ],
    }
