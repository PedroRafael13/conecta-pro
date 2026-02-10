"""
Testes unitários para models de Contract.
"""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from modules.crm.models.contract import (
    AddendumType,
    AdjustmentIndex,
    Contract,
    ContractAddendum,
    ContractItem,
    ContractSLAReport,
    ContractStatus,
    ContractTemplate,
    ContractType,
    ServiceType,
)


class TestContractEnums:
    """Testes para enums de Contract."""

    def test_contract_type_values(self):
        """Testa valores do ContractType."""
        assert ContractType.SERVICE.value == "recurring"
        assert ContractType.SERVICE.value == "one_time"

    def test_contract_status_values(self):
        """Testa valores do ContractStatus."""
        assert ContractStatus.DRAFT.value == "draft"
        assert ContractStatus.PENDING_SIGNATURE.value == "pending_signature"
        assert ContractStatus.ACTIVE.value == "active"
        assert ContractStatus.SUSPENDED.value == "suspended"
        assert ContractStatus.DRAFT.value == "cancelled"
        assert ContractStatus.TERMINATED.value == "terminated"

    def test_adjustment_index_values(self):
        """Testa valores do AdjustmentIndex."""
        assert AdjustmentIndex.IGPM.value == "igpm"
        assert AdjustmentIndex.IPCA.value == "ipca"
        assert AdjustmentIndex.INPC.value == "inpc"
        assert AdjustmentIndex.IGPM.value == "fixed"
        assert AdjustmentIndex.CUSTOM.value == "custom"

    def test_addendum_type_values(self):
        """Testa valores do AddendumType."""
        assert AddendumType.ADJUSTMENT.value == "adjustment"
        assert AddendumType.SCOPE_CHANGE.value == "scope_change"
        assert AddendumType.TERM_CHANGE.value == "term_change"
        assert AddendumType.TEAM_CHANGE.value == "team_change"
        assert AddendumType.EQUIPMENT_CHANGE.value == "equipment_change"
        assert AddendumType.OTHER.value == "other"

    def test_service_type_values(self):
        """Testa valores do ServiceType."""
        assert ServiceType.RECORRENTE.value == "security"
        assert ServiceType.RECORRENTE.value == "remote_gatehouse"
        assert ServiceType.RECORRENTE.value == "electronic_security"
        assert ServiceType.RECORRENTE.value == "monitoring_24h"
        assert ServiceType.RECORRENTE.value == "cleaning"
        assert ServiceType.RECORRENTE.value == "gardening"
        assert ServiceType.RECORRENTE.value == "maintenance"
        assert ServiceType.RECORRENTE.value == "facilities"


