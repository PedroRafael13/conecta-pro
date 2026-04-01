"""
Controller de Certidoes - Licitacoes
====================================
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.bidding.schemas.certificate import (
    CertificateBulkStatusResponse,
    CertificateCreate,
    CertificateRenewRequest,
    CertificateRenewResponse,
    CertificateResponse,
    CertificateUpdate,
)
from modules.bidding.services.certificate_service import CertificateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/certificates", tags=["Licitacoes - Certidoes"])


@router.get("")
async def list_certificates(
    current_user: CurrentActiveUser,
    cnpj: str | None = None,
    tipo: str | None = None,
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista certidoes com filtros."""
    service = CertificateService(db)
    items, total = await service.list(cnpj, tipo, status, page, size)
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/status/{cnpj}", response_model=CertificateBulkStatusResponse)
async def get_status_geral(cnpj: str, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Retorna status geral das certidoes de uma empresa."""
    service = CertificateService(db)
    return await service.get_status_geral(cnpj)


@router.get("/tipos")
async def get_tipos_certidao(current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Retorna tipos de certidao disponiveis."""
    service = CertificateService(db)
    tipos = await service.get_tipos_certidao()
    return {"tipos": tipos}


@router.get("/pendentes-renovacao")
async def get_pendentes_renovacao(current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Lista certidoes pendentes de renovacao automatica."""
    service = CertificateService(db)
    return await service.get_pending_renewal()


@router.get("/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(certificate_id: UUID, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Busca certidao por ID."""
    service = CertificateService(db)
    cert = await service.get_by_id(certificate_id)
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certidao nao encontrada")
    return cert


@router.get("/cnpj/{cnpj}/tipo/{tipo}", response_model=CertificateResponse)
async def get_by_cnpj_tipo(cnpj: str, tipo: str, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Busca certidao mais recente por CNPJ e tipo."""
    service = CertificateService(db)
    cert = await service.get_by_tipo(cnpj, tipo)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Certidao do tipo {tipo} nao encontrada para CNPJ {cnpj}"
        )
    return cert


@router.post("", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED)
async def create_certificate(data: CertificateCreate, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Cria nova certidao."""
    service = CertificateService(db)
    return await service.create(data)


@router.put("/{certificate_id}", response_model=CertificateResponse)
async def update_certificate(
    certificate_id: UUID, data: CertificateUpdate, current_user: CurrentActiveUser, db: Session = Depends(get_db)
):
    """Atualiza certidao."""
    service = CertificateService(db)
    cert = await service.update(certificate_id, data)
    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certidao nao encontrada")
    return cert


@router.delete("/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certificate(certificate_id: UUID, current_user: CurrentActiveUser, db: Session = Depends(get_db)):
    """Remove certidao."""
    service = CertificateService(db)
    if not await service.delete(certificate_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certidao nao encontrada")


@router.post("/renovar", response_model=CertificateRenewResponse)
async def renovar_certidao(
    data: CertificateRenewRequest, current_user: CurrentActiveUser, db: Session = Depends(get_db)
):
    """Solicita renovacao de certidao."""
    service = CertificateService(db)
    return await service.renovar(data)


@router.post("/atualizar-status")
async def atualizar_todos_status(
    current_user: CurrentActiveUser, cnpj: str | None = None, db: Session = Depends(get_db)
):
    """Atualiza status de todas as certidoes."""
    service = CertificateService(db)
    updated = await service.atualizar_todos_status(cnpj)
    return {"certidoes_atualizadas": updated}
