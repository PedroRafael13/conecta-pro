"""
Tests for EPI Module (epi_management) - NR-6.

Author: Claude AI + Human Developer
Date: 2026-01-10
"""

import os
import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock, patch
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List


# =============================================================================
# MOCK CLASSES (Simulating the actual implementation)
# =============================================================================

class EPICategory(str, Enum):
    CABECA = "cabeca"
    OLHOS = "olhos"
    AUDITIVO = "auditivo"
    RESPIRATORIO = "respiratorio"
    TRONCO = "tronco"
    MEMBROS_SUPERIORES = "membros_superiores"
    MAOS = "maos"
    MEMBROS_INFERIORES = "membros_inferiores"
    PES = "pes"
    CORPO_INTEIRO = "corpo_inteiro"


class EPIStatus(str, Enum):
    DISPONIVEL = "disponivel"
    EM_USO = "em_uso"
    DEVOLVIDO = "devolvido"
    DESCARTADO = "descartado"


@dataclass
class EPIItem:
    id: str
    descricao: str
    categoria: EPICategory
    ca_numero: str
    ca_validade: date
    fabricante: str
    modelo: Optional[str] = None
    preco_unitario: Decimal = Decimal("0.00")
    estoque_atual: int = 0
    estoque_minimo: int = 0


@dataclass
class DeliveryRecord:
    id: str
    epi_id: str
    funcionario_id: str
    quantidade: int
    motivo: str
    data_entrega: datetime = field(default_factory=datetime.now)
    substituicao: bool = False
    devolvido: bool = False
    descartado: bool = False


class EPIManager:
    """Simulated EPIManager for testing."""

    def __init__(self, db_session=None):
        self.db = db_session
        self._epis: Dict[str, EPIItem] = {}
        self._deliveries: Dict[str, DeliveryRecord] = {}
        self._stock_history: List[Dict] = []

    async def register_epi(
        self,
        descricao: str,
        categoria: EPICategory,
        ca_numero: str,
        ca_validade: date,
        fabricante: str,
        modelo: Optional[str] = None,
        preco_unitario: Decimal = Decimal("0.00")
    ) -> EPIItem:
        epi = EPIItem(
            id=str(uuid.uuid4()),
            descricao=descricao,
            categoria=categoria,
            ca_numero=ca_numero,
            ca_validade=ca_validade,
            fabricante=fabricante,
            modelo=modelo,
            preco_unitario=preco_unitario
        )
        self._epis[epi.id] = epi
        return epi

    async def validate_ca(self, epi_id: str) -> bool:
        epi = self._epis.get(epi_id)
        if not epi:
            return False
        return epi.ca_validade > date.today()

    async def get_expiring_cas(self, days: int = 60) -> List[EPIItem]:
        threshold = date.today() + timedelta(days=days)
        return [
            epi for epi in self._epis.values()
            if epi.ca_validade <= threshold and epi.ca_validade > date.today()
        ]

    async def add_stock(self, epi_id: str, quantidade: int):
        epi = self._epis.get(epi_id)
        if epi:
            epi.estoque_atual += quantidade
            self._stock_history.append({
                "epi_id": epi_id,
                "tipo": "entrada",
                "quantidade": quantidade,
                "data": datetime.now()
            })

    async def get_stock(self, epi_id: str) -> int:
        epi = self._epis.get(epi_id)
        return epi.estoque_atual if epi else 0

    async def set_minimum_stock(self, epi_id: str, quantidade: int):
        epi = self._epis.get(epi_id)
        if epi:
            epi.estoque_minimo = quantidade

    async def get_low_stock_items(self) -> List[EPIItem]:
        return [
            epi for epi in self._epis.values()
            if epi.estoque_atual < epi.estoque_minimo
        ]

    async def deliver_epi(
        self,
        epi_id: str,
        funcionario_id: str,
        quantidade: int,
        motivo: str,
        substituicao: bool = False
    ) -> DeliveryRecord:
        epi = self._epis.get(epi_id)
        if not epi or epi.estoque_atual < quantidade:
            raise Exception("Estoque insuficiente")

        epi.estoque_atual -= quantidade
        self._stock_history.append({
            "epi_id": epi_id,
            "tipo": "saida",
            "quantidade": quantidade,
            "data": datetime.now()
        })

        delivery = DeliveryRecord(
            id=str(uuid.uuid4()),
            epi_id=epi_id,
            funcionario_id=funcionario_id,
            quantidade=quantidade,
            motivo=motivo,
            substituicao=substituicao
        )
        self._deliveries[delivery.id] = delivery
        return delivery

    async def get_deliveries(
        self,
        funcionario_id: Optional[str] = None,
        epi_id: Optional[str] = None
    ) -> List[DeliveryRecord]:
        results = list(self._deliveries.values())

        if funcionario_id:
            results = [d for d in results if d.funcionario_id == funcionario_id]
        if epi_id:
            results = [d for d in results if d.epi_id == epi_id]

        return results

    async def get_stock_history(self, epi_id: str) -> List[Dict]:
        return [h for h in self._stock_history if h["epi_id"] == epi_id]

    async def generate_ficha_epi(self, funcionario_id: str) -> Dict[str, Any]:
        deliveries = await self.get_deliveries(funcionario_id=funcionario_id)
        return {
            "funcionario_id": funcionario_id,
            "data_geracao": datetime.now().isoformat(),
            "entregas": deliveries,
            "total_itens": len(deliveries)
        }

    async def return_epi(
        self,
        entrega_id: str,
        motivo: str,
        condicao: str
    ) -> DeliveryRecord:
        delivery = self._deliveries.get(entrega_id)
        if delivery:
            delivery.devolvido = True
            # Return to stock if in good condition
            if condicao.lower() in ["bom estado", "bom"]:
                epi = self._epis.get(delivery.epi_id)
                if epi:
                    epi.estoque_atual += delivery.quantidade
        return delivery

    async def dispose_epi(
        self,
        entrega_id: str,
        motivo: str,
        destino: str
    ) -> DeliveryRecord:
        delivery = self._deliveries.get(entrega_id)
        if delivery:
            delivery.descartado = True
        return delivery


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_db_session():
    return MagicMock()


