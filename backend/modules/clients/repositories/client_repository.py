"""
Client Repository - Data Access Layer
Sprint 30: Cadastro de Clientes/Condomínios
"""

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, joinedload

from modules.clients.models.client import Client, ClientStatus
from modules.clients.models.client_contract import ClientContract
from modules.clients.models.condominium import Condominium, CondominiumStatus
from modules.clients.models.integration_settings import IntegrationSettings
from modules.clients.models.unit import Unit, UnitStatus
from modules.clients.schemas.client_schemas import (
    ClientContractCreate,
    ClientContractUpdate,
    ClientCreate,
    ClientFilter,
    ClientUpdate,
    CondominiumCreate,
    CondominiumUpdate,
    IntegrationSettingsCreate,
    IntegrationSettingsUpdate,
    UnitCreate,
    UnitUpdate,
)

logger = logging.getLogger(__name__)


class ClientRepository:
    """Repository for Client and related entities."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # CLIENT METHODS
    # =========================================================================

    def create_client(self, data: ClientCreate, created_by: UUID | None = None) -> Client:
        """Create a new client."""
        # Generate code
        sequence = self._get_next_client_sequence()
        code = Client.generate_code(sequence)

        client = Client(code=code, created_by=created_by, **data.model_dump(exclude_none=True))
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        logger.info("Client created: %s", client.code)
        return client

    def get_client(self, client_id: UUID) -> Client | None:
        """Get client by ID."""
        return self.db.query(Client).filter(Client.id == client_id).first()

    def get_client_by_code(self, code: str) -> Client | None:
        """Get client by code."""
        return self.db.query(Client).filter(Client.code == code).first()

    def get_client_by_document(self, document: str) -> Client | None:
        """Get client by document number."""
        return self.db.query(Client).filter(Client.document_number == document).first()

    def get_client_with_relations(self, client_id: UUID) -> Client | None:
        """Get client with all relations loaded."""
        return (
            self.db.query(Client)
            .options(
                joinedload(Client.condominiums), joinedload(Client.contracts), joinedload(Client.integration_settings)
            )
            .filter(Client.id == client_id)
            .first()
        )

    def list_clients(  # pylint: disable=too-many-branches
        self,
        filters: ClientFilter | None = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[Client], int]:
        """List clients with filtering and pagination."""
        query = self.db.query(Client)

        if filters:
            if filters.type:
                query = query.filter(Client.type == filters.type)
            if filters.status:
                query = query.filter(Client.status == filters.status)
            if filters.segment:
                query = query.filter(Client.segment == filters.segment)
            if filters.is_defaulter is not None:
                query = query.filter(Client.is_defaulter == filters.is_defaulter)
            if filters.is_vip is not None:
                query = query.filter(Client.is_vip == filters.is_vip)
            if filters.guardian_enabled is not None:
                query = query.filter(Client.guardian_enabled == filters.guardian_enabled)
            if filters.plus_enabled is not None:
                query = query.filter(Client.plus_enabled == filters.plus_enabled)
            if filters.city:
                query = query.filter(Client.address_city.ilike(f"%{filters.city}%"))
            if filters.state:
                query = query.filter(Client.address_state == filters.state)
            if filters.sales_rep_id:
                query = query.filter(Client.sales_rep_id == filters.sales_rep_id)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Client.legal_name.ilike(search_term),
                        Client.trade_name.ilike(search_term),
                        Client.document_number.ilike(search_term),
                        Client.code.ilike(search_term),
                        Client.email.ilike(search_term),
                    )
                )

        total = query.count()

        # Ordering
        order_column = getattr(Client, order_by, Client.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)

        clients = query.offset(skip).limit(limit).all()
        return clients, total

    def update_client(self, client_id: UUID, data: ClientUpdate, updated_by: UUID | None = None) -> Client | None:
        """Update a client."""
        client = self.get_client(client_id)
        if not client:
            return None

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(client, field, value)

        client.updated_by = updated_by
        client.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(client)
        logger.info("Client updated: %s", client.code)
        return client

    def delete_client(self, client_id: UUID) -> bool:
        """Delete a client."""
        client = self.get_client(client_id)
        if not client:
            return False

        self.db.delete(client)
        self.db.commit()
        logger.info("Client deleted: %s", client.code)
        return True

    def get_client_stats(self) -> dict:
        """Get client statistics."""
        total = self.db.query(func.count(Client.id)).scalar() or 0
        active = self.db.query(func.count(Client.id)).filter(Client.status == ClientStatus.ATIVO).scalar() or 0
        inactive = self.db.query(func.count(Client.id)).filter(Client.status == ClientStatus.INATIVO).scalar() or 0
        defaulters = self.db.query(func.count(Client.id)).filter(Client.is_defaulter.is_(True)).scalar() or 0
        vip = self.db.query(func.count(Client.id)).filter(Client.is_vip.is_(True)).scalar() or 0

        by_type = dict(self.db.query(Client.type, func.count(Client.id)).group_by(Client.type).all())
        by_status = dict(self.db.query(Client.status, func.count(Client.id)).group_by(Client.status).all())
        by_segment = dict(
            self.db.query(Client.segment, func.count(Client.id))
            .filter(Client.segment.isnot(None))
            .group_by(Client.segment)
            .all()
        )

        total_revenue = self.db.query(func.sum(Client.total_revenue)).scalar() or Decimal("0")
        avg_contracts = 0.0
        if total > 0:
            total_contracts = self.db.query(func.sum(Client.total_contracts)).scalar() or 0
            avg_contracts = total_contracts / total

        return {
            "total_clients": total,
            "active_clients": active,
            "inactive_clients": inactive,
            "defaulter_clients": defaulters,
            "vip_clients": vip,
            "by_type": {k.value if k else "none": v for k, v in by_type.items()},
            "by_status": {k.value if k else "none": v for k, v in by_status.items()},
            "by_segment": {k.value if k else "none": v for k, v in by_segment.items()},
            "total_revenue": total_revenue,
            "average_contracts_per_client": avg_contracts,
        }

    def _get_next_client_sequence(self) -> int:
        """Get next client sequence number."""
        year = datetime.now().year
        pattern = f"CLI-{year}-%"
        max_code = self.db.query(func.max(Client.code)).filter(Client.code.like(pattern)).scalar()
        if max_code:
            try:
                return int(max_code.split("-")[-1]) + 1
            except (ValueError, IndexError):
                pass
        return 1

    # =========================================================================
    # CONDOMINIUM METHODS
    # =========================================================================

    def create_condominium(self, data: CondominiumCreate, created_by: UUID | None = None) -> Condominium:
        """Create a new condominium."""
        client = self.get_client(data.client_id)
        if not client:
            raise ValueError("Client not found")

        sequence = self._get_next_condominium_sequence(client.code)
        code = Condominium.generate_code(client.code, sequence)

        condominium = Condominium(code=code, created_by=created_by, **data.model_dump(exclude_none=True))
        self.db.add(condominium)
        self.db.commit()
        self.db.refresh(condominium)
        logger.info("Condominium created: %s", condominium.code)
        return condominium

    def get_condominium(self, condominium_id: UUID) -> Condominium | None:
        """Get condominium by ID."""
        return self.db.query(Condominium).filter(Condominium.id == condominium_id).first()

    def get_condominium_with_units(self, condominium_id: UUID) -> Condominium | None:
        """Get condominium with units loaded."""
        return (
            self.db.query(Condominium)
            .options(joinedload(Condominium.units))
            .filter(Condominium.id == condominium_id)
            .first()
        )

    def list_condominiums_by_client(
        self, client_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Condominium], int]:
        """List condominiums for a client."""
        query = self.db.query(Condominium).filter(Condominium.client_id == client_id)
        total = query.count()
        condominiums = query.order_by(desc(Condominium.created_at)).offset(skip).limit(limit).all()
        return condominiums, total

    def update_condominium(
        self, condominium_id: UUID, data: CondominiumUpdate, updated_by: UUID | None = None
    ) -> Condominium | None:
        """Update a condominium."""
        condominium = self.get_condominium(condominium_id)
        if not condominium:
            return None

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(condominium, field, value)

        condominium.updated_by = updated_by
        condominium.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(condominium)
        logger.info("Condominium updated: %s", condominium.code)
        return condominium

    def delete_condominium(self, condominium_id: UUID) -> bool:
        """Delete a condominium."""
        condominium = self.get_condominium(condominium_id)
        if not condominium:
            return False

        self.db.delete(condominium)
        self.db.commit()
        logger.info("Condominium deleted: %s", condominium.code)
        return True

    def get_condominium_stats(self, client_id: UUID | None = None) -> dict:
        """Get condominium statistics."""
        query = self.db.query(Condominium)
        if client_id:
            query = query.filter(Condominium.client_id == client_id)

        total = query.count()
        active = query.filter(Condominium.status == CondominiumStatus.ATIVO).count()
        total_units = query.with_entities(func.sum(Condominium.total_units)).scalar() or 0

        by_type = dict(
            query.with_entities(Condominium.type, func.count(Condominium.id)).group_by(Condominium.type).all()
        )
        by_status = dict(
            query.with_entities(Condominium.status, func.count(Condominium.id)).group_by(Condominium.status).all()
        )

        return {
            "total_condominiums": total,
            "active_condominiums": active,
            "total_units": total_units,
            "by_type": {k.value if k else "none": v for k, v in by_type.items()},
            "by_status": {k.value if k else "none": v for k, v in by_status.items()},
        }

    def _get_next_condominium_sequence(self, client_code: str) -> int:
        """Get next condominium sequence for client."""
        pattern = f"{client_code}-COND-%"
        max_code = self.db.query(func.max(Condominium.code)).filter(Condominium.code.like(pattern)).scalar()
        if max_code:
            try:
                return int(max_code.split("-")[-1]) + 1
            except (ValueError, IndexError):
                pass
        return 1

    # =========================================================================
    # UNIT METHODS
    # =========================================================================

    def create_unit(self, data: UnitCreate, created_by: UUID | None = None) -> Unit:
        """Create a new unit."""
        condominium = self.get_condominium(data.condominium_id)
        if not condominium:
            raise ValueError("Condominium not found")

        code = Unit.generate_code(condominium.code, data.block, data.number)

        unit = Unit(code=code, created_by=created_by, **data.model_dump(exclude_none=True))
        self.db.add(unit)
        self.db.commit()
        self.db.refresh(unit)

        # Update condominium unit count
        condominium.update_unit_count(condominium.total_units + 1)
        self.db.commit()

        logger.info("Unit created: %s", unit.code)
        return unit

    def get_unit(self, unit_id: UUID) -> Unit | None:
        """Get unit by ID."""
        return self.db.query(Unit).filter(Unit.id == unit_id).first()

    def list_units_by_condominium(
        self, condominium_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Unit], int]:
        """List units for a condominium."""
        query = self.db.query(Unit).filter(Unit.condominium_id == condominium_id)
        total = query.count()
        units = query.order_by(Unit.block, Unit.number).offset(skip).limit(limit).all()
        return units, total

    def update_unit(self, unit_id: UUID, data: UnitUpdate, updated_by: UUID | None = None) -> Unit | None:
        """Update a unit."""
        unit = self.get_unit(unit_id)
        if not unit:
            return None

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(unit, field, value)

        unit.updated_by = updated_by
        unit.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(unit)
        logger.info("Unit updated: %s", unit.code)
        return unit

    def delete_unit(self, unit_id: UUID) -> bool:
        """Delete a unit."""
        unit = self.get_unit(unit_id)
        if not unit:
            return False

        condominium = unit.condominium
        self.db.delete(unit)
        self.db.commit()

        # Update condominium unit count
        if condominium:
            condominium.update_unit_count(max(0, condominium.total_units - 1))
            self.db.commit()

        logger.info("Unit deleted: %s", unit.code)
        return True

    def get_unit_stats(self, condominium_id: UUID) -> dict:
        """Get unit statistics for a condominium."""
        query = self.db.query(Unit).filter(Unit.condominium_id == condominium_id)

        total = query.count()
        occupied = query.filter(Unit.status.in_([UnitStatus.OCUPADA, UnitStatus.ALUGADA])).count()
        available = query.filter(Unit.status == UnitStatus.DISPONIVEL).count()
        defaulters = query.filter(Unit.is_defaulter.is_(True)).count()

        occupancy_rate = (occupied / total * 100) if total > 0 else 0.0

        total_fees = query.with_entities(func.sum(Unit.monthly_fee)).scalar() or Decimal("0")

        by_type = dict(query.with_entities(Unit.type, func.count(Unit.id)).group_by(Unit.type).all())
        by_status = dict(query.with_entities(Unit.status, func.count(Unit.id)).group_by(Unit.status).all())

        return {
            "total_units": total,
            "occupied_units": occupied,
            "available_units": available,
            "defaulter_units": defaulters,
            "occupancy_rate": occupancy_rate,
            "by_type": {k.value if k else "none": v for k, v in by_type.items()},
            "by_status": {k.value if k else "none": v for k, v in by_status.items()},
            "total_monthly_fees": total_fees,
        }

    # =========================================================================
    # CLIENT CONTRACT METHODS
    # =========================================================================

    def create_client_contract(self, data: ClientContractCreate, created_by: UUID | None = None) -> ClientContract:
        """Create a new client contract."""
        contract = ClientContract(created_by=created_by, **data.model_dump(exclude_none=True))
        contract.calculate_value()
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        logger.info("Client contract created: %s", contract.id)
        return contract

    def get_client_contract(self, contract_id: UUID) -> ClientContract | None:
        """Get client contract by ID."""
        return self.db.query(ClientContract).filter(ClientContract.id == contract_id).first()

    def list_contracts_by_client(
        self, client_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[ClientContract], int]:
        """List contracts for a client."""
        query = self.db.query(ClientContract).filter(ClientContract.client_id == client_id)
        total = query.count()
        contracts = query.order_by(desc(ClientContract.created_at)).offset(skip).limit(limit).all()
        return contracts, total

    def update_client_contract(
        self, contract_id: UUID, data: ClientContractUpdate, updated_by: UUID | None = None
    ) -> ClientContract | None:
        """Update a client contract."""
        contract = self.get_client_contract(contract_id)
        if not contract:
            return None

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(contract, field, value)

        contract.calculate_value()
        contract.updated_by = updated_by
        contract.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(contract)
        logger.info("Client contract updated: %s", contract.id)
        return contract

    # =========================================================================
    # INTEGRATION SETTINGS METHODS
    # =========================================================================

    def create_integration_settings(
        self, data: IntegrationSettingsCreate, created_by: UUID | None = None
    ) -> IntegrationSettings:
        """Create new integration settings."""
        settings = IntegrationSettings(created_by=created_by, **data.model_dump(exclude_none=True))
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        logger.info("Integration settings created: %s", settings.id)
        return settings

    def get_integration_settings(self, settings_id: UUID) -> IntegrationSettings | None:
        """Get integration settings by ID."""
        return self.db.query(IntegrationSettings).filter(IntegrationSettings.id == settings_id).first()

    def list_integration_settings_by_client(self, client_id: UUID) -> list[IntegrationSettings]:
        """List integration settings for a client."""
        return self.db.query(IntegrationSettings).filter(IntegrationSettings.client_id == client_id).all()

    def update_integration_settings(
        self, settings_id: UUID, data: IntegrationSettingsUpdate, updated_by: UUID | None = None
    ) -> IntegrationSettings | None:
        """Update integration settings."""
        settings = self.get_integration_settings(settings_id)
        if not settings:
            return None

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(settings, field, value)

        settings.updated_by = updated_by
        settings.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(settings)
        logger.info("Integration settings updated: %s", settings.id)
        return settings