class TestContractModel:
    """Testes para o modelo Contract."""

    @pytest.fixture
    def contract(self):
        """Fixture para contrato básico."""
        return Contract(
            id=uuid.uuid4(),
            contract_number="CONT-2025-00001",
            client_id=uuid.uuid4(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.DRAFT,
            name="Contrato de Vigilância",
            monthly_value=Decimal("10000.00"),
            total_value=Decimal("120000.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            auto_renewal=True,
            adjustment_enabled=True,
            adjustment_index=AdjustmentIndex.IGPM,
        )

    @pytest.fixture
    def active_contract(self, contract):
        """Fixture para contrato ativo."""
        contract.status = ContractStatus.ACTIVE
        return contract

    def test_generate_number(self):
        """Testa geração de número do contrato."""
        year = date.today().year
        number = Contract.generate_number(1)
        assert number == f"CONT-{year}-00001"

        number = Contract.generate_number(999)
        assert number == f"CONT-{year}-00999"

    def test_is_draft(self, contract):
        """Testa propriedade is_draft."""
        assert contract.is_draft is True
        contract.status = ContractStatus.ACTIVE
        assert contract.is_draft is False

    def test_is_active_contract(self, contract):
        """Testa propriedade is_active_contract."""
        assert contract.is_active_contract is False
        contract.status = ContractStatus.ACTIVE
        assert contract.is_active_contract is True

    def test_is_pending_signature(self, contract):
        """Testa propriedade is_pending_signature."""
        assert contract.is_pending_signature is False
        contract.status = ContractStatus.PENDING_SIGNATURE
        assert contract.is_pending_signature is True

    def test_is_terminated(self, contract):
        """Testa propriedade is_terminated."""
        assert contract.is_terminated is False
        contract.status = ContractStatus.DRAFT
        assert contract.is_terminated is True
        contract.status = ContractStatus.TERMINATED
        assert contract.is_terminated is True

    def test_is_renewable(self, contract):
        """Testa propriedade is_renewable."""
        # Draft não é renovável
        assert contract.is_renewable is False

        # Ativo com auto_renewal é renovável
        contract.status = ContractStatus.ACTIVE
        assert contract.is_renewable is True

        # Sem auto_renewal não é renovável
        contract.auto_renewal = False
        assert contract.is_renewable is False

        # Pontual não é renovável
        contract.auto_renewal = True
        contract.contract_type = ContractType.SERVICE
        assert contract.is_renewable is False

    def test_days_until_end(self, contract):
        """Testa propriedade days_until_end."""
        contract.end_date = date.today() + timedelta(days=30)
        assert contract.days_until_end == 30

        contract.end_date = date.today() + timedelta(days=1)
        assert contract.days_until_end == 1

        contract.end_date = None
        assert contract.days_until_end is None

    def test_is_expiring_soon(self, contract):
        """Testa propriedade is_expiring_soon."""
        contract.end_date = date.today() + timedelta(days=30)
        assert contract.is_expiring_soon is True

        contract.end_date = date.today() + timedelta(days=31)
        assert contract.is_expiring_soon is False

        contract.end_date = date.today() + timedelta(days=1)
        assert contract.is_expiring_soon is True

        contract.end_date = None
        assert contract.is_expiring_soon is False

    def test_is_expired(self, contract):
        """Testa propriedade is_expired."""
        contract.end_date = date.today() + timedelta(days=1)
        assert contract.is_expired is False

        contract.end_date = date.today() - timedelta(days=1)
        assert contract.is_expired is True

        contract.end_date = None
        assert contract.is_expired is False

    def test_needs_adjustment(self, contract):
        """Testa propriedade needs_adjustment."""
        contract.next_adjustment_date = date.today()
        assert contract.needs_adjustment is True

        contract.next_adjustment_date = date.today() - timedelta(days=1)
        assert contract.needs_adjustment is True

        contract.next_adjustment_date = date.today() + timedelta(days=1)
        assert contract.needs_adjustment is False

        contract.adjustment_enabled = False
        contract.next_adjustment_date = date.today()
        assert contract.needs_adjustment is False

    def test_days_until_adjustment(self, contract):
        """Testa propriedade days_until_adjustment."""
        contract.next_adjustment_date = date.today() + timedelta(days=30)
        assert contract.days_until_adjustment == 30

        contract.next_adjustment_date = None
        assert contract.days_until_adjustment is None

    def test_calculate_next_adjustment_date(self, contract):
        """Testa cálculo da próxima data de reajuste."""
        contract.start_date = date(2024, 1, 1)
        contract.adjustment_base_date = date(2024, 1, 1)

        next_date = contract.calculate_next_adjustment_date()
        assert next_date is not None
        assert next_date.month == 1
        assert next_date.day == 1

    def test_calculate_next_adjustment_date_disabled(self, contract):
        """Testa que não calcula reajuste quando desabilitado."""
        contract.adjustment_enabled = False
        next_date = contract.calculate_next_adjustment_date()
        assert next_date is None

    def test_get_sla_indicators(self, contract):
        """Testa obtenção de indicadores SLA."""
        contract.sla_config = {
            "indicators": [
                {"name": "Tempo de Resposta", "target": 95},
                {"name": "Disponibilidade", "target": 99.5},
            ]
        }

        indicators = contract.get_sla_indicators()
        assert len(indicators) == 2
        assert indicators[0]["name"] == "Tempo de Resposta"

    def test_get_sla_indicators_empty(self, contract):
        """Testa indicadores SLA quando vazio."""
        contract.sla_config = None
        assert contract.get_sla_indicators() == []

        contract.sla_config = {}
        assert contract.get_sla_indicators() == []


class TestContractTemplateModel:
    """Testes para o modelo ContractTemplate."""

    @pytest.fixture
    def template(self):
        """Fixture para template básico."""
        return ContractTemplate(
            id=uuid.uuid4(),
            name="Template Vigilância",
            description="Template padrão para contratos de vigilância",
            service_type=ServiceType.RECORRENTE,
            content_template="Contrato de {{client_name}} com valor {{value}}",
            variables=["client_name", "value"],
            version=1,
        )

    def test_render_template(self, template):
        """Testa renderização do template."""
        context = {
            "client_name": "Empresa ABC",
            "value": "R$ 10.000,00",
        }

        rendered = template.render(context)
        assert "Empresa ABC" in rendered
        assert "R$ 10.000,00" in rendered

    def test_render_template_partial(self, template):
        """Testa renderização parcial do template."""
        context = {"client_name": "Empresa ABC"}

        rendered = template.render(context)
        assert "Empresa ABC" in rendered
        assert "{{value}}" in rendered


class TestContractItemModel:
    """Testes para o modelo ContractItem."""

    @pytest.fixture
    def item(self):
        """Fixture para item de contrato."""
        return ContractItem(
            id=uuid.uuid4(),
            contract_id=uuid.uuid4(),
            service_type=ServiceType.RECORRENTE,
            service_name="Vigilância Patrimonial",
            quantity=4,
            unit_price=Decimal("2500.00"),
            total_price=Decimal("10000.00"),
        )

    def test_calculate_total(self, item):
        """Testa cálculo do total."""
        total = item.calculate_total()
        assert total == Decimal("10000.00")

    def test_calculate_total_single(self, item):
        """Testa cálculo do total com quantidade 1."""
        item.quantity = 1
        item.unit_price = Decimal("5000.00")
        total = item.calculate_total()
        assert total == Decimal("5000.00")


class TestContractAddendumModel:
    """Testes para o modelo ContractAddendum."""

    @pytest.fixture
    def addendum(self):
        """Fixture para aditivo."""
        return ContractAddendum(
            id=uuid.uuid4(),
            contract_id=uuid.uuid4(),
            addendum_number="ADI-2025-00001",
            addendum_type=AddendumType.ADJUSTMENT,
            previous_value=Decimal("10000.00"),
            new_value=Decimal("10500.00"),
            adjustment_percent=Decimal("5.00"),
            effective_date=date.today(),
            description="Reajuste anual",
        )

    def test_generate_number(self):
        """Testa geração de número do aditivo."""
        year = date.today().year
        number = ContractAddendum.generate_number(1)
        assert number == f"ADI-{year}-00001"

    def test_is_adjustment(self, addendum):
        """Testa propriedade is_adjustment."""
        assert addendum.is_adjustment is True
        addendum.addendum_type = AddendumType.SCOPE_CHANGE
        assert addendum.is_adjustment is False

    def test_value_difference(self, addendum):
        """Testa cálculo da diferença de valor."""
        diff = addendum.value_difference
        assert diff == Decimal("500.00")

    def test_value_difference_none(self, addendum):
        """Testa diferença de valor quando não há valores."""
        addendum.previous_value = None
        addendum.new_value = None
        assert addendum.value_difference is None


class TestContractSLAReportModel:
    """Testes para o modelo ContractSLAReport."""

    @pytest.fixture
    def report(self):
        """Fixture para relatório SLA."""
        return ContractSLAReport(
            id=uuid.uuid4(),
            contract_id=uuid.uuid4(),
            year=2025,
            month=1,
            indicators=[
                {"name": "Tempo de Resposta", "target": 95, "actual": 97},
                {"name": "Disponibilidade", "target": 99.5, "actual": 99.8},
            ],
            overall_score=Decimal("100.50"),
            penalty_applied=False,
            penalty_percent=Decimal("0"),
            penalty_amount=Decimal("0"),
            status="draft",
        )

    def test_period_label(self, report):
        """Testa label do período."""
        assert report.period_label == "2025-01"

    def test_is_approved(self, report):
        """Testa propriedade is_approved."""
        assert report.is_approved is False
        report.status = "approved"
        assert report.is_approved is True

    def test_is_target_met(self, report):
        """Testa propriedade is_target_met."""
        assert report.is_target_met is True
        report.overall_score = Decimal("95.00")
        assert report.is_target_met is False

    def test_get_indicator_result(self, report):
        """Testa obtenção de resultado de indicador."""
        result = report.get_indicator_result("Tempo de Resposta")
        assert result is not None
        assert result["actual"] == 97

    def test_get_indicator_result_not_found(self, report):
        """Testa indicador não encontrado."""
        result = report.get_indicator_result("Inexistente")
        assert result is None
