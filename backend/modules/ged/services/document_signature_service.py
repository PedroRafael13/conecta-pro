"""Service para DocumentSignature."""

import logging
import hashlib
from typing import Optional, List
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ged.repositories.document_signature_repository import (
    DocumentSignatureRepository,
)
from modules.ged.repositories.document_repository import DocumentRepository
from modules.ged.models.document_signature import (
    SignatureType,
    SignatureStatus,
    SignatureRole,
)
from modules.ged.schemas.document_signature import (
    DocumentSignatureCreate,
    DocumentSignatureUpdate,
    DocumentSignatureResponse,
    SignatureRequest,
    SignatureRefusalRequest,
    SignatureStats,
)

logger = logging.getLogger(__name__)


class DocumentSignatureService:
    """Service para operações de assinatura digital."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = DocumentSignatureRepository(session)
        self.document_repository = DocumentRepository(session)

    async def create(
        self, data: DocumentSignatureCreate
    ) -> DocumentSignatureResponse:
        """Cria solicitação de assinatura."""
        # Verifica se documento existe
        document = await self.document_repository.get_by_id(data.document_id)
        if not document:
            raise ValueError("Documento não encontrado")

        # Define ordem se não especificada
        if data.order is None:
            existing = await self.repository.get_by_document(data.document_id)
            data.order = len(existing) + 1

        signature = await self.repository.create(data)
        await self.session.commit()
        logger.info(
            "Solicitação de assinatura criada: %s para documento %s",
            signature.id,
            data.document_id,
        )
        return DocumentSignatureResponse.model_validate(signature)

    async def create_bulk(
        self, document_id: str, signers: List[dict], created_by: str
    ) -> List[DocumentSignatureResponse]:
        """Cria múltiplas solicitações de assinatura."""
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            raise ValueError("Documento não encontrado")

        created = []
        for idx, signer in enumerate(signers, start=1):
            data = DocumentSignatureCreate(
                document_id=document_id,
                signer_id=signer.get("signer_id"),
                signer_email=signer.get("signer_email"),
                signer_name=signer.get("signer_name"),
                signer_cpf=signer.get("signer_cpf"),
                signer_role=signer.get("role", SignatureRole.PARTE),
                signature_type=signer.get("type", SignatureType.ELETRONICA),
                order=signer.get("order", idx),
                is_sequential=signer.get("is_sequential", False),
                deadline=signer.get("deadline"),
                message=signer.get("message"),
                created_by=created_by,
            )
            signature = await self.repository.create(data)
            created.append(DocumentSignatureResponse.model_validate(signature))

        await self.session.commit()
        logger.info(
            "%s solicitações de assinatura criadas para documento %s",
            len(created),
            document_id,
        )
        return created

    async def get_by_id(
        self, signature_id: str
    ) -> Optional[DocumentSignatureResponse]:
        """Busca assinatura por ID."""
        signature = await self.repository.get_by_id(signature_id)
        if not signature:
            return None
        return DocumentSignatureResponse.model_validate(signature)

    async def get_by_token(
        self, token: str
    ) -> Optional[DocumentSignatureResponse]:
        """Busca assinatura por token."""
        signature = await self.repository.get_by_token(token)
        if not signature:
            return None
        return DocumentSignatureResponse.model_validate(signature)

    async def update(
        self, signature_id: str, data: DocumentSignatureUpdate
    ) -> Optional[DocumentSignatureResponse]:
        """Atualiza assinatura."""
        signature = await self.repository.update(signature_id, data)
        if not signature:
            return None
        await self.session.commit()
        logger.info("Assinatura atualizada: %s", signature_id)
        return DocumentSignatureResponse.model_validate(signature)

    async def delete(self, signature_id: str) -> bool:
        """Remove assinatura."""
        signature = await self.repository.get_by_id(signature_id)
        if signature and signature.is_signed:
            raise ValueError("Não é possível remover assinatura já realizada")

        result = await self.repository.delete(signature_id)
        if result:
            await self.session.commit()
            logger.info("Assinatura removida: %s", signature_id)
        return result

    async def get_by_document(
        self, document_id: str, status: SignatureStatus = None
    ) -> List[DocumentSignatureResponse]:
        """Retorna assinaturas de um documento."""
        signatures = await self.repository.get_by_document(document_id, status)
        return [DocumentSignatureResponse.model_validate(s) for s in signatures]

    async def get_pending_by_document(
        self, document_id: str
    ) -> List[DocumentSignatureResponse]:
        """Retorna assinaturas pendentes do documento."""
        signatures = await self.repository.get_pending_by_document(document_id)
        return [DocumentSignatureResponse.model_validate(s) for s in signatures]

    async def get_by_signer(
        self,
        signer_id: str = None,
        signer_email: str = None,
        status: SignatureStatus = None,
    ) -> List[DocumentSignatureResponse]:
        """Retorna assinaturas por signatário."""
        signatures = await self.repository.get_by_signer(
            signer_id=signer_id,
            signer_email=signer_email,
            status=status,
        )
        return [DocumentSignatureResponse.model_validate(s) for s in signatures]

    async def get_pending_by_signer(
        self, signer_id: str = None, signer_email: str = None
    ) -> List[DocumentSignatureResponse]:
        """Retorna assinaturas pendentes do signatário."""
        signatures = await self.repository.get_pending_by_signer(
            signer_id=signer_id,
            signer_email=signer_email,
        )
        return [DocumentSignatureResponse.model_validate(s) for s in signatures]

    async def sign(
        self, signature_id: str, data: SignatureRequest
    ) -> Optional[DocumentSignatureResponse]:
        """Registra assinatura."""
        signature = await self.repository.get_by_id(signature_id)
        if not signature:
            return None

        # Verifica se é pendente
        if not signature.is_pending:
            raise ValueError("Assinatura não está pendente")

        # Verifica se é sequencial e se é a vez
        if signature.is_sequential:
            next_sig = await self.repository.get_next_in_sequence(
                signature.document_id
            )
            if next_sig and next_sig.id != signature_id:
                raise ValueError("Não é a vez desta assinatura na sequência")

        # Calcula hash da assinatura
        signature_hash = self._calculate_signature_hash(
            document_id=signature.document_id,
            signer_id=signature.signer_id or signature.signer_email,
            signature_data=data.signature_data,
            timestamp=datetime.utcnow().isoformat(),
        )

        signature = await self.repository.sign(
            signature_id=signature_id,
            signature_data=data.signature_data,
            signature_hash=signature_hash,
            ip_address=data.ip_address,
            user_agent=data.user_agent,
            geolocation=data.geolocation,
        )

        # Verifica se documento foi completamente assinado
        await self._check_document_fully_signed(signature.document_id)

        await self.session.commit()
        logger.info("Assinatura realizada: %s", signature_id)
        return DocumentSignatureResponse.model_validate(signature)

    async def refuse(
        self, signature_id: str, data: SignatureRefusalRequest
    ) -> Optional[DocumentSignatureResponse]:
        """Recusa assinatura."""
        signature = await self.repository.get_by_id(signature_id)
        if not signature:
            return None

        if not signature.is_pending:
            raise ValueError("Assinatura não está pendente")

        signature = await self.repository.refuse(signature_id, data.reason)
        await self.session.commit()
        logger.info("Assinatura recusada: %s", signature_id)
        return DocumentSignatureResponse.model_validate(signature)

    async def cancel(
        self, signature_id: str
    ) -> Optional[DocumentSignatureResponse]:
        """Cancela assinatura."""
        signature = await self.repository.get_by_id(signature_id)
        if not signature:
            return None

        if signature.is_signed:
            raise ValueError("Não é possível cancelar assinatura já realizada")

        signature = await self.repository.cancel(signature_id)
        await self.session.commit()
        logger.info("Assinatura cancelada: %s", signature_id)
        return DocumentSignatureResponse.model_validate(signature)

    async def verify(
        self, signature_id: str
    ) -> Optional[DocumentSignatureResponse]:
        """Verifica assinatura."""
        signature = await self.repository.get_by_id(signature_id)
        if not signature:
            return None

        if not signature.is_signed:
            raise ValueError("Assinatura não foi realizada")

        # Valida hash
        verification_method = "hash_validation"
        signature = await self.repository.verify(signature_id, verification_method)
        await self.session.commit()
        logger.info("Assinatura verificada: %s", signature_id)
        return DocumentSignatureResponse.model_validate(signature)

    async def send_notification(
        self, signature_id: str
    ) -> Optional[DocumentSignatureResponse]:
        """Envia notificação de assinatura."""
        signature = await self.repository.send_notification(signature_id)
        if not signature:
            return None
        await self.session.commit()
        logger.info("Notificação enviada: %s", signature_id)
        return DocumentSignatureResponse.model_validate(signature)

    async def send_reminder(
        self, signature_id: str
    ) -> Optional[DocumentSignatureResponse]:
        """Envia lembrete de assinatura."""
        signature = await self.repository.send_reminder(signature_id)
        if not signature:
            return None
        await self.session.commit()
        logger.info("Lembrete enviado: %s", signature_id)
        return DocumentSignatureResponse.model_validate(signature)

    async def regenerate_token(
        self, signature_id: str, expires_in_hours: int = 72
    ) -> Optional[str]:
        """Regenera token de assinatura."""
        token = await self.repository.regenerate_token(
            signature_id, expires_in_hours
        )
        if token:
            await self.session.commit()
            logger.info("Token regenerado: %s", signature_id)
        return token

    async def extend_deadline(
        self, signature_id: str, new_deadline: datetime
    ) -> Optional[DocumentSignatureResponse]:
        """Estende prazo de assinatura."""
        signature = await self.repository.extend_deadline(signature_id, new_deadline)
        if not signature:
            return None
        await self.session.commit()
        logger.info("Prazo estendido: %s até %s", signature_id, new_deadline)
        return DocumentSignatureResponse.model_validate(signature)

    async def expire_overdue(self) -> int:
        """Expira assinaturas vencidas."""
        count = await self.repository.expire_overdue()
        await self.session.commit()
        logger.info("%s assinaturas expiradas", count)
        return count

    async def get_next_in_sequence(
        self, document_id: str
    ) -> Optional[DocumentSignatureResponse]:
        """Retorna próxima assinatura na sequência."""
        signature = await self.repository.get_next_in_sequence(document_id)
        if not signature:
            return None
        return DocumentSignatureResponse.model_validate(signature)

    async def is_document_fully_signed(self, document_id: str) -> bool:
        """Verifica se documento está completamente assinado."""
        return await self.repository.is_document_fully_signed(document_id)

    async def get_stats(
        self, document_id: str = None
    ) -> SignatureStats:
        """Retorna estatísticas de assinaturas."""
        stats = await self.repository.get_stats(document_id)
        return SignatureStats(**stats)

    def _calculate_signature_hash(
        self,
        document_id: str,
        signer_id: str,
        signature_data: str,
        timestamp: str,
    ) -> str:
        """Calcula hash da assinatura."""
        content = f"{document_id}:{signer_id}:{signature_data}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def _check_document_fully_signed(self, document_id: str) -> None:
        """Verifica e atualiza status do documento se completamente assinado."""
        is_fully_signed = await self.repository.is_document_fully_signed(
            document_id
        )
        if is_fully_signed:
            document = await self.document_repository.get_by_id(document_id)
            if document:
                document.is_signed = True
                document.signed_at = datetime.utcnow()
                logger.info(
                    "Documento %s completamente assinado", document_id
                )

    async def request_signatures(
        self,
        document_id: str,
        signers: List[dict],
        created_by: str,
        sequential: bool = False,
        deadline_days: int = 7,
        message: str = None,
    ) -> List[DocumentSignatureResponse]:
        """Solicita assinaturas para documento."""
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            raise ValueError("Documento não encontrado")

        # Marca documento como requerendo assinatura
        document.requires_signature = True
        document.signature_count = len(signers)

        # Calcula deadline padrão
        default_deadline = datetime.utcnow() + timedelta(days=deadline_days)

        signatures = []
        for idx, signer in enumerate(signers, start=1):
            data = DocumentSignatureCreate(
                document_id=document_id,
                signer_id=signer.get("user_id"),
                signer_email=signer["email"],
                signer_name=signer.get("name"),
                signer_cpf=signer.get("cpf"),
                signer_role=signer.get("role", SignatureRole.PARTE),
                signature_type=signer.get("type", SignatureType.ELETRONICA),
                order=idx,
                is_sequential=sequential,
                deadline=signer.get("deadline", default_deadline),
                message=message,
                created_by=created_by,
            )
            signature = await self.repository.create(data)
            signatures.append(DocumentSignatureResponse.model_validate(signature))

        await self.session.commit()
        logger.info(
            "Assinaturas solicitadas para documento %s: %s signatários",
            document_id,
            len(signers),
        )
        return signatures

    async def cancel_all_pending(self, document_id: str) -> int:
        """Cancela todas as assinaturas pendentes do documento."""
        pending = await self.repository.get_pending_by_document(document_id)
        count = 0
        for sig in pending:
            await self.repository.cancel(sig.id)
            count += 1

        await self.session.commit()
        logger.info(
            "%s assinaturas canceladas para documento %s", count, document_id
        )
        return count

    async def get_signature_certificate(
        self, signature_id: str
    ) -> Optional[dict]:
        """Gera certificado de assinatura."""
        signature = await self.repository.get_by_id(signature_id)
        if not signature or not signature.is_signed:
            return None

        document = await self.document_repository.get_by_id(signature.document_id)
        if not document:
            return None

        return {
            "certificate_id": f"CERT-{signature.id[:8].upper()}",
            "document_id": document.id,
            "document_title": document.title,
            "document_code": document.code,
            "signer_name": signature.signer_name,
            "signer_email": signature.signer_email,
            "signer_cpf": signature.signer_cpf,
            "signer_role": signature.signer_role.value,
            "signature_type": signature.signature_type.value,
            "signed_at": signature.signed_at.isoformat() if signature.signed_at else None,
            "signature_hash": signature.signature_hash,
            "ip_address": signature.ip_address,
            "verified": signature.is_verified,
            "verified_at": (
                signature.verified_at.isoformat() if signature.verified_at else None
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }
