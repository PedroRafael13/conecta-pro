"""
Controller de Folha de Pagamento — Departamento Pessoal.

Re-exporta endpoints de folha do módulo HR e adiciona endpoints
para cálculo individual e fechamento mensal.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.services.payroll_service import PayrollService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payroll", tags=["DP - Folha de Pagamento"])

# Re-export do router existente de payroll
# IMPORTANTE: usar include_router (NÃO append) para preservar prefixos
try:
    from modules.hr.payroll_integration.controllers import router as _payroll_router

    router.include_router(_payroll_router)
except ImportError:
    logger.info("Router de payroll não disponível para re-export")


@router.get("/employee/{employee_id}/calculate")
async def calculate_employee_payroll(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12, description="Mês de referência"),
    year: int = Query(..., ge=2020, le=2030, description="Ano de referência"),
) -> Any:
    """Calcula a folha de pagamento de um funcionário."""
    service = PayrollService(db)
    try:
        return await service.calculate_employee_payroll(employee_id, month, year)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# RUBRICAS (BENEFITS) POR FUNCIONÁRIO
# =============================================================================


@router.get("/benefits")
async def list_all_benefits(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    employee_id: str | None = Query(None, description="Filtrar por funcionário"),
    status: str = Query("active", description="Status: active, inactive"),
) -> Any:
    """Lista rubricas/benefícios cadastrados por funcionário."""
    from sqlalchemy import text

    sql = "SELECT b.*, e.nome as employee_name FROM employee_benefits b JOIN employees e ON b.employee_id = e.id WHERE b.status = :status"
    params: dict = {"status": status}
    if employee_id:
        sql += " AND b.employee_id = :emp_id"
        params["emp_id"] = employee_id
    sql += " ORDER BY e.nome, b.type"

    result = await db.execute(text(sql), params)
    rows = result.fetchall()

    return {
        "items": [
            {
                "id": str(r.id),
                "employee_id": str(r.employee_id),
                "employee_name": r.employee_name,
                "type": r.type,
                "provider": r.provider,
                "plan_name": r.plan_name,
                "employee_contribution": float(r.employee_contribution or 0),
                "company_contribution": float(r.company_contribution or 0),
                "start_date": r.start_date.isoformat() if r.start_date else None,
                "end_date": r.end_date.isoformat() if r.end_date else None,
                "status": r.status,
                "notes": r.notes,
            }
            for r in rows
        ],
        "total": len(rows),
    }


@router.post("/benefits")
async def create_benefit(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    employee_id: str = Query(..., description="ID do funcionário"),
    benefit_type: str = Query(
        ..., description="Tipo: Emprestimo Consignado, Pensao Alimenticia, Vale Refeicao, Plano Saude, etc"
    ),
    employee_contribution: float = Query(0, description="Valor desconto do funcionário"),
    company_contribution: float = Query(0, description="Valor da empresa"),
    provider: str = Query("", description="Fornecedor/banco"),
    plan_name: str = Query("", description="Nome do plano/descrição"),
    notes: str = Query("", description="Observações"),
) -> Any:
    """Cadastra nova rubrica/benefício para um funcionário."""
    from sqlalchemy import text

    result = await db.execute(
        text(
            "INSERT INTO employee_benefits (employee_id, type, provider, plan_name, employee_contribution, company_contribution, notes, status) "
            "VALUES (:emp_id, :type, :provider, :plan, :emp_val, :co_val, :notes, 'active') RETURNING id"
        ),
        {
            "emp_id": employee_id,
            "type": type,
            "provider": provider or None,
            "plan": plan_name or None,
            "emp_val": employee_contribution,
            "co_val": company_contribution,
            "notes": notes or None,
        },
    )
    new_id = result.scalar()
    await db.commit()
    return {"id": str(new_id), "message": f"Rubrica '{type}' cadastrada para funcionário {employee_id}"}


@router.delete("/benefits/{benefit_id}")
async def delete_benefit(
    benefit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Desativa uma rubrica/benefício."""
    from sqlalchemy import text

    await db.execute(
        text("UPDATE employee_benefits SET status = 'inactive', updated_at = now() WHERE id = :id"),
        {"id": benefit_id},
    )
    await db.commit()
    return {"message": "Rubrica desativada"}


@router.get("/rubricas")
async def list_rubricas(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista rubricas disponíveis (tabela de referência)."""
    from sqlalchemy import text

    result = await db.execute(text("SELECT * FROM rubricas_folha WHERE ativo ORDER BY codigo"))
    rows = result.fetchall()
    return {
        "items": [
            {
                "id": r.id,
                "codigo": r.codigo,
                "descricao": r.descricao,
                "tipo": r.tipo,
                "valor_fixo": float(r.valor_fixo) if r.valor_fixo else None,
                "percentual": float(r.percentual) if r.percentual else None,
                "incide_inss": r.incide_inss,
                "incide_irrf": r.incide_irrf,
                "incide_fgts": r.incide_fgts,
            }
            for r in rows
        ],
        "total": len(rows),
    }


@router.post("/close")
async def close_payroll(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    month: int = Query(..., ge=1, le=12, description="Mês de referência"),
    year: int = Query(..., ge=2020, le=2030, description="Ano de referência"),
) -> Any:
    """Fecha a folha de pagamento mensal para todos os funcionários ativos."""
    service = PayrollService(db)
    result = await service.close_payroll(month, year)
    await db.commit()
    return result
