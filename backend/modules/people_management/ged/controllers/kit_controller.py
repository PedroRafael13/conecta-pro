"""
Controller de Kits Documentais — endpoints REST.

Gerencia o ciclo de vida dos kits documentais mensais:
criacao, montagem automatica, envio, aprovacao e exportacao.
"""

import logging
import os
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.ged.schemas.kit import (
    KitCreate,
    KitListResponse,
    KitResponse,
    KitSummary,
    KitUpdate,
)
from modules.people_management.ged.services.export_service import ExportService
from modules.people_management.ged.services.kit_builder_service import KitBuilderService
from modules.people_management.ged.services.kit_service import KitService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kits", tags=["GED - Kits Documentais"])


class KitSendRequest(BaseModel):
    """Schema para marcar kit como enviado."""

    method: str = Field(..., description="Metodo de envio: email, google_drive, portal, impresso")
    sent_to: str | None = Field(None, max_length=500, description="Destinatario(s)")


class KitApproveRequest(BaseModel):
    """Schema para aprovar kit."""

    approved_by: str = Field(..., max_length=255, description="Nome de quem aprovou")


class KitBuildRequest(BaseModel):
    """Schema para solicitar montagem automatica de kit."""

    reference_month: date | None = Field(None, description="Mes de referencia (usa o do kit se nao informado)")


@router.get("", response_model=KitListResponse)
async def list_kits(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    client_id: str | None = Query(None, description="Filtrar por cliente"),
    status: str | None = Query(None, description="Filtrar por status"),
    year: int | None = Query(None, ge=2020, le=2030, description="Filtrar por ano"),
    month: int | None = Query(None, ge=1, le=12, description="Filtrar por mes"),
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(20, ge=1, le=100, description="Limite"),
) -> Any:
    """Lista kits documentais com filtros e paginacao."""
    service = KitService(db)
    return await service.list_kits(
        client_id=client_id,
        status=status,
        year=year,
        month=month,
        skip=skip,
        limit=limit,
    )


@router.get("/summary", response_model=KitSummary)
async def get_kit_summary(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    year: int | None = Query(None, ge=2020, le=2030, description="Ano de referencia"),
    month: int | None = Query(None, ge=1, le=12, description="Mes de referencia"),
) -> Any:
    """Retorna resumo geral dos kits para dashboard."""
    service = KitService(db)
    reference_month = None
    if year and month:
        reference_month = date(year, month, 1)
    return await service.get_kit_summary(reference_month=reference_month)


@router.post("", response_model=KitResponse, status_code=201)
async def create_kit(
    data: KitCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo kit documental para um cliente/mes."""
    service = KitService(db)
    try:
        result = await service.create_kit(data)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{kit_id}", response_model=KitResponse)
async def get_kit(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um kit com resumo de documentos."""
    service = KitService(db)
    try:
        return await service.get_kit(kit_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{kit_id}", response_model=KitResponse)
async def update_kit(
    kit_id: str,
    data: KitUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza campos editaveis de um kit."""
    service = KitService(db)
    try:
        result = await service.update_kit(kit_id, data)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{kit_id}")
async def delete_kit(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Remove um kit. Somente permitido se status = EM_MONTAGEM."""
    service = KitService(db)
    try:
        result = await service.delete_kit(kit_id)
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{kit_id}/build")
async def build_kit(
    kit_id: str,
    data: KitBuildRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dispara montagem automatica do kit.

    Coleta documentos de DP, Fiscal e Operacoes automaticamente.
    """
    kit_service = KitService(db)
    try:
        kit_resp = await kit_service.get_kit(kit_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    builder = KitBuilderService(db)
    try:
        ref_month = data.reference_month or kit_resp.reference_month
        result = await builder.build_kit_for_client(
            client_id=kit_resp.client_id,
            reference_month=ref_month,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{kit_id}/send", response_model=KitResponse)
async def send_kit(
    kit_id: str,
    data: KitSendRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Marca o kit como enviado com metodo e destinatario."""
    service = KitService(db)
    try:
        result = await service.mark_kit_sent(
            kit_id=kit_id,
            method=data.method,
            sent_to=data.sent_to,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{kit_id}/approve", response_model=KitResponse)
async def approve_kit(
    kit_id: str,
    data: KitApproveRequest,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Aprova o kit documental."""
    service = KitService(db)
    try:
        result = await service.approve_kit(
            kit_id=kit_id,
            approved_by=data.approved_by,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{kit_id}/export/zip")
async def export_zip(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Gera e retorna o ZIP do kit para download."""
    export_svc = ExportService(db)
    try:
        result = await export_svc.generate_zip(kit_id)
        await db.commit()

        zip_path = result["zip_path"]
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="Arquivo ZIP nao foi gerado corretamente")

        # Registrar log de acesso
        await export_svc.log_access(
            kit_id=kit_id,
            action="downloaded",
            actor_type="internal",
            actor_id=str(current_user.id),
            actor_name=getattr(current_user, "full_name", None) or str(current_user.id),
            ip=None,
            user_agent=None,
            notes="Download ZIP via API",
        )
        await db.commit()

        return FileResponse(
            path=zip_path,
            filename=result["zip_filename"],
            media_type="application/zip",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{kit_id}/export/pdf")
async def export_pdf(
    kit_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Gera e retorna o PDF consolidado do kit para download."""
    export_svc = ExportService(db)
    try:
        result = await export_svc.generate_consolidated_pdf(kit_id)
        await db.commit()

        pdf_path = result["pdf_path"]
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Arquivo PDF nao foi gerado corretamente")

        # Detectar tipo MIME pelo arquivo gerado
        media_type = "application/pdf"
        if pdf_path.endswith(".txt"):
            media_type = "text/plain"

        await export_svc.log_access(
            kit_id=kit_id,
            action="downloaded",
            actor_type="internal",
            actor_id=str(current_user.id),
            actor_name=getattr(current_user, "full_name", None) or str(current_user.id),
            ip=None,
            user_agent=None,
            notes="Download PDF consolidado via API",
        )
        await db.commit()

        return FileResponse(
            path=pdf_path,
            filename=result["pdf_filename"],
            media_type=media_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
