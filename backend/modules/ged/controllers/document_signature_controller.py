"""Controller para DocumentSignature."""

import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth.dependencies import get_current_user
from modules.ged.services.document_signature_service import DocumentSignatureService
from modules.ged.models.document_signature import SignatureStatus
from modules.ged.schemas.document_signature import (
    DocumentSignatureCreate,
    DocumentSignatureUpdate,
    DocumentSignatureResponse,
    SignatureRequest,
    SignatureRefusalRequest,
    SignatureStats,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document-signatures", tags=["GED - Assinaturas"])


@router.post(
    "/", response_model=DocumentSignatureResponse, status_code=status.HTTP_201_CREATED
)
async def create_signature(
    data: DocumentSignatureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> DocumentSignatureResponse:
    """Cria solicitação de assinatura."""
    service = DocumentSignatureService(db)
    try:
        data.created_by = current_user["id"]
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        logger.error("Erro ao criar assinatura: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar assinatura",
        ) from e


@router.post("/bulk", response_model=List[DocumentSignatureResponse])
async def create_bulk_signatures(
    document_id: str = Query(...),
    signers: List[dict] = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[DocumentSignatureResponse]:
    """Cria múltiplas solicitações de assinatura."""
    service = DocumentSignatureService(db)
    try:
        return await service.create_bulk(document_id, signers, current_user["id"])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/{signature_id}", response_model=DocumentSignatureResponse)
async def get_signature(
    signature_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Busca assinatura por ID."""
    service = DocumentSignatureService(db)
    signature = await service.get_by_id(signature_id)
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assinatura não encontrada"
        )
    return signature


@router.get("/token/{token}", response_model=DocumentSignatureResponse)
async def get_by_token(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> DocumentSignatureResponse:
    """Busca assinatura por token."""
    service = DocumentSignatureService(db)
    signature = await service.get_by_token(token)
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assinatura não encontrada"
        )
    return signature


@router.put("/{signature_id}", response_model=DocumentSignatureResponse)
async def update_signature(
    signature_id: str,
    data: DocumentSignatureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Atualiza assinatura."""
    service = DocumentSignatureService(db)
    signature = await service.update(signature_id, data)
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assinatura não encontrada"
        )
    return signature


@router.delete("/{signature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_signature(
    signature_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> None:
    """Remove assinatura."""
    service = DocumentSignatureService(db)
    try:
        if not await service.delete(signature_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assinatura não encontrada",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.get("/document/{document_id}", response_model=List[DocumentSignatureResponse])
async def get_by_document(
    document_id: str,
    signature_status: Optional[SignatureStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> List[DocumentSignatureResponse]:
    """Retorna assinaturas de um documento."""
    service = DocumentSignatureService(db)
    return await service.get_by_document(document_id, signature_status)


@router.get(
    "/document/{document_id}/pending", response_model=List[DocumentSignatureResponse]
)
async def get_pending_by_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> List[DocumentSignatureResponse]:
    """Retorna assinaturas pendentes do documento."""
    service = DocumentSignatureService(db)
    return await service.get_pending_by_document(document_id)


@router.get("/signer/list", response_model=List[DocumentSignatureResponse])
async def get_by_signer(
    signature_status: Optional[SignatureStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[DocumentSignatureResponse]:
    """Retorna assinaturas do usuário."""
    service = DocumentSignatureService(db)
    return await service.get_by_signer(
        signer_id=current_user["id"],
        status=signature_status,
    )


@router.get("/signer/pending", response_model=List[DocumentSignatureResponse])
async def get_pending_by_signer(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[DocumentSignatureResponse]:
    """Retorna assinaturas pendentes do usuário."""
    service = DocumentSignatureService(db)
    return await service.get_pending_by_signer(signer_id=current_user["id"])


@router.post("/{signature_id}/sign", response_model=DocumentSignatureResponse)
async def sign(
    signature_id: str,
    data: SignatureRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Registra assinatura."""
    service = DocumentSignatureService(db)
    try:
        # Adiciona informações da requisição
        data.ip_address = request.client.host if request.client else None
        data.user_agent = request.headers.get("user-agent")

        signature = await service.sign(signature_id, data)
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assinatura não encontrada",
            )
        return signature
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post("/{signature_id}/refuse", response_model=DocumentSignatureResponse)
async def refuse(
    signature_id: str,
    data: SignatureRefusalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Recusa assinatura."""
    service = DocumentSignatureService(db)
    try:
        signature = await service.refuse(signature_id, data)
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assinatura não encontrada",
            )
        return signature
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post("/{signature_id}/cancel", response_model=DocumentSignatureResponse)
async def cancel(
    signature_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Cancela assinatura."""
    service = DocumentSignatureService(db)
    try:
        signature = await service.cancel(signature_id)
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assinatura não encontrada",
            )
        return signature
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post("/{signature_id}/verify", response_model=DocumentSignatureResponse)
async def verify(
    signature_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Verifica assinatura."""
    service = DocumentSignatureService(db)
    try:
        signature = await service.verify(signature_id)
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assinatura não encontrada",
            )
        return signature
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post("/{signature_id}/notify", response_model=DocumentSignatureResponse)
async def send_notification(
    signature_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Envia notificação."""
    service = DocumentSignatureService(db)
    signature = await service.send_notification(signature_id)
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assinatura não encontrada"
        )
    return signature


@router.post("/{signature_id}/remind", response_model=DocumentSignatureResponse)
async def send_reminder(
    signature_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Envia lembrete."""
    service = DocumentSignatureService(db)
    signature = await service.send_reminder(signature_id)
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assinatura não encontrada"
        )
    return signature


@router.post("/{signature_id}/regenerate-token")
async def regenerate_token(
    signature_id: str,
    expires_in_hours: int = Query(72, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Regenera token de assinatura."""
    service = DocumentSignatureService(db)
    token = await service.regenerate_token(signature_id, expires_in_hours)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assinatura não encontrada"
        )
    return {"token": token}


@router.post("/{signature_id}/extend", response_model=DocumentSignatureResponse)
async def extend_deadline(
    signature_id: str,
    new_deadline: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> DocumentSignatureResponse:
    """Estende prazo de assinatura."""
    service = DocumentSignatureService(db)
    signature = await service.extend_deadline(signature_id, new_deadline)
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assinatura não encontrada"
        )
    return signature


@router.post("/expire-overdue/run")
async def expire_overdue(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Expira assinaturas vencidas."""
    service = DocumentSignatureService(db)
    count = await service.expire_overdue()
    return {"expired_count": count}


@router.get(
    "/document/{document_id}/next", response_model=Optional[DocumentSignatureResponse]
)
async def get_next_in_sequence(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> Optional[DocumentSignatureResponse]:
    """Retorna próxima assinatura na sequência."""
    service = DocumentSignatureService(db)
    return await service.get_next_in_sequence(document_id)


@router.get("/document/{document_id}/fully-signed")
async def is_fully_signed(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Verifica se documento está completamente assinado."""
    service = DocumentSignatureService(db)
    is_signed = await service.is_document_fully_signed(document_id)
    return {"is_fully_signed": is_signed}


@router.get("/stats/summary", response_model=SignatureStats)
async def get_stats(
    document_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> SignatureStats:
    """Retorna estatísticas."""
    service = DocumentSignatureService(db)
    return await service.get_stats(document_id)


@router.post("/request", response_model=List[DocumentSignatureResponse])
async def request_signatures(
    document_id: str = Query(...),
    signers: List[dict] = Query(...),
    sequential: bool = Query(False),
    deadline_days: int = Query(7, ge=1, le=90),
    message: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[DocumentSignatureResponse]:
    """Solicita assinaturas para documento."""
    service = DocumentSignatureService(db)
    try:
        return await service.request_signatures(
            document_id=document_id,
            signers=signers,
            created_by=current_user["id"],
            sequential=sequential,
            deadline_days=deadline_days,
            message=message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.post("/document/{document_id}/cancel-all")
async def cancel_all_pending(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Cancela todas as assinaturas pendentes."""
    service = DocumentSignatureService(db)
    count = await service.cancel_all_pending(document_id)
    return {"cancelled_count": count}


@router.get("/{signature_id}/certificate")
async def get_certificate(
    signature_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retorna certificado de assinatura."""
    service = DocumentSignatureService(db)
    certificate = await service.get_signature_certificate(signature_id)
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assinatura não encontrada ou não realizada",
        )
    return certificate
