"""Testes para Opportunity model."""

from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest

from modules.crm.models.opportunity import (
    LossReason,
    Opportunity,
    OpportunityPriority,
    OpportunityStage,
)
from tests.factories import OpportunityFactory


class TestOpportunityModel:
    """Testes para o modelo Opportunity."""

    def test_create_opportunity_basic(self):
        """Testa criacao basica de opportunity."""
        opp = Opportunity(
            id=str(uuid4()),
            title="Teste Opportunity",
            contact_name="Contato",
            contact_email="contato@test.com",
            stage=OpportunityStage.QUALIFICATION.value,
            priority=OpportunityPriority.MEDIUM.value,
            value=10000.0,
            probability=25,
        )

        assert opp.title == "Teste Opportunity"
        assert opp.contact_email == "contato@test.com"
        assert opp.stage == "qualification"
        assert opp.priority == "medium"

    def test_opportunity_with_all_fields(self):
        """Testa opportunity com todos os campos."""
        opp = OpportunityFactory.build(
            title="Opportunity Completa",
            contact_name="Contato Completo",
            contact_email="completo@test.com",
            contact_phone="11999999999",
            company_name="Empresa",
            description="Descricao da opportunity",
            stage="proposal",
            priority="high",
            value=50000.0,
            probability=60,
            notes="Notas importantes",
        )

        assert opp.title == "Opportunity Completa"
        assert opp.company_name == "Empresa"
        assert opp.description == "Descricao da opportunity"
        assert opp.priority == "high"

    def test_opportunity_default_values(self):
        """Testa valores padrao."""
        opp = OpportunityFactory.build()

        assert opp.is_active is True
        assert opp.created_at is not None
        assert opp.updated_at is not None


class TestOpportunityProperties:
    """Testes para propriedades calculadas do Opportunity."""

    def test_weighted_value_calculation(self):
        """Testa calculo de valor ponderado."""
        opp = OpportunityFactory.build(value=10000.0, probability=50)

        # weighted_value = value * (probability / 100)
        expected = 10000.0 * (50 / 100)
        assert opp.weighted_value == expected

    def test_weighted_value_high_probability(self):
        """Testa valor ponderado com alta probabilidade."""
        opp = OpportunityFactory.build(value=100000.0, probability=80)

        expected = 100000.0 * 0.8
        assert opp.weighted_value == expected

    def test_weighted_value_zero_probability(self):
        """Testa valor ponderado com probabilidade zero."""
        opp = OpportunityFactory.build(value=50000.0, probability=0)

        assert opp.weighted_value == 0.0

    def test_is_open_true_for_open_stages(self):
        """Testa is_open para estagios abertos."""
        open_stages = [
            OpportunityStage.QUALIFICATION.value,
            OpportunityStage.NEEDS_ANALYSIS.value,
            OpportunityStage.PROPOSAL.value,
            OpportunityStage.NEGOTIATION.value,
        ]

        for stage in open_stages:
            opp = OpportunityFactory.build(stage=stage)
            assert opp.is_open is True, f"Stage {stage} should be open"

    def test_is_open_false_for_closed_stages(self):
        """Testa is_open para estagios fechados."""
        closed_stages = [
            OpportunityStage.CLOSED_WON.value,
            OpportunityStage.CLOSED_LOST.value,
        ]

        for stage in closed_stages:
            opp = OpportunityFactory.build(stage=stage)
            assert opp.is_open is False, f"Stage {stage} should be closed"

    def test_is_won_true(self):
        """Testa is_won quando ganhou."""
        opp = OpportunityFactory.build(stage="closed_won")
        assert opp.is_won is True

    def test_is_won_false(self):
        """Testa is_won para outros estagios."""
        opp = OpportunityFactory.build(stage="qualification")
        assert opp.is_won is False

        opp = OpportunityFactory.build(stage="closed_lost")
        assert opp.is_won is False

    def test_is_lost_true(self):
        """Testa is_lost quando perdeu."""
        opp = OpportunityFactory.build(stage="closed_lost")
        assert opp.is_lost is True

    def test_is_lost_false(self):
        """Testa is_lost para outros estagios."""
        opp = OpportunityFactory.build(stage="qualification")
        assert opp.is_lost is False

        opp = OpportunityFactory.build(stage="closed_won")
        assert opp.is_lost is False

    def test_days_in_pipeline_open(self):
        """Testa dias no pipeline para opportunity aberta."""
        created = datetime.utcnow() - timedelta(days=10)
        opp = OpportunityFactory.build(stage="qualification", created_at=created)

        # Deve ter aproximadamente 10 dias
        assert opp.days_in_pipeline >= 9
        assert opp.days_in_pipeline <= 11

    def test_days_in_pipeline_closed(self):
        """Testa dias no pipeline para opportunity fechada."""
        created = datetime.utcnow() - timedelta(days=30)
        closed = date.today() - timedelta(days=10)

        opp = OpportunityFactory.build(
            stage="closed_won",
            created_at=created,
            actual_close_date=closed,
        )

        # Deve calcular ate a data de fechamento: 30 - 10 = 20 dias
        assert opp.days_in_pipeline == 20

    def test_is_overdue_true(self):
        """Testa is_overdue quando atrasado."""
        past_date = date.today() - timedelta(days=5)
        opp = OpportunityFactory.build(
            stage="qualification",
            expected_close_date=past_date,
        )

        assert opp.is_overdue is True

    def test_is_overdue_false_future(self):
        """Testa is_overdue com data futura."""
        future_date = date.today() + timedelta(days=30)
        opp = OpportunityFactory.build(
            stage="qualification",
            expected_close_date=future_date,
        )

        assert opp.is_overdue is False

    def test_is_overdue_false_no_date(self):
        """Testa is_overdue sem data prevista."""
        opp = OpportunityFactory.build(
            stage="qualification",
            expected_close_date=None,
        )

        assert opp.is_overdue is False

    def test_is_overdue_false_closed(self):
        """Testa is_overdue para opportunity fechada."""
        past_date = date.today() - timedelta(days=5)
        opp = OpportunityFactory.build(
            stage="closed_won",
            expected_close_date=past_date,
        )

        # Nao esta atrasado pois ja fechou
        assert opp.is_overdue is False


