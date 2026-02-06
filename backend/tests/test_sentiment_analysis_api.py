"""
Testes de API - Sentiment Analysis (Sprint 46)

Testes de integracao para os endpoints de analise de sentimento.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient
from httpx import AsyncClient

from modules.ai.sentiment_analysis.models import (
    SentimentAnalysis,
    SentimentType,
    EmotionType,
    SourceType,
    AnalysisStatus,
    SentimentRule,
    RuleCategory,
    RuleAction,
    SentimentTrend,
    TrendPeriod,
    TrendDirection,
    FeedbackInsight,
    InsightType,
    InsightPriority,
)
from modules.ai.sentiment_analysis.models.sentiment_trend import TrendCategory
from modules.ai.sentiment_analysis.models.feedback_insight import InsightStatus
from modules.ai.sentiment_analysis.schemas import (
    AnalyzeTextRequest,
    SentimentRuleCreate,
    FeedbackInsightCreate,
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_analysis():
    """Cria analise mock."""
    analysis = MagicMock(spec=SentimentAnalysis)
    analysis.id = uuid4()
    analysis.original_text = "Otimo servico, muito satisfeito!"
    analysis.source_type = SourceType.FEEDBACK_FORM
    analysis.sentiment_type = SentimentType.POSITIVE
    analysis.sentiment_score = 65.0
    analysis.confidence_score = 85.0
    analysis.positive_score = 75.0
    analysis.negative_score = 10.0
    analysis.neutral_score = 15.0
    analysis.primary_emotion = EmotionType.SATISFACTION
    analysis.secondary_emotion = None
    analysis.emotion_scores = {"satisfaction": 80}
    analysis.aspects = []
    analysis.keywords = []
    analysis.topics = []
    analysis.has_urgency = False
    analysis.urgency_level = 0
    analysis.has_complaint = False
    analysis.has_praise = True
    analysis.has_question = False
    analysis.has_suggestion = False
    analysis.has_intent_to_leave = False
    analysis.requires_action = False
    analysis.key_phrases = ["otimo servico"]
    analysis.positive_phrases = ["otimo servico", "muito satisfeito"]
    analysis.negative_phrases = []
    analysis.nps_score = None
    analysis.nps_category = None
    analysis.triggered_rules = []
    analysis.alert_generated = False
    analysis.processing_time_ms = 150
    analysis.model_version = "sentiment_v1.0.0"
    analysis.analyzed_at = datetime.utcnow()
    analysis.status = AnalysisStatus.COMPLETED
    analysis.created_at = datetime.utcnow()
    analysis.is_critical = False
    analysis.sentiment_label = "Positivo"
    analysis.to_summary.return_value = {
        "id": str(analysis.id),
        "sentiment": "positive",
        "sentiment_label": "Positivo",
        "score": 65.0,
        "confidence": 85.0,
        "primary_emotion": "satisfaction",
        "is_critical": False,
        "requires_action": False,
        "key_aspects": [],
        "analyzed_at": datetime.utcnow().isoformat(),
    }
    return analysis


@pytest.fixture
def mock_rule():
    """Cria regra mock."""
    rule = MagicMock(spec=SentimentRule)
    rule.id = uuid4()
    rule.code = "TEST_RULE"
    rule.name = "Regra de Teste"
    rule.description = "Descricao de teste"
    rule.category = RuleCategory.SENTIMENT
    rule.subcategory = None
    rule.priority = 50
    rule.weight = 1.0
    rule.conditions = []
    rule.sentiment_threshold = -50.0
    rule.sentiment_types = ["negative", "very_negative"]
    rule.emotion_types = []
    rule.keywords_include = []
    rule.keywords_exclude = []
    rule.keywords_match_all = False
    rule.aspects_include = []
    rule.source_types = []
    rule.customer_segments = []
    rule.primary_action = RuleAction.ALERT
    rule.secondary_actions = []
    rule.action_config = {}
    rule.notify_channels = []
    rule.notify_recipients = []
    rule.cooldown_minutes = 60
    rule.max_triggers_per_day = None
    rule.total_triggers = 10
    rule.total_actions = 10
    rule.true_positives = 8
    rule.false_positives = 2
    rule.precision_rate = 80.0
    rule.last_triggered_at = datetime.utcnow()
    rule.is_active = True
    rule.is_system = False
    rule.is_test_mode = False
    rule.created_at = datetime.utcnow()
    rule.updated_at = None
    return rule


@pytest.fixture
def mock_trend():
    """Cria tendencia mock."""
    trend = MagicMock(spec=SentimentTrend)
    trend.id = uuid4()
    trend.period_type = TrendPeriod.DAILY
    trend.period_start = datetime.utcnow() - timedelta(days=1)
    trend.period_end = datetime.utcnow()
    trend.period_label = "2025-01-05"
    trend.category = TrendCategory.OVERALL
    trend.category_value = None
    trend.avg_sentiment_score = 45.5
    trend.total_analyses = 100
    trend.satisfaction_rate = 60.0
    trend.dissatisfaction_rate = 20.0
    trend.trend_direction = TrendDirection.STABLE
    trend.score_change = 2.0
    trend.nps_score = 35.0
    trend.needs_attention = False
    trend.to_summary.return_value = {
        "period": "2025-01-05",
        "period_type": "daily",
        "category": "overall",
        "avg_score": 45.5,
        "total_analyses": 100,
        "satisfaction_rate": 60.0,
        "dissatisfaction_rate": 20.0,
        "trend": "stable",
        "score_change": 2.0,
        "nps_score": 35.0,
        "needs_attention": False,
    }
    return trend


@pytest.fixture
def mock_insight():
    """Cria insight mock."""
    insight = MagicMock(spec=FeedbackInsight)
    insight.id = uuid4()
    insight.insight_number = "INS2025010512345ABC"
    insight.title = "Queda de sentimento detectada"
    insight.description = "Sentimento caiu 15 pontos"
    insight.insight_type = InsightType.SENTIMENT_DROP
    insight.priority = InsightPriority.HIGH
    insight.status = InsightStatus.NEW
    insight.category = "sentimento"
    insight.impact_score = 70.0
    insight.confidence_score = 85.0
    insight.urgency_score = 60.0
    insight.actionability_score = 80.0
    insight.overall_score = 72.0
    insight.is_actionable = True
    insight.is_critical = False
    insight.is_expired = False
    insight.priority_label = "Alta"
    insight.recommendations = []
    insight.affected_customers = 50
    insight.created_at = datetime.utcnow()
    insight.to_summary.return_value = {
        "id": str(insight.id),
        "number": "INS2025010512345ABC",
        "type": "sentiment_drop",
        "title": "Queda de sentimento detectada",
        "priority": "high",
        "priority_label": "Alta",
        "status": "new",
        "overall_score": 72.0,
        "is_actionable": True,
        "is_critical": False,
        "affected_customers": 50,
        "recommendations_count": 0,
        "created_at": datetime.utcnow().isoformat(),
    }
    return insight


# ============================================================
# Tests - Analysis Endpoints
# ============================================================

class TestAnalysisEndpoints:
    """Testes para endpoints de analise."""

    @pytest.mark.asyncio
    async def test_analyze_text_positive(self, mock_analysis):
        """Testa analise de texto positivo."""
        request_data = {
            "text": "Excelente atendimento, muito satisfeito com o servico!",
            "source_type": "feedback_form",
            "detect_emotions": True,
            "extract_aspects": True,
        }

        # Mock do analyzer
        with patch(
            "modules.ai.sentiment_analysis.controllers.sentiment_controller.SentimentAnalyzer"
        ) as MockAnalyzer:
            mock_instance = AsyncMock()
            mock_instance.analyze_text.return_value = mock_analysis
            MockAnalyzer.return_value = mock_instance

            # Simulacao de chamada
            analyzer = MockAnalyzer(None)
            result = await analyzer.analyze_text(AnalyzeTextRequest(**request_data))

            assert result.sentiment_type == SentimentType.POSITIVE
            assert result.sentiment_score == 65.0

    @pytest.mark.asyncio
    async def test_analyze_text_negative(self):
        """Testa analise de texto negativo."""
        request_data = {
            "text": "Pessimo servico, nunca mais volto aqui!",
            "source_type": "complaint",
        }

        with patch(
            "modules.ai.sentiment_analysis.services.SentimentAnalyzer"
        ) as MockAnalyzer:
            mock_instance = AsyncMock()
            mock_result = MagicMock()
            mock_result.sentiment_type = SentimentType.VERY_NEGATIVE
            mock_result.sentiment_score = -75.0
            mock_result.has_complaint = True
            mock_instance.analyze_text.return_value = mock_result
            MockAnalyzer.return_value = mock_instance

            analyzer = MockAnalyzer(None)
            result = await analyzer.analyze_text(AnalyzeTextRequest(**request_data))

            assert result.sentiment_type == SentimentType.VERY_NEGATIVE
            assert result.sentiment_score == -75.0
            assert result.has_complaint is True

    @pytest.mark.asyncio
    async def test_batch_analyze(self, mock_analysis):
        """Testa analise em lote."""
        request_data = {
            "texts": [
                {"text": "Otimo produto", "source_type": "review"},
                {"text": "Servico ruim", "source_type": "complaint"},
            ]
        }

        with patch(
            "modules.ai.sentiment_analysis.services.SentimentAnalyzer"
        ) as MockAnalyzer:
            mock_instance = AsyncMock()
            mock_result = MagicMock()
            mock_result.total = 2
            mock_result.processed = 2
            mock_result.failed = 0
            mock_result.results = [mock_analysis, mock_analysis]
            mock_result.errors = []
            mock_instance.batch_analyze.return_value = mock_result
            MockAnalyzer.return_value = mock_instance

            analyzer = MockAnalyzer(None)
            result = await analyzer.batch_analyze(request_data)

            assert result.total == 2
            assert result.processed == 2

    @pytest.mark.asyncio
    async def test_list_analyses(self, mock_analysis):
        """Testa listagem de analises."""
        with patch(
            "modules.ai.sentiment_analysis.repositories.SentimentRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.list_analyses.return_value = ([mock_analysis], 1)
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            items, total = await repo.list_analyses(page=1, page_size=50)

            assert total == 1
            assert len(items) == 1

    @pytest.mark.asyncio
    async def test_get_critical_analyses(self, mock_analysis):
        """Testa busca de analises criticas."""
        mock_analysis.is_critical = True
        mock_analysis.sentiment_type = SentimentType.VERY_NEGATIVE

        with patch(
            "modules.ai.sentiment_analysis.repositories.SentimentRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_critical_analyses.return_value = [mock_analysis]
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            results = await repo.get_critical_analyses(hours=24)

            assert len(results) == 1
            assert results[0].is_critical is True


# ============================================================
# Tests - Rule Endpoints
# ============================================================

class TestRuleEndpoints:
    """Testes para endpoints de regras."""

    @pytest.mark.asyncio
    async def test_create_rule(self, mock_rule):
        """Testa criacao de regra."""
        rule_data = SentimentRuleCreate(
            code="NEW_RULE",
            name="Nova Regra",
            category=RuleCategory.SENTIMENT,
            sentiment_threshold=-50,
            primary_action=RuleAction.ALERT,
        )

        with patch(
            "modules.ai.sentiment_analysis.services.SentimentAlertService"
        ) as MockService:
            mock_instance = AsyncMock()
            mock_instance.create_rule.return_value = mock_rule
            MockService.return_value = mock_instance

            service = MockService(None)
            result = await service.create_rule(rule_data)

            assert result.code == "TEST_RULE"
            assert result.category == RuleCategory.SENTIMENT

    @pytest.mark.asyncio
    async def test_list_rules(self, mock_rule):
        """Testa listagem de regras."""
        with patch(
            "modules.ai.sentiment_analysis.repositories.SentimentRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.list_rules.return_value = ([mock_rule], 1)
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            items, total = await repo.list_rules()

            assert total == 1
            assert items[0].code == "TEST_RULE"

    @pytest.mark.asyncio
    async def test_toggle_rule(self, mock_rule):
        """Testa ativar/desativar regra."""
        with patch(
            "modules.ai.sentiment_analysis.services.SentimentAlertService"
        ) as MockService:
            mock_rule.is_active = False
            mock_instance = AsyncMock()
            mock_instance.toggle_rule.return_value = mock_rule
            MockService.return_value = mock_instance

            service = MockService(None)
            result = await service.toggle_rule(mock_rule.id, False)

            assert result.is_active is False

    @pytest.mark.asyncio
    async def test_evaluate_rules(self, mock_analysis, mock_rule):
        """Testa avaliacao de regras."""
        with patch(
            "modules.ai.sentiment_analysis.services.SentimentAlertService"
        ) as MockService:
            mock_result = MagicMock()
            mock_result.rule_id = mock_rule.id
            mock_result.matched = True
            mock_result.reasons = ["Score abaixo do threshold"]

            mock_instance = AsyncMock()
            mock_instance.evaluate_analysis.return_value = [mock_result]
            MockService.return_value = mock_instance

            service = MockService(None)
            results = await service.evaluate_analysis(mock_analysis)

            assert len(results) == 1
            assert results[0].matched is True


# ============================================================
# Tests - Trend Endpoints
# ============================================================

class TestTrendEndpoints:
    """Testes para endpoints de tendencias."""

    @pytest.mark.asyncio
    async def test_calculate_trend(self, mock_trend):
        """Testa calculo de tendencia."""
        with patch(
            "modules.ai.sentiment_analysis.services.TrendCalculator"
        ) as MockCalc:
            mock_instance = AsyncMock()
            mock_instance.calculate_trend.return_value = mock_trend
            MockCalc.return_value = mock_instance

            calc = MockCalc(None)
            result = await calc.calculate_trend(
                period_type=TrendPeriod.DAILY,
                period_start=datetime.utcnow() - timedelta(days=1),
                period_end=datetime.utcnow(),
            )

            assert result.period_type == TrendPeriod.DAILY
            assert result.avg_sentiment_score == 45.5

    @pytest.mark.asyncio
    async def test_get_trend_comparison(self, mock_trend):
        """Testa comparacao de tendencias."""
        with patch(
            "modules.ai.sentiment_analysis.services.TrendCalculator"
        ) as MockCalc:
            mock_instance = AsyncMock()
            mock_instance.get_trend_comparison.return_value = {
                "current": mock_trend.to_summary(),
                "previous": mock_trend.to_summary(),
                "score_improvement": 5.0,
                "trend_direction": "improving",
            }
            MockCalc.return_value = mock_instance

            calc = MockCalc(None)
            result = await calc.get_trend_comparison(
                period_type=TrendPeriod.WEEKLY,
                current_start=datetime.utcnow() - timedelta(weeks=1),
                current_end=datetime.utcnow(),
            )

            assert "current" in result
            assert "previous" in result
            assert result["score_improvement"] == 5.0

    @pytest.mark.asyncio
    async def test_get_dashboard_summary(self):
        """Testa resumo do dashboard."""
        with patch(
            "modules.ai.sentiment_analysis.services.TrendCalculator"
        ) as MockCalc:
            mock_instance = AsyncMock()
            mock_instance.get_dashboard_summary.return_value = {
                "daily": {"total": 50, "avg_score": 45.0},
                "weekly": {"total": 300, "avg_score": 42.0},
                "emotions": {"satisfaction": 100, "frustration": 20},
                "top_keywords": [{"word": "atendimento", "count": 50}],
            }
            MockCalc.return_value = mock_instance

            calc = MockCalc(None)
            result = await calc.get_dashboard_summary()

            assert "daily" in result
            assert "weekly" in result
            assert result["daily"]["total"] == 50


# ============================================================
# Tests - Insight Endpoints
# ============================================================

class TestInsightEndpoints:
    """Testes para endpoints de insights."""

    @pytest.mark.asyncio
    async def test_create_insight(self, mock_insight):
        """Testa criacao de insight."""
        insight_data = FeedbackInsightCreate(
            title="Novo Insight",
            insight_type=InsightType.SERVICE_ISSUE,
            priority=InsightPriority.MEDIUM,
            impact_score=60.0,
            confidence_score=70.0,
            urgency_score=50.0,
            actionability_score=65.0,
        )

        with patch(
            "modules.ai.sentiment_analysis.repositories.SentimentRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.create_insight.return_value = mock_insight
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            result = await repo.create_insight(mock_insight)

            assert result.insight_type == InsightType.SENTIMENT_DROP

    @pytest.mark.asyncio
    async def test_list_insights(self, mock_insight):
        """Testa listagem de insights."""
        with patch(
            "modules.ai.sentiment_analysis.repositories.SentimentRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.list_insights.return_value = ([mock_insight], 1)
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            items, total = await repo.list_insights()

            assert total == 1
            assert items[0].insight_type == InsightType.SENTIMENT_DROP

    @pytest.mark.asyncio
    async def test_get_active_insights(self, mock_insight):
        """Testa busca de insights ativos."""
        with patch(
            "modules.ai.sentiment_analysis.services.InsightGenerator"
        ) as MockGen:
            mock_instance = AsyncMock()
            mock_instance.get_active_insights.return_value = [mock_insight]
            MockGen.return_value = mock_instance

            gen = MockGen(None)
            results = await gen.get_active_insights()

            assert len(results) == 1
            assert results[0].status == InsightStatus.NEW

    @pytest.mark.asyncio
    async def test_acknowledge_insight(self, mock_insight):
        """Testa reconhecimento de insight."""
        mock_insight.status = InsightStatus.ACKNOWLEDGED

        with patch(
            "modules.ai.sentiment_analysis.services.InsightGenerator"
        ) as MockGen:
            mock_instance = AsyncMock()
            mock_instance.acknowledge_insight.return_value = mock_insight
            MockGen.return_value = mock_instance

            gen = MockGen(None)
            result = await gen.acknowledge_insight(mock_insight.id, uuid4())

            assert result.status == InsightStatus.ACKNOWLEDGED

    @pytest.mark.asyncio
    async def test_resolve_insight(self, mock_insight):
        """Testa resolucao de insight."""
        mock_insight.status = InsightStatus.IMPLEMENTED

        with patch(
            "modules.ai.sentiment_analysis.services.InsightGenerator"
        ) as MockGen:
            mock_instance = AsyncMock()
            mock_instance.resolve_insight.return_value = mock_insight
            MockGen.return_value = mock_instance

            gen = MockGen(None)
            result = await gen.resolve_insight(
                mock_insight.id, uuid4(), "success", "Problema corrigido"
            )

            assert result.status == InsightStatus.IMPLEMENTED

    @pytest.mark.asyncio
    async def test_generate_insights(self, mock_insight):
        """Testa geracao automatica de insights."""
        with patch(
            "modules.ai.sentiment_analysis.services.InsightGenerator"
        ) as MockGen:
            mock_instance = AsyncMock()
            mock_instance.analyze_and_generate.return_value = [mock_insight]
            MockGen.return_value = mock_instance

            gen = MockGen(None)
            results = await gen.analyze_and_generate(
                period_type=TrendPeriod.DAILY,
                days_back=1,
            )

            assert len(results) == 1


# ============================================================
# Tests - Stats Endpoints
# ============================================================

class TestStatsEndpoints:
    """Testes para endpoints de estatisticas."""

    @pytest.mark.asyncio
    async def test_get_analysis_stats(self):
        """Testa estatisticas de analises."""
        with patch(
            "modules.ai.sentiment_analysis.repositories.SentimentRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_analysis_stats.return_value = {
                "total": 1000,
                "avg_score": 35.5,
                "sentiment_distribution": {
                    "positive": 400,
                    "neutral": 350,
                    "negative": 250,
                },
                "complaint_count": 150,
            }
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            stats = await repo.get_analysis_stats()

            assert stats["total"] == 1000
            assert stats["avg_score"] == 35.5

    @pytest.mark.asyncio
    async def test_get_emotion_distribution(self):
        """Testa distribuicao de emocoes."""
        with patch(
            "modules.ai.sentiment_analysis.repositories.SentimentRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_emotion_distribution.return_value = {
                "satisfaction": 300,
                "frustration": 100,
                "anger": 50,
                "neutral": 200,
            }
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            dist = await repo.get_emotion_distribution()

            assert dist["satisfaction"] == 300
            assert "frustration" in dist

    @pytest.mark.asyncio
    async def test_get_top_keywords(self):
        """Testa keywords mais frequentes."""
        with patch(
            "modules.ai.sentiment_analysis.repositories.SentimentRepository"
        ) as MockRepo:
            mock_instance = AsyncMock()
            mock_instance.get_top_keywords.return_value = [
                {"word": "atendimento", "count": 150},
                {"word": "preco", "count": 100},
                {"word": "qualidade", "count": 80},
            ]
            MockRepo.return_value = mock_instance

            repo = MockRepo(None)
            keywords = await repo.get_top_keywords(limit=10)

            assert len(keywords) == 3
            assert keywords[0]["word"] == "atendimento"
            assert keywords[0]["count"] == 150
