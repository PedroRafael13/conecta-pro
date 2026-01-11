"""
Repository de Edital (Tender) - Licitacoes
==========================================
"""

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session, selectinload

from modules.bidding.models.tender import Tender, TenderDocument, TenderStatus
from modules.bidding.schemas.tender import TenderCreate, TenderUpdate, TenderSearchParams

logger = logging.getLogger(__name__)


class TenderRepository:
    """Repository para operacoes com editais."""

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, tender_id: UUID) -> Optional[Tender]:
        """Busca edital por ID."""
        result = await self.db.execute(
            select(Tender)
            .options(selectinload(Tender.documentos))
            .where(Tender.id == tender_id, Tender.ativo == True)
        )
        return result.scalar_one_or_none()

    async def get_by_numero(self, numero: str, ano: int) -> Optional[Tender]:
        """Busca edital por numero e ano."""
        result = await self.db.execute(
            select(Tender).where(
                Tender.numero == numero,
                Tender.ano == ano,
                Tender.ativo == True
            )
        )
        return result.scalar_one_or_none()

    async def get_by_pncp_id(self, pncp_id: str) -> Optional[Tender]:
        """Busca edital por ID do PNCP."""
        result = await self.db.execute(
            select(Tender).where(Tender.pncp_id == pncp_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        params: TenderSearchParams
    ) -> Tuple[List[Tender], int]:
        """Lista editais com filtros e paginacao."""
        query = select(Tender).where(Tender.ativo == True)

        # Filtros
        if params.uf:
            query = query.where(Tender.orgao_uf == params.uf)

        if params.municipio:
            query = query.where(Tender.orgao_municipio.ilike(f"%{params.municipio}%"))

        if params.modalidade:
            query = query.where(Tender.modalidade == params.modalidade)

        if params.segmento:
            query = query.where(Tender.segmento == params.segmento)

        if params.status:
            query = query.where(Tender.status == params.status)

        if params.participando is not None:
            query = query.where(Tender.participando == params.participando)

        if params.interesse is not None:
            query = query.where(Tender.interesse == params.interesse)

        if params.data_inicio:
            query = query.where(Tender.data_abertura >= params.data_inicio)

        if params.data_fim:
            query = query.where(Tender.data_abertura <= params.data_fim)

        if params.valor_min:
            query = query.where(Tender.valor_estimado >= params.valor_min)

        if params.valor_max:
            query = query.where(Tender.valor_estimado <= params.valor_max)

        if params.termo_busca:
            termo = f"%{params.termo_busca}%"
            query = query.where(
                or_(
                    Tender.objeto.ilike(termo),
                    Tender.orgao_nome.ilike(termo),
                    Tender.numero.ilike(termo)
                )
            )

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginacao e ordenacao
        query = query.order_by(Tender.data_abertura.desc())
        offset = (params.page - 1) * params.size
        query = query.offset(offset).limit(params.size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, data: TenderCreate, user_id: UUID = None) -> Tender:
        """Cria novo edital."""
        tender = Tender(
            **data.model_dump(exclude_unset=True),
            created_by=user_id
        )
        self.db.add(tender)
        await self.db.commit()
        await self.db.refresh(tender)
        logger.info(f"Edital criado: {tender.numero}/{tender.ano}")
        return tender

    async def update(
        self,
        tender_id: UUID,
        data: TenderUpdate,
        user_id: UUID = None
    ) -> Optional[Tender]:
        """Atualiza edital existente."""
        tender = await self.get_by_id(tender_id)
        if not tender:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tender, field, value)

        tender.updated_by = user_id
        tender.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(tender)
        logger.info(f"Edital atualizado: {tender.numero}/{tender.ano}")
        return tender

    async def delete(self, tender_id: UUID) -> bool:
        """Remove edital (soft delete)."""
        tender = await self.get_by_id(tender_id)
        if not tender:
            return False

        tender.ativo = False
        tender.updated_at = datetime.utcnow()
        await self.db.commit()
        logger.info(f"Edital removido: {tender.numero}/{tender.ano}")
        return True

    async def get_abertos(self, uf: str = "AM") -> List[Tender]:
        """Lista editais abertos para participacao."""
        result = await self.db.execute(
            select(Tender).where(
                Tender.orgao_uf == uf,
                Tender.status == TenderStatus.OPEN.value,
                Tender.ativo == True,
                or_(
                    Tender.data_encerramento_propostas.is_(None),
                    Tender.data_encerramento_propostas > datetime.utcnow()
                )
            ).order_by(Tender.data_abertura.asc())
        )
        return list(result.scalars().all())

    async def get_participando(self) -> List[Tender]:
        """Lista editais que estamos participando."""
        result = await self.db.execute(
            select(Tender).where(
                Tender.participando == True,
                Tender.ativo == True
            ).order_by(Tender.data_abertura.asc())
        )
        return list(result.scalars().all())

    async def get_por_segmento(self, segmento: str, uf: str = "AM") -> List[Tender]:
        """Lista editais por segmento."""
        result = await self.db.execute(
            select(Tender).where(
                Tender.segmento == segmento,
                Tender.orgao_uf == uf,
                Tender.ativo == True,
                Tender.status.in_([
                    TenderStatus.PUBLISHED.value,
                    TenderStatus.OPEN.value
                ])
            ).order_by(Tender.data_abertura.asc())
        )
        return list(result.scalars().all())

    async def count_by_status(self, uf: str = "AM") -> dict:
        """Conta editais por status."""
        result = await self.db.execute(
            select(Tender.status, func.count(Tender.id))
            .where(Tender.orgao_uf == uf, Tender.ativo == True)
            .group_by(Tender.status)
        )
        return {row[0]: row[1] for row in result.all()}

    # Documentos do edital
    async def add_document(
        self,
        tender_id: UUID,
        nome: str,
        tipo: str,
        arquivo_url: str = None,
        **kwargs
    ) -> TenderDocument:
        """Adiciona documento ao edital."""
        doc = TenderDocument(
            tender_id=tender_id,
            nome=nome,
            tipo=tipo,
            arquivo_url=arquivo_url,
            **kwargs
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def get_documents(self, tender_id: UUID) -> List[TenderDocument]:
        """Lista documentos de um edital."""
        result = await self.db.execute(
            select(TenderDocument)
            .where(TenderDocument.tender_id == tender_id)
            .order_by(TenderDocument.ordem)
        )
        return list(result.scalars().all())