class TestOpportunityStage:
    """Testes para OpportunityStage enum."""

    def test_all_stages_exist(self):
        """Testa que todos os estagios existem."""
        expected = [
            "qualification",
            "needs_analysis",
            "proposal",
            "negotiation",
            "closed_won",
            "closed_lost",
        ]

        for stage in expected:
            assert hasattr(OpportunityStage, stage.upper())
            assert OpportunityStage[stage.upper()].value == stage

    def test_stage_values(self):
        """Testa valores dos estagios."""
        assert OpportunityStage.QUALIFICATION.value == "qualification"
        assert OpportunityStage.NEEDS_ANALYSIS.value == "needs_analysis"
        assert OpportunityStage.PROPOSAL.value == "proposal"
        assert OpportunityStage.NEGOTIATION.value == "negotiation"
        assert OpportunityStage.CLOSED_WON.value == "closed_won"
        assert OpportunityStage.CLOSED_LOST.value == "closed_lost"


class TestOpportunityPriority:
    """Testes para OpportunityPriority enum."""

    def test_all_priorities_exist(self):
        """Testa que todas as prioridades existem."""
        expected = ["low", "medium", "high", "critical"]

        for priority in expected:
            assert hasattr(OpportunityPriority, priority.upper())
            assert OpportunityPriority[priority.upper()].value == priority

    def test_priority_values(self):
        """Testa valores das prioridades."""
        assert OpportunityPriority.LOW.value == "low"
        assert OpportunityPriority.MEDIUM.value == "medium"
        assert OpportunityPriority.HIGH.value == "high"
        assert OpportunityPriority.CRITICAL.value == "critical"


class TestLossReason:
    """Testes para LossReason enum."""

    def test_all_reasons_exist(self):
        """Testa que todos os motivos existem."""
        expected = [
            "price",
            "competitor",
            "no_budget",
            "no_decision",
            "timing",
            "product_fit",
            "no_response",
            "other",
        ]

        for reason in expected:
            assert hasattr(LossReason, reason.upper())
            assert LossReason[reason.upper()].value == reason

    def test_reason_values(self):
        """Testa valores dos motivos."""
        assert LossReason.PRICE.value == "price"
        assert LossReason.COMPETITOR.value == "competitor"
        assert LossReason.NO_BUDGET.value == "no_budget"
        assert LossReason.NO_DECISION.value == "no_decision"


class TestOpportunityFactory:
    """Testes para OpportunityFactory."""

    def test_build_creates_opportunity(self):
        """Testa que build cria opportunity valida."""
        opp = OpportunityFactory.build()

        assert opp.id is not None
        assert opp.title is not None
        assert opp.contact_email is not None

    def test_build_won(self):
        """Testa criacao de opportunity ganha."""
        opp = OpportunityFactory.build_won()

        assert opp.stage == "closed_won"
        assert opp.probability == 100
        assert opp.is_won is True
        assert opp.actual_close_date is not None

    def test_build_lost(self):
        """Testa criacao de opportunity perdida."""
        opp = OpportunityFactory.build_lost()

        assert opp.stage == "closed_lost"
        assert opp.probability == 0
        assert opp.is_lost is True
        assert opp.loss_reason == "price"

    def test_build_high_value(self):
        """Testa criacao de opportunity de alto valor."""
        opp = OpportunityFactory.build_high_value()

        assert opp.value == 100000.0
        assert opp.priority == "high"
        assert opp.stage == "proposal"

    def test_build_batch(self):
        """Testa criacao de lote de opportunities."""
        opps = OpportunityFactory.build_batch(5)

        assert len(opps) == 5
        for opp in opps:
            assert opp.id is not None

    def test_build_with_custom_values(self):
        """Testa criacao com valores customizados."""
        opp = OpportunityFactory.build(
            title="Custom Opportunity",
            contact_email="custom@test.com",
            value=99999.0,
        )

        assert opp.title == "Custom Opportunity"
        assert opp.contact_email == "custom@test.com"
        assert opp.value == 99999.0
