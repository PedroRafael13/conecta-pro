"""Testes do Personalization Engine - Sprint 03."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.notifications.engine.behavioral_analyzer import (
    BehavioralAnalyzer,
    BehaviorPattern,
    EngagementLevel,
    EngagementPrediction,
    UserBehaviorProfile,
)
from modules.notifications.engine.channel_selector import (
    Channel,
    ChannelRecommendation,
    ChannelSelector,
)
from modules.notifications.engine.content_personalizer import (
    ContentPersonalizer,
    PersonalizedContent,
)
from modules.notifications.engine.personalization_engine import (
    PersonalizationEngine,
    PersonalizedNotification,
    UserProfile,
)
from modules.notifications.engine.timing_optimizer import (
    TimingOptimizer,
    TimingPrediction,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_db():
    """Mock da sessão do banco."""
    return AsyncMock()


@pytest.fixture
def personalization_engine():
    """Instância do PersonalizationEngine."""
    return PersonalizationEngine()


@pytest.fixture
def timing_optimizer():
    """Instância do TimingOptimizer."""
    return TimingOptimizer()


@pytest.fixture
def channel_selector():
    """Instância do ChannelSelector."""
    return ChannelSelector()


@pytest.fixture
def content_personalizer():
    """Instância do ContentPersonalizer."""
    return ContentPersonalizer()


@pytest.fixture
def behavioral_analyzer():
    """Instância do BehavioralAnalyzer."""
    return BehavioralAnalyzer()


# ============================================================================
# Tests - PersonalizationEngine
# ============================================================================


class TestPersonalizationEngine:
    """Testes do PersonalizationEngine."""

    @pytest.mark.asyncio
    async def test_personalize_notification(
        self,
        mock_db,
        personalization_engine,
    ):
        """Testa personalização de notificação."""
        result = await personalization_engine.personalize_notification(
            db=mock_db,
            user_id=1,
            notification_type="reminder",
            base_content={
                "title": "Olá {{user.nome}}",
                "body": "Você tem um lembrete pendente.",
            },
        )

        assert isinstance(result, PersonalizedNotification)
        assert result.user_id == 1
        assert result.content is not None
        assert 0 <= result.engagement_score <= 1

    @pytest.mark.asyncio
    async def test_get_user_profile(
        self,
        mock_db,
        personalization_engine,
    ):
        """Testa obtenção do perfil do usuário."""
        profile = await personalization_engine.get_user_profile(mock_db, user_id=1)

        assert isinstance(profile, UserProfile)
        assert profile.user_id == 1
        assert profile.preferences is not None
        assert len(profile.activity_patterns) > 0


# ============================================================================
# Tests - TimingOptimizer
# ============================================================================


class TestTimingOptimizer:
    """Testes do TimingOptimizer."""

    @pytest.mark.asyncio
    async def test_optimize_send_time(
        self,
        mock_db,
        timing_optimizer,
    ):
        """Testa otimização de horário de envio."""
        result = await timing_optimizer.optimize_send_time(
            db=mock_db,
            user_id=1,
            notification_type="marketing",
        )

        assert isinstance(result, TimingPrediction)
        assert result.optimal_datetime is not None
        assert 0 <= result.confidence <= 1
        assert result.reasoning is not None

    @pytest.mark.asyncio
    async def test_optimize_with_deadline(
        self,
        mock_db,
        timing_optimizer,
    ):
        """Testa otimização com deadline."""
        deadline = datetime.utcnow() + timedelta(hours=2)

        result = await timing_optimizer.optimize_send_time(
            db=mock_db,
            user_id=1,
            notification_type="urgent",
            deadline=deadline,
        )

        assert result.optimal_datetime <= deadline

    @pytest.mark.asyncio
    async def test_quiet_hours_handling(
        self,
        mock_db,
        timing_optimizer,
    ):
        """Testa respeito ao horário de silêncio."""
        result = await timing_optimizer.optimize_send_time(
            db=mock_db,
            user_id=1,
            notification_type="marketing",
        )

        # Marketing não deve ser enviado em quiet hours
        hour = result.optimal_datetime.hour
        assert not (hour >= 22 or hour < 8), "Marketing fora de quiet hours"

    def test_calculate_hourly_scores(
        self,
        timing_optimizer,
    ):
        """Testa cálculo de scores por hora."""
        patterns = {
            "peak_hours": [9, 10, 14, 15],
            "low_activity_hours": [0, 1, 2, 3, 4, 5],
            "avg_response_time_by_hour": dict.fromkeys(range(24), 30),
        }
        preferences = {
            "quiet_hours_start": MagicMock(hour=22),
            "quiet_hours_end": MagicMock(hour=8),
        }
        historical = {
            "open_rate_by_hour": dict.fromkeys(range(24), 0.5),
            "click_rate_by_hour": dict.fromkeys(range(24), 0.2),
        }

        scores = timing_optimizer._calculate_hourly_scores(patterns, preferences, historical, "marketing")

        assert len(scores) == 24
        # Peak hours devem ter scores maiores
        assert scores[9] > scores[3]


# ============================================================================
# Tests - ChannelSelector
# ============================================================================


class TestChannelSelector:
    """Testes do ChannelSelector."""

    @pytest.mark.asyncio
    async def test_select_channel(
        self,
        mock_db,
        channel_selector,
    ):
        """Testa seleção de canal."""
        result = await channel_selector.select_channel(
            db=mock_db,
            user_id=1,
            notification_type="reminder",
        )

        assert isinstance(result, ChannelRecommendation)
        assert isinstance(result.primary_channel, Channel)
        assert len(result.fallback_channels) <= channel_selector.fallback_count

    @pytest.mark.asyncio
    async def test_force_channel(
        self,
        mock_db,
        channel_selector,
    ):
        """Testa forçar canal específico."""
        result = await channel_selector.select_channel(
            db=mock_db,
            user_id=1,
            notification_type="reminder",
            force_channel=Channel.EMAIL,
        )

        assert result.primary_channel == Channel.EMAIL
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_multi_channel_strategy(
        self,
        mock_db,
        channel_selector,
    ):
        """Testa estratégia multi-canal."""
        strategy = await channel_selector.get_multi_channel_strategy(
            db=mock_db,
            user_id=1,
            notification_type="reminder",
            importance="high",
        )

        assert len(strategy) > 1
        # Primeiro canal sem delay
        assert strategy[0][1] == 0
        # Fallbacks com delay
        for _channel, delay in strategy[1:]:
            assert delay > 0

    @pytest.mark.asyncio
    async def test_critical_strategy(
        self,
        mock_db,
        channel_selector,
    ):
        """Testa estratégia para notificações críticas."""
        strategy = await channel_selector.get_multi_channel_strategy(
            db=mock_db,
            user_id=1,
            notification_type="urgent",
            importance="critical",
        )

        # Notificações críticas enviam em múltiplos canais simultaneamente
        delays = [delay for _, delay in strategy]
        assert all(d == 0 for d in delays)

    def test_channel_affinity(
        self,
        channel_selector,
    ):
        """Testa afinidade tipo-canal."""
        urgent_channels = channel_selector.TYPE_CHANNEL_AFFINITY.get("urgent", [])
        assert Channel.PUSH in urgent_channels
        assert Channel.SMS in urgent_channels

        marketing_channels = channel_selector.TYPE_CHANNEL_AFFINITY.get("marketing", [])
        assert Channel.EMAIL in marketing_channels


# ============================================================================
# Tests - ContentPersonalizer
# ============================================================================


class TestContentPersonalizer:
    """Testes do ContentPersonalizer."""

    @pytest.mark.asyncio
    async def test_personalize_content(
        self,
        mock_db,
        content_personalizer,
    ):
        """Testa personalização de conteúdo."""
        result = await content_personalizer.personalize(
            db=mock_db,
            template_title="Olá {{user.primeiro_nome}}!",
            template_body="Bem-vindo ao {{user.condominio}}.",
            user_id=1,
        )

        assert isinstance(result, PersonalizedContent)
        assert "{{" not in result.title
        assert "{{" not in result.body
        assert result.personalization_score > 0

    @pytest.mark.asyncio
    async def test_tone_adjustment(
        self,
        mock_db,
        content_personalizer,
    ):
        """Testa ajuste de tom."""
        formal = await content_personalizer.personalize(
            db=mock_db,
            template_title="[SAUDACAO] {{user.nome}}",
            template_body="Informamos que...",
            user_id=1,
            tone="formal",
        )

        casual = await content_personalizer.personalize(
            db=mock_db,
            template_title="[SAUDACAO] {{user.nome}}",
            template_body="Informamos que...",
            user_id=1,
            tone="casual",
        )

        # Both should return valid personalized content
        assert formal is not None
        assert casual is not None
        # Check tone is recorded in metadata
        assert formal.metadata.get("tone") == "formal"
        assert casual.metadata.get("tone") == "casual"

    @pytest.mark.asyncio
    async def test_channel_optimization(
        self,
        mock_db,
        content_personalizer,
    ):
        """Testa otimização para canal."""
        long_body = "x" * 500
        content = PersonalizedContent(
            title="Título",
            body=long_body,
            summary="Resumo",
            cta_text=None,
            cta_url=None,
            image_url=None,
            metadata={},
            personalization_score=0.5,
            variables_used=[],
        )

        sms_optimized = await content_personalizer.optimize_for_channel(
            content=content,
            channel="sms",
        )

        assert len(sms_optimized.body) <= 160

    def test_truncate(
        self,
        content_personalizer,
    ):
        """Testa truncamento de texto."""
        long_text = "Esta é uma frase muito longa que precisa ser truncada"
        truncated = content_personalizer._truncate(long_text, max_length=20)

        assert len(truncated) <= 20
        assert truncated.endswith("...")

    def test_greeting_by_hour(
        self,
        content_personalizer,
    ):
        """Testa saudação por hora."""
        assert content_personalizer._get_greeting(9) == "Bom dia"
        assert content_personalizer._get_greeting(14) == "Boa tarde"
        assert content_personalizer._get_greeting(21) == "Boa noite"


# ============================================================================
# Tests - BehavioralAnalyzer
# ============================================================================


class TestBehavioralAnalyzer:
    """Testes do BehavioralAnalyzer."""

    @pytest.mark.asyncio
    async def test_analyze_user(
        self,
        mock_db,
        behavioral_analyzer,
    ):
        """Testa análise de usuário."""
        profile = await behavioral_analyzer.analyze_user(mock_db, user_id=1)

        assert isinstance(profile, UserBehaviorProfile)
        assert profile.user_id == 1
        assert isinstance(profile.engagement_level, EngagementLevel)
        assert 0 <= profile.notification_fatigue_score <= 1
        assert 0 <= profile.churn_risk_score <= 1

    @pytest.mark.asyncio
    async def test_predict_engagement(
        self,
        mock_db,
        behavioral_analyzer,
    ):
        """Testa predição de engajamento."""
        prediction = await behavioral_analyzer.predict_engagement(
            db=mock_db,
            user_id=1,
            notification_type="reminder",
        )

        assert isinstance(prediction, EngagementPrediction)
        assert 0 <= prediction.open_probability <= 1
        assert 0 <= prediction.click_probability <= 1
        assert prediction.best_time_to_send is not None

    @pytest.mark.asyncio
    async def test_get_insights(
        self,
        mock_db,
        behavioral_analyzer,
    ):
        """Testa obtenção de insights."""
        insights = await behavioral_analyzer.get_insights(mock_db, user_id=1)

        assert isinstance(insights, list)
        for insight in insights:
            assert insight.insight_type is not None
            assert insight.recommendation is not None

    @pytest.mark.asyncio
    async def test_should_send_notification(
        self,
        mock_db,
        behavioral_analyzer,
    ):
        """Testa decisão de envio."""
        # Notificação crítica sempre deve enviar
        should_send, reason = await behavioral_analyzer.should_send_notification(
            db=mock_db,
            user_id=1,
            notification_type="urgent",
            importance="critical",
        )

        assert should_send is True
        assert "Critical" in reason

    def test_identify_patterns(
        self,
        behavioral_analyzer,
    ):
        """Testa identificação de padrões."""
        history = {
            "response_times": [5, 8, 10],  # Rápido
            "consecutive_ignores": 0,
            "by_hour": {h: {"sent": 10, "opened": 8} for h in range(24)},
        }
        activity = {
            "sessions_30d": 25,
            "actions_30d": 60,
        }

        patterns = behavioral_analyzer._identify_patterns(history, activity)

        assert BehaviorPattern.QUICK_RESPONDER in patterns
        assert BehaviorPattern.POWER_USER in patterns

    def test_engagement_level_calculation(
        self,
        behavioral_analyzer,
    ):
        """Testa cálculo de nível de engajamento."""
        high_engagement = {"total_sent": 100, "total_opened": 85, "total_clicked": 35}
        low_engagement = {"total_sent": 100, "total_opened": 10, "total_clicked": 2}

        high_level = behavioral_analyzer._calculate_engagement_level(high_engagement)
        low_level = behavioral_analyzer._calculate_engagement_level(low_engagement)

        assert high_level == EngagementLevel.HIGHLY_ENGAGED
        assert low_level in [EngagementLevel.LOW, EngagementLevel.AT_RISK]

    def test_fatigue_score_calculation(
        self,
        behavioral_analyzer,
    ):
        """Testa cálculo de score de fadiga."""
        fatigued = {
            "notifications_today": 10,
            "consecutive_ignores": 5,
            "last_engagement": datetime.utcnow() - timedelta(days=10),
        }
        fresh = {
            "notifications_today": 1,
            "consecutive_ignores": 0,
            "last_engagement": datetime.utcnow(),
        }

        fatigued_score = behavioral_analyzer._calculate_fatigue_score(fatigued)
        fresh_score = behavioral_analyzer._calculate_fatigue_score(fresh)

        assert fatigued_score > fresh_score
        assert fatigued_score > 0.5


# ============================================================================
# Tests - Integration
# ============================================================================


class TestIntegration:
    """Testes de integração entre componentes."""

    @pytest.mark.asyncio
    async def test_full_personalization_flow(
        self,
        mock_db,
    ):
        """Testa fluxo completo de personalização."""
        engine = PersonalizationEngine()

        # Personalizar notificação
        result = await engine.personalize_notification(
            db=mock_db,
            user_id=1,
            notification_type="reminder",
            base_content={
                "title": "Olá {{user.nome}}",
                "body": "Lembrete: {{context.evento}}",
            },
            context={"evento": "Assembleia"},
        )

        assert result.content["title"] is not None
        assert result.optimal_time is not None
        assert result.preferred_channel is not None
        assert result.engagement_score > 0

    @pytest.mark.asyncio
    async def test_behavior_affects_channel(
        self,
        mock_db,
    ):
        """Testa que comportamento afeta seleção de canal."""
        analyzer = BehavioralAnalyzer()
        selector = ChannelSelector()

        # Obter perfil do usuário
        await analyzer.analyze_user(mock_db, user_id=1)

        # Selecionar canal
        recommendation = await selector.select_channel(
            db=mock_db,
            user_id=1,
            notification_type="marketing",
        )

        # O canal deve ser apropriado para o tipo
        assert recommendation.primary_channel in [Channel.EMAIL, Channel.PUSH, Channel.IN_APP]
