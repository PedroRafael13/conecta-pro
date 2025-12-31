"""Repository para integração com sistemas externos."""

import logging
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from modules.hr.payroll_integration.models import (
    PayrollIntegration,
    IntegrationType,
    IntegrationStatus,
)
from modules.hr.payroll_integration.schemas import (
    PayrollIntegrationCreate,
    PayrollIntegrationUpdate,
)

logger = logging.getLogger(__name__)


class PayrollIntegrationRepository:
    """Repository para operações de integração."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: PayrollIntegrationCreate,
        condominio_id: UUID,
        *,
        created_by: UUID = None,
    ) -> PayrollIntegration:
        """Cria nova integração."""
        integration = PayrollIntegration(
            condominio_id=condominio_id,
            name=data.name,
            description=data.description,
            integration_type=data.integration_type.value,
            endpoint_url=data.endpoint_url,
            api_version=data.api_version,
            auth_type=data.auth_type,
            credentials=data.credentials.model_dump() if data.credentials else {},
            esocial_config=(
                data.esocial_config.model_dump() if data.esocial_config else {}
            ),
            field_mapping=data.field_mapping or {},
            rubrica_mapping=data.rubrica_mapping or {},
            sync_config=data.sync_config.model_dump() if data.sync_config else {},
            webhook_url=data.webhook_url,
            webhook_events=data.webhook_events or [],
            status=IntegrationStatus.CONFIGURING.value,
            created_by=created_by,
        )

        self.db.add(integration)
        await self.db.commit()
        await self.db.refresh(integration)

        logger.info("Integração criada: %s", integration.name)
        return integration

    async def get_by_id(
        self,
        integration_id: UUID,
    ) -> Optional[PayrollIntegration]:
        """Busca integração por ID."""
        query = select(PayrollIntegration).where(
            and_(
                PayrollIntegration.id == integration_id,
                PayrollIntegration.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_type(
        self,
        integration_type: IntegrationType,
        condominio_id: UUID,
    ) -> Optional[PayrollIntegration]:
        """Busca integração por tipo."""
        query = select(PayrollIntegration).where(
            and_(
                PayrollIntegration.integration_type == integration_type.value,
                PayrollIntegration.condominio_id == condominio_id,
                PayrollIntegration.ativo.is_(True),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_integrations(
        self,
        condominio_id: UUID,
        *,
        integration_type: IntegrationType = None,
        status: IntegrationStatus = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[PayrollIntegration], int]:
        """Lista integrações com filtros."""
        conditions = [
            PayrollIntegration.condominio_id == condominio_id,
            PayrollIntegration.ativo.is_(True),
        ]

        if integration_type:
            conditions.append(
                PayrollIntegration.integration_type == integration_type.value
            )
        if status:
            conditions.append(PayrollIntegration.status == status.value)

        # Count
        count_query = select(func.count(PayrollIntegration.id)).where(
            and_(*conditions)
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Fetch
        query = (
            select(PayrollIntegration)
            .where(and_(*conditions))
            .order_by(PayrollIntegration.name)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        integrations = list(result.scalars().all())

        return integrations, total

    async def update(
        self,
        integration_id: UUID,
        data: PayrollIntegrationUpdate,
    ) -> Optional[PayrollIntegration]:
        """Atualiza integração."""
        integration = await self.get_by_id(integration_id)
        if not integration:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Tratar nested objects
        if "credentials" in update_data and update_data["credentials"]:
            update_data["credentials"] = update_data["credentials"].model_dump()
        if "esocial_config" in update_data and update_data["esocial_config"]:
            update_data["esocial_config"] = update_data["esocial_config"].model_dump()
        if "sync_config" in update_data and update_data["sync_config"]:
            update_data["sync_config"] = update_data["sync_config"].model_dump()
        if "status" in update_data and update_data["status"]:
            update_data["status"] = update_data["status"].value

        for field, value in update_data.items():
            if value is not None:
                setattr(integration, field, value)

        integration.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(integration)

        return integration

    async def update_status(
        self,
        integration_id: UUID,
        status: IntegrationStatus,
    ) -> Optional[PayrollIntegration]:
        """Atualiza status da integração."""
        integration = await self.get_by_id(integration_id)
        if not integration:
            return None

        integration.status = status.value
        integration.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(integration)

        return integration

    async def record_sync(
        self,
        integration_id: UUID,
        *,
        success: bool,
        records: int = 0,
        message: str = None,
    ) -> Optional[PayrollIntegration]:
        """Registra resultado de sincronização."""
        integration = await self.get_by_id(integration_id)
        if not integration:
            return None

        integration.record_sync(success, records, message)
        await self.db.commit()
        await self.db.refresh(integration)

        return integration

    async def update_mapping(
        self,
        integration_id: UUID,
        *,
        field_mapping: dict = None,
        rubrica_mapping: dict = None,
    ) -> Optional[PayrollIntegration]:
        """Atualiza mapeamentos."""
        integration = await self.get_by_id(integration_id)
        if not integration:
            return None

        if field_mapping is not None:
            integration.field_mapping = field_mapping
        if rubrica_mapping is not None:
            integration.rubrica_mapping = rubrica_mapping

        integration.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(integration)

        return integration

    async def delete(self, integration_id: UUID) -> bool:
        """Soft delete da integração."""
        integration = await self.get_by_id(integration_id)
        if not integration:
            return False

        integration.ativo = False
        integration.status = IntegrationStatus.INACTIVE.value
        integration.updated_at = datetime.utcnow()
        await self.db.commit()

        return True

    async def get_active_integrations(
        self,
        condominio_id: UUID,
    ) -> List[PayrollIntegration]:
        """Retorna integrações ativas."""
        query = select(PayrollIntegration).where(
            and_(
                PayrollIntegration.condominio_id == condominio_id,
                PayrollIntegration.ativo.is_(True),
                PayrollIntegration.status == IntegrationStatus.ACTIVE.value,
            )
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_esocial_integration(
        self,
        condominio_id: UUID,
    ) -> Optional[PayrollIntegration]:
        """Retorna integração eSocial ativa."""
        return await self.get_by_type(IntegrationType.ESOCIAL, condominio_id)
