"""
Repository de Proposta - Licitacoes
===================================
"""

import builtins
import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.bidding.models.proposal import BiddingProposal, BiddingProposalItem, ProposalStatus
from modules.bidding.schemas.proposal import ProposalCreate, ProposalUpdate

logger = logging.getLogger(__name__)


class ProposalRepository:
    """Repository para operacoes com propostas."""

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, proposal_id: UUID) -> BiddingProposal | None:
        """Busca proposta por ID."""
        result = await self.db.execute(
            select(BiddingProposal).where(BiddingProposal.id == proposal_id, BiddingProposal.ativo)
        )
        return result.scalar_one_or_none()

    async def get_by_tender(self, tender_id: UUID) -> list[BiddingProposal]:
        """Lista propostas de um edital."""
        result = await self.db.execute(
            select(BiddingProposal)
            .where(BiddingProposal.tender_id == tender_id, BiddingProposal.ativo)
            .order_by(BiddingProposal.versao.desc())
        )
        return list(result.scalars().all())

    async def get_latest_by_tender(self, tender_id: UUID) -> BiddingProposal | None:
        """Busca proposta mais recente de um edital."""
        result = await self.db.execute(
            select(BiddingProposal)
            .where(BiddingProposal.tender_id == tender_id, BiddingProposal.ativo)
            .order_by(BiddingProposal.versao.desc())
        )
        return result.scalar_one_or_none()

    async def list(
        self, tender_id: UUID = None, status: str = None, page: int = 1, size: int = 50
    ) -> tuple[list[BiddingProposal], int]:
        """Lista propostas com filtros."""
        query = select(BiddingProposal).where(BiddingProposal.ativo)

        if tender_id:
            query = query.where(BiddingProposal.tender_id == tender_id)

        if status:
            query = query.where(BiddingProposal.status == status)

        # Total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginacao
        query = query.order_by(BiddingProposal.created_at.desc())
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, data: ProposalCreate, user_id: UUID = None) -> BiddingProposal:
        """Cria nova proposta."""
        # Verifica versao
        existing = await self.get_latest_by_tender(data.tender_id)
        versao = (existing.versao + 1) if existing else 1

        # Cria proposta
        proposal_data = data.model_dump(exclude={"itens"})
        proposal = BiddingProposal(**proposal_data, versao=versao, created_by=user_id)

        self.db.add(proposal)
        await self.db.commit()
        await self.db.refresh(proposal)

        # Adiciona itens
        if data.itens:
            for item_data in data.itens:
                item = BiddingProposalItem(
                    proposal_id=proposal.id,
                    **item_data.model_dump(),
                    valor_total=item_data.quantidade * item_data.valor_unitario,
                )
                self.db.add(item)
            await self.db.commit()

        logger.info(f"Proposta criada: {proposal.numero} v{proposal.versao}")
        return proposal

    async def update(self, proposal_id: UUID, data: ProposalUpdate, user_id: UUID = None) -> BiddingProposal | None:
        """Atualiza proposta existente."""
        proposal = await self.get_by_id(proposal_id)
        if not proposal:
            return None

        # Verifica se pode editar
        if proposal.status not in [ProposalStatus.DRAFT.value, ProposalStatus.READY.value]:
            logger.warning(f"Tentativa de editar proposta com status {proposal.status}")
            return None

        update_data = data.model_dump(exclude_unset=True, exclude={"itens"})
        for field, value in update_data.items():
            setattr(proposal, field, value)

        proposal.updated_by = user_id
        proposal.updated_at = datetime.utcnow()

        # Atualiza itens se fornecidos
        if data.itens is not None:
            # Remove itens antigos
            await self.db.execute(
                BiddingProposalItem.__table__.delete().where(BiddingProposalItem.proposal_id == proposal_id)
            )

            # Adiciona novos itens
            for item_data in data.itens:
                item = BiddingProposalItem(
                    proposal_id=proposal.id,
                    **item_data.model_dump(),
                    valor_total=item_data.quantidade * item_data.valor_unitario,
                )
                self.db.add(item)

        await self.db.commit()
        await self.db.refresh(proposal)
        logger.info(f"Proposta atualizada: {proposal.numero} v{proposal.versao}")
        return proposal

    async def delete(self, proposal_id: UUID) -> bool:
        """Remove proposta (soft delete)."""
        proposal = await self.get_by_id(proposal_id)
        if not proposal:
            return False

        proposal.ativo = False
        proposal.updated_at = datetime.utcnow()
        await self.db.commit()
        logger.info(f"Proposta removida: {proposal.numero} v{proposal.versao}")
        return True

    async def submit(self, proposal_id: UUID) -> BiddingProposal | None:
        """Marca proposta como enviada."""
        proposal = await self.get_by_id(proposal_id)
        if not proposal:
            return None

        if proposal.status != ProposalStatus.READY.value:
            logger.warning(f"Proposta {proposal_id} nao esta pronta para envio")
            return None

        proposal.status = ProposalStatus.SUBMITTED.value
        proposal.data_envio = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(proposal)
        logger.info(f"Proposta enviada: {proposal.numero}")
        return proposal

    async def register_result(
        self, proposal_id: UUID, status: str, posicao: int = None, valor_final: Decimal = None
    ) -> BiddingProposal | None:
        """Registra resultado da proposta."""
        proposal = await self.get_by_id(proposal_id)
        if not proposal:
            return None

        proposal.status = status
        proposal.posicao_classificacao = posicao
        proposal.valor_lance_final = valor_final
        proposal.data_resultado = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(proposal)
        logger.info(f"Resultado registrado: {proposal.numero} - {status}")
        return proposal

    async def add_lance(self, proposal_id: UUID, valor: Decimal) -> BiddingProposal | None:
        """Adiciona lance ao historico (pregao)."""
        proposal = await self.get_by_id(proposal_id)
        if not proposal:
            return None

        proposal.adicionar_lance(valor)
        await self.db.commit()
        await self.db.refresh(proposal)
        logger.info(f"Lance adicionado: {proposal.numero} - R$ {valor}")
        return proposal

    async def get_vencedoras(self) -> builtins.list[BiddingProposal]:
        """Lista propostas vencedoras."""
        result = await self.db.execute(
            select(BiddingProposal)
            .where(BiddingProposal.status == ProposalStatus.WINNER.value, BiddingProposal.ativo)
            .order_by(BiddingProposal.data_resultado.desc())
        )
        return list(result.scalars().all())

    async def count_by_status(self) -> dict:
        """Conta propostas por status."""
        result = await self.db.execute(
            select(BiddingProposal.status, func.count(BiddingProposal.id))
            .where(BiddingProposal.ativo)
            .group_by(BiddingProposal.status)
        )
        return {row[0]: row[1] for row in result.all()}

    async def get_items(self, proposal_id: UUID) -> builtins.list[BiddingProposalItem]:
        """Lista itens de uma proposta."""
        result = await self.db.execute(
            select(BiddingProposalItem)
            .where(BiddingProposalItem.proposal_id == proposal_id)
            .order_by(BiddingProposalItem.numero_item)
        )
        return list(result.scalars().all())
