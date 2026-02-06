"""Controller para OccurrenceAttachment."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.auth.dependencies import get_current_user, require_roles
from modules.occurrences.models.attachment import AttachmentType
from modules.occurrences.schemas.attachment import (
    AttachmentCreate,
    AttachmentListResponse,
    AttachmentResponse,
)
from modules.occurrences.services.attachment_service import AttachmentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/occurrence-attachments", tags=["Occurrence Attachments"])


async def get_attachment_service(
    session: AsyncSession = Depends(get_async_session),
) -> AttachmentService:
    """Dependency para AttachmentService."""
    return AttachmentService(session)


@router.post(
    "/",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar anexo",
)
async def create_attachment(
    data: AttachmentCreate,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),
) -> AttachmentResponse:
    """Cria um novo anexo para uma ocorrencia."""
    try:
        # Define uploader se nao informado
        if not data.uploaded_by_id:
            data.uploaded_by_id = current_user.get("sub")
        if not data.uploaded_by_name:
            data.uploaded_by_name = current_user.get("name", "Usuario")

        result = await service.create(data)
        logger.info(
            f"Anexo {result.id} criado na ocorrencia {data.occurrence_id} "
            f"por {current_user.get('email')}"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar anexo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar anexo",
        )


@router.post(
    "/upload",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload de arquivo",
)
async def upload_attachment(
    occurrence_id: UUID = Query(..., description="ID da ocorrencia"),
    file: UploadFile = File(..., description="Arquivo para upload"),
    description: Optional[str] = Query(None, description="Descricao"),
    is_public: bool = Query(True, description="Visivel publicamente"),
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),
) -> AttachmentResponse:
    """Faz upload de arquivo e cria anexo."""
    try:
        result = await service.upload_file(
            occurrence_id=occurrence_id,
            file=file,
            uploaded_by_id=current_user.get("sub"),
            uploaded_by_name=current_user.get("name", "Usuario"),
            description=description,
            is_public=is_public,
        )
        logger.info(
            f"Arquivo {file.filename} uploaded para ocorrencia {occurrence_id} "
            f"por {current_user.get('email')}"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro no upload do arquivo",
        )


@router.get(
    "/occurrence/{occurrence_id}",
    response_model=AttachmentListResponse,
    summary="Listar anexos de uma ocorrencia",
)
async def list_attachments_by_occurrence(
    occurrence_id: UUID,
    attachment_type: Optional[AttachmentType] = Query(None, description="Tipo"),
    is_public: Optional[bool] = Query(None, description="Apenas publicos"),
    page: int = Query(1, ge=1, description="Pagina"),
    page_size: int = Query(50, ge=1, le=200, description="Itens por pagina"),
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> AttachmentListResponse:
    """Lista anexos de uma ocorrencia."""
    return await service.list_by_occurrence(
        occurrence_id, attachment_type, is_public, page, page_size
    )


@router.get(
    "/occurrence/{occurrence_id}/images",
    response_model=list[AttachmentResponse],
    summary="Listar imagens",
)
async def list_images(
    occurrence_id: UUID,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[AttachmentResponse]:
    """Lista apenas imagens de uma ocorrencia."""
    return await service.list_images(occurrence_id)


@router.get(
    "/occurrence/{occurrence_id}/documents",
    response_model=list[AttachmentResponse],
    summary="Listar documentos",
)
async def list_documents(
    occurrence_id: UUID,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[AttachmentResponse]:
    """Lista apenas documentos de uma ocorrencia."""
    return await service.list_documents(occurrence_id)


@router.get(
    "/occurrence/{occurrence_id}/media",
    response_model=list[AttachmentResponse],
    summary="Listar midias",
)
async def list_media(
    occurrence_id: UUID,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> list[AttachmentResponse]:
    """Lista videos e audios de uma ocorrencia."""
    return await service.list_media(occurrence_id)


@router.get(
    "/occurrence/{occurrence_id}/stats",
    summary="Estatisticas de anexos",
)
async def get_attachment_stats(
    occurrence_id: UUID,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retorna estatisticas de anexos por tipo."""
    return await service.get_stats_by_type(occurrence_id)


@router.get(
    "/{attachment_id}",
    response_model=AttachmentResponse,
    summary="Buscar anexo por ID",
)
async def get_attachment(
    attachment_id: UUID,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> AttachmentResponse:
    """Busca anexo por ID."""
    result = await service.get_by_id(attachment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anexo nao encontrado",
        )
    return result


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar anexo",
)
async def delete_attachment(
    attachment_id: UUID,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(get_current_user),
) -> None:
    """Deleta um anexo."""
    # Verificar permissao
    existing = await service.get_by_id(attachment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anexo nao encontrado",
        )

    user_id = current_user.get("sub")
    user_role = current_user.get("role", "morador")
    if existing.uploaded_by_id != user_id and user_role not in ["admin", "sindico"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissao para deletar este anexo",
        )

    result = await service.delete(attachment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar anexo",
        )
    logger.info(f"Anexo {attachment_id} deletado por {current_user.get('email')}")


@router.post(
    "/{attachment_id}/toggle-public",
    response_model=AttachmentResponse,
    summary="Alternar visibilidade",
)
async def toggle_attachment_public(
    attachment_id: UUID,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: dict = Depends(require_roles(["admin", "sindico"])),
) -> AttachmentResponse:
    """Alterna visibilidade publica do anexo."""
    result = await service.toggle_public(attachment_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anexo nao encontrado",
        )
    logger.info(
        f"Visibilidade do anexo {attachment_id} alterada por {current_user.get('email')}"
    )
    return result
