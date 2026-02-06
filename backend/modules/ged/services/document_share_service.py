"""Service para DocumentShare."""

import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ged.repositories.document_share_repository import DocumentShareRepository
from modules.ged.repositories.document_repository import DocumentRepository
from modules.ged.models.document_share import ShareType, SharePermission
from modules.ged.schemas.document_share import (
    DocumentShareCreate,
    DocumentShareUpdate,
    DocumentShareFilter,
    DocumentShareResponse,
    DocumentShareListResponse,
    DocumentShareLinkRequest,
)

logger = logging.getLogger(__name__)


class DocumentShareService:
    """Service para operações de compartilhamento."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session
        self.repository = DocumentShareRepository(session)
        self.document_repository = DocumentRepository(session)

    async def create(self, data: DocumentShareCreate) -> DocumentShareResponse:
        """Cria compartilhamento."""
        # Verifica se documento existe
        document = await self.document_repository.get_by_id(data.document_id)
        if not document:
            raise ValueError("Documento não encontrado")

        # Verifica se já existe compartilhamento para este destinatário
        existing = await self.repository.get_by_document_and_recipient(
            document_id=data.document_id,
            recipient_id=data.recipient_id,
            recipient_email=data.recipient_email,
        )
        if existing:
            raise ValueError("Compartilhamento já existe para este destinatário")

        share = await self.repository.create(data)
        await self.session.commit()
        logger.info(
            "Compartilhamento criado: %s para documento %s",
            share.id,
            data.document_id,
        )
        return DocumentShareResponse.model_validate(share)

    async def get_by_id(self, share_id: str) -> Optional[DocumentShareResponse]:
        """Busca compartilhamento por ID."""
        share = await self.repository.get_by_id(share_id)
        if not share:
            return None
        return DocumentShareResponse.model_validate(share)

    async def get_by_token(self, token: str) -> Optional[DocumentShareResponse]:
        """Busca compartilhamento por token."""
        share = await self.repository.get_by_token(token)
        if not share:
            return None
        return DocumentShareResponse.model_validate(share)

    async def update(
        self, share_id: str, data: DocumentShareUpdate
    ) -> Optional[DocumentShareResponse]:
        """Atualiza compartilhamento."""
        share = await self.repository.update(share_id, data)
        if not share:
            return None
        await self.session.commit()
        logger.info("Compartilhamento atualizado: %s", share_id)
        return DocumentShareResponse.model_validate(share)

    async def delete(self, share_id: str) -> bool:
        """Remove compartilhamento."""
        result = await self.repository.delete(share_id)
        if result:
            await self.session.commit()
            logger.info("Compartilhamento removido: %s", share_id)
        return result

    async def list(
        self,
        filters: Optional[DocumentShareFilter] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> DocumentShareListResponse:
        """Lista compartilhamentos com filtros."""
        skip = (page - 1) * page_size
        shares, total = await self.repository.list_with_filters(
            filters=filters,
            skip=skip,
            limit=page_size,
            order_by=order_by,
            order_desc=order_desc,
        )

        pages = (total + page_size - 1) // page_size if total > 0 else 0

        return DocumentShareListResponse(
            items=[DocumentShareResponse.model_validate(s) for s in shares],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_by_document(
        self, document_id: str
    ) -> List[DocumentShareResponse]:
        """Retorna compartilhamentos de um documento."""
        shares = await self.repository.get_by_document(document_id)
        return [DocumentShareResponse.model_validate(s) for s in shares]

    async def get_by_owner(
        self, owner_id: str, page: int = 1, page_size: int = 20
    ) -> List[DocumentShareResponse]:
        """Retorna compartilhamentos do proprietário."""
        skip = (page - 1) * page_size
        shares = await self.repository.get_by_owner(owner_id, skip, page_size)
        return [DocumentShareResponse.model_validate(s) for s in shares]

    async def get_by_recipient(
        self,
        recipient_id: str = None,
        recipient_email: str = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[DocumentShareResponse]:
        """Retorna compartilhamentos para o destinatário."""
        skip = (page - 1) * page_size
        shares = await self.repository.get_by_recipient(
            recipient_id=recipient_id,
            recipient_email=recipient_email,
            skip=skip,
            limit=page_size,
        )
        return [DocumentShareResponse.model_validate(s) for s in shares]

    async def create_public_link(
        self, data: DocumentShareLinkRequest
    ) -> DocumentShareResponse:
        """Cria link público para documento."""
        # Verifica se documento existe
        document = await self.document_repository.get_by_id(data.document_id)
        if not document:
            raise ValueError("Documento não encontrado")

        # Cria compartilhamento com link
        share_data = DocumentShareCreate(
            document_id=data.document_id,
            share_type=ShareType.PUBLICO,
            permission=data.permission,
            shared_by=data.shared_by,
            expires_at=data.expires_at,
            max_access_count=data.max_access_count,
            password_protected=data.password is not None,
            password=data.password,
            message=data.message,
            notify_on_access=data.notify_on_access,
        )
        share = await self.repository.create(share_data)
        await self.session.commit()
        logger.info(
            "Link público criado: %s para documento %s",
            share.id,
            data.document_id,
        )
        return DocumentShareResponse.model_validate(share)

    async def access_by_link(
        self,
        token: str,
        password: str = None,
        ip_address: str = None,  # pylint: disable=unused-argument
        user_agent: str = None,  # pylint: disable=unused-argument
    ) -> Optional[DocumentShareResponse]:
        """Acessa documento via link."""
        share = await self.repository.get_by_token(token)
        if not share:
            return None

        # Verifica senha se necessário
        if share.password_protected:
            if not password:
                raise ValueError("Senha requerida")
            if not await self.repository.verify_password(share.id, password):
                raise ValueError("Senha incorreta")

        # Verifica se ainda é válido
        if not share.is_active:
            raise ValueError("Link expirado ou inativo")

        if share.is_expired:
            raise ValueError("Link expirado")

        if share.access_count_exceeded:
            raise ValueError("Limite de acessos excedido")

        # Registra acesso
        await self.repository.record_access(share.id)
        await self.session.commit()

        logger.info("Acesso via link: %s", share.id)
        return DocumentShareResponse.model_validate(share)

    async def revoke(
        self, share_id: str, revoked_by: str = None
    ) -> Optional[DocumentShareResponse]:
        """Revoga compartilhamento."""
        share = await self.repository.revoke(share_id, revoked_by or "system")
        if not share:
            return None
        await self.session.commit()
        logger.info("Compartilhamento revogado: %s", share_id)
        return DocumentShareResponse.model_validate(share)

    async def accept(
        self, share_id: str, user_id: str
    ) -> Optional[DocumentShareResponse]:
        """Aceita compartilhamento."""
        share = await self.repository.accept(share_id, user_id)
        if not share:
            return None
        await self.session.commit()
        logger.info("Compartilhamento aceito: %s por %s", share_id, user_id)
        return DocumentShareResponse.model_validate(share)

    async def reject(
        self, share_id: str, reason: str = None
    ) -> Optional[DocumentShareResponse]:
        """Rejeita compartilhamento."""
        share = await self.repository.reject(share_id, reason)
        if not share:
            return None
        await self.session.commit()
        logger.info("Compartilhamento rejeitado: %s", share_id)
        return DocumentShareResponse.model_validate(share)

    async def extend_expiry(
        self, share_id: str, new_expiry: datetime
    ) -> Optional[DocumentShareResponse]:
        """Estende validade do compartilhamento."""
        share = await self.repository.extend_expiry(share_id, new_expiry)
        if not share:
            return None
        await self.session.commit()
        logger.info("Validade estendida: %s até %s", share_id, new_expiry)
        return DocumentShareResponse.model_validate(share)

    async def update_permission(
        self, share_id: str, permission: SharePermission
    ) -> Optional[DocumentShareResponse]:
        """Atualiza permissão do compartilhamento."""
        share = await self.repository.update_permission(share_id, permission)
        if not share:
            return None
        await self.session.commit()
        logger.info("Permissão atualizada: %s -> %s", share_id, permission.value)
        return DocumentShareResponse.model_validate(share)

    async def regenerate_token(self, share_id: str) -> Optional[str]:
        """Regenera token de acesso."""
        token = await self.repository.regenerate_token(share_id)
        if token:
            await self.session.commit()
            logger.info("Token regenerado: %s", share_id)
        return token

    async def set_password(
        self, share_id: str, password: str
    ) -> Optional[DocumentShareResponse]:
        """Define senha para compartilhamento."""
        share = await self.repository.set_password(share_id, password)
        if not share:
            return None
        await self.session.commit()
        logger.info("Senha definida: %s", share_id)
        return DocumentShareResponse.model_validate(share)

    async def remove_password(
        self, share_id: str
    ) -> Optional[DocumentShareResponse]:
        """Remove senha do compartilhamento."""
        share = await self.repository.remove_password(share_id)
        if not share:
            return None
        await self.session.commit()
        logger.info("Senha removida: %s", share_id)
        return DocumentShareResponse.model_validate(share)

    async def expire_overdue(self) -> int:
        """Expira compartilhamentos vencidos."""
        count = await self.repository.expire_overdue()
        await self.session.commit()
        logger.info("%s compartilhamentos expirados", count)
        return count

    async def get_access_log(
        self, share_id: str
    ) -> List[dict]:
        """Retorna log de acessos."""
        share = await self.repository.get_by_id(share_id)
        if not share:
            return []
        return share.access_log or []

    async def get_stats(self, document_id: str = None) -> dict:
        """Retorna estatísticas de compartilhamento."""
        return await self.repository.get_stats(document_id)
