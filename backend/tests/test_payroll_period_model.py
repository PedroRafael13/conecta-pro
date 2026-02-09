"""Testes para PayrollPeriod model."""

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.hr.payroll_integration.models import (
    PayrollPeriod,
    PeriodStatus,
    PeriodType,
)


class TestPayrollPeriodModel:
    """Testes para o modelo PayrollPeriod."""

    def test_create_period_monthly(self):
        """Testa criação de período mensal."""
        period = PayrollPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            code="2024-12",
            name="Dezembro 2024",
            period_type=PeriodType.MONTHLY.value,
            status=PeriodStatus.DRAFT.value,
            reference_year=2024,
            reference_month=12,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        assert period.code == "2024-12"
        assert period.reference_year == 2024
        assert period.reference_month == 12
        assert period.period_type == PeriodType.MONTHLY.value
        assert period.status == PeriodStatus.DRAFT.value

    def test_period_is_open(self):
        """Testa propriedade is_open."""
        period = PayrollPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            code="2024-12",
            name="Dezembro 2024",
            period_type=PeriodType.MONTHLY.value,
            status=PeriodStatus.OPEN.value,
            reference_year=2024,
            reference_month=12,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        assert period.is_open is True

        period.status = PeriodStatus.CLOSED.value
        assert period.is_open is False

    def test_period_is_editable(self):
        """Testa propriedade is_editable."""
        period = PayrollPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            code="2024-12",
            name="Dezembro 2024",
            period_type=PeriodType.MONTHLY.value,
            status=PeriodStatus.DRAFT.value,
            reference_year=2024,
            reference_month=12,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        # Draft é editável
        assert period.is_editable is True

        # Open é editável
        period.status = PeriodStatus.OPEN.value
        assert period.is_editable is True

        # Calculated é editável
        period.status = PeriodStatus.CALCULATED.value
        assert period.is_editable is True

        # Closed não é editável
        period.status = PeriodStatus.CLOSED.value
        assert period.is_editable is False

        # Exported não é editável
        period.status = PeriodStatus.EXPORTED.value
        assert period.is_editable is False

    def test_period_can_calculate(self):
        """Testa propriedade can_calculate."""
        period = PayrollPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            code="2024-12",
            name="Dezembro 2024",
            period_type=PeriodType.MONTHLY.value,
            status=PeriodStatus.OPEN.value,
            reference_year=2024,
            reference_month=12,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        # Open pode calcular
        assert period.can_calculate is True

        # Calculated pode recalcular
        period.status = PeriodStatus.CALCULATED.value
        assert period.can_calculate is True

        # Closed não pode calcular
        period.status = PeriodStatus.CLOSED.value
        assert period.can_calculate is False

    def test_period_can_approve(self):
        """Testa propriedade can_approve."""
        period = PayrollPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            code="2024-12",
            name="Dezembro 2024",
            period_type=PeriodType.MONTHLY.value,
            status=PeriodStatus.CALCULATED.value,
            reference_year=2024,
            reference_month=12,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        # Calculated pode aprovar
        assert period.can_approve is True

        # Reviewing pode aprovar
        period.status = PeriodStatus.REVIEWING.value
        assert period.can_approve is True

        # Draft não pode aprovar
        period.status = PeriodStatus.DRAFT.value
        assert period.can_approve is False

    def test_period_can_close(self):
        """Testa propriedade can_close."""
        period = PayrollPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            code="2024-12",
            name="Dezembro 2024",
            period_type=PeriodType.MONTHLY.value,
            status=PeriodStatus.APPROVED.value,
            reference_year=2024,
            reference_month=12,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        # Approved pode fechar
        assert period.can_close is True

        # Calculated não pode fechar
        period.status = PeriodStatus.CALCULATED.value
        assert period.can_close is False

    def test_period_can_export(self):
        """Testa propriedade can_export."""
        period = PayrollPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            code="2024-12",
            name="Dezembro 2024",
            period_type=PeriodType.MONTHLY.value,
            status=PeriodStatus.CLOSED.value,
            reference_year=2024,
            reference_month=12,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        # Closed pode exportar
        assert period.can_export is True

        # Approved pode exportar
        period.status = PeriodStatus.APPROVED.value
        assert period.can_export is True

        # Draft não pode exportar
        period.status = PeriodStatus.DRAFT.value
        assert period.can_export is False

    def test_period_totals(self):
        """Testa totais do período."""
        period = PayrollPeriod(
            id=uuid4(),
            condominio_id=uuid4(),
            code="2024-12",
            name="Dezembro 2024",
            period_type=PeriodType.MONTHLY.value,
            status=PeriodStatus.CALCULATED.value,
            reference_year=2024,
            reference_month=12,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
            total_employees=10,
            total_earnings=Decimal("50000.00"),
            total_deductions=Decimal("10000.00"),
            total_net=Decimal("40000.00"),
            total_employer_cost=Decimal("15000.00"),
        )

        assert period.total_employees == 10
        assert period.total_earnings == Decimal("50000.00")
        assert period.total_deductions == Decimal("10000.00")
        assert period.total_net == Decimal("40000.00")
        assert period.total_employer_cost == Decimal("15000.00")


class TestPeriodType:
    """Testes para PeriodType enum."""

    def test_period_types(self):
        """Testa tipos de período."""
        assert PeriodType.MONTHLY.value == "monthly"
        assert PeriodType.BIWEEKLY.value == "biweekly"
        assert PeriodType.WEEKLY.value == "weekly"
        assert PeriodType.SUPPLEMENTARY.value == "supplementary"
        assert PeriodType.VACATION.value == "vacation"
        assert PeriodType.TERMINATION.value == "termination"
        assert PeriodType.ADVANCE.value == "advance"


class TestPeriodStatus:
    """Testes para PeriodStatus enum."""

    def test_period_statuses(self):
        """Testa status de período."""
        assert PeriodStatus.DRAFT.value == "draft"
        assert PeriodStatus.OPEN.value == "open"
        assert PeriodStatus.CALCULATING.value == "calculating"
        assert PeriodStatus.CALCULATED.value == "calculated"
        assert PeriodStatus.REVIEWING.value == "reviewing"
        assert PeriodStatus.APPROVED.value == "approved"
        assert PeriodStatus.CLOSED.value == "closed"
        assert PeriodStatus.EXPORTED.value == "exported"
        assert PeriodStatus.CANCELLED.value == "cancelled"
