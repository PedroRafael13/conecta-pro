"""Testes para Pipeline Service."""

from datetime import date, datetime, timedelta

import pytest

from modules.crm.services.pipeline_service import PipelineService, pipeline_service
from tests.factories import OpportunityFactory


class TestPipelineService:
    """Testes para PipelineService."""

    def setup_method(self):
        """Setup para cada teste."""
        self.service = PipelineService()

    def test_calculate_weighted_pipeline(self):
        """Testa calculo do valor ponderado total."""
        opps = [
            OpportunityFactory.build(value=10000.0, probability=50, stage="qualification"),
            OpportunityFactory.build(value=20000.0, probability=75, stage="proposal"),
            OpportunityFactory.build(value=30000.0, probability=100, stage="closed_won"),
        ]

        # Apenas opportunities abertas contam
        # 10000 * 0.5 + 20000 * 0.75 = 5000 + 15000 = 20000
        result = self.service.calculate_weighted_pipeline(opps)

        assert result == 20000.0

    def test_calculate_weighted_pipeline_empty(self):
        """Testa calculo com lista vazia."""
        result = self.service.calculate_weighted_pipeline([])
        assert result == 0.0

    def test_calculate_win_rate(self):
        """Testa calculo de win rate."""
        opps = [
            OpportunityFactory.build_won(),
            OpportunityFactory.build_won(),
            OpportunityFactory.build_won(),
            OpportunityFactory.build_lost(),
            OpportunityFactory.build_lost(),
        ]

        # 3 won, 2 lost = 60% win rate
        result = self.service.calculate_win_rate(opps)

        assert result == 60.0

    def test_calculate_win_rate_all_won(self):
        """Testa win rate quando todas ganhas."""
        opps = OpportunityFactory.build_batch(3)
        for opp in opps:
            opp.stage = "closed_won"
            opp.actual_close_date = date.today()

        result = self.service.calculate_win_rate(opps)

        assert result == 100.0

    def test_calculate_win_rate_no_closed(self):
        """Testa win rate sem opportunities fechadas."""
        opps = OpportunityFactory.build_batch(3)  # Todas em qualification

        result = self.service.calculate_win_rate(opps)

        assert result == 0.0

    def test_calculate_avg_deal_size(self):
        """Testa calculo de ticket medio."""
        opps = [
            OpportunityFactory.build_won(value=10000.0),
            OpportunityFactory.build_won(value=20000.0),
            OpportunityFactory.build_won(value=30000.0),
            OpportunityFactory.build_lost(value=5000.0),  # Perdidas nao contam
        ]

        # (10000 + 20000 + 30000) / 3 = 20000
        result = self.service.calculate_avg_deal_size(opps)

        assert result == 20000.0

    def test_calculate_avg_deal_size_no_won(self):
        """Testa ticket medio sem ganhos."""
        opps = OpportunityFactory.build_batch(3)  # Todas abertas

        result = self.service.calculate_avg_deal_size(opps)

        assert result == 0.0

    def test_calculate_avg_sales_cycle(self):
        """Testa calculo do ciclo de vendas."""
        created = datetime.utcnow() - timedelta(days=30)
        closed = date.today()

        opps = [
            OpportunityFactory.build_won(created_at=created, actual_close_date=closed),
            OpportunityFactory.build_won(created_at=created, actual_close_date=closed),
        ]

        result = self.service.calculate_avg_sales_cycle(opps)

        # Ambos tem 30 dias
        assert result == 30.0

    def test_calculate_avg_sales_cycle_no_closed(self):
        """Testa ciclo sem fechados."""
        opps = OpportunityFactory.build_batch(3)

        result = self.service.calculate_avg_sales_cycle(opps)

        assert result == 0.0

    def test_get_overdue_opportunities(self):
        """Testa obtencao de opportunities atrasadas."""
        past_date = date.today() - timedelta(days=10)
        future_date = date.today() + timedelta(days=10)

        opps = [
            OpportunityFactory.build(stage="qualification", expected_close_date=past_date),
            OpportunityFactory.build(stage="proposal", expected_close_date=future_date),
            OpportunityFactory.build(stage="negotiation", expected_close_date=past_date),
            OpportunityFactory.build_won(),  # Fechada nao conta
        ]

        result = self.service.get_overdue_opportunities(opps)

        assert len(result) == 2

    def test_get_overdue_opportunities_none(self):
        """Testa quando nao ha atrasadas."""
        future_date = date.today() + timedelta(days=30)
        opps = OpportunityFactory.build_batch(3)
        for opp in opps:
            opp.expected_close_date = future_date

        result = self.service.get_overdue_opportunities(opps)

        assert len(result) == 0

    def test_get_stagnant_opportunities(self):
        """Testa obtencao de opportunities estagnadas."""
        old_date = datetime.utcnow() - timedelta(days=45)
        recent_date = datetime.utcnow() - timedelta(days=5)

        opps = [
            OpportunityFactory.build(stage="qualification", updated_at=old_date),
            OpportunityFactory.build(stage="proposal", updated_at=recent_date),
            OpportunityFactory.build(stage="negotiation", updated_at=old_date),
        ]

        result = self.service.get_stagnant_opportunities(opps, days_threshold=30)

        assert len(result) == 2

    def test_get_stagnant_opportunities_none(self):
        """Testa quando nao ha estagnadas."""
        recent = datetime.utcnow() - timedelta(days=5)
        opps = OpportunityFactory.build_batch(3)
        for opp in opps:
            opp.updated_at = recent

        result = self.service.get_stagnant_opportunities(opps)

        assert len(result) == 0

    def test_calculate_loss_analysis(self):
        """Testa analise de perdas."""
        opps = [
            OpportunityFactory.build_lost(value=10000.0, loss_reason="price"),
            OpportunityFactory.build_lost(value=20000.0, loss_reason="price", competitor="Concorrente A"),
            OpportunityFactory.build_lost(value=15000.0, loss_reason="competitor", competitor="Concorrente A"),
            OpportunityFactory.build_won(),  # Nao conta
        ]

        result = self.service.calculate_loss_analysis(opps)

        assert result["total_lost"] == 3
        assert result["total_lost_value"] == 45000.0
        assert result["by_reason"]["price"]["count"] == 2
        assert len(result["top_competitors"]) == 1
        assert result["top_competitors"][0]["name"] == "Concorrente A"

    def test_calculate_loss_analysis_empty(self):
        """Testa analise sem perdas."""
        opps = [
            OpportunityFactory.build_won(),
            OpportunityFactory.build(stage="qualification"),
        ]

        result = self.service.calculate_loss_analysis(opps)

        assert result["total_lost"] == 0
        assert result["total_lost_value"] == 0.0

    def test_get_health_score_healthy(self):
        """Testa score de saude quando saudavel."""
        # Criar opportunities recentes e sem atraso
        future_date = date.today() + timedelta(days=30)
        recent = datetime.utcnow() - timedelta(days=5)

        opps = [
            OpportunityFactory.build(stage="qualification", expected_close_date=future_date, updated_at=recent),
            OpportunityFactory.build(stage="proposal", expected_close_date=future_date, updated_at=recent),
            OpportunityFactory.build_won(),
            OpportunityFactory.build_won(),
        ]

        result = self.service.get_health_score(opps)

        assert result["status"] == "healthy"
        assert result["score"] >= 80

    def test_get_health_score_critical(self):
        """Testa score de saude quando critico."""
        past_date = date.today() - timedelta(days=30)
        old_date = datetime.utcnow() - timedelta(days=60)

        opps = [
            OpportunityFactory.build(stage="qualification", expected_close_date=past_date, updated_at=old_date),
            OpportunityFactory.build(stage="qualification", expected_close_date=past_date, updated_at=old_date),
            OpportunityFactory.build(stage="qualification", expected_close_date=past_date, updated_at=old_date),
            OpportunityFactory.build_lost(),
            OpportunityFactory.build_lost(),
        ]

        result = self.service.get_health_score(opps)

        assert result["status"] in ["warning", "critical"]
        assert len(result["recommendations"]) > 0

    def test_get_health_score_empty(self):
        """Testa score com lista vazia."""
        result = self.service.get_health_score([])

        assert result["score"] == 0
        assert result["status"] == "empty"

    def test_forecast_revenue(self):
        """Testa previsao de receita."""
        today = date.today()

        # Criar opportunities com expected_close_date neste mes
        opps = [
            OpportunityFactory.build(
                stage="proposal",
                value=10000.0,
                probability=50,
                expected_close_date=today,
            ),
            OpportunityFactory.build(
                stage="negotiation",
                value=20000.0,
                probability=75,
                expected_close_date=today,
            ),
        ]

        result = self.service.forecast_revenue(opps, months_ahead=3)

        assert len(result) == 3
        # Primeiro mes deve ter as 2 opportunities
        assert result[0].opportunity_count == 2
        assert result[0].expected_value == 30000.0
        assert result[0].weighted_value == (10000 * 0.5) + (20000 * 0.75)

    def test_forecast_revenue_empty(self):
        """Testa previsao sem opportunities."""
        result = self.service.forecast_revenue([], months_ahead=3)

        assert len(result) == 3
        for forecast in result:
            assert forecast.opportunity_count == 0
            assert forecast.expected_value == 0.0

    def test_stage_conversion_rates(self):
        """Testa taxas de conversao entre estagios."""
        opps = [
            OpportunityFactory.build(stage="qualification"),
            OpportunityFactory.build(stage="qualification"),
            OpportunityFactory.build(stage="proposal"),
            OpportunityFactory.build_won(),
        ]

        result = self.service.get_stage_conversion_rates(opps)

        # Verifica que retornou conversoes
        assert "qualification_to_needs_analysis" in result or len(result) > 0


