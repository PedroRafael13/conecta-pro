"""
Testes unitários para ContractService.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from modules.crm.models.contract import (
    AdjustmentIndex,
    Contract,
    ContractStatus,
    ContractType,
)
from modules.crm.services.contract_service import ContractService


class TestContractService:
    """Testes para ContractService."""

    @pytest.fixture
    def service(self):
        """Fixture para o serviço."""
        return ContractService()

    @pytest.fixture
    def active_contract(self):
        """Fixture para contrato ativo."""
        return Contract(
            id=uuid.uuid4(),
            contract_number="CONT-2025-00001",
            client_id=uuid.uuid4(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            name="Contrato de Vigilância",
            monthly_value=Decimal("10000.00"),
            total_value=Decimal("120000.00"),
            start_date=date.today() - timedelta(days=365),
            end_date=date.today() + timedelta(days=30),
            auto_renewal=True,
            renewal_period_months=12,
            adjustment_enabled=True,
            adjustment_index=AdjustmentIndex.IGPM,
            next_adjustment_date=date.today(),
        )

    @pytest.fixture
    def draft_contract(self):
        """Fixture para contrato em rascunho."""
        return Contract(
            id=uuid.uuid4(),
            contract_number="CONT-2025-00002",
            client_id=uuid.uuid4(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.DRAFT,
            name="Contrato Novo",
            monthly_value=Decimal("5000.00"),
            start_date=date.today(),
            auto_renewal=False,
            adjustment_enabled=False,
        )


class TestCalculateRenewal:
    """Testes para calculate_renewal."""

    @pytest.fixture
    def service(self):
        return ContractService()

    @pytest.fixture
    def active_contract(self):
        return Contract(
            id=uuid.uuid4(),
            contract_number="CONT-2025-00001",
            client_id=uuid.uuid4(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            name="Contrato",
            monthly_value=Decimal("10000.00"),
            start_date=date.today() - timedelta(days=365),
            end_date=date.today() + timedelta(days=30),
            auto_renewal=True,
            renewal_period_months=12,
            adjustment_enabled=True,
            adjustment_index=AdjustmentIndex.IGPM,
            next_adjustment_date=date.today(),
        )

    def test_calculate_renewal_success(self, service, active_contract):
        """Testa renovação bem-sucedida."""
        result = service.calculate_renewal(active_contract)

        assert result.success is True
        assert result.new_end_date is not None
        assert result.new_value is not None
        assert result.message == "Renovação calculada com sucesso"

    def test_calculate_renewal_with_adjustment(self, service, active_contract):
        """Testa renovação com reajuste."""
        result = service.calculate_renewal(active_contract)

        assert result.success is True
        assert result.adjustment_applied is True
        assert result.adjustment_percent is not None
        assert result.new_value > active_contract.monthly_value

    def test_calculate_renewal_custom_adjustment(self, service, active_contract):
        """Testa renovação com reajuste personalizado."""
        result = service.calculate_renewal(
            active_contract,
            custom_adjustment_percent=Decimal("10.00"),
        )

        assert result.success is True
        assert result.adjustment_applied is True
        assert result.adjustment_percent == Decimal("10.00")
        assert result.new_value == Decimal("11000.00")

    def test_calculate_renewal_custom_end_date(self, service, active_contract):
        """Testa renovação com data fim personalizada."""
        custom_date = date.today() + timedelta(days=730)

        result = service.calculate_renewal(
            active_contract,
            new_end_date=custom_date,
        )

        assert result.success is True
        assert result.new_end_date == custom_date

    def test_calculate_renewal_not_renewable(self, service, active_contract):
        """Testa que contrato não renovável falha."""
        active_contract.auto_renewal = False

        result = service.calculate_renewal(active_contract)

        assert result.success is False
        assert "não é elegível" in result.message

    def test_calculate_renewal_not_active(self, service, active_contract):
        """Testa que contrato não ativo falha."""
        active_contract.status = ContractStatus.DRAFT

        result = service.calculate_renewal(active_contract)

        assert result.success is False
        assert "não é elegível" in result.message


class TestCalculateAdjustment:
    """Testes para calculate_adjustment."""

    @pytest.fixture
    def service(self):
        return ContractService()

    @pytest.fixture
    def contract(self):
        return Contract(
            id=uuid.uuid4(),
            contract_number="CONT-2025-00001",
            client_id=uuid.uuid4(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            name="Contrato",
            monthly_value=Decimal("10000.00"),
            start_date=date.today(),
            adjustment_enabled=True,
            adjustment_index=AdjustmentIndex.IGPM,
        )

    def test_calculate_adjustment_igpm(self, service, contract):
        """Testa reajuste pelo IGP-M."""
        result = service.calculate_adjustment(contract)

        assert result.success is True
        assert result.previous_value == Decimal("10000.00")
        assert result.new_value > result.previous_value
        assert result.adjustment_percent == Decimal("4.50")  # IGP-M simulado
        assert result.index_used == AdjustmentIndex.IGPM

    def test_calculate_adjustment_ipca(self, service, contract):
        """Testa reajuste pelo IPCA."""
        contract.adjustment_index = AdjustmentIndex.IPCA

        result = service.calculate_adjustment(contract)

        assert result.success is True
        assert result.adjustment_percent == Decimal("4.23")  # IPCA simulado
        assert result.index_used == AdjustmentIndex.IPCA

    def test_calculate_adjustment_fixed(self, service, contract):
        """Testa reajuste por percentual fixo."""
        contract.adjustment_index = AdjustmentIndex.IGPM
        contract.adjustment_fixed_percent = Decimal("6.00")

        result = service.calculate_adjustment(contract)

        assert result.success is True
        assert result.adjustment_percent == Decimal("6.00")
        assert result.index_used == AdjustmentIndex.IGPM
        assert result.new_value == Decimal("10600.00")

    def test_calculate_adjustment_custom(self, service, contract):
        """Testa reajuste com percentual personalizado."""
        result = service.calculate_adjustment(
            contract,
            custom_percent=Decimal("8.50"),
        )

        assert result.success is True
        assert result.adjustment_percent == Decimal("8.50")
        assert result.index_used == AdjustmentIndex.CUSTOM
        assert result.new_value == Decimal("10850.00")

    def test_calculate_adjustment_disabled(self, service, contract):
        """Testa que reajuste desabilitado falha."""
        contract.adjustment_enabled = False

        result = service.calculate_adjustment(contract)

        assert result.success is False
        assert "não habilitado" in result.message
        assert result.new_value == result.previous_value


class TestCalculateSLA:
    """Testes para calculate_sla."""

    @pytest.fixture
    def service(self):
        return ContractService()

    @pytest.fixture
    def contract_with_sla(self):
        return Contract(
            id=uuid.uuid4(),
            contract_number="CONT-2025-00001",
            client_id=uuid.uuid4(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            name="Contrato com SLA",
            monthly_value=Decimal("10000.00"),
            start_date=date.today(),
            has_sla=True,
            sla_config={
                "indicators": [
                    {"name": "Tempo de Resposta", "target": 95, "weight": 2},
                    {"name": "Disponibilidade", "target": 99.5, "weight": 3},
                ],
                "penalty": {
                    "min_score": 80,
                    "max_penalty_percent": 10,
                },
            },
        )

    def test_calculate_sla_target_met(self, service, contract_with_sla):
        """Testa SLA com metas atingidas."""
        results = [
            {"name": "Tempo de Resposta", "target": 95, "actual": 97, "weight": 2},
            {"name": "Disponibilidade", "target": 99.5, "actual": 99.8, "weight": 3},
        ]

        calculation = service.calculate_sla(contract_with_sla, results)

        assert calculation.target_met is True
        assert calculation.overall_score >= Decimal("100")
        assert calculation.penalty_applicable is False
        assert calculation.penalty_percent == Decimal("0")

    def test_calculate_sla_partial_met(self, service, contract_with_sla):
        """Testa SLA parcialmente atingido."""
        results = [
            {"name": "Tempo de Resposta", "target": 95, "actual": 90, "weight": 2},
            {"name": "Disponibilidade", "target": 99.5, "actual": 99.8, "weight": 3},
        ]

        calculation = service.calculate_sla(contract_with_sla, results)

        assert calculation.target_met is False
        assert calculation.overall_score < Decimal("100")
        assert calculation.penalty_applicable is True

    def test_calculate_sla_penalty(self, service, contract_with_sla):
        """Testa cálculo de penalidade."""
        results = [
            {"name": "Tempo de Resposta", "target": 95, "actual": 70, "weight": 2},
            {"name": "Disponibilidade", "target": 99.5, "actual": 80, "weight": 3},
        ]

        calculation = service.calculate_sla(contract_with_sla, results)

        assert calculation.penalty_applicable is True
        assert calculation.penalty_percent > Decimal("0")
        assert calculation.penalty_amount > Decimal("0")

    def test_calculate_sla_no_sla_config(self, service, contract_with_sla):
        """Testa contrato sem SLA."""
        contract_with_sla.has_sla = False

        calculation = service.calculate_sla(contract_with_sla, [])

        assert calculation.overall_score == Decimal("100")
        assert calculation.target_met is True
        assert calculation.penalty_applicable is False


class TestGetContractAlerts:
    """Testes para get_contract_alerts."""

    @pytest.fixture
    def service(self):
        return ContractService()

    def create_contract(
        self,
        days_until_end: int = 60,
        needs_adjustment: bool = False,
    ):
        """Helper para criar contrato."""
        contract = Contract(
            id=uuid.uuid4(),
            contract_number=f"CONT-2025-{uuid.uuid4().hex[:5]}",
            client_id=uuid.uuid4(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            name="Contrato Teste",
            monthly_value=Decimal("10000.00"),
            start_date=date.today() - timedelta(days=365),
            end_date=date.today() + timedelta(days=days_until_end),
            adjustment_enabled=needs_adjustment,
            next_adjustment_date=date.today() if needs_adjustment else None,
        )
        return contract

    def test_get_alerts_expiring_soon(self, service):
        """Testa alertas de contratos expirando."""
        contracts = [
            self.create_contract(days_until_end=7),
            self.create_contract(days_until_end=15),
            self.create_contract(days_until_end=60),
        ]

        alerts = service.get_contract_alerts(contracts, days_ahead=30)

        assert len(alerts) == 2
        assert alerts[0].severity == "critical"  # 7 dias
        assert alerts[1].severity == "high"  # 15 dias

    def test_get_alerts_expired(self, service):
        """Testa alertas de contratos vencidos."""
        contracts = [
            self.create_contract(days_until_end=-5),  # Vencido
        ]

        alerts = service.get_contract_alerts(contracts)

        assert len(alerts) == 1
        assert alerts[0].alert_type == "expiring"
        assert alerts[0].severity == "critical"
        assert "vencido" in alerts[0].message.lower()

    def test_get_alerts_needs_adjustment(self, service):
        """Testa alertas de reajuste."""
        contracts = [
            self.create_contract(needs_adjustment=True),
        ]

        alerts = service.get_contract_alerts(contracts)

        assert len(alerts) >= 1
        adjustment_alerts = [a for a in alerts if a.alert_type == "needs_adjustment"]
        assert len(adjustment_alerts) == 1

    def test_get_alerts_sorted_by_severity(self, service):
        """Testa ordenação por severidade."""
        contracts = [
            self.create_contract(days_until_end=25),  # medium
            self.create_contract(days_until_end=5),  # critical
            self.create_contract(days_until_end=12),  # high
        ]

        alerts = service.get_contract_alerts(contracts)

        assert alerts[0].severity == "critical"
        assert alerts[1].severity == "high"
        assert alerts[2].severity == "medium"


class TestGenerateContractSummary:
    """Testes para generate_contract_summary."""

    @pytest.fixture
    def service(self):
        return ContractService()

    def create_contract(self, status=ContractStatus.ACTIVE, monthly_value=Decimal("10000")):
        """Helper para criar contrato."""
        return Contract(
            id=uuid.uuid4(),
            contract_number=f"CONT-2025-{uuid.uuid4().hex[:5]}",
            client_id=uuid.uuid4(),
            contract_type=ContractType.SERVICE,
            status=status,
            name="Contrato",
            monthly_value=monthly_value,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
        )

    def test_generate_summary(self, service):
        """Testa geração de resumo."""
        contracts = [
            self.create_contract(ContractStatus.ACTIVE, Decimal("10000")),
            self.create_contract(ContractStatus.ACTIVE, Decimal("20000")),
            self.create_contract(ContractStatus.DRAFT, Decimal("5000")),
        ]

        summary = service.generate_contract_summary(contracts)

        assert summary["total_contracts"] == 3
        assert summary["active_contracts"] == 2
        assert summary["total_monthly_revenue"] == 30000.0
        assert summary["average_contract_value"] == 15000.0

    def test_generate_summary_empty(self, service):
        """Testa resumo com lista vazia."""
        summary = service.generate_contract_summary([])

        assert summary["total_contracts"] == 0
        assert summary["active_contracts"] == 0
        assert summary["total_monthly_revenue"] == 0


class TestGetCurrentEconomicIndex:
    """Testes para get_current_economic_index."""

    @pytest.fixture
    def service(self):
        return ContractService()

    def test_get_igpm(self, service):
        """Testa obtenção do IGP-M."""
        index = service.get_current_economic_index(AdjustmentIndex.IGPM)
        assert index == Decimal("4.50")

    def test_get_ipca(self, service):
        """Testa obtenção do IPCA."""
        index = service.get_current_economic_index(AdjustmentIndex.IPCA)
        assert index == Decimal("4.23")

    def test_get_inpc(self, service):
        """Testa obtenção do INPC."""
        index = service.get_current_economic_index(AdjustmentIndex.INPC)
        assert index == Decimal("4.18")

    def test_get_unknown(self, service):
        """Testa índice desconhecido."""
        index = service.get_current_economic_index(AdjustmentIndex.CUSTOM)
        assert index == Decimal("0")


class TestHelperMethods:
    """Testes para métodos auxiliares."""

    @pytest.fixture
    def service(self):
        return ContractService()

    def test_add_months(self, service):
        """Testa adição de meses."""
        start = date(2025, 1, 15)

        # Adicionar 1 mês
        result = service._add_months(start, 1)
        assert result == date(2025, 2, 15)

        # Adicionar 12 meses
        result = service._add_months(start, 12)
        assert result == date(2026, 1, 15)

    def test_add_months_end_of_month(self, service):
        """Testa adição de meses no fim do mês."""
        start = date(2025, 1, 31)

        # Fevereiro não tem 31 dias
        result = service._add_months(start, 1)
        assert result == date(2025, 2, 28)

    def test_days_in_month(self, service):
        """Testa dias no mês."""
        assert service._days_in_month(2025, 1) == 31
        assert service._days_in_month(2025, 2) == 28
        assert service._days_in_month(2024, 2) == 29  # Ano bissexto
        assert service._days_in_month(2025, 4) == 30
