"""Repository para DocumentSignature."""

import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.ged.models.document_signature import (
    DocumentSignature,
    SignatureStatus,
)
from modules.ged.schemas.document_signature import (
    DocumentSignatureCreate,
    DocumentSignatureUpdate,
)

logger = logging.getLogger(__name__)


class DocumentSignatureRepository:
    """Repository para operações de DocumentSignature."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: DocumentSignatureCreate) -> DocumentSignature:
        """Cria uma nova assinatura."""
        signature = DocumentSignature(**data.model_dump())
        signature.generate_token()
        self.session.add(signature)
        await self.session.flush()
        return signature

    async def get_by_id(self, signature_id: str) -> Optional[DocumentSignature]:
        """Busca assinatura por ID."""
        result = await self.session.execute(
            select(DocumentSignature).where(DocumentSignature.id == signature_id)
        )
        return result.scalar_one_or_none()

    async def get_by_token(self, token: str) -> Optional[DocumentSignature]:
        """Busca assinatura por token."""
        result = await self.session.execute(
            select(DocumentSignature).where(DocumentSignature.signature_token == token)
        )
        return result.scalar_one_or_none()

    async def update(
        self, signature_id: str, data: DocumentSignatureUpdate
    ) -> Optional[DocumentSignature]:
        """Atualiza uma assinatura."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(signature, field, value)

        await self.session.flush()
        return signature

    async def delete(self, signature_id: str) -> bool:
        """Remove assinatura."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return False

        await self.session.delete(signature)
        await self.session.flush()
        return True

    async def get_by_document(
        self, document_id: str, status: SignatureStatus = None
    ) -> List[DocumentSignature]:
        """Retorna assinaturas de um documento."""
        query = select(DocumentSignature).where(
            DocumentSignature.document_id == document_id
        )
        if status:
            query = query.where(DocumentSignature.status == status)

        query = query.order_by(DocumentSignature.order)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_by_document(
        self, document_id: str
    ) -> List[DocumentSignature]:
        """Retorna assinaturas pendentes de um documento."""
        return await self.get_by_document(document_id, SignatureStatus.PENDENTE)

    async def get_by_signer(
        self, signer_id: str = None, signer_email: str = None, status: SignatureStatus = None
    ) -> List[DocumentSignature]:
        """Retorna assinaturas por signatário."""
        query = select(DocumentSignature)

        if signer_id:
            query = query.where(DocumentSignature.signer_id == signer_id)
        elif signer_email:
            query = query.where(DocumentSignature.signer_email == signer_email)
        else:
            return []

        if status:
            query = query.where(DocumentSignature.status == status)

        query = query.order_by(DocumentSignature.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_by_signer(
        self, signer_id: str = None, signer_email: str = None
    ) -> List[DocumentSignature]:
        """Retorna assinaturas pendentes do signatário."""
        return await self.get_by_signer(
            signer_id=signer_id,
            signer_email=signer_email,
            status=SignatureStatus.PENDENTE,
        )

    async def sign(
        self,
        signature_id: str,
        signature_data: str,
        signature_hash: str,
        ip_address: str = None,
        user_agent: str = None,
        geolocation: dict = None,
    ) -> Optional[DocumentSignature]:
        """Registra assinatura."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None

        signature.sign(
            signature_data=signature_data,
            signature_hash=signature_hash,
            ip_address=ip_address,
            user_agent=user_agent,
            geolocation=geolocation,
        )
        await self.session.flush()
        return signature

    async def refuse(
        self, signature_id: str, reason: str
    ) -> Optional[DocumentSignature]:
        """Recusa assinatura."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None
        signature.refuse(reason)
        await self.session.flush()
        return signature

    async def cancel(self, signature_id: str) -> Optional[DocumentSignature]:
        """Cancela assinatura."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None
        signature.cancel()
        await self.session.flush()
        return signature

    async def verify(
        self, signature_id: str, method: str
    ) -> Optional[DocumentSignature]:
        """Verifica assinatura."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None
        signature.verify(method)
        await self.session.flush()
        return signature

    async def send_notification(
        self, signature_id: str
    ) -> Optional[DocumentSignature]:
        """Marca notificação como enviada."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None
        signature.send_notification()
        await self.session.flush()
        return signature

    async def send_reminder(self, signature_id: str) -> Optional[DocumentSignature]:
        """Registra envio de lembrete."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None
        signature.send_reminder()
        await self.session.flush()
        return signature

    async def regenerate_token(
        self, signature_id: str, expires_in_hours: int = 72
    ) -> Optional[str]:
        """Regenera token de assinatura."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None
        token = signature.generate_token(expires_in_hours)
        await self.session.flush()
        return token

    async def extend_deadline(
        self, signature_id: str, new_deadline: datetime
    ) -> Optional[DocumentSignature]:
        """Estende prazo."""
        signature = await self.get_by_id(signature_id)
        if not signature:
            return None
        signature.extend_deadline(new_deadline)
        await self.session.flush()
        return signature

    async def expire_overdue(self) -> int:
        """Expira assinaturas vencidas."""
        now = datetime.utcnow()
        query = select(DocumentSignature).where(
            and_(
                DocumentSignature.status == SignatureStatus.PENDENTE,
                DocumentSignature.deadline < now,
            )
        )
        result = await self.session.execute(query)
        signatures = result.scalars().all()

        count = 0
        for signature in signatures:
            signature.check_and_expire()
            count += 1

        await self.session.flush()
        return count

    async def get_next_in_sequence(
        self, document_id: str
    ) -> Optional[DocumentSignature]:
        """Retorna próxima assinatura na sequência."""
        # Busca assinaturas pendentes ordenadas por ordem
        pending = await self.get_pending_by_document(document_id)
        if not pending:
            return None

        # Se a primeira é sequencial, verifica se as anteriores foram assinadas
        for sig in pending:
            if sig.is_sequential:
                # Verifica se é a vez dele
                previous = await self._get_previous_signatures(document_id, sig.order)
                all_signed = all(s.is_signed for s in previous)
                if all_signed:
                    return sig
            else:
                return sig

        return None

    async def _get_previous_signatures(
        self, document_id: str, order: int
    ) -> List[DocumentSignature]:
        """Retorna assinaturas anteriores na ordem."""
        query = (
            select(DocumentSignature)
            .where(
                and_(
                    DocumentSignature.document_id == document_id,
                    DocumentSignature.order < order,
                )
            )
            .order_by(DocumentSignature.order)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def is_document_fully_signed(self, document_id: str) -> bool:
        """Verifica se documento foi completamente assinado."""
        signatures = await self.get_by_document(document_id)
        if not signatures:
            return False
        return all(s.is_signed for s in signatures)

    async def get_stats(self, document_id: str = None) -> dict:
        """Retorna estatísticas de assinaturas."""
        query = select(DocumentSignature)
        if document_id:
            query = query.where(DocumentSignature.document_id == document_id)

        result = await self.session.execute(query)
        signatures = result.scalars().all()

        stats = {
            "total_signatures": len(signatures),
            "pending": 0,
            "signed": 0,
            "refused": 0,
            "expired": 0,
            "by_type": {},
            "by_role": {},
            "avg_time_to_sign_hours": 0,
        }

        total_time = 0
        signed_count = 0

        for sig in signatures:
            # Por status
            if sig.is_pending:
                stats["pending"] += 1
            elif sig.is_signed:
                stats["signed"] += 1
                # Calcula tempo médio
                if sig.created_at and sig.signed_at:
                    delta = sig.signed_at - sig.created_at
                    total_time += delta.total_seconds() / 3600
                    signed_count += 1
            elif sig.is_refused:
                stats["refused"] += 1
            elif sig.is_expired:
                stats["expired"] += 1

            # Por tipo
            sig_type = sig.signature_type.value
            stats["by_type"][sig_type] = stats["by_type"].get(sig_type, 0) + 1

            # Por papel
            role = sig.signer_role.value
            stats["by_role"][role] = stats["by_role"].get(role, 0) + 1

        if signed_count > 0:
            stats["avg_time_to_sign_hours"] = round(total_time / signed_count, 2)

        return stats