class TestPipelineServiceSingleton:
    """Testes para singleton do pipeline service."""

    def test_singleton_exists(self):
        """Testa que singleton existe."""
        assert pipeline_service is not None
        assert isinstance(pipeline_service, PipelineService)

    def test_singleton_methods(self):
        """Testa que singleton tem os metodos."""
        assert hasattr(pipeline_service, "calculate_weighted_pipeline")
        assert hasattr(pipeline_service, "calculate_win_rate")
        assert hasattr(pipeline_service, "get_health_score")
        assert hasattr(pipeline_service, "forecast_revenue")


class TestSalesVelocity:
    """Testes para calculo de velocidade de vendas."""

    def test_calculate_sales_velocity(self):
        """Testa calculo de velocidade."""
        service = PipelineService()

        created = datetime.utcnow() - timedelta(days=30)
        closed = date.today()

        opps = [
            OpportunityFactory.build(stage="qualification", value=10000.0, probability=50),
            OpportunityFactory.build(stage="proposal", value=20000.0, probability=75),
            OpportunityFactory.build_won(value=15000.0, created_at=created, actual_close_date=closed),
            OpportunityFactory.build_won(value=25000.0, created_at=created, actual_close_date=closed),
        ]

        result = service.calculate_sales_velocity(opps)

        # Deve retornar um valor positivo
        assert result >= 0

    def test_calculate_sales_velocity_no_data(self):
        """Testa velocidade sem dados suficientes."""
        service = PipelineService()

        # Apenas opportunities abertas, sem fechadas
        opps = OpportunityFactory.build_batch(3)

        result = service.calculate_sales_velocity(opps)

        # Sem ciclo de vendas, retorna 0
        assert result == 0.0
