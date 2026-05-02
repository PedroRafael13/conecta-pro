"""D7 — Payment controller: endpoints de pagamento Inter com 2FA OTP.

Prefixo: /api/v1/financeiro/inter/payments
"""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database.session import get_db
from modules.integrations.inter.services.payment_service import (
    IdempotenciaError,
    InterPaymentService,
    LimiteDiarioError,
    OTPInvalidoError,
    PaymentError,
    SaldoInsuficienteError,
    StatusInvalidoError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financeiro/inter/payments", tags=["D7-Payments"])


# ── Schemas de entrada ────────────────────────────────────────────────────────


class PrepararPayload(BaseModel):
    payment_type: str
    destinatario: dict
    valor: float = Field(gt=0)
    data_pagamento: date
    observacoes: str = ""


class AprovarPayload(BaseModel):
    otp_code: str = Field(min_length=6, max_length=6)


class CancelarPayload(BaseModel):
    motivo: str = Field(min_length=3)


# ── helpers ───────────────────────────────────────────────────────────────────


def _handle_payment_error(exc: Exception) -> HTTPException:
    if isinstance(exc, LimiteDiarioError):
        return HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, SaldoInsuficienteError):
        return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    if isinstance(exc, OTPInvalidoError):
        return HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    if isinstance(exc, StatusInvalidoError):
        return HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, IdempotenciaError):
        return HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))
    return HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ── endpoints ─────────────────────────────────────────────────────────────────


@router.post("", status_code=201)
async def preparar_pagamento(
    payload: PrepararPayload,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """D7.1 — Prepara pagamento (status='preparado'). Sem chamada Inter."""
    svc = InterPaymentService(db)
    try:
        return await svc.preparar(
            payment_type=payload.payment_type,
            destinatario=payload.destinatario,
            valor=payload.valor,
            data_pagamento=payload.data_pagamento,
            prepared_by=str(current_user.id),
            observacoes=payload.observacoes,
        )
    except PaymentError as exc:
        raise _handle_payment_error(exc) from exc


@router.post("/{payment_id}/gerar-otp")
async def gerar_otp(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """D7.1 — Gera OTP 6 dígitos e envia email Jordan."""
    svc = InterPaymentService(db)
    try:
        return await svc.gerar_otp(payment_id, str(current_user.id))
    except PaymentError as exc:
        raise _handle_payment_error(exc) from exc


@router.post("/{payment_id}/aprovar")
async def aprovar_pagamento(
    payment_id: str,
    payload: AprovarPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """D7.1 — Valida OTP e aprova pagamento (status='aprovado')."""
    ip = request.client.host if request.client else ""
    svc = InterPaymentService(db)
    try:
        return await svc.aprovar(payment_id, payload.otp_code, str(current_user.id), ip)
    except PaymentError as exc:
        raise _handle_payment_error(exc) from exc


@router.post("/{payment_id}/executar")
async def executar_pagamento(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """D7.1 — Chama Inter API. Apenas após status='aprovado'. Idempotente (max 1x)."""
    svc = InterPaymentService(db)
    try:
        return await svc.executar(payment_id, str(current_user.id))
    except PaymentError as exc:
        raise _handle_payment_error(exc) from exc


@router.post("/{payment_id}/cancelar")
async def cancelar_pagamento(
    payment_id: str,
    payload: CancelarPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """D7.1 — Cancela pagamento se não executado ainda."""
    ip = request.client.host if request.client else ""
    svc = InterPaymentService(db)
    try:
        return await svc.cancelar(payment_id, payload.motivo, str(current_user.id), ip)
    except PaymentError as exc:
        raise _handle_payment_error(exc) from exc


@router.get("")
async def listar_pagamentos(
    status_filter: str | None = None,
    payment_type: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista pagamentos com filtros."""
    svc = InterPaymentService(db)
    return {"payments": await svc.listar(status_filter, payment_type, from_date, to_date, limit)}


@router.get("/saldo-limite")
async def saldo_limite(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retorna limite diário consumido e disponível."""
    svc = InterPaymentService(db)
    return await svc.saldo_resumo()


@router.get("/{payment_id}/audit")
async def audit_log(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retorna audit log completo de um pagamento."""
    svc = InterPaymentService(db)
    return {"payment_id": payment_id, "audit": await svc.audit_log(payment_id)}
