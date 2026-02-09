"""Testes para PayrollEvent model."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.hr.payroll_integration.models import (
    DEFAULT_RUBRICAS,
    EventCategory,
    EventStatus,
    EventType,
    PayrollEvent,
)


class TestPayrollEventModel:
    """Testes para o modelo PayrollEvent."""

    def test_create_event_earning(self):
        """Testa criação de evento de provento."""
        event = PayrollEvent(
            id=uuid4(),
            condominio_id=uuid4(),
            period_id=uuid4(),
            employee_id=uuid4(),
            event_code="001",
            event_name="Salário Base",
            event_type=EventType.EARNING.value,
            event_category=EventCategory.SALARY.value,
            value=Decimal("3000.00"),
        )

        assert event.event_code == "001"
        assert event.event_name == "Salário Base"
        assert event.event_type == EventType.EARNING.value
        assert event.event_category == EventCategory.SALARY.value
        assert event.value == Decimal("3000.00")

    def test_create_event_deduction(self):
        """Testa criação de evento de desconto."""
        event = PayrollEvent(
            id=uuid4(),
            condominio_id=uuid4(),
            period_id=uuid4(),
            employee_id=uuid4(),
            event_code="101",
            event_name="INSS",
            event_type=EventType.DEDUCTION.value,
            event_category=EventCategory.INSS.value,
            value=Decimal("330.00"),
            esocial_code="1101",
        )

        assert event.event_code == "101"
        assert event.event_type == EventType.DEDUCTION.value
        assert event.event_category == EventCategory.INSS.value
        assert event.value == Decimal("330.00")
        assert event.esocial_code == "1101"

    def test_event_with_reference(self):
        """Testa evento com referência (horas, dias, etc.)."""
        event = PayrollEvent(
            id=uuid4(),
            condominio_id=uuid4(),
            period_id=uuid4(),
            employee_id=uuid4(),
            event_code="003",
            event_name="Hora Extra 50%",
            event_type=EventType.EARNING.value,
            event_category=EventCategory.OVERTIME_50.value,
            reference=Decimal("10.00"),
            value=Decimal("204.55"),
        )

        assert event.reference == Decimal("10.00")
        assert event.value == Decimal("204.55")

    def test_event_esocial_incidences(self):
        """Testa incidências eSocial do evento."""
        event = PayrollEvent(
            id=uuid4(),
            condominio_id=uuid4(),
            period_id=uuid4(),
            employee_id=uuid4(),
            event_code="001",
            event_name="Salário Base",
            event_type=EventType.EARNING.value,
            event_category=EventCategory.SALARY.value,
            value=Decimal("3000.00"),
            esocial_incidences={"inss": True, "irrf": True, "fgts": True},
        )

        assert event.esocial_incidences["inss"] is True
        assert event.esocial_incidences["irrf"] is True
        assert event.esocial_incidences["fgts"] is True

    def test_event_proportional(self):
        """Testa evento proporcional."""
        event = PayrollEvent(
            id=uuid4(),
            condominio_id=uuid4(),
            period_id=uuid4(),
            employee_id=uuid4(),
            event_code="001",
            event_name="Salário Base",
            event_type=EventType.EARNING.value,
            event_category=EventCategory.SALARY.value,
            value=Decimal("1500.00"),
            is_proportional=True,
            proportional_days=15,
        )

        assert event.is_proportional is True
        assert event.proportional_days == 15

    def test_event_adjustment(self):
        """Testa ajuste de evento."""
        event = PayrollEvent(
            id=uuid4(),
            condominio_id=uuid4(),
            period_id=uuid4(),
            employee_id=uuid4(),
            event_code="001",
            event_name="Salário Base",
            event_type=EventType.EARNING.value,
            event_category=EventCategory.SALARY.value,
            value=Decimal("3500.00"),
            original_value=Decimal("3000.00"),
            adjustment_reason="Reajuste salarial",
            adjusted_by=uuid4(),
            adjusted_at=datetime.utcnow(),
        )

        assert event.value == Decimal("3500.00")
        assert event.original_value == Decimal("3000.00")
        assert event.adjustment_reason == "Reajuste salarial"


class TestEventType:
    """Testes para EventType enum."""

    def test_event_types(self):
        """Testa tipos de evento."""
        assert EventType.EARNING.value == "earning"
        assert EventType.DEDUCTION.value == "deduction"
        assert EventType.INFORMATIVE.value == "informative"
        assert EventType.EMPLOYER.value == "employer"


class TestEventCategory:
    """Testes para EventCategory enum."""

    def test_earning_categories(self):
        """Testa categorias de proventos."""
        assert EventCategory.SALARY.value == "salary"
        assert EventCategory.OVERTIME_50.value == "overtime_50"
        assert EventCategory.OVERTIME_100.value == "overtime_100"
        assert EventCategory.NIGHT_SHIFT.value == "night_shift"
        assert EventCategory.DSR.value == "dsr"
        assert EventCategory.COMMISSION.value == "commission"
        assert EventCategory.BONUS.value == "bonus"
        assert EventCategory.VACATION.value == "vacation"
        assert EventCategory.THIRTEENTH.value == "thirteenth"

    def test_deduction_categories(self):
        """Testa categorias de descontos."""
        assert EventCategory.INSS.value == "inss"
        assert EventCategory.IRRF.value == "irrf"
        assert EventCategory.FGTS.value == "fgts"
        assert EventCategory.TRANSPORT_VOUCHER.value == "transport_voucher"
        assert EventCategory.MEAL_VOUCHER.value == "meal_voucher"
        assert EventCategory.ABSENCE.value == "absence"
        assert EventCategory.LOAN.value == "loan"
        assert EventCategory.ALIMONY.value == "alimony"
        assert EventCategory.UNION_FEE.value == "union_fee"


class TestEventStatus:
    """Testes para EventStatus enum."""

    def test_event_statuses(self):
        """Testa status de evento."""
        assert EventStatus.ACTIVE.value == "active"
        assert EventStatus.CANCELLED.value == "cancelled"
        assert EventStatus.ADJUSTED.value == "adjusted"
        assert EventStatus.PENDING.value == "pending"


class TestDefaultRubricas:
    """Testes para rubricas padrão."""

    def test_default_rubricas_exist(self):
        """Testa existência de rubricas padrão."""
        assert "001" in DEFAULT_RUBRICAS
        assert "003" in DEFAULT_RUBRICAS
        assert "004" in DEFAULT_RUBRICAS
        assert "101" in DEFAULT_RUBRICAS
        assert "102" in DEFAULT_RUBRICAS

    def test_rubrica_structure(self):
        """Testa estrutura da rubrica."""
        rubrica = DEFAULT_RUBRICAS["001"]

        assert "name" in rubrica
        assert "type" in rubrica
        assert "category" in rubrica
        assert "esocial_code" in rubrica
        assert "incidences" in rubrica

        assert rubrica["name"] == "Salário Base"
        assert rubrica["type"] == "earning"
        assert rubrica["category"] == "salary"

    def test_rubrica_incidences(self):
        """Testa incidências das rubricas."""
        # Salário tem todas incidências
        salario = DEFAULT_RUBRICAS["001"]
        assert salario["incidences"]["inss"] is True
        assert salario["incidences"]["irrf"] is True
        assert salario["incidences"]["fgts"] is True

        # Vale transporte não tem incidências
        vt = DEFAULT_RUBRICAS["103"]
        assert vt["incidences"]["inss"] is False
        assert vt["incidences"]["irrf"] is False
        assert vt["incidences"]["fgts"] is False
