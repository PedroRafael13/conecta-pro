"""
Repository para operações de banco de dados com Opportunity.
"""

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.crm.models.lead import Lead, LeadStatus
from modules.crm.models.opportunity import (
    Opportunity,
    OpportunityStage,
)
from modules.crm.schemas.opportunity import (
    OpportunityClose,
    OpportunityCreate,
    OpportunityCreateFromLead,
    OpportunityFilter,
    OpportunityUpdate,
    PipelineStats,
)


class OpportunityRepository:
    """Repository para operações CRUD de Opportunity."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: OpportunityCreate) -> Opportunity:
        """
        Cria uma nova opportunity.

        Args:
            data: Dados da opportunity

        Returns:
            Opportunity criada
        """
        opportunity = Opportunity(
            id=str(uuid4()),
            title=data.title,
            description=data.description,
            lead_id=data.lead_id,
            contact_name=data.contact_name,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            company_name=data.company_name,
            stage=data.stage.value,
            priority=data.priority.value,
            value=data.value,
            probability=data.probability,
            expected_close_date=data.expected_close_date,
            owner_id=data.owner_id,
            notes=data.notes,
        )

        self.db.add(opportunity)
        await self.db.commit()
        await self.db.refresh(opportunity)

        logger.info(f"Opportunity criada: {opportunity.id} ({opportunity.title})")
        return opportunity

    async def create_from_lead(self, data: OpportunityCreateFromLead) -> Optional[Opportunity]:
        """
        Cria uma opportunity a partir de um lead.

        Args:
            data: Dados com lead_id e informações adicionais

        Returns:
            Opportunity criada ou None se lead não encontrado
        """
        # Buscar o lead
        result = await self.db.execute(
            select(Lead).where(Lead.id == data.lead_id, Lead.is_active.is_(True))
        )
        lead = result.scalar_one_or_none()

        if not lead:
            return None

        # Criar opportunity com dados do lead
        opportunity = Opportunity(
            id=str(uuid4()),
            title=data.title,
            description=data.description,
            lead_id=lead.id,
            contact_name=lead.name,
            contact_email=lead.email,
            contact_phone=lead.phone,
            company_name=lead.company,
            stage=OpportunityStage.QUALIFICATION.value,
            priority=data.priority.value,
            value=data.value,
            probability=data.probability,
            expected_close_date=data.expected_close_date,
            owner_id=data.owner_id or lead.assigned_to_id,
            notes=data.notes,
        )

        # Atualizar status do lead para WON (convertido)
        lead.status = LeadStatus.WON.value
        lead.updated_at = datetime.utcnow()

        self.db.add(opportunity)
        await self.db.commit()
        await self.db.refresh(opportunity)

        logger.info(
            f"Lead {lead.id} convertido em Opportunity {opportunity.id}"
        )
        return opportunity

    async def get_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        """
        Busca opportunity por ID.

        Args:
            opportunity_id: ID da opportunity

        Returns:
            Opportunity ou None
        """
        result = await self.db.execute(
            select(Opportunity).where(
                Opportunity.id == opportunity_id,
                Opportunity.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[OpportunityFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Opportunity], int]:
        """
        Lista opportunities com filtros e paginação.

        Args:
            filters: Filtros de busca
            page: Página atual
            page_size: Itens por página

        Returns:
            Tupla (opportunities, total)
        """
        query = select(Opportunity).where(Opportunity.is_active.is_(True))

        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(Opportunity.id)).where(
            Opportunity.is_active.is_(True)
        )
        if filters:
            count_query = self._apply_filters(count_query, filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Opportunity.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        opportunities = list(result.scalars().all())

        return opportunities, total

    def _apply_filters(self, query, filters: OpportunityFilter):
        """Aplica filtros à query."""
        if filters.stage:
            query = query.where(Opportunity.stage == filters.stage.value)

        if filters.priority:
            query = query.where(Opportunity.priority == filters.priority.value)

        if filters.owner_id:
            query = query.where(Opportunity.owner_id == filters.owner_id)

        if filters.is_open is not None:
            open_stages = [
                OpportunityStage.QUALIFICATION.value,
                OpportunityStage.NEEDS_ANALYSIS.value,
                OpportunityStage.PROPOSAL.value,
                OpportunityStage.NEGOTIATION.value,
            ]
            if filters.is_open:
                query = query.where(Opportunity.stage.in_(open_stages))
            else:
                query = query.where(Opportunity.stage.notin_(open_stages))

        if filters.min_value is not None:
            query = query.where(Opportunity.value >= filters.min_value)

        if filters.max_value is not None:
            query = query.where(Opportunity.value <= filters.max_value)

        if filters.company_name:
            query = query.where(
                Opportunity.company_name.ilike(f"%{filters.company_name}%")
            )

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Opportunity.title.ilike(search_term),
                    Opportunity.contact_name.ilike(search_term),
                    Opportunity.contact_email.ilike(search_term),
                    Opportunity.company_name.ilike(search_term),
                )
            )

        return query

    async def update(
        self, opportunity_id: str, data: OpportunityUpdate
    ) -> Optional[Opportunity]:
        """
        Atualiza uma opportunity.

        Args:
            opportunity_id: ID da opportunity
            data: Dados para atualização

        Returns:
            Opportunity atualizada ou None
        """
        opportunity = await self.get_by_id(opportunity_id)
        if not opportunity:
            return None

        # Atualizar apenas campos fornecidos
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "stage" and value:
                setattr(opportunity, field, value.value)
            elif field == "priority" and value:
                setattr(opportunity, field, value.value)
            else:
                setattr(opportunity, field, value)

        opportunity.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(opportunity)

        logger.info(f"Opportunity atualizada: {opportunity.id}")
        return opportunity

    async def update_stage(
        self,
        opportunity_id: str,
        stage: OpportunityStage,
        notes: Optional[str] = None,
    ) -> Optional[Opportunity]:
        """
        Atualiza estágio da opportunity.

        Args:
            opportunity_id: ID da opportunity
            stage: Novo estágio
            notes: Observações

        Returns:
            Opportunity atualizada ou None
        """
        opportunity = await self.get_by_id(opportunity_id)
        if not opportunity:
            return None

        old_stage = opportunity.stage
        opportunity.stage = stage.value

        # Atualizar probabilidade baseada no estágio
        stage_probabilities = {
            OpportunityStage.QUALIFICATION.value: 10,
            OpportunityStage.NEEDS_ANALYSIS.value: 25,
            OpportunityStage.PROPOSAL.value: 50,
            OpportunityStage.NEGOTIATION.value: 75,
            OpportunityStage.CLOSED_WON.value: 100,
            OpportunityStage.CLOSED_LOST.value: 0,
        }
        opportunity.probability = stage_probabilities.get(stage.value, 50)

        if notes:
            existing_notes = opportunity.notes or ""
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            opportunity.notes = (
                f"{existing_notes}\n[{timestamp}] {old_stage} -> {stage.value}: {notes}"
            ).strip()

        opportunity.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(opportunity)

        logger.info(
            f"Opportunity {opportunity.id} stage: {old_stage} -> {stage.value}"
        )
        return opportunity

    async def close(
        self, opportunity_id: str, data: OpportunityClose
    ) -> Optional[Opportunity]:
        """
        Fecha uma opportunity (ganhou ou perdeu).

        Args:
            opportunity_id: ID da opportunity
            data: Dados de fechamento

        Returns:
            Opportunity fechada ou None
        """
        opportunity = await self.get_by_id(opportunity_id)
        if not opportunity:
            return None

        if data.won:
            opportunity.stage = OpportunityStage.CLOSED_WON.value
            opportunity.probability = 100
            opportunity.win_notes = data.notes
        else:
            opportunity.stage = OpportunityStage.CLOSED_LOST.value
            opportunity.probability = 0
            opportunity.loss_reason = data.loss_reason.value if data.loss_reason else None
            opportunity.competitor = data.competitor
            opportunity.loss_notes = data.notes

        opportunity.actual_close_date = data.actual_close_date or date.today()
        opportunity.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(opportunity)

        status = "WON" if data.won else "LOST"
        logger.info(f"Opportunity {opportunity.id} fechada: {status}")
        return opportunity

    async def delete(self, opportunity_id: str) -> bool:
        """
        Soft delete de opportunity.

        Args:
            opportunity_id: ID da opportunity

        Returns:
            True se deletada
        """
        opportunity = await self.get_by_id(opportunity_id)
        if not opportunity:
            return False

        opportunity.is_active = False
        opportunity.updated_at = datetime.utcnow()

        await self.db.commit()

        logger.info(f"Opportunity deletada (soft): {opportunity.id}")
        return True

    async def get_pipeline_stats(  # pylint: disable=too-many-locals
        self, owner_id: Optional[str] = None
    ) -> PipelineStats:
        """
        Obtém estatísticas do pipeline de vendas.

        Args:
            owner_id: Filtrar por responsável

        Returns:
            Estatísticas do pipeline
        """
        base_query = select(Opportunity).where(Opportunity.is_active.is_(True))

        if owner_id:
            base_query = base_query.where(Opportunity.owner_id == owner_id)

        result = await self.db.execute(base_query)
        opportunities = list(result.scalars().all())

        if not opportunities:
            return PipelineStats(
                total_opportunities=0,
                open_opportunities=0,
                won_opportunities=0,
                lost_opportunities=0,
                total_value=0.0,
                weighted_value=0.0,
                won_value=0.0,
                lost_value=0.0,
                win_rate=0.0,
                avg_deal_size=0.0,
                avg_days_to_close=0.0,
                by_stage={},
                by_priority={},
                overdue_count=0,
            )

        # Calcular estatísticas
        open_count = 0
        won_count = 0
        lost_count = 0
        total_value = 0.0
        weighted_value = 0.0
        won_value = 0.0
        lost_value = 0.0
        by_stage: dict[str, int] = {}
        by_priority: dict[str, int] = {}
        overdue_count = 0
        total_days_to_close = 0
        closed_count = 0

        for opp in opportunities:
            total_value += opp.value
            weighted_value += opp.weighted_value
            by_stage[opp.stage] = by_stage.get(opp.stage, 0) + 1
            by_priority[opp.priority] = by_priority.get(opp.priority, 0) + 1

            if opp.is_open:
                open_count += 1
                if opp.is_overdue:
                    overdue_count += 1
            elif opp.is_won:
                won_count += 1
                won_value += opp.value
                if opp.actual_close_date:
                    total_days_to_close += opp.days_in_pipeline
                    closed_count += 1
            elif opp.is_lost:
                lost_count += 1
                lost_value += opp.value
                if opp.actual_close_date:
                    total_days_to_close += opp.days_in_pipeline
                    closed_count += 1

        # Calcular métricas derivadas
        total_closed = won_count + lost_count
        win_rate = (won_count / total_closed * 100) if total_closed > 0 else 0.0
        avg_deal_size = total_value / len(opportunities) if opportunities else 0.0
        avg_days_to_close = (
            total_days_to_close / closed_count if closed_count > 0 else 0.0
        )

        return PipelineStats(
            total_opportunities=len(opportunities),
            open_opportunities=open_count,
            won_opportunities=won_count,
            lost_opportunities=lost_count,
            total_value=total_value,
            weighted_value=weighted_value,
            won_value=won_value,
            lost_value=lost_value,
            win_rate=win_rate,
            avg_deal_size=avg_deal_size,
            avg_days_to_close=avg_days_to_close,
            by_stage=by_stage,
            by_priority=by_priority,
            overdue_count=overdue_count,
        )