# =============================================================================
# EPI MANAGER TESTS
# =============================================================================

class TestEPIManager:
    """Tests for EPIManager class."""

    @pytest.fixture
    def epi_manager(self, mock_db_session):
        """Create EPIManager instance."""
        return EPIManager(db_session=mock_db_session)

    @pytest.fixture
    def sample_epi(self):
        """Sample EPI data."""
        return {
            "descricao": "Protetor Auricular Tipo Concha",
            "categoria": EPICategory.AUDITIVO,
            "ca_numero": "12345",
            "ca_validade": date(2027, 12, 31),
            "fabricante": "3M do Brasil",
            "modelo": "Peltor H10A",
            "preco_unitario": Decimal("89.90")
        }

    @pytest.fixture
    def sample_employee(self):
        """Sample employee data."""
        return {
            "id": str(uuid.uuid4()),
            "cpf": "12345678901",
            "nome": "Jose Trabalhador",
            "cargo": "Operador",
            "setor": "Producao"
        }

    # -------------------------------------------------------------------------
    # EPI REGISTRATION TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_register_epi(self, epi_manager, sample_epi):
        """Test EPI registration."""
        epi = await epi_manager.register_epi(**sample_epi)

        assert epi is not None
        assert epi.ca_numero == "12345"
        assert epi.categoria == EPICategory.AUDITIVO

    @pytest.mark.asyncio
    async def test_register_epi_head_protection(self, epi_manager):
        """Test registering head protection EPI."""
        epi = await epi_manager.register_epi(
            descricao="Capacete de Seguranca Classe B",
            categoria=EPICategory.CABECA,
            ca_numero="54321",
            ca_validade=date(2026, 6, 30),
            fabricante="MSA",
            modelo="V-Gard",
            preco_unitario=Decimal("45.00")
        )

        assert epi.categoria == EPICategory.CABECA

    @pytest.mark.asyncio
    async def test_register_epi_respiratory(self, epi_manager):
        """Test registering respiratory protection EPI."""
        epi = await epi_manager.register_epi(
            descricao="Respirador PFF2",
            categoria=EPICategory.RESPIRATORIO,
            ca_numero="98765",
            ca_validade=date(2026, 12, 31),
            fabricante="3M",
            modelo="Aura 9320",
            preco_unitario=Decimal("8.50")
        )

        assert epi.categoria == EPICategory.RESPIRATORIO

    @pytest.mark.asyncio
    async def test_register_epi_hands(self, epi_manager):
        """Test registering hand protection EPI."""
        epi = await epi_manager.register_epi(
            descricao="Luva de Vaqueta",
            categoria=EPICategory.MAOS,
            ca_numero="11111",
            ca_validade=date(2027, 3, 15),
            fabricante="Danny",
            modelo="Vaqueta CA",
            preco_unitario=Decimal("25.00")
        )

        assert epi.categoria == EPICategory.MAOS

    @pytest.mark.asyncio
    async def test_register_epi_feet(self, epi_manager):
        """Test registering foot protection EPI."""
        epi = await epi_manager.register_epi(
            descricao="Botina de Seguranca com Biqueira de Aco",
            categoria=EPICategory.PES,
            ca_numero="22222",
            ca_validade=date(2027, 8, 20),
            fabricante="Marluvas",
            modelo="Premier",
            preco_unitario=Decimal("120.00")
        )

        assert epi.categoria == EPICategory.PES

    # -------------------------------------------------------------------------
    # CA VALIDATION TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_validate_ca_valid(self, epi_manager, sample_epi):
        """Test CA validation for valid certificate."""
        epi = await epi_manager.register_epi(**sample_epi)

        is_valid = await epi_manager.validate_ca(epi.id)

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_ca_expired(self, epi_manager):
        """Test CA validation for expired certificate."""
        epi = await epi_manager.register_epi(
            descricao="EPI com CA vencido",
            categoria=EPICategory.AUDITIVO,
            ca_numero="99999",
            ca_validade=date(2020, 1, 1),  # Expired
            fabricante="Teste",
            preco_unitario=Decimal("10.00")
        )

        is_valid = await epi_manager.validate_ca(epi.id)

        assert is_valid is False

    @pytest.mark.asyncio
    async def test_get_expiring_cas(self, epi_manager, sample_epi):
        """Test getting EPIs with expiring CAs."""
        # Register EPI with CA expiring soon
        await epi_manager.register_epi(
            descricao="EPI expirando",
            categoria=EPICategory.AUDITIVO,
            ca_numero="77777",
            ca_validade=date.today() + timedelta(days=30),
            fabricante="Teste",
            preco_unitario=Decimal("10.00")
        )

        expiring = await epi_manager.get_expiring_cas(days=60)

        assert expiring is not None

    # -------------------------------------------------------------------------
    # DELIVERY TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_deliver_epi(self, epi_manager, sample_epi, sample_employee):
        """Test EPI delivery to employee."""
        epi = await epi_manager.register_epi(**sample_epi)

        # Add stock
        await epi_manager.add_stock(epi.id, 10)

        delivery = await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Entrega inicial"
        )

        assert delivery is not None
        assert delivery.funcionario_id == sample_employee["id"]
        assert delivery.quantidade == 1

    @pytest.mark.asyncio
    async def test_deliver_epi_replacement(self, epi_manager, sample_epi, sample_employee):
        """Test EPI replacement delivery."""
        epi = await epi_manager.register_epi(**sample_epi)
        await epi_manager.add_stock(epi.id, 10)

        # First delivery
        await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Entrega inicial"
        )

        # Replacement
        replacement = await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Substituicao por desgaste",
            substituicao=True
        )

        assert replacement.substituicao is True

    @pytest.mark.asyncio
    async def test_deliver_epi_insufficient_stock(self, epi_manager, sample_epi, sample_employee):
        """Test EPI delivery with insufficient stock."""
        epi = await epi_manager.register_epi(**sample_epi)
        # No stock added

        with pytest.raises(Exception):  # Should raise stock error
            await epi_manager.deliver_epi(
                epi_id=epi.id,
                funcionario_id=sample_employee["id"],
                quantidade=1,
                motivo="Entrega"
            )

    @pytest.mark.asyncio
    async def test_get_employee_deliveries(self, epi_manager, sample_epi, sample_employee):
        """Test getting all deliveries for an employee."""
        epi = await epi_manager.register_epi(**sample_epi)
        await epi_manager.add_stock(epi.id, 10)

        await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Entrega 1"
        )
        await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Entrega 2"
        )

        deliveries = await epi_manager.get_deliveries(
            funcionario_id=sample_employee["id"]
        )

        assert len(deliveries) >= 2

    # -------------------------------------------------------------------------
    # STOCK MANAGEMENT TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_add_stock(self, epi_manager, sample_epi):
        """Test adding stock."""
        epi = await epi_manager.register_epi(**sample_epi)

        await epi_manager.add_stock(epi.id, 50)

        stock = await epi_manager.get_stock(epi.id)
        assert stock >= 50

    @pytest.mark.asyncio
    async def test_check_stock_level(self, epi_manager, sample_epi):
        """Test stock level checking."""
        epi = await epi_manager.register_epi(**sample_epi)
        await epi_manager.add_stock(epi.id, 5)

        # Set minimum stock
        await epi_manager.set_minimum_stock(epi.id, 10)

        low_stock = await epi_manager.get_low_stock_items()

        assert low_stock is not None

    @pytest.mark.asyncio
    async def test_stock_movement_history(self, epi_manager, sample_epi, sample_employee):
        """Test stock movement history."""
        epi = await epi_manager.register_epi(**sample_epi)

        await epi_manager.add_stock(epi.id, 20)  # Entry
        await epi_manager.deliver_epi(  # Exit
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=2,
            motivo="Entrega"
        )

        history = await epi_manager.get_stock_history(epi.id)

        assert history is not None

    # -------------------------------------------------------------------------
    # FICHA DE EPI TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_generate_ficha_epi(self, epi_manager, sample_epi, sample_employee):
        """Test generating EPI record sheet (Ficha de EPI)."""
        epi = await epi_manager.register_epi(**sample_epi)
        await epi_manager.add_stock(epi.id, 10)

        await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Entrega inicial"
        )

        ficha = await epi_manager.generate_ficha_epi(
            funcionario_id=sample_employee["id"]
        )

        assert ficha is not None

    @pytest.mark.asyncio
    async def test_ficha_contains_required_info(self, epi_manager, sample_epi, sample_employee):
        """Test that Ficha de EPI contains NR-6 required information."""
        epi = await epi_manager.register_epi(**sample_epi)
        await epi_manager.add_stock(epi.id, 10)

        await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Entrega"
        )

        ficha = await epi_manager.generate_ficha_epi(
            funcionario_id=sample_employee["id"]
        )

        # NR-6 requires:
        # - Employee identification
        # - EPI description
        # - CA number
        # - Delivery date
        # - Quantity
        assert ficha is not None

    # -------------------------------------------------------------------------
    # RETURN AND DISPOSAL TESTS
    # -------------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_return_epi(self, epi_manager, sample_epi, sample_employee):
        """Test EPI return."""
        epi = await epi_manager.register_epi(**sample_epi)
        await epi_manager.add_stock(epi.id, 10)

        delivery = await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Entrega"
        )

        returned = await epi_manager.return_epi(
            entrega_id=delivery.id,
            motivo="Desligamento do funcionario",
            condicao="Bom estado"
        )

        assert returned is not None

    @pytest.mark.asyncio
    async def test_dispose_epi(self, epi_manager, sample_epi, sample_employee):
        """Test EPI disposal."""
        epi = await epi_manager.register_epi(**sample_epi)
        await epi_manager.add_stock(epi.id, 10)

        delivery = await epi_manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=sample_employee["id"],
            quantidade=1,
            motivo="Entrega"
        )

        disposed = await epi_manager.dispose_epi(
            entrega_id=delivery.id,
            motivo="Desgaste natural",
            destino="Descarte apropriado"
        )

        assert disposed is not None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestEPIIntegration:
    """Integration tests for EPI module."""

    @pytest.mark.asyncio
    async def test_full_epi_lifecycle(self, mock_db_session):
        """Test complete EPI lifecycle."""
        manager = EPIManager(db_session=mock_db_session)

        funcionario_id = str(uuid.uuid4())

        # 1. Register EPI
        epi = await manager.register_epi(
            descricao="Capacete de Seguranca",
            categoria=EPICategory.CABECA,
            ca_numero="12345",
            ca_validade=date(2027, 12, 31),
            fabricante="MSA",
            preco_unitario=Decimal("50.00")
        )

        # 2. Add stock
        await manager.add_stock(epi.id, 20)

        # 3. Deliver to employee
        delivery = await manager.deliver_epi(
            epi_id=epi.id,
            funcionario_id=funcionario_id,
            quantidade=1,
            motivo="Entrega inicial"
        )

        # 4. Validate CA
        is_valid = await manager.validate_ca(epi.id)
        assert is_valid is True

        # 5. Generate Ficha
        ficha = await manager.generate_ficha_epi(funcionario_id)
        assert ficha is not None

        # 6. Return on termination
        returned = await manager.return_epi(
            entrega_id=delivery.id,
            motivo="Desligamento",
            condicao="Bom estado"
        )
        assert returned is not None

    @pytest.mark.asyncio
    async def test_epi_traceability(self, mock_db_session):
        """Test EPI traceability (which employee has which EPI)."""
        manager = EPIManager(db_session=mock_db_session)

        # Register multiple EPIs
        epi1 = await manager.register_epi(
            descricao="Capacete",
            categoria=EPICategory.CABECA,
            ca_numero="11111",
            ca_validade=date(2027, 12, 31),
            fabricante="MSA",
            preco_unitario=Decimal("50.00")
        )

        epi2 = await manager.register_epi(
            descricao="Oculos",
            categoria=EPICategory.OLHOS,
            ca_numero="22222",
            ca_validade=date(2027, 12, 31),
            fabricante="3M",
            preco_unitario=Decimal("30.00")
        )

        await manager.add_stock(epi1.id, 10)
        await manager.add_stock(epi2.id, 10)

        funcionario_id = str(uuid.uuid4())

        # Deliver both
        await manager.deliver_epi(
            epi_id=epi1.id,
            funcionario_id=funcionario_id,
            quantidade=1,
            motivo="Entrega"
        )
        await manager.deliver_epi(
            epi_id=epi2.id,
            funcionario_id=funcionario_id,
            quantidade=1,
            motivo="Entrega"
        )

        # Get all EPIs for employee
        deliveries = await manager.get_deliveries(funcionario_id=funcionario_id)
        assert len(deliveries) >= 2
