"""Controller para Document."""

import hashlib
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from core.security.file_validator import ged_file_validator
from modules.ged.models.document import (
    DocumentCategory,
    DocumentConfidentiality,
    DocumentStatus,
    DocumentType,
)
from modules.ged.schemas.document import (
    DocumentCreate,
    DocumentFilter,
    DocumentListResponse,
    DocumentOCRResult,
    DocumentResponse,
    DocumentStats,
    DocumentUpdate,
    DocumentUploadRequest,
)
from modules.ged.services.document_ai_service import DocumentAIService
from modules.ged.services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["GED - Documentos"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DocumentResponse:
    """Cria um novo documento."""
    service = DocumentService(db)
    try:
        data.created_by = str(current_user.id) if hasattr(current_user, "id") else current_user["id"]
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("Erro ao criar documento: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar documento",
        ) from e


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    folder_id: str = Form(...),
    document_type: str = Form(default="outro"),
    category: str = Form(default="outro"),
    confidentiality: str = Form(default="interno"),
    description: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DocumentResponse:
    """Upload de documento com arquivo."""
    try:
        # Validar arquivo (tamanho, tipo MIME, magic number)
        content = await ged_file_validator.validate_file(file)

        # Diretório de upload
        upload_dir = Path("/app/uploads/ged")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Calcular checksum SHA-256
        checksum = hashlib.sha256(content).hexdigest()

        # Nome único do arquivo
        file_extension = Path(file.filename or "file").suffix.lstrip(".")
        if not file_extension:
            file_extension = "bin"
        unique_filename = f"{checksum}.{file_extension}"
        file_path = upload_dir / unique_filename

        # Salvar arquivo
        with open(file_path, "wb") as f:
            f.write(content)

        # Criar documento no banco
        service = DocumentService(db)
        document_data = DocumentCreate(
            title=title,
            description=description,
            folder_id=folder_id,
            document_type=DocumentType(document_type),
            category=DocumentCategory(category),
            confidentiality=DocumentConfidentiality(confidentiality),
            file_name=file.filename or "file",
            file_extension=file_extension,
            file_path=str(file_path),
            file_size_bytes=len(content),
            mime_type=file.content_type or "application/octet-stream",
            checksum=checksum,
            owner_id=str(current_user.id) if hasattr(current_user, "id") else current_user["id"],
            created_by=str(current_user.id) if hasattr(current_user, "id") else current_user["id"],
        )

        logger.info(f"Upload realizado: {file.filename} ({len(content)} bytes)")
        result = await service.create(document_data)

        # Disparar processamento IA em background (nao bloqueia resposta)
        from modules.ged.tasks.ai_processing import process_document_ai

        background_tasks.add_task(process_document_ai, str(result.id))
        logger.info("IA Background agendado para documento %s", result.id)

        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Erro ao fazer upload de documento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao fazer upload: {str(e)}",
        ) from e


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Busca documento por ID."""
    service = DocumentService(db)
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.get("/code/{code}", response_model=DocumentResponse)
async def get_document_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Busca documento por código."""
    service = DocumentService(db)
    document = await service.get_by_code(code)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Atualiza documento."""
    service = DocumentService(db)
    document = await service.update(document_id, data)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> None:
    """Remove documento."""
    service = DocumentService(db)
    if not await service.delete(document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    folder_id: str | None = Query(None),
    condominium_id: str | None = Query(None),
    document_type: DocumentType | None = Query(None),
    category: DocumentCategory | None = Query(None),
    document_status: DocumentStatus | None = Query(None),
    confidentiality: DocumentConfidentiality | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    order_by: str = Query("created_at"),
    order_desc: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentListResponse:
    """Lista documentos com filtros."""
    service = DocumentService(db)
    filters = DocumentFilter(
        folder_id=folder_id,
        condominium_id=condominium_id,
        document_type=document_type,
        category=category,
        status=document_status,
        confidentiality=confidentiality,
    )
    return await service.list(filters, page, page_size, order_by, order_desc)


@router.get("/folder/{folder_id}", response_model=list[DocumentResponse])
async def get_by_folder(
    folder_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[DocumentResponse]:
    """Retorna documentos de uma pasta."""
    service = DocumentService(db)
    return await service.get_by_folder(folder_id, page, page_size)


@router.get("/pending/approval", response_model=list[DocumentResponse])
async def get_pending_approval(
    condominium_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[DocumentResponse]:
    """Retorna documentos pendentes de aprovação."""
    service = DocumentService(db)
    return await service.get_pending_approval(condominium_id, page, page_size)


@router.get("/pending/signature", response_model=list[DocumentResponse])
async def get_pending_signature(
    condominium_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[DocumentResponse]:
    """Retorna documentos pendentes de assinatura."""
    service = DocumentService(db)
    return await service.get_pending_signature(condominium_id, page, page_size)


@router.get("/expired/list", response_model=list[DocumentResponse])
async def get_expired(
    condominium_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[DocumentResponse]:
    """Retorna documentos expirados."""
    service = DocumentService(db)
    return await service.get_expired(condominium_id, page, page_size)


@router.get("/expiring/soon", response_model=list[DocumentResponse])
async def get_expiring_soon(
    days: int = Query(30, ge=1, le=365),
    condominium_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[DocumentResponse]:
    """Retorna documentos prestes a expirar."""
    service = DocumentService(db)
    return await service.get_expiring_soon(days, condominium_id)


@router.post("/{document_id}/approve", response_model=DocumentResponse)
async def approve_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DocumentResponse:
    """Aprova documento."""
    service = DocumentService(db)
    document = await service.approve(
        document_id, str(current_user.id) if hasattr(current_user, "id") else current_user["id"]
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/{document_id}/reject", response_model=DocumentResponse)
async def reject_document(
    document_id: str,
    reason: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Rejeita documento."""
    service = DocumentService(db)
    document = await service.reject(document_id, reason)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/{document_id}/publish", response_model=DocumentResponse)
