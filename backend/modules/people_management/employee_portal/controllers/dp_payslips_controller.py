"""DP Payslips Controller — Gestão de contracheques pelo Departamento Pessoal.

Endpoints (prefixo /dp/payslips):
  GET    /                  — listar contracheques (filtros: employee_id, mes, ano, status)
  POST   /                  — criar contracheque manualmente
  GET    /{id}              — detalhe
  PATCH  /{id}/publicar     — publicar (torna visível no portal)
  PATCH  /{id}/rascunho     — reverter para rascunho
  DELETE /{id}              — soft delete
  POST   /importar-lote     — importar vários contracheques de uma vez
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dp/payslips", tags=["DP - Contracheques"])


# ─────────────────────────── SCHEMAS ──────────────────────────────


class ItemHolerite(BaseModel):
    descricao: str
    valor: float
    tipo: str = "provento"  # provento | desconto


class PayslipCreateBody(BaseModel):
    employee_id: str
    mes: int = Field(..., ge=1, le=12)
    ano: int = Field(..., ge=2020, le=2030)
    salario_bruto: float = Field(..., ge=0)
    salario_liquido: float = Field(..., ge=0)
    proventos: list[ItemHolerite] = Field(default_factory=list)
    descontos: list[ItemHolerite] = Field(default_factory=list)
    observacoes: str | None = None


class PayslipLoteItem(PayslipCreateBody):
    pass


# ─────────────────────────── ENDPOINTS ────────────────────────────


@router.get("/")
async def listar_payslips(
    employee_id: str | None = Query(None),
    mes: int | None = Query(None, ge=1, le=12),
    ano: int | None = Query(None, ge=2020, le=2030),
    payslip_status: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista contracheques com filtros. Acessível apenas pelo DP/admin."""
    try:
        from modules.hr.employee_portal.models.payslip import PaySlip

        stmt = select(PaySlip).where(PaySlip.is_active == True)  # noqa: E712
        if employee_id:
            stmt = stmt.where(PaySlip.employee_id == uuid.UUID(employee_id))
        if mes:
            stmt = stmt.where(PaySlip.competence_month == mes)
        if ano:
            stmt = stmt.where(PaySlip.competence_year == ano)
        if payslip_status:
            stmt = stmt.where(PaySlip.status == payslip_status)

        stmt = stmt.order_by(PaySlip.competence_year.desc(), PaySlip.competence_month.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        payslips = result.scalars().all()

        return {
            "payslips": [_serialize_payslip(p) for p in payslips],
            "page": page,
            "page_size": page_size,
            "total": len(payslips),
        }
    except Exception as exc:
        logger.warning("Erro ao listar payslips: %s", exc)
        return {"payslips": [], "page": page, "page_size": page_size, "total": 0}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_payslip(body: PayslipCreateBody, db: AsyncSession = Depends(get_db)) -> Any:
    """Cria contracheque manualmente. Status inicial: DRAFT."""
    try:
        from modules.hr.employee_portal.models.payslip import PaySlip, PaySlipStatus, PaySlipType

        payslip = PaySlip(
            id=uuid.uuid4(),
            employee_id=uuid.UUID(body.employee_id),
            competence_month=body.mes,
            competence_year=body.ano,
            gross_salary=body.salario_bruto,
            net_salary=body.salario_liquido,
            deductions=sum(d.valor for d in body.descontos),
            status=PaySlipStatus.DRAFT,
            payslip_type=PaySlipType.MONTHLY,
            notes=body.observacoes,
            items=[
                {"descricao": i.descricao, "valor": i.valor, "tipo": i.tipo} for i in (body.proventos + body.descontos)
            ],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
        )
        db.add(payslip)
        await db.commit()
        await db.refresh(payslip)
        return _serialize_payslip(payslip)
    except Exception as exc:
        await db.rollback()
        logger.error("Erro ao criar payslip: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar contracheque: {exc}",
        ) from exc


@router.get("/{payslip_id}")
async def detalhe_payslip(payslip_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Any:
    """Retorna detalhe de um contracheque."""
    payslip = await _get_or_404(db, payslip_id)
    return _serialize_payslip(payslip)


@router.patch("/{payslip_id}/publicar")
async def publicar_payslip(payslip_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Any:
    """Publica contracheque — torna visível no portal do funcionário."""
    payslip = await _get_or_404(db, payslip_id)
    try:
        from modules.hr.employee_portal.models.payslip import PaySlipStatus

        payslip.status = PaySlipStatus.PUBLISHED
        payslip.published_at = datetime.utcnow()
        payslip.updated_at = datetime.utcnow()
        await db.commit()

        # Dispara auto-notificação para o funcionário
        try:
            from modules.people_management.employee_portal.services.auto_notification_service import (
                AutoNotificationService,
            )

            await AutoNotificationService(db).notify_payslip_published(
                employee_id=str(payslip.employee_id),
                mes=payslip.competence_month,
                ano=payslip.competence_year,
            )
        except Exception as notif_err:
            logger.warning("Auto-notificação payslip falhou: %s", notif_err)

        return {"message": "Contracheque publicado com sucesso.", "payslip_id": str(payslip_id)}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.patch("/{payslip_id}/rascunho")
async def reverter_rascunho(payslip_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Any:
    """Reverte contracheque para rascunho."""
    payslip = await _get_or_404(db, payslip_id)
    try:
        from modules.hr.employee_portal.models.payslip import PaySlipStatus

        payslip.status = PaySlipStatus.DRAFT
        payslip.updated_at = datetime.utcnow()
        await db.commit()
        return {"message": "Contracheque revertido para rascunho.", "payslip_id": str(payslip_id)}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.delete("/{payslip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_payslip(payslip_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    """Soft delete de contracheque."""
    payslip = await _get_or_404(db, payslip_id)
    try:
        payslip.is_active = False
        payslip.updated_at = datetime.utcnow()
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/importar-lote", status_code=status.HTTP_201_CREATED)
async def importar_lote(items: list[PayslipLoteItem], db: AsyncSession = Depends(get_db)) -> Any:
    """Importa múltiplos contracheques de uma vez. Máximo 100 por lote."""
    if len(items) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo de 100 contracheques por lote.",
        )
    criados = 0
    erros = []
    for item in items:
        try:
            from modules.hr.employee_portal.models.payslip import PaySlip, PaySlipStatus, PaySlipType

            p = PaySlip(
                id=uuid.uuid4(),
                employee_id=uuid.UUID(item.employee_id),
                competence_month=item.mes,
                competence_year=item.ano,
                gross_salary=item.salario_bruto,
                net_salary=item.salario_liquido,
                deductions=sum(d.valor for d in item.descontos),
                status=PaySlipStatus.DRAFT,
                payslip_type=PaySlipType.MONTHLY,
                notes=item.observacoes,
                items=[
                    {"descricao": i.descricao, "valor": i.valor, "tipo": i.tipo}
                    for i in (item.proventos + item.descontos)
                ],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True,
            )
            db.add(p)
            criados += 1
        except Exception as exc:
            erros.append({"employee_id": item.employee_id, "erro": str(exc)})

    await db.commit()
    return {"criados": criados, "erros": erros}


# ─────────────────────────── HELPERS ──────────────────────────────


async def _get_or_404(db: AsyncSession, payslip_id: uuid.UUID):
    try:
        from modules.hr.employee_portal.models.payslip import PaySlip

        result = await db.execute(
            select(PaySlip).where(PaySlip.id == payslip_id, PaySlip.is_active == True)  # noqa: E712
        )
        payslip = result.scalar_one_or_none()
    except Exception:
        payslip = None

    if not payslip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contracheque não encontrado.")
    return payslip


def _serialize_payslip(p: Any) -> dict:
    return {
        "id": str(p.id),
        "employee_id": str(p.employee_id),
        "mes": p.competence_month,
        "ano": p.competence_year,
        "salario_bruto": float(p.gross_salary or 0),
        "salario_liquido": float(p.net_salary or 0),
        "descontos": float(p.deductions or 0),
        "status": str(p.status) if p.status else "draft",
        "tipo": str(p.payslip_type) if p.payslip_type else "monthly",
        "observacoes": p.notes,
        "items": p.items or [],
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "published_at": p.published_at.isoformat() if hasattr(p, "published_at") and p.published_at else None,
    }
