"""Testes para LeadService e LeadScoringEngine."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from modules.crm.models.lead import LeadSource, LeadStatus
from modules.crm.services.lead_service import LeadScoringEngine, LeadService, lead_service
from tests.factories import LeadFactory


class TestLeadScoringEngine:
    """Testes para o motor de scoring de leads."""

    def setup_method(self):
        """Setup para cada teste."""
        self.engine = LeadScoringEngine()

    def test_calculate_score_complete_lead(self):
        """Testa scoring de lead com dados completos."""
        lead = LeadFactory.build(
            company="Empresa Grande",
            company_size="enterprise",
            industry="condominios",
            source="referral",
            status="qualified",
        )

        score, probability = self.engine.calculate_score(lead)

        assert score >= 70
        assert probability >= 40.0

    def test_calculate_score_minimal_lead(self):
        """Testa scoring de lead com dados mínimos."""
        from datetime import datetime
        from modules.crm.models.lead import Lead

        # Criar lead diretamente com dados mínimos
        lead = Lead(
            id="test-minimal",
            name="Minimal",
            email="min@test.com",
            phone=None,
            company=None,
            position=None,
            company_size=None,
            industry=None,
            source="cold_call",
            status="new",
            score=0,
            probability=0.0,
            expected_value=0.0,
            notes=None,
            created_at=datetime.now(),
        )

        score, probability = self.engine.calculate_score(lead)

        # Com cold_call (40) e new (30), score será baixo
        assert score < 60
        assert probability < 30.0

    def test_score_completeness_all_fields(self):
        """Testa pontuação de completude com todos os campos."""
        lead = LeadFactory.build(
            name="Teste",
            email="test@test.com",
            phone="11999999999",
            company="Empresa",
            position="Gerente",
            company_size="medium",
            industry="condominios",
            notes="Nota",
        )

        score = self.engine._score_completeness(lead)

        # Soma: 15+15+15+20+10+10+10+5 = 100
        assert score == 100

    def test_score_completeness_partial(self):
        """Testa pontuação de completude parcial."""
        from modules.crm.models.lead import Lead

        # Criar lead diretamente para controle total
        lead = Lead(
            id="test-partial",
            name="Teste",
            email="test@test.com",
            phone=None,
            company=None,
            position=None,
            company_size=None,
            industry=None,
            source="website",
            status="new",
            score=0,
            probability=0.0,
            expected_value=0.0,
            notes=None,
        )

        score = self.engine._score_completeness(lead)

        # Apenas name (15) + email (15) = 30
        assert score == 30

    def test_score_source_referral(self):
        """Testa que referral tem score máximo."""
        lead = LeadFactory.build(source="referral")
        score = self.engine._score_source(lead)
        assert score == 100

    def test_score_source_cold_call(self):
        """Testa que cold call tem score baixo."""
        lead = LeadFactory.build(source="cold_call")
        score = self.engine._score_source(lead)
        assert score == 40

    def test_score_company_size_enterprise(self):
        """Testa pontuação para empresa enterprise."""
        lead = LeadFactory.build(company_size="enterprise")
        score = self.engine._score_company_size(lead)
        assert score == 100

    def test_score_company_size_micro(self):
        """Testa pontuação para micro empresa."""
        lead = LeadFactory.build(company_size="micro")
        score = self.engine._score_company_size(lead)
        assert score == 40

    def test_score_company_size_unknown(self):
        """Testa pontuação neutra para tamanho desconhecido."""
        from modules.crm.models.lead import Lead

        lead = Lead(
            id="test-no-size",
            name="Test",
            email="test@test.com",
            company_size=None,
            source="website",
            status="new",
            score=0,
            probability=0.0,
            expected_value=0.0,
        )
        score = self.engine._score_company_size(lead)
        assert score == 50

    def test_score_industry_priority(self):
        """Testa pontuação para setor prioritário."""
        lead = LeadFactory.build(industry="condominios")
        score = self.engine._score_industry(lead)
        assert score == 100

    def test_score_industry_partial_match(self):
        """Testa match parcial de setor."""
        # O match é case-insensitive (lower())
        lead = LeadFactory.build(industry="seguranca patrimonial")
        score = self.engine._score_industry(lead)
        assert score == 90

    def test_score_industry_unknown(self):
        """Testa pontuação neutra para setor desconhecido."""
        lead = LeadFactory.build(industry="varejo")
        score = self.engine._score_industry(lead)
        assert score == 50

    def test_score_engagement_won(self):
        """Testa pontuação máxima para lead ganho."""
        lead = LeadFactory.build(status="won")
        score = self.engine._score_engagement(lead)
        assert score == 100

    def test_score_engagement_lost(self):
        """Testa pontuação zero para lead perdido."""
        lead = LeadFactory.build(status="lost")
        score = self.engine._score_engagement(lead)
        assert score == 0

    def test_score_response_time_recent(self):
        """Testa pontuação para contato recente."""
        lead = LeadFactory.build(last_contact_at=datetime.now())
        score = self.engine._score_response_time(lead)
        assert score == 100

    def test_score_response_time_old(self):
        """Testa pontuação para contato antigo."""
        lead = LeadFactory.build(last_contact_at=datetime.now() - timedelta(days=60))
        score = self.engine._score_response_time(lead)
        assert score == 10

    def test_score_response_time_new_lead(self):
        """Testa pontuação para lead novo sem contato."""
        lead = LeadFactory.build(
            last_contact_at=None,
            created_at=datetime.now(),
        )
        score = self.engine._score_response_time(lead)
        assert score == 100

    def test_probability_calculation_won(self):
        """Testa probabilidade máxima para lead ganho."""
        probability = self.engine._calculate_probability(100, "won")
        assert probability == 100.0

    def test_probability_calculation_lost(self):
        """Testa probabilidade zero para lead perdido."""
        probability = self.engine._calculate_probability(80, "lost")
        assert probability == 0.0

    def test_probability_calculation_new(self):
        """Testa probabilidade para lead novo."""
        probability = self.engine._calculate_probability(50, "new")
        # 50 * 0.6 * 0.5 = 15
        assert probability == 15.0

    def test_score_bounds(self):
        """Testa que score está entre 0 e 100."""
        # Lead com score muito alto
        high_lead = LeadFactory.build(
            company_size="enterprise",
            industry="condominios",
            source="referral",
            status="won",
        )
        score, _ = self.engine.calculate_score(high_lead)
        assert 0 <= score <= 100

        # Lead com score muito baixo
        low_lead = LeadFactory.build(
            company_size="micro",
            industry="varejo",
            source="cold_call",
            status="lost",
            company=None,
        )
        score, _ = self.engine.calculate_score(low_lead)
        assert 0 <= score <= 100


class TestLeadService:
    """Testes para LeadService."""

    def setup_method(self):
        """Setup para cada teste."""
        self.service = LeadService()

    def test_calculate_score_delegates_to_engine(self):
        """Testa que calculate_score delega para o engine."""
        lead = LeadFactory.build()
        score, probability = self.service.calculate_score(lead)

        assert isinstance(score, int)
        assert isinstance(probability, float)

    def test_get_recommended_action_lost(self):
        """Testa ação para lead perdido."""
        lead = LeadFactory.build(status="lost")
        action = self.service.get_recommended_action(lead)

        assert "Arquivar" in action or "reengajamento" in action

    def test_get_recommended_action_won(self):
        """Testa ação para lead ganho."""
        lead = LeadFactory.build(status="won")
        action = self.service.get_recommended_action(lead)

        assert "onboarding" in action

    def test_get_recommended_action_hot_new(self):
        """Testa ação para lead quente novo."""
        lead = LeadFactory.build(score=85, status="new")
        action = self.service.get_recommended_action(lead)

        assert "imediato" in action or "quente" in action

    def test_get_recommended_action_hot_qualified(self):
        """Testa ação para lead quente qualificado."""
        lead = LeadFactory.build(score=85, status="qualified")
        action = self.service.get_recommended_action(lead)

        assert "proposta" in action

    def test_get_recommended_action_medium_no_contact(self):
        """Testa ação para lead médio sem contato."""
        lead = LeadFactory.build(score=60, last_contact_at=None)
        action = self.service.get_recommended_action(lead)

        assert "primeiro contato" in action

    def test_get_recommended_action_medium_needs_followup(self):
        """Testa ação para lead médio precisando follow-up."""
        lead = LeadFactory.build(
            score=60,
            last_contact_at=datetime.now() - timedelta(days=10),
        )
        action = self.service.get_recommended_action(lead)

        assert "follow-up" in action

    def test_get_recommended_action_cold_no_company(self):
        """Testa ação para lead frio sem empresa."""
        from modules.crm.models.lead import Lead

        lead = Lead(
            id="test-cold",
            name="Cold Lead",
            email="cold@test.com",
            company=None,
            source="cold_call",
            status="new",
            score=30,
            probability=10.0,
            expected_value=0.0,
        )
        action = self.service.get_recommended_action(lead)

        assert "Qualificar" in action

    def test_get_recommended_action_cold_with_company(self):
        """Testa ação para lead frio com empresa."""
        lead = LeadFactory.build(score=30, company="Empresa")
        action = self.service.get_recommended_action(lead)

        assert "Nutrir" in action

    def test_get_next_contact_date_won(self):
        """Testa que lead ganho não tem próximo contato."""
        lead = LeadFactory.build(status="won")
        next_date = self.service.get_next_contact_date(lead)

        assert next_date is None

    def test_get_next_contact_date_lost(self):
        """Testa que lead perdido não tem próximo contato."""
        lead = LeadFactory.build(status="lost")
        next_date = self.service.get_next_contact_date(lead)

        assert next_date is None

    def test_get_next_contact_date_hot(self):
        """Testa próximo contato para lead quente (1 dia)."""
        lead = LeadFactory.build(score=85)
        next_date = self.service.get_next_contact_date(lead)

        assert next_date is not None
        delta = next_date - datetime.now()
        assert delta.days <= 1

    def test_get_next_contact_date_medium(self):
        """Testa próximo contato para lead médio (3 dias)."""
        lead = LeadFactory.build(score=60)
        next_date = self.service.get_next_contact_date(lead)

        assert next_date is not None
        delta = next_date - datetime.now()
        assert 2 <= delta.days <= 4

    def test_get_next_contact_date_cold(self):
        """Testa próximo contato para lead frio (7 dias)."""
        lead = LeadFactory.build(score=30)
        next_date = self.service.get_next_contact_date(lead)

        assert next_date is not None
        delta = next_date - datetime.now()
        assert 6 <= delta.days <= 8


class TestLeadServiceInstance:
    """Testes para instância global do serviço."""

    def test_global_instance_exists(self):
        """Testa que instância global existe."""
        assert lead_service is not None

    def test_global_instance_is_lead_service(self):
        """Testa que instância é LeadService."""
        assert isinstance(lead_service, LeadService)

    def test_global_instance_has_scoring_engine(self):
        """Testa que instância tem scoring engine."""
        assert hasattr(lead_service, "scoring_engine")
        assert isinstance(lead_service.scoring_engine, LeadScoringEngine)
