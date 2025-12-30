"""Testes para Lead model."""

from datetime import datetime
from uuid import uuid4

import pytest

from modules.crm.models.lead import Lead, LeadSource, LeadStatus
from tests.factories import LeadFactory


class TestLeadModel:
    """Testes para o modelo Lead."""

    def test_create_lead_basic(self):
        """Testa criação básica de lead."""
        lead = Lead(
            id=str(uuid4()),
            name="Teste",
            email="teste@test.com",
            source=LeadSource.WEBSITE.value,
            status=LeadStatus.NEW.value,
            score=50,
            probability=25.0,
            expected_value=10000.0,
        )

        assert lead.name == "Teste"
        assert lead.email == "teste@test.com"
        assert lead.source == "website"
        assert lead.status == "new"

    def test_lead_with_all_fields(self):
        """Testa lead com todos os campos."""
        lead = LeadFactory.build(
            name="Lead Completo",
            email="completo@test.com",
            phone="11999999999",
            company="Empresa",
            position="Gerente",
            company_size="large",
            industry="condominios",
            source="referral",
            status="qualified",
            score=80,
            probability=60.0,
            expected_value=50000.0,
            notes="Notas importantes",
        )

        assert lead.name == "Lead Completo"
        assert lead.company == "Empresa"
        assert lead.position == "Gerente"
        assert lead.company_size == "large"
        assert lead.industry == "condominios"

    def test_lead_default_values(self):
        """Testa valores padrão."""
        lead = LeadFactory.build()

        assert lead.is_active is True
        assert lead.created_at is not None
        assert lead.updated_at is not None


class TestLeadProperties:
    """Testes para propriedades calculadas do Lead."""

    def test_is_hot_true(self):
        """Testa propriedade is_hot quando score >= 70."""
        lead = LeadFactory.build(score=75)
        assert lead.is_hot is True

        lead = LeadFactory.build(score=70)
        assert lead.is_hot is True

    def test_is_hot_false(self):
        """Testa propriedade is_hot quando score < 70."""
        lead = LeadFactory.build(score=69)
        assert lead.is_hot is False

        lead = LeadFactory.build(score=50)
        assert lead.is_hot is False

    def test_is_qualified_true(self):
        """Testa is_qualified para status qualificado."""
        qualified_statuses = ["qualified", "proposal", "negotiation", "won"]

        for status in qualified_statuses:
            lead = LeadFactory.build(status=status)
            assert lead.is_qualified is True, f"Status {status} should be qualified"

    def test_is_qualified_false(self):
        """Testa is_qualified para status não qualificado."""
        unqualified_statuses = ["new", "contacted", "lost"]

        for status in unqualified_statuses:
            lead = LeadFactory.build(status=status)
            assert lead.is_qualified is False, f"Status {status} should not be qualified"

    def test_weighted_value_calculation(self):
        """Testa cálculo de valor ponderado."""
        lead = LeadFactory.build(expected_value=10000.0, probability=50.0)

        # weighted_value = expected_value * (probability / 100)
        expected = 10000.0 * (50.0 / 100)
        assert lead.weighted_value == expected

    def test_weighted_value_high_probability(self):
        """Testa valor ponderado com alta probabilidade."""
        lead = LeadFactory.build(expected_value=100000.0, probability=80.0)

        expected = 100000.0 * 0.8
        assert lead.weighted_value == expected

    def test_weighted_value_zero_probability(self):
        """Testa valor ponderado com probabilidade zero."""
        lead = LeadFactory.build(expected_value=50000.0, probability=0.0)

        assert lead.weighted_value == 0.0


class TestLeadStatus:
    """Testes para LeadStatus enum."""

    def test_all_statuses_exist(self):
        """Testa que todos os status existem."""
        expected = ["new", "contacted", "qualified", "proposal", "negotiation", "won", "lost"]

        for status in expected:
            assert hasattr(LeadStatus, status.upper())
            assert LeadStatus[status.upper()].value == status

    def test_status_values(self):
        """Testa valores dos status."""
        assert LeadStatus.NEW.value == "new"
        assert LeadStatus.CONTACTED.value == "contacted"
        assert LeadStatus.QUALIFIED.value == "qualified"
        assert LeadStatus.PROPOSAL.value == "proposal"
        assert LeadStatus.NEGOTIATION.value == "negotiation"
        assert LeadStatus.WON.value == "won"
        assert LeadStatus.LOST.value == "lost"


class TestLeadSource:
    """Testes para LeadSource enum."""

    def test_all_sources_exist(self):
        """Testa que todas as fontes existem."""
        expected = [
            "website", "referral", "social_media", "email_campaign",
            "event", "partner", "cold_call", "other"
        ]

        for source in expected:
            assert hasattr(LeadSource, source.upper())
            assert LeadSource[source.upper()].value == source

    def test_source_values(self):
        """Testa valores das fontes."""
        assert LeadSource.WEBSITE.value == "website"
        assert LeadSource.REFERRAL.value == "referral"
        assert LeadSource.SOCIAL_MEDIA.value == "social_media"
        assert LeadSource.EMAIL_CAMPAIGN.value == "email_campaign"
        assert LeadSource.EVENT.value == "event"
        assert LeadSource.PARTNER.value == "partner"
        assert LeadSource.COLD_CALL.value == "cold_call"
        assert LeadSource.OTHER.value == "other"


class TestLeadFactory:
    """Testes para LeadFactory."""

    def test_build_creates_lead(self):
        """Testa que build cria lead válido."""
        lead = LeadFactory.build()

        assert lead.id is not None
        assert lead.name is not None
        assert lead.email is not None

    def test_build_hot_lead(self):
        """Testa criação de lead quente."""
        lead = LeadFactory.build_hot_lead()

        assert lead.score == 85
        assert lead.is_hot is True
        assert lead.status == "qualified"

    def test_build_cold_lead(self):
        """Testa criação de lead frio."""
        lead = LeadFactory.build_cold_lead()

        assert lead.score == 25
        assert lead.is_hot is False
        assert lead.company is None
        assert lead.status == "new"

    def test_build_batch(self):
        """Testa criação de lote de leads."""
        leads = LeadFactory.build_batch(5)

        assert len(leads) == 5
        for lead in leads:
            assert lead.id is not None

    def test_build_with_custom_values(self):
        """Testa criação com valores customizados."""
        lead = LeadFactory.build(
            name="Custom Lead",
            email="custom@test.com",
            score=99,
        )

        assert lead.name == "Custom Lead"
        assert lead.email == "custom@test.com"
        assert lead.score == 99
