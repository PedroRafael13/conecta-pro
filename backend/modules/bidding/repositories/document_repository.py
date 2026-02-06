"""
Repository de Documento da Empresa - Licitacoes
===============================================
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session

from modules.bidding.models.company_document import CompanyDocument, DocumentStatus
from modules.bidding.schemas.document import CompanyDocumentCreate, CompanyDocumentUpdate

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Repository para operacoes com documentos da empresa."""

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, document_id: UUID) -> Optional[CompanyDocument]:
        """Busca documento por ID."""
        result = await self.db.execute(
            select(CompanyDocument).where(
                CompanyDocument.id == document_id,
                CompanyDocument.ativo == True
            )
        )
        return result.scalar_one_or_none()

    async def get_by_tipo(self, tipo: str) -> Optional[CompanyDocument]:
        """Busca documento mais recente por tipo."""
        result = await self.db.execute(
            select(CompanyDocument).where(
                CompanyDocument.tipo == tipo,
                CompanyDocument.ativo == True
            ).order_by(CompanyDocument.data_validade.desc())
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        tipo: str = None,
        status: str = None,
        page: int = 1,
        size: int = 50
    ) -> Tuple[List[CompanyDocument], int]:
        """Lista documentos com filtros."""
        query = select(CompanyDocument).where(CompanyDocument.ativo == True)

        if tipo:
            query = query.where(CompanyDocument.tipo == tipo)

        if status:
            query = query.where(CompanyDocument.status == status)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginacao
        query = query.order_by(CompanyDocument.data_validade.asc())
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(
        self,
        data: CompanyDocumentCreate,
        user_id: UUID = None
    ) -> CompanyDocument:
        """Cria novo documento."""
        document = CompanyDocument(
            **data.model_dump(exclude_unset=True),
            created_by=user_id
        )

        # Atualiza status baseado na validade
        document.atualizar_status()

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        logger.info(f"Documento criado: {document.tipo} - {document.nome}")
        return document

    async def update(
        self,
        document_id: UUID,
        data: CompanyDocumentUpdate,
        user_id: UUID = None
    ) -> Optional[CompanyDocument]:
        """Atualiza documento existente."""
        document = await self.get_by_id(document_id)
        if not document:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        document.updated_by = user_id
        document.updated_at = datetime.utcnow()
        document.atualizar_status()

        await self.db.commit()
        await self.db.refresh(document)
        logger.info(f"Documento atualizado: {document.tipo} - {document.nome}")
        return document

    async def delete(self, document_id: UUID) -> bool:
        """Remove documento (soft delete)."""
        document = await self.get_by_id(document_id)
        if not document:
            return False

        document.ativo = False
        document.updated_at = datetime.utcnow()
        await self.db.commit()
        logger.info(f"Documento removido: {document.tipo} - {document.nome}")
        return True

    async def get_expiring(self, days: int = 30) -> List[CompanyDocument]:
        """Lista documentos vencendo nos proximos X dias."""
        limite = date.today() + timedelta(days=days)
        result = await self.db.execute(
            select(CompanyDocument).where(
                CompanyDocument.ativo == True,
                CompanyDocument.data_validade.isnot(None),
                CompanyDocument.data_validade <= limite,
                CompanyDocument.data_validade >= date.today()
            ).order_by(CompanyDocument.data_validade.asc())
        )
        return list(result.scalars().all())

    async def get_expired(self) -> List[CompanyDocument]:
        """Lista documentos vencidos."""
        result = await self.db.execute(
            select(CompanyDocument).where(
                CompanyDocument.ativo == True,
                CompanyDocument.data_validade.isnot(None),
                CompanyDocument.data_validade < date.today()
            ).order_by(CompanyDocument.data_validade.desc())
        )
        return list(result.scalars().all())

    async def get_pending_renewal(self) -> List[CompanyDocument]:
        """Lista documentos que precisam renovacao."""
        result = await self.db.execute(
            select(CompanyDocument).where(
                CompanyDocument.ativo == True,
                CompanyDocument.certidao_automatica == True,
                or_(
                    CompanyDocument.status == DocumentStatus.EXPIRED.value,
                    CompanyDocument.status == DocumentStatus.EXPIRING.value
                )
            ).order_by(CompanyDocument.data_validade.asc())
        )
        return list(result.scalars().all())

    async def get_all_valid(self) -> List[CompanyDocument]:
        """Lista todos documentos validos."""
        result = await self.db.execute(
            select(CompanyDocument).where(
                CompanyDocument.ativo == True,
                CompanyDocument.status == DocumentStatus.VALID.value
            ).order_by(CompanyDocument.tipo)
        )
        return list(result.scalars().all())

    async def update_all_status(self) -> int:
        """Atualiza status de todos os documentos baseado na validade."""
        result = await self.db.execute(
            select(CompanyDocument).where(CompanyDocument.ativo == True)
        )
        documents = result.scalars().all()

        updated = 0
        for doc in documents:
            old_status = doc.status
            doc.atualizar_status()
            if doc.status != old_status:
                updated += 1

        await self.db.commit()
        logger.info(f"Status atualizado para {updated} documentos")
        return updated

    async def count_by_status(self) -> dict:
        """Conta documentos por status."""
        result = await self.db.execute(
            select(CompanyDocument.status, func.count(CompanyDocument.id))
            .where(CompanyDocument.ativo == True)
            .group_by(CompanyDocument.status)
        )
        return {row[0]: row[1] for row in result.all()}

    async def get_by_tipos(self, tipos: List[str]) -> List[CompanyDocument]:
        """Busca documentos mais recentes de tipos especificos."""
        # Subquery para pegar o mais recente de cada tipo
        documents = []
        for tipo in tipos:
            doc = await self.get_by_tipo(tipo)
            if doc:
                documents.append(doc)
        return documents
