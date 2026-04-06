"""
Module: EPIManagement
Description: Sistema de gestao de Equipamentos de Protecao Individual (EPI)
             e Coletiva (EPC) conforme NR-6.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: NR-6 (Portaria MTb 3.214/78) - Equipamentos de Protecao Individual
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()


class EPICategory(StrEnum):
    """Categorias de EPI conforme NR-6 Anexo I."""

    PROTECAO_CABECA = "protecao_cabeca"  # A
    PROTECAO_OLHOS_FACE = "protecao_olhos_face"  # B
    PROTECAO_AUDITIVA = "protecao_auditiva"  # C
    PROTECAO_RESPIRATORIA = "protecao_respiratoria"  # D
    PROTECAO_TRONCO = "protecao_tronco"  # E
    PROTECAO_MEMBROS_SUP = "protecao_membros_sup"  # F
    PROTECAO_MEMBROS_INF = "protecao_membros_inf"  # G
    PROTECAO_CORPO_INTEIRO = "protecao_corpo_inteiro"  # H
    PROTECAO_QUEDAS = "protecao_quedas"  # I


class EPIStatus(StrEnum):
    """Status de um EPI em estoque ou entregue."""

    DISPONIVEL = "disponivel"
    EM_USO = "em_uso"
    DANIFICADO = "danificado"
    VENCIDO = "vencido"
    DESCARTADO = "descartado"
    MANUTENCAO = "manutencao"


class DeliveryStatus(StrEnum):
    """Status de entrega de EPI."""

    ENTREGUE = "entregue"
    DEVOLVIDO = "devolvido"
    EXTRAVIADO = "extraviado"
    SUBSTITUIDO = "substituido"


class EPIManagementError(Exception):
    """Erro em operacao de gestao de EPI."""

    pass


@dataclass
class CACertificate:
    """Certificado de Aprovacao (CA) do Ministerio do Trabalho."""

    number: str  # Numero do CA
    issuer: str  # Orgao emissor
    issue_date: date
    expiry_date: date
    description: str
    approved_for: list[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        """Verifica se CA esta valido."""
        return date.today() <= self.expiry_date

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "issuer": self.issuer,
            "issue_date": self.issue_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat(),
            "description": self.description,
            "approved_for": self.approved_for,
            "is_valid": self.is_valid(),
        }


@dataclass
class EPIModel:
    """Modelo/tipo de EPI cadastrado."""

    id: UUID
    name: str
    category: EPICategory
    manufacturer: str
    model: str
    ca_certificate: CACertificate
    description: str | None = None
    shelf_life_days: int | None = None  # Vida util em dias
    replacement_frequency_days: int | None = None  # Frequencia de troca
    unit_cost: float | None = None
    minimum_stock: int = 0
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "category": self.category.value,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "ca_certificate": self.ca_certificate.to_dict(),
            "description": self.description,
            "shelf_life_days": self.shelf_life_days,
            "replacement_frequency_days": self.replacement_frequency_days,
            "unit_cost": self.unit_cost,
            "minimum_stock": self.minimum_stock,
        }


@dataclass
class EPIInventoryItem:
    """Item de EPI no inventario."""

    id: UUID
    epi_model_id: UUID
    epi_model_name: str
    batch_number: str | None = None
    serial_number: str | None = None
    purchase_date: date | None = None
    manufacture_date: date | None = None
    expiry_date: date | None = None
    status: EPIStatus = EPIStatus.DISPONIVEL
    location: str | None = None
    current_holder_id: str | None = None
    notes: str | None = None

    def is_expired(self) -> bool:
        """Verifica se EPI expirou."""
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "epi_model_id": str(self.epi_model_id),
            "epi_model_name": self.epi_model_name,
            "batch_number": self.batch_number,
            "serial_number": self.serial_number,
            "status": self.status.value,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "is_expired": self.is_expired(),
            "current_holder_id": self.current_holder_id,
        }


@dataclass
class EPIDelivery:
    """Registro de entrega de EPI a funcionario."""

    id: UUID
    employee_id: str
    employee_name: str
    employee_cpf: str
    inventory_item_id: UUID
    epi_model_name: str
    epi_category: EPICategory
    delivery_date: datetime
    delivered_by: str
    status: DeliveryStatus = DeliveryStatus.ENTREGUE
    return_date: datetime | None = None
    return_reason: str | None = None
    replacement_id: UUID | None = None  # Se foi substituido
    training_provided: bool = False
    signature_collected: bool = False
    observations: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "epi_model_name": self.epi_model_name,
            "epi_category": self.epi_category.value,
            "delivery_date": self.delivery_date.isoformat(),
            "status": self.status.value,
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "training_provided": self.training_provided,
            "signature_collected": self.signature_collected,
        }


@dataclass
class EPIRequirement:
    """Requisito de EPI por funcao/risco."""

    function_id: str
    function_name: str
    risk_factor: str
    required_epis: list[UUID]  # IDs dos modelos de EPI
    mandatory: bool = True
    replacement_frequency_days: int | None = None


# SQLAlchemy Models
class EPIModelDBModel(Base):
    """Modelo de banco para tipos de EPI."""

    __tablename__ = "health_epi_models"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    manufacturer = Column(String(255), nullable=False)
    model = Column(String(100), nullable=False)
    ca_number = Column(String(50), nullable=False, index=True)
    ca_expiry_date = Column(Date, nullable=False, index=True)
    ca_data = Column(JSONB, default={})
    description = Column(Text, nullable=True)
    shelf_life_days = Column(Integer, nullable=True)
    replacement_frequency_days = Column(Integer, nullable=True)
    unit_cost = Column(Float, nullable=True)
    minimum_stock = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Modelos canônicos em modules.health_occupational.models.epi:
#   EPIInventory  → health_epi_inventory
#   EPIDelivery   → health_epi_deliveries


class EPIConfig(BaseModel):
    """Configuracao do sistema de EPI."""

    alert_days_before_expiry: int = Field(default=30, ge=7)
    alert_days_before_replacement: int = Field(default=7, ge=1)
    require_training_confirmation: bool = True
    require_signature: bool = True
    low_stock_threshold: int = Field(default=10, ge=1)


class EPIManager:
    """
    Gerenciador de Equipamentos de Protecao Individual.

    Coordena cadastro, inventario, entregas e controle
    de EPIs conforme NR-6.

    Example:
        >>> manager = EPIManager()
        >>> delivery = await manager.deliver_epi(
        ...     employee_id="emp123",
        ...     inventory_item_id=item_id,
        ...     delivered_by="safety_tech"
        ... )
    """

    def __init__(self, config: EPIConfig | None = None):
        """
        Inicializa o gerenciador de EPI.

        Args:
            config: Configuracao do sistema.
        """
        self.config = config or EPIConfig()
        self._models: dict[UUID, EPIModel] = {}
        self._inventory: dict[UUID, EPIInventoryItem] = {}
        self._deliveries: dict[UUID, EPIDelivery] = {}
        self._requirements: list[EPIRequirement] = []
        logger.info("EPIManager inicializado")

    async def register_epi_model(
        self,
        name: str,
        category: EPICategory,
        manufacturer: str,
        model: str,
        ca_number: str,
        ca_issue_date: date,
        ca_expiry_date: date,
        description: str | None = None,
        shelf_life_days: int | None = None,
        replacement_frequency_days: int | None = None,
        unit_cost: float | None = None,
        minimum_stock: int = 0,
    ) -> EPIModel:
        """
        Cadastra modelo de EPI.

        Args:
            name: Nome do EPI.
            category: Categoria NR-6.
            manufacturer: Fabricante.
            model: Modelo.
            ca_number: Numero do CA.
            ca_issue_date: Data emissao CA.
            ca_expiry_date: Data vencimento CA.
            description: Descricao.
            shelf_life_days: Vida util.
            replacement_frequency_days: Frequencia de troca.
            unit_cost: Custo unitario.
            minimum_stock: Estoque minimo.

        Returns:
            EPIModel: Modelo cadastrado.
        """
        ca = CACertificate(
            number=ca_number,
            issuer="MTE",
            issue_date=ca_issue_date,
            expiry_date=ca_expiry_date,
            description=f"CA para {name}",
        )

        epi_model = EPIModel(
            id=uuid4(),
            name=name,
            category=category,
            manufacturer=manufacturer,
            model=model,
            ca_certificate=ca,
            description=description,
            shelf_life_days=shelf_life_days,
            replacement_frequency_days=replacement_frequency_days,
            unit_cost=unit_cost,
            minimum_stock=minimum_stock,
        )

        self._models[epi_model.id] = epi_model

        logger.info("Modelo EPI cadastrado: %s (CA: %s)", name, ca_number)

        return epi_model

    async def add_to_inventory(
        self,
        epi_model_id: UUID,
        quantity: int = 1,
        batch_number: str | None = None,
        manufacture_date: date | None = None,
        expiry_date: date | None = None,
        purchase_date: date | None = None,
        location: str | None = None,
    ) -> list[EPIInventoryItem]:
        """
        Adiciona itens ao inventario.

        Args:
            epi_model_id: ID do modelo.
            quantity: Quantidade.
            batch_number: Numero do lote.
            manufacture_date: Data de fabricacao.
            expiry_date: Data de validade.
            purchase_date: Data de compra.
            location: Local de armazenamento.

        Returns:
            List[EPIInventoryItem]: Itens adicionados.
        """
        model = self._models.get(epi_model_id)
        if not model:
            raise EPIManagementError(f"Modelo EPI nao encontrado: {epi_model_id}")

        items = []
        for _i in range(quantity):
            item = EPIInventoryItem(
                id=uuid4(),
                epi_model_id=epi_model_id,
                epi_model_name=model.name,
                batch_number=batch_number,
                serial_number=f"{batch_number or 'SN'}-{uuid4().hex[:8].upper()}",
                purchase_date=purchase_date or date.today(),
                manufacture_date=manufacture_date,
                expiry_date=expiry_date,
                status=EPIStatus.DISPONIVEL,
                location=location,
            )
            self._inventory[item.id] = item
            items.append(item)

        logger.info("Adicionados %d itens ao inventario: %s", quantity, model.name)

        return items

    async def deliver_epi(
        self,
        employee_id: str,
        employee_name: str,
        employee_cpf: str,
        inventory_item_id: UUID,
        delivered_by: str,
        training_provided: bool = False,
        signature_collected: bool = False,
        observations: str | None = None,
    ) -> EPIDelivery:
        """
        Registra entrega de EPI a funcionario.

        Args:
            employee_id: ID do funcionario.
            employee_name: Nome do funcionario.
            employee_cpf: CPF do funcionario.
            inventory_item_id: ID do item no inventario.
            delivered_by: ID de quem entregou.
            training_provided: Se treinamento foi realizado.
            signature_collected: Se assinatura foi coletada.
            observations: Observacoes.

        Returns:
            EPIDelivery: Registro de entrega.
        """
        item = self._inventory.get(inventory_item_id)
        if not item:
            raise EPIManagementError(f"Item nao encontrado no inventario: {inventory_item_id}")

        if item.status != EPIStatus.DISPONIVEL:
            raise EPIManagementError(f"Item nao disponivel: {item.status.value}")

        if item.is_expired():
            raise EPIManagementError("Nao e possivel entregar EPI vencido")

        model = self._models.get(item.epi_model_id)
        if not model:
            raise EPIManagementError("Modelo EPI nao encontrado")

        # Verifica CA valido
        if not model.ca_certificate.is_valid():
            raise EPIManagementError(f"CA vencido: {model.ca_certificate.number}")

        delivery = EPIDelivery(
            id=uuid4(),
            employee_id=employee_id,
            employee_name=employee_name,
            employee_cpf=employee_cpf,
            inventory_item_id=inventory_item_id,
            epi_model_name=model.name,
            epi_category=model.category,
            delivery_date=datetime.utcnow(),
            delivered_by=delivered_by,
            status=DeliveryStatus.ENTREGUE,
            training_provided=training_provided,
            signature_collected=signature_collected,
            observations=observations,
        )

        # Atualiza status do item
        item.status = EPIStatus.EM_USO
        item.current_holder_id = employee_id

        self._deliveries[delivery.id] = delivery

        logger.info("EPI entregue: employee=%s, item=%s (%s)", employee_id, model.name, item.serial_number)

        return delivery

    async def return_epi(
        self, delivery_id: UUID, return_reason: str, item_status: EPIStatus = EPIStatus.DISPONIVEL
    ) -> EPIDelivery:
        """
        Registra devolucao de EPI.

        Args:
            delivery_id: ID da entrega.
            return_reason: Motivo da devolucao.
            item_status: Status do item devolvido.

        Returns:
            EPIDelivery: Registro atualizado.
        """
        delivery = self._deliveries.get(delivery_id)
        if not delivery:
            raise EPIManagementError(f"Entrega nao encontrada: {delivery_id}")

        if delivery.status != DeliveryStatus.ENTREGUE:
            raise EPIManagementError(f"Entrega nao pode ser devolvida: {delivery.status.value}")

        item = self._inventory.get(delivery.inventory_item_id)
        if item:
            item.status = item_status
            item.current_holder_id = None

        delivery.status = DeliveryStatus.DEVOLVIDO
        delivery.return_date = datetime.utcnow()
        delivery.return_reason = return_reason

        logger.info("EPI devolvido: delivery=%s, reason=%s", delivery_id, return_reason)

        return delivery

    async def replace_epi(
        self, delivery_id: UUID, new_inventory_item_id: UUID, replacement_reason: str, delivered_by: str
    ) -> EPIDelivery:
        """
        Substitui EPI de funcionario.

        Args:
            delivery_id: ID da entrega original.
            new_inventory_item_id: ID do novo item.
            replacement_reason: Motivo da substituicao.
            delivered_by: ID de quem fez a troca.

        Returns:
            EPIDelivery: Nova entrega.
        """
        old_delivery = self._deliveries.get(delivery_id)
        if not old_delivery:
            raise EPIManagementError(f"Entrega nao encontrada: {delivery_id}")

        # Devolve item antigo
        await self.return_epi(delivery_id, replacement_reason, EPIStatus.DANIFICADO)

        # Entrega novo item
        new_delivery = await self.deliver_epi(
            employee_id=old_delivery.employee_id,
            employee_name=old_delivery.employee_name,
            employee_cpf=old_delivery.employee_cpf,
            inventory_item_id=new_inventory_item_id,
            delivered_by=delivered_by,
            training_provided=True,  # Assume treinamento ja feito
            signature_collected=True,
            observations=f"Substituicao de {old_delivery.epi_model_name}. Motivo: {replacement_reason}",
        )

        old_delivery.status = DeliveryStatus.SUBSTITUIDO
        old_delivery.replacement_id = new_delivery.id

        return new_delivery

    async def get_employee_epis(self, employee_id: str, only_active: bool = True) -> list[EPIDelivery]:
        """
        Lista EPIs de um funcionario.

        Args:
            employee_id: ID do funcionario.
            only_active: Se apenas ativos.

        Returns:
            List[EPIDelivery]: Entregas do funcionario.
        """
        deliveries = [d for d in self._deliveries.values() if d.employee_id == employee_id]

        if only_active:
            deliveries = [d for d in deliveries if d.status == DeliveryStatus.ENTREGUE]

        return sorted(deliveries, key=lambda x: x.delivery_date, reverse=True)

    async def get_expiring_items(self, days: int | None = None) -> list[EPIInventoryItem]:
        """Lista itens proximos de vencer."""
        days = days or self.config.alert_days_before_expiry
        cutoff = date.today() + timedelta(days=days)

        return [
            item for item in self._inventory.values() if item.expiry_date and date.today() <= item.expiry_date <= cutoff
        ]

    async def get_expired_items(self) -> list[EPIInventoryItem]:
        """Lista itens vencidos."""
        return [item for item in self._inventory.values() if item.is_expired()]

    async def get_low_stock_models(self) -> list[dict[str, Any]]:
        """Lista modelos com estoque baixo."""
        low_stock = []

        for model in self._models.values():
            available = sum(
                1
                for item in self._inventory.values()
                if item.epi_model_id == model.id and item.status == EPIStatus.DISPONIVEL
            )
            if available <= model.minimum_stock:
                low_stock.append(
                    {
                        "model_id": str(model.id),
                        "model_name": model.name,
                        "minimum_stock": model.minimum_stock,
                        "current_stock": available,
                        "shortage": model.minimum_stock - available,
                    }
                )

        return low_stock

    async def check_employee_compliance(self, employee_id: str, function_id: str) -> dict[str, Any]:
        """
        Verifica compliance de EPI de funcionario.

        Args:
            employee_id: ID do funcionario.
            function_id: ID da funcao.

        Returns:
            Dict: Status de compliance.
        """
        deliveries = await self.get_employee_epis(employee_id, only_active=True)
        delivered_categories = {d.epi_category for d in deliveries}

        # Busca requisitos da funcao
        requirements = [r for r in self._requirements if r.function_id == function_id]

        compliance = {
            "employee_id": employee_id,
            "function_id": function_id,
            "is_compliant": True,
            "delivered_epis": [d.to_dict() for d in deliveries],
            "missing_epis": [],
            "expiring_soon": [],
        }

        # Verifica requisitos
        for req in requirements:
            for model_id in req.required_epis:
                model = self._models.get(model_id)
                if model and model.category not in delivered_categories:
                    compliance["is_compliant"] = False
                    compliance["missing_epis"].append(
                        {
                            "model_name": model.name,
                            "category": model.category.value,
                            "risk_factor": req.risk_factor,
                        }
                    )

        # Verifica vencimentos
        for delivery in deliveries:
            item = self._inventory.get(delivery.inventory_item_id)
            if item and item.expiry_date:
                days_left = (item.expiry_date - date.today()).days
                if days_left <= self.config.alert_days_before_expiry:
                    compliance["expiring_soon"].append(
                        {
                            "epi_name": delivery.epi_model_name,
                            "expiry_date": item.expiry_date.isoformat(),
                            "days_remaining": days_left,
                        }
                    )

        return compliance

    async def generate_delivery_receipt(self, delivery_id: UUID) -> dict[str, Any]:
        """
        Gera ficha de entrega de EPI.

        Args:
            delivery_id: ID da entrega.

        Returns:
            Dict: Dados da ficha de entrega.
        """
        delivery = self._deliveries.get(delivery_id)
        if not delivery:
            raise EPIManagementError(f"Entrega nao encontrada: {delivery_id}")

        item = self._inventory.get(delivery.inventory_item_id)
        model = None
        if item:
            model = self._models.get(item.epi_model_id)

        receipt = {
            "receipt_number": f"EPI-{delivery.id.hex[:8].upper()}",
            "date": delivery.delivery_date.isoformat(),
            "employee": {
                "id": delivery.employee_id,
                "name": delivery.employee_name,
                "cpf": delivery.employee_cpf,
            },
            "epi": {
                "name": delivery.epi_model_name,
                "category": delivery.epi_category.value,
                "serial_number": item.serial_number if item else None,
                "ca_number": model.ca_certificate.number if model else None,
                "ca_valid_until": model.ca_certificate.expiry_date.isoformat() if model else None,
            },
            "delivery": {
                "delivered_by": delivery.delivered_by,
                "training_provided": delivery.training_provided,
                "signature_collected": delivery.signature_collected,
                "observations": delivery.observations,
            },
            "terms": [
                "Recebi o EPI acima especificado em perfeitas condicoes de uso",
                "Comprometo-me a usa-lo adequadamente conforme treinamento recebido",
                "Responsabilizo-me pela guarda e conservacao do equipamento",
                "Comunicarei qualquer dano ou extravio imediatamente",
            ],
        }

        return receipt

    async def get_inventory_summary(self) -> dict[str, Any]:
        """Gera resumo do inventario."""
        summary = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_items": len(self._inventory),
            "by_status": {},
            "by_category": {},
            "expiring_soon": len(await self.get_expiring_items()),
            "expired": len(await self.get_expired_items()),
            "low_stock_models": await self.get_low_stock_models(),
        }

        for item in self._inventory.values():
            # Por status
            status = item.status.value
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

        for model in self._models.values():
            # Por categoria
            cat = model.category.value
            count = sum(1 for item in self._inventory.values() if item.epi_model_id == model.id)
            summary["by_category"][cat] = summary["by_category"].get(cat, 0) + count

        return summary


# Singleton
_epi_manager: EPIManager | None = None


def get_epi_manager() -> EPIManager:
    """Retorna instancia singleton do EPIManager."""
    global _epi_manager
    if _epi_manager is None:
        _epi_manager = EPIManager()
    return _epi_manager


def init_epi_manager(config: EPIConfig | None = None) -> EPIManager:
    """Inicializa o EPIManager singleton."""
    global _epi_manager
    _epi_manager = EPIManager(config)
    return _epi_manager
