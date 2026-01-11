"""
Controller de Documentos da Empresa - Licitacoes
================================================
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from modules.bidding.services.document_service import DocumentService
from modules.bidding.schemas.document import (
    CompanyDocumentCreate, CompanyDocumentUpdate, CompanyDocumentResponse,
    DocumentExpiringResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Licitacoes - Documentos"])


@router.get("/")
async def list_documents(
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Lista documentos da empresa com filtros."""
    service = DocumentService(db)
    items, total = await service.list(tipo, status, page, size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/expiring", response_model=DocumentExpiringResponse)
async def get_expiring(
    dias: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Lista documentos vencendo e vencidos."""
    service = DocumentService(db)
    return await service.get_expiring(dias)


@router.get("/status")
async def get_status_geral(db: Session = Depends(get_db)):
    """Retorna status geral dos documentos."""
    service = DocumentService(db)
    return await service.get_status_geral()


@router.get("/habilitacao")
async def verificar_habilitacao(db: Session = Depends(get_db)):
    """Verifica se empresa esta habilitada para licitar."""
    service = DocumentService(db)
    return await service.verificar_habilitacao()


@router.get("/tipos")
async def get_tipos_documento(db: Session = Depends(get_db)):
    """Retorna tipos de documento disponiveis."""
    service = DocumentService(db)
    tipos = await service.get_tipos_documento()
    return {"tipos": tipos}


@router.get("/tipo/{tipo}", response_model=CompanyDocumentResponse)
async def get_by_tipo(
    tipo: str,
    db: Session = Depends(get_db)
):
    """Busca documento mais recente por tipo."""
    service = DocumentService(db)
    doc = await service.get_by_tipo(tipo)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento do tipo {tipo} nao encontrado"
        )
    return doc


@router.get("/{document_id}", response_model=CompanyDocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Busca documento por ID."""
    service = DocumentService(db)
    doc = await service.get(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento nao encontrado"
        )
    return doc


@router.post("/", response_model=CompanyDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: CompanyDocumentCreate,
    db: Session = Depends(get_db)
):
    """Cria novo documento."""
    service = DocumentService(db)
    return await service.create(data)


@router.put("/{document_id}", response_model=CompanyDocumentResponse)
async def update_document(
    document_id: UUID,
    data: CompanyDocumentUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza documento."""
    service = DocumentService(db)
    doc = await service.update(document_id, data)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento nao encontrado"
        )
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """Remove documento."""
    service = DocumentService(db)
    if not await service.delete(document_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento nao encontrado"
        )


@router.post("/atualizar-status")
async def atualizar_todos_status(db: Session = Depends(get_db)):
    """Atualiza status de todos os documentos baseado na validade."""
    service = DocumentService(db)
    updated = await service.atualizar_todos_status()
    return {"documentos_atualizados": updated}