async def publish_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Publica documento."""
    service = DocumentService(db)
    document = await service.publish(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/{document_id}/archive", response_model=DocumentResponse)
async def archive_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DocumentResponse:
    """Arquiva documento."""
    service = DocumentService(db)
    document = await service.archive(
        document_id, str(current_user.id) if hasattr(current_user, "id") else current_user["id"]
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/{document_id}/unarchive", response_model=DocumentResponse)
async def unarchive_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Desarquiva documento."""
    service = DocumentService(db)
    document = await service.unarchive(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/{document_id}/move", response_model=DocumentResponse)
async def move_document(
    document_id: str,
    folder_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Move documento para outra pasta."""
    service = DocumentService(db)
    try:
        document = await service.move(document_id, folder_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento não encontrado",
            )
        return document
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/{document_id}/view", response_model=DocumentResponse)
async def view_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Registra visualização."""
    service = DocumentService(db)
    document = await service.view(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/{document_id}/download", response_model=DocumentResponse)
async def register_download(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Registra download."""
    service = DocumentService(db)
    document = await service.download(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.get("/{document_id}/download")
async def download_file(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> FileResponse:
    """Faz download do arquivo do documento."""
    service = DocumentService(db)
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado no sistema")

    # Registra o download
    await service.download(document_id)

    return FileResponse(
        path=str(file_path),
        filename=document.file_name,
        media_type=document.mime_type,
    )


@router.get("/{document_id}/preview")
async def get_preview_url(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, str]:
    """Retorna URL de preview do documento."""
    service = DocumentService(db)
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")

    # Se tem preview_path, usa ele, senão usa o arquivo original
    preview_url = f"/api/v1/ged/documents/{document_id}/download"
    if document.preview_path:
        preview_url = document.preview_path

    return {"url": preview_url}


@router.get("/{document_id}/view-url")
async def get_view_url(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, str]:
    """Retorna URL de visualização do documento."""
    service = DocumentService(db)
    document = await service.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")

    # Registra a visualização
    await service.view(document_id)

    # URL para visualização (pode ser adaptado para viewer específico por tipo)
    view_url = f"/api/v1/ged/documents/{document_id}/download"

    return {"url": view_url}


@router.get("/search/query", response_model=list[DocumentResponse])
async def search_documents(
    query: str = Query(..., min_length=2),
    condominium_id: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[DocumentResponse]:
    """Busca full-text em documentos."""
    service = DocumentService(db)
    return await service.search(query, condominium_id, limit)


@router.get("/stats/summary", response_model=DocumentStats)
async def get_stats(
    condominium_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentStats:
    """Retorna estatísticas."""
    service = DocumentService(db)
    return await service.get_stats(condominium_id)


@router.post("/{document_id}/submit-approval", response_model=DocumentResponse)
async def submit_for_approval(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentResponse:
    """Submete documento para aprovação."""
    service = DocumentService(db)
    document = await service.submit_for_approval(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/{document_id}/new-version", response_model=DocumentResponse)
async def create_new_version(
    document_id: str,
    data: DocumentUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DocumentResponse:
    """Cria nova versão do documento."""
    service = DocumentService(db)
    document = await service.create_new_version(
        document_id=document_id,
        file_name=data.file_name,
        file_path=data.file_path,
        file_size_bytes=data.file_size_bytes,
        mime_type=data.mime_type,
        checksum=data.checksum,
        created_by=str(current_user.id) if hasattr(current_user, "id") else current_user["id"],
        change_summary=data.change_summary,
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return document


@router.post("/check-expiry/run")
async def check_expiry(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, int]:
    """Verifica e marca documentos expirados."""
    service = DocumentService(db)
    count = await service.check_expiry()
    return {"expired_count": count}


# Endpoints de IA
@router.post("/ai/classify")
async def classify_document(
    text: str = Query(..., min_length=10),
    file_name: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, Any]:
    """Classifica documento usando IA."""
    service = DocumentAIService(db)
    return await service.classify_document(text, file_name)


@router.post("/{document_id}/ai/analyze-ocr", response_model=DocumentOCRResult)
async def analyze_ocr(
    document_id: str,
    ocr_text: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentOCRResult:
    """Analisa texto OCR do documento."""
    service = DocumentAIService(db)
    result = await service.analyze_ocr_text(document_id, ocr_text)
    return DocumentOCRResult(**result)


@router.post("/ai/extract-keywords")
async def extract_keywords(
    text: str = Query(..., min_length=10),
    max_keywords: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, list[str]]:
    """Extrai palavras-chave do texto."""
    service = DocumentAIService(db)
    keywords = await service.extract_keywords(text, max_keywords)
    return {"keywords": keywords}


@router.post("/ai/check-duplicates")
async def check_duplicates(
    checksum: str = Query(...),
    title: str = Query(...),
    condominium_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, Any]:
    """Verifica documentos duplicados."""
    service = DocumentAIService(db)
    return await service.find_duplicates(checksum, title, condominium_id)


@router.get("/ai/insights")
async def get_insights(
    condominium_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, Any]:
    """Retorna insights sobre documentos."""
    service = DocumentAIService(db)
    return await service.get_insights(condominium_id)


@router.get("/ai/trends")
async def get_trends(
    condominium_id: str | None = Query(None),
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, Any]:
    """Retorna tendências de documentos."""
    service = DocumentAIService(db)
    return await service.get_trends(condominium_id, days)


@router.get("/ai/dashboard")
async def get_ai_dashboard(
    condominium_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict[str, Any]:
    """Retorna dashboard com IA."""
    service = DocumentAIService(db)
    return await service.get_dashboard(condominium_id)
