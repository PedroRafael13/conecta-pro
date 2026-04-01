"""Controller para documentos do funcionário."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user, require_roles
from core.database import get_async_session
from modules.hr.employee_portal.models import DocumentType
from modules.hr.employee_portal.schemas import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentSignRequest,
)
from modules.hr.employee_portal.services import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Portal - Documentos"])


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="Listar documentos",
)
async def list_documents(
    document_type: DocumentType | None = Query(None, alias="type"),
    category: str | None = Query(None),
    search: str | None = Query(None, max_length=100),
    pending_ack: bool = Query(False, description="Apenas pendentes de ciência"),
    pending_signature: bool = Query(False, description="Apenas pendentes de assinatura"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Lista documentos do funcionário."""
    service = DocumentService(db)
    employee_id = UUID(current_user["employee_id"])

    documents, total = await service.list_employee_documents(
        employee_id,
        page=page,
        page_size=page_size,
        document_type=document_type,
        category=category,
        search=search,
        only_pending_ack=pending_ack,
        only_pending_signature=pending_signature,
    )

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/pending",
    summary="Contagem de documentos pendentes",
)
async def get_pending_counts(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Retorna contagem de documentos pendentes."""
    service = DocumentService(db)
    employee_id = UUID(current_user["employee_id"])

    return await service.get_pending_counts(employee_id)


@router.get(
    "/categories",
    summary="Listar categorias",
)
async def list_categories(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Retorna categorias de documentos disponíveis."""
    service = DocumentService(db)
    employee_id = UUID(current_user["employee_id"])

    categories = await service.get_document_categories(employee_id)
    return {"categories": categories}


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Visualizar documento",
)
async def view_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Visualiza documento específico (registra visualização)."""
    service = DocumentService(db)
    employee_id = UUID(current_user["employee_id"])

    try:
        document = await service.view_document(document_id, employee_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado",
            )
        return DocumentResponse.model_validate(document)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{document_id}/download",
    summary="Download do documento",
)
async def download_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Download do arquivo do documento."""
    service = DocumentService(db)
    employee_id = UUID(current_user["employee_id"])

    document = await service.download_document(document_id, employee_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado",
        )

    if not document.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não disponível",
        )

    return FileResponse(
        path=document.file_path,
        filename=document.file_name or f"documento_{document.id}.pdf",
        media_type=document.mime_type or "application/pdf",
    )


@router.post("/{document_id}/acknowledge", response_model=DocumentResponse, summary="Dar ciência no documento")
async def acknowledge_document(
    document_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Registra ciência no documento."""
    service = DocumentService(db)
    employee_id = UUID(current_user["employee_id"])

    # Capturar informações do request
    ip_address = request.client.host if request.client else None
    device_info = request.headers.get("User-Agent", "")[:500]

    try:
        document = await service.acknowledge_document(
            document_id,
            employee_id,
            ip_address=ip_address,
            device_info=device_info,
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado",
            )
        return DocumentResponse.model_validate(document)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{document_id}/sign", response_model=DocumentResponse, summary="Assinar documento digitalmente")
async def sign_document(
    document_id: UUID,
    data: DocumentSignRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Assina documento digitalmente."""
    service = DocumentService(db)
    employee_id = UUID(current_user["employee_id"])

    try:
        document = await service.sign_document(
            document_id,
            employee_id,
            data.signature_hash,
            certificate=data.certificate,
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado",
            )
        return DocumentResponse.model_validate(document)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# --- Endpoints administrativos ---


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload de documento",
    dependencies=[Depends(require_roles(["admin", "hr"]))],
)
async def upload_document(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Faz upload de documento para funcionário."""
    service = DocumentService(db)
    condominio_id = UUID(current_user["condominio_id"])

    document = await service.upload_document(
        data,
        condominio_id,
        created_by=UUID(current_user["sub"]),
    )

    return DocumentResponse.model_validate(document)


@router.post(
    "/{document_id}/publish",
    response_model=DocumentResponse,
    summary="Publicar documento",
    dependencies=[Depends(require_roles(["admin", "hr"]))],
)
async def publish_document(
    document_id: UUID,
    send_notification: bool = Query(True),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Publica documento para visualização do funcionário."""
    service = DocumentService(db)

    document = await service.publish_document(
        document_id,
        published_by=UUID(current_user["sub"]),
        send_notification=send_notification,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento não encontrado",
        )

    return DocumentResponse.model_validate(document)
