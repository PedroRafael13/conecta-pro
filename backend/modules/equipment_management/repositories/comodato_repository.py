"""Repository para EquipmentComodato."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.equipment_management.models.comodato import (
    ComodatoStatus,
    EquipmentComodato,
)
from modules.equipment_management.schemas.comodato import (
    ComodatoCreate,
    ComodatoFilter,
    ComodatoUpdate,
)

logger = logging.getLogger(__name__)


class ComodatoRepository:
    """Repository para operações de EquipmentComodato."""

    def __init__(self, session: AsyncSession):
        """Inicializa o repository."""
        self.session = session

    async def create(self, data: ComodatoCreate) -> EquipmentComodato:
        """Cria um novo comodato."""
        comodato = EquipmentComodato(
            equipment_id=data.equipment_id,
            equipment_code=data.equipment_code,
            equipment_name=data.equipment_name,
            equipment_type=data.equipment_type,
            serial_number=data.serial_number,
            equipment_value=data.equipment_value,
            equipment_condition=data.equipment_condition,
            client_id=data.client_id,
            client_name=data.client_name,
            client_document=data.client_document,
            contract_id=data.contract_id,
            responsible_name=data.responsible_name,
            responsible_document=data.responsible_document,
            responsible_phone=data.responsible_phone,
            responsible_email=data.responsible_email,
            start_date=data.start_date,
            end_date=data.end_date,
            duration_months=data.duration_months,
            auto_renewal=data.auto_renewal,
            renewal_period_months=data.renewal_period_months,
            notice_period_days=data.notice_period_days,
            usage_location=data.usage_location,
            usage_address=data.usage_address,
            gps_latitude=data.gps_latitude,
            gps_longitude=data.gps_longitude,
            terms=data.terms,
            special_conditions=data.special_conditions,
            usage_restrictions=data.usage_restrictions,
            maintenance_responsibility=data.maintenance_responsibility,
            damage_penalty_percent=data.damage_penalty_percent,
            loss_penalty_percent=data.loss_penalty_percent,
            early_return_penalty=data.early_return_penalty,
            notes=data.notes,
        )
        self.session.add(comodato)
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Comodato criado: {comodato.comodato_code}")
        return comodato

    async def get_by_id(self, comodato_id: str | UUID) -> Optional[EquipmentComodato]:
        """Busca comodato por ID."""
        if isinstance(comodato_id, str):
            comodato_id = UUID(comodato_id)
        result = await self.session.execute(
            select(EquipmentComodato).where(
                and_(
                    EquipmentComodato.id == comodato_id,
                    EquipmentComodato.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[EquipmentComodato]:
        """Busca comodato por código."""
        result = await self.session.execute(
            select(EquipmentComodato).where(
                and_(
                    EquipmentComodato.comodato_code == code,
                    EquipmentComodato.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_equipment(self, equipment_id: str) -> Optional[EquipmentComodato]:
        """Busca comodato ativo de um equipamento."""
        result = await self.session.execute(
            select(EquipmentComodato).where(
                and_(
                    EquipmentComodato.equipment_id == equipment_id,
                    EquipmentComodato.status == ComodatoStatus.ACTIVE,
                    EquipmentComodato.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, comodato_id: str | UUID, data: ComodatoUpdate
    ) -> Optional[EquipmentComodato]:
        """Atualiza um comodato."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comodato, field, value)

        comodato.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Comodato atualizado: {comodato.comodato_code}")
        return comodato

    async def delete(self, comodato_id: str | UUID) -> bool:
        """Soft delete de comodato."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return False

        comodato.is_active = False
        comodato.updated_at = datetime.utcnow()
        await self.session.flush()
        logger.info(f"Comodato desativado: {comodato.comodato_code}")
        return True

    async def list_with_filters(
        self,
        filters: Optional[ComodatoFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[EquipmentComodato], int]:
        """Lista comodatos com filtros e paginação."""
        query = select(EquipmentComodato).where(EquipmentComodato.is_active == True)

        if filters:
            conditions = []

            if filters.search:
                search_term = f"%{filters.search}%"
                conditions.append(
                    or_(
                        EquipmentComodato.comodato_code.ilike(search_term),
                        EquipmentComodato.equipment_name.ilike(search_term),
                        EquipmentComodato.equipment_code.ilike(search_term),
                        EquipmentComodato.client_name.ilike(search_term),
                        EquipmentComodato.responsible_name.ilike(search_term),
                    )
                )

            if filters.status:
                conditions.append(EquipmentComodato.status == filters.status)

            if filters.client_id:
                conditions.append(EquipmentComodato.client_id == filters.client_id)

            if filters.equipment_id:
                conditions.append(EquipmentComodato.equipment_id == filters.equipment_id)

            if filters.is_signed is not None:
                if filters.is_signed:
                    conditions.append(EquipmentComodato.signed_at != None)
                else:
                    conditions.append(EquipmentComodato.signed_at == None)

            if filters.is_delivered is not None:
                if filters.is_delivered:
                    conditions.append(EquipmentComodato.delivered_at != None)
                else:
                    conditions.append(EquipmentComodato.delivered_at == None)

            if filters.is_expired is not None:
                now = datetime.utcnow()
                if filters.is_expired:
                    conditions.append(
                        and_(
                            EquipmentComodato.end_date < now,
                            EquipmentComodato.status == ComodatoStatus.ACTIVE,
                        )
                    )
                else:
                    conditions.append(
                        or_(
                            EquipmentComodato.end_date >= now,
                            EquipmentComodato.end_date == None,
                        )
                    )

            if filters.has_damages is not None:
                conditions.append(EquipmentComodato.has_damages == filters.has_damages)

            if filters.date_from:
                conditions.append(EquipmentComodato.start_date >= filters.date_from)

            if filters.date_to:
                conditions.append(EquipmentComodato.start_date <= filters.date_to)

            if conditions:
                query = query.where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        query = query.order_by(EquipmentComodato.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_client(self, client_id: str) -> list[EquipmentComodato]:
        """Lista comodatos de um cliente."""
        result = await self.session.execute(
            select(EquipmentComodato)
            .where(
                and_(
                    EquipmentComodato.client_id == client_id,
                    EquipmentComodato.is_active == True,
                )
            )
            .order_by(EquipmentComodato.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active(self, client_id: Optional[str] = None) -> list[EquipmentComodato]:
        """Lista comodatos ativos."""
        conditions = [
            EquipmentComodato.status == ComodatoStatus.ACTIVE,
            EquipmentComodato.is_active == True,
        ]

        if client_id:
            conditions.append(EquipmentComodato.client_id == client_id)

        result = await self.session.execute(
            select(EquipmentComodato)
            .where(and_(*conditions))
            .order_by(EquipmentComodato.end_date)
        )
        return list(result.scalars().all())

    async def get_pending_signature(self) -> list[EquipmentComodato]:
        """Lista comodatos aguardando assinatura."""
        result = await self.session.execute(
            select(EquipmentComodato)
            .where(
                and_(
                    EquipmentComodato.status == ComodatoStatus.PENDING_SIGNATURE,
                    EquipmentComodato.is_active == True,
                )
            )
            .order_by(EquipmentComodato.created_at)
        )
        return list(result.scalars().all())

    async def get_pending_delivery(self) -> list[EquipmentComodato]:
        """Lista comodatos assinados aguardando entrega."""
        result = await self.session.execute(
            select(EquipmentComodato)
            .where(
                and_(
                    EquipmentComodato.status == ComodatoStatus.ACTIVE,
                    EquipmentComodato.signed_at != None,
                    EquipmentComodato.delivered_at == None,
                    EquipmentComodato.is_active == True,
                )
            )
            .order_by(EquipmentComodato.signed_at)
        )
        return list(result.scalars().all())

    async def get_pending_return(self) -> list[EquipmentComodato]:
        """Lista comodatos com devolução solicitada."""
        result = await self.session.execute(
            select(EquipmentComodato)
            .where(
                and_(
                    EquipmentComodato.return_requested_at != None,
                    EquipmentComodato.returned_at == None,
                    EquipmentComodato.is_active == True,
                )
            )
            .order_by(EquipmentComodato.return_scheduled_at)
        )
        return list(result.scalars().all())

    async def get_expiring(self, days: int = 30) -> list[EquipmentComodato]:
        """Lista comodatos expirando em X dias."""
        now = datetime.utcnow()
        limit_date = now + timedelta(days=days)

        result = await self.session.execute(
            select(EquipmentComodato)
            .where(
                and_(
                    EquipmentComodato.end_date > now,
                    EquipmentComodato.end_date <= limit_date,
                    EquipmentComodato.status == ComodatoStatus.ACTIVE,
                    EquipmentComodato.is_active == True,
                )
            )
            .order_by(EquipmentComodato.end_date)
        )
        return list(result.scalars().all())

    async def get_expired(self) -> list[EquipmentComodato]:
        """Lista comodatos expirados não devolvidos."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(EquipmentComodato)
            .where(
                and_(
                    EquipmentComodato.end_date < now,
                    EquipmentComodato.status == ComodatoStatus.ACTIVE,
                    EquipmentComodato.returned_at == None,
                    EquipmentComodato.is_active == True,
                )
            )
            .order_by(EquipmentComodato.end_date)
        )
        return list(result.scalars().all())

    async def get_with_damages(self) -> list[EquipmentComodato]:
        """Lista comodatos com danos registrados."""
        result = await self.session.execute(
            select(EquipmentComodato)
            .where(
                and_(
                    EquipmentComodato.has_damages == True,
                    EquipmentComodato.is_active == True,
                )
            )
            .order_by(EquipmentComodato.returned_at.desc())
        )
        return list(result.scalars().all())

    async def sign(
        self,
        comodato_id: str | UUID,
        signed_by_client: str,
        signed_by_company: str,
    ) -> Optional[EquipmentComodato]:
        """Registra assinatura do contrato."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.sign(
            signed_by_client=signed_by_client,
            signed_by_company=signed_by_company,
        )
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Comodato assinado: {comodato.comodato_code}")
        return comodato

    async def deliver(
        self,
        comodato_id: str | UUID,
        delivered_by: str,
        received_by: str,
        notes: Optional[str] = None,
        photos: Optional[list] = None,
    ) -> Optional[EquipmentComodato]:
        """Registra entrega do equipamento."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.deliver(
            delivered_by=delivered_by,
            received_by=received_by,
            notes=notes,
            photos=photos,
        )
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Comodato entregue: {comodato.comodato_code}")
        return comodato

    async def request_return(
        self, comodato_id: str | UUID
    ) -> Optional[EquipmentComodato]:
        """Solicita devolução."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.request_return()
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Devolução solicitada: {comodato.comodato_code}")
        return comodato

    async def schedule_return(
        self, comodato_id: str | UUID, scheduled_date: datetime
    ) -> Optional[EquipmentComodato]:
        """Agenda devolução."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.schedule_return(scheduled_date=scheduled_date)
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Devolução agendada: {comodato.comodato_code}")
        return comodato

    async def register_return(
        self,
        comodato_id: str | UUID,
        returned_by: str,
        condition: str,
        notes: Optional[str] = None,
        photos: Optional[list] = None,
    ) -> Optional[EquipmentComodato]:
        """Registra devolução."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.register_return(
            returned_by=returned_by,
            condition=condition,
            notes=notes,
            photos=photos,
        )
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Comodato devolvido: {comodato.comodato_code}")
        return comodato

    async def register_damage(
        self,
        comodato_id: str | UUID,
        description: str,
        cost: float,
    ) -> Optional[EquipmentComodato]:
        """Registra dano no equipamento."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.register_damage(description=description, cost=cost)
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Dano registrado: {comodato.comodato_code}")
        return comodato

    async def mark_as_lost(self, comodato_id: str | UUID) -> Optional[EquipmentComodato]:
        """Marca equipamento como perdido."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.mark_as_lost()
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Equipamento perdido: {comodato.comodato_code}")
        return comodato

    async def terminate(
        self, comodato_id: str | UUID, reason: str
    ) -> Optional[EquipmentComodato]:
        """Encerra contrato."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.terminate(reason=reason)
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Comodato encerrado: {comodato.comodato_code}")
        return comodato

    async def transfer(
        self,
        comodato_id: str | UUID,
        new_client_id: str,
        reason: str,
    ) -> Optional[EquipmentComodato]:
        """Transfere comodato para outro cliente."""
        comodato = await self.get_by_id(comodato_id)
        if not comodato:
            return None

        comodato.transfer(new_client_id=new_client_id, reason=reason)
        await self.session.flush()
        await self.session.refresh(comodato)
        logger.info(f"Comodato transferido: {comodato.comodato_code}")
        return comodato

    async def get_stats(self, client_id: Optional[str] = None) -> dict:
        """Estatísticas de comodatos."""
        conditions = [EquipmentComodato.is_active == True]

        if client_id:
            conditions.append(EquipmentComodato.client_id == client_id)

        result = await self.session.execute(
            select(EquipmentComodato).where(and_(*conditions))
        )
        comodatos = list(result.scalars().all())

        now = datetime.utcnow()
        stats = {
            "total": len(comodatos),
            "by_status": {},
            "active": 0,
            "pending_signature": 0,
            "pending_delivery": 0,
            "pending_return": 0,
            "returned": 0,
            "terminated": 0,
            "with_damages": 0,
            "lost": 0,
            "expiring_30_days": 0,
            "expired": 0,
            "total_value": 0.0,
            "total_penalty_applied": 0.0,
        }

        for c in comodatos:
            # Por status
            status_key = c.status.value if c.status else "unknown"
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1

            if c.status == ComodatoStatus.ACTIVE:
                stats["active"] += 1

                if not c.signed_at:
                    pass
                elif not c.delivered_at:
                    stats["pending_delivery"] += 1

                if c.return_requested_at and not c.returned_at:
                    stats["pending_return"] += 1

                if c.end_date:
                    if c.end_date < now:
                        stats["expired"] += 1
                    elif c.end_date <= now + timedelta(days=30):
                        stats["expiring_30_days"] += 1

            elif c.status == ComodatoStatus.PENDING_SIGNATURE:
                stats["pending_signature"] += 1
            elif c.status == ComodatoStatus.RETURNED:
                stats["returned"] += 1
            elif c.status == ComodatoStatus.TERMINATED:
                stats["terminated"] += 1

            if c.has_damages:
                stats["with_damages"] += 1

            if c.is_lost:
                stats["lost"] += 1

            if c.equipment_value:
                stats["total_value"] += c.equipment_value

            if c.penalty_applied:
                stats["total_penalty_applied"] += c.penalty_applied

        return stats
