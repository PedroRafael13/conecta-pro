"""Testes para o Churn Predictor."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import numpy as np
import pandas as pd
import pytest

from modules.analytics.ml.features.feature_store import FeatureStore
from modules.analytics.ml.registry.model_registry import ModelRegistry
from modules.analytics.models.churn.churn_predictor import (
    ChurnAnalytics,
    ChurnPrediction,
    ChurnPredictor,
    ChurnRiskLevel,
    RetentionAction,
    RetentionActionType,
)


@pytest.fixture
def feature_store():
    """Feature store mockado."""
    return MagicMock(spec=FeatureStore)


@pytest.fixture
def model_registry():
    """Model registry mockado."""
    return MagicMock(spec=ModelRegistry)


@pytest.fixture
def churn_predictor(feature_store, model_registry):
    """Instância do ChurnPredictor."""
    return ChurnPredictor(feature_store, model_registry)


@pytest.fixture
def mock_db():
    """Mock da sessão do banco."""
    return AsyncMock()


class TestChurnPrediction:
    """Testes de predição de churn."""

    @pytest.mark.asyncio
    async def test_predict_returns_valid_prediction(
        self,
        churn_predictor,
        feature_store,
        mock_db,
    ):
        """Deve retornar predição válida."""
        # Arrange
        user_id = 1
        feature_store.get_user_features = AsyncMock(
            return_value={
                "tenure_days": 100,
                "total_spent": 5000,
                "avg_order_value": 250,
                "order_frequency": 20,
                "last_activity_days": 5,
                "login_frequency": 15,
            }
        )
        feature_store.get_engagement_features = AsyncMock(
            return_value={
                "session_duration_avg": 300,
                "pages_per_session": 10,
                "notification_response_rate": 0.6,
            }
        )
        feature_store.get_transaction_features = AsyncMock(
            return_value={
                "transaction_count_30d": 5,
                "transaction_value_30d": 1000,
                "refund_rate": 0.02,
            }
        )

        # Act
        prediction = await churn_predictor.predict(mock_db, user_id)

        # Assert
        assert isinstance(prediction, ChurnPrediction)
        assert prediction.user_id == user_id
        assert 0 <= prediction.churn_probability <= 1
        assert isinstance(prediction.risk_level, ChurnRiskLevel)
        assert 0 <= prediction.confidence <= 1

    @pytest.mark.asyncio
    async def test_predict_high_risk_user(
        self,
        churn_predictor,
        feature_store,
        mock_db,
    ):
        """Deve identificar usuário de alto risco."""
        # Arrange - usuário inativo com poucos logins
        user_id = 2
        feature_store.get_user_features = AsyncMock(
            return_value={
                "tenure_days": 365,
                "total_spent": 500,
                "avg_order_value": 50,
                "order_frequency": 2,
                "last_activity_days": 45,  # Muito inativo
                "login_frequency": 1,  # Raramente loga
            }
        )
        feature_store.get_engagement_features = AsyncMock(
            return_value={
                "session_duration_avg": 60,
                "pages_per_session": 2,
                "notification_response_rate": 0.1,
            }
        )
        feature_store.get_transaction_features = AsyncMock(
            return_value={
                "transaction_count_30d": 0,  # Sem transações recentes
                "transaction_value_30d": 0,
                "refund_rate": 0.15,
            }
        )

        # Act
        prediction = await churn_predictor.predict(mock_db, user_id)

        # Assert
        assert prediction.churn_probability > 0.5
        assert prediction.risk_level in [
            ChurnRiskLevel.HIGH,
            ChurnRiskLevel.CRITICAL,
        ]

    @pytest.mark.asyncio
    async def test_predict_includes_retention_actions(
        self,
        churn_predictor,
        feature_store,
        mock_db,
    ):
        """Deve incluir ações de retenção."""
        # Arrange
        feature_store.get_user_features = AsyncMock(
            return_value={
                "tenure_days": 200,
                "total_spent": 3000,
                "avg_order_value": 150,
                "order_frequency": 10,
                "last_activity_days": 20,
                "login_frequency": 3,
            }
        )
        feature_store.get_engagement_features = AsyncMock(return_value={})
        feature_store.get_transaction_features = AsyncMock(return_value={})

        # Act
        prediction = await churn_predictor.predict(mock_db, 1)

        # Assert
        assert len(prediction.retention_actions) > 0
        for action in prediction.retention_actions:
            assert isinstance(action, RetentionAction)
            assert action.priority >= 1
            assert action.expected_impact >= 0

    @pytest.mark.asyncio
    async def test_predict_includes_contributing_factors(
        self,
        churn_predictor,
        feature_store,
        mock_db,
    ):
        """Deve incluir fatores contribuintes."""
        # Arrange
        feature_store.get_user_features = AsyncMock(
            return_value={
                "last_activity_days": 30,
                "login_frequency": 2,
            }
        )
        feature_store.get_engagement_features = AsyncMock(return_value={})
        feature_store.get_transaction_features = AsyncMock(return_value={})

        # Act
        prediction = await churn_predictor.predict(mock_db, 1)

        # Assert
        assert len(prediction.contributing_factors) > 0


class TestChurnRiskClassification:
    """Testes de classificação de risco."""

    def test_classify_risk_very_low(self, churn_predictor):
        """Deve classificar como muito baixo."""
        assert churn_predictor._classify_risk(0.05) == ChurnRiskLevel.VERY_LOW

    def test_classify_risk_low(self, churn_predictor):
        """Deve classificar como baixo."""
        assert churn_predictor._classify_risk(0.15) == ChurnRiskLevel.LOW

    def test_classify_risk_medium(self, churn_predictor):
        """Deve classificar como médio."""
        assert churn_predictor._classify_risk(0.35) == ChurnRiskLevel.MEDIUM

    def test_classify_risk_high(self, churn_predictor):
        """Deve classificar como alto."""
        assert churn_predictor._classify_risk(0.65) == ChurnRiskLevel.HIGH

    def test_classify_risk_critical(self, churn_predictor):
        """Deve classificar como crítico."""
        assert churn_predictor._classify_risk(0.85) == ChurnRiskLevel.CRITICAL


class TestRuleBasedPrediction:
    """Testes da predição baseada em regras."""

    def test_rule_based_inactivity_increases_score(self, churn_predictor):
        """Inatividade deve aumentar score."""
        features_inactive = {"last_activity_days": 35}
        features_active = {"last_activity_days": 5}

        score_inactive = churn_predictor._rule_based_prediction(features_inactive)
        score_active = churn_predictor._rule_based_prediction(features_active)

        assert score_inactive > score_active

    def test_rule_based_low_login_increases_score(self, churn_predictor):
        """Baixa frequência de login deve aumentar score."""
        features_low = {"login_frequency": 1}
        features_high = {"login_frequency": 15}

        score_low = churn_predictor._rule_based_prediction(features_low)
        score_high = churn_predictor._rule_based_prediction(features_high)

        assert score_low > score_high

    def test_rule_based_no_transactions_increases_score(self, churn_predictor):
        """Sem transações recentes deve aumentar score."""
        features_none = {"transaction_count_30d": 0}
        features_many = {"transaction_count_30d": 10}

        score_none = churn_predictor._rule_based_prediction(features_none)
        score_many = churn_predictor._rule_based_prediction(features_many)

        assert score_none > score_many

    def test_rule_based_max_score_capped(self, churn_predictor):
        """Score não deve exceder 0.95."""
        features_worst = {
            "last_activity_days": 60,
            "login_frequency": 0,
            "transaction_count_30d": 0,
            "refund_rate": 0.5,
            "notification_response_rate": 0,
        }

        score = churn_predictor._rule_based_prediction(features_worst)
        assert score <= 0.95


class TestHighRiskUsers:
    """Testes de busca de usuários de alto risco."""

    @pytest.mark.asyncio
    async def test_get_high_risk_users_returns_sorted_list(
        self,
        churn_predictor,
        feature_store,
        mock_db,
    ):
        """Deve retornar lista ordenada por probabilidade."""
        # Arrange
        feature_store.get_user_features = AsyncMock(
            return_value={
                "last_activity_days": 25,
                "login_frequency": 2,
            }
        )
        feature_store.get_engagement_features = AsyncMock(return_value={})
        feature_store.get_transaction_features = AsyncMock(return_value={})

        # Act
        users = await churn_predictor.get_high_risk_users(
            mock_db,
            limit=10,
            min_risk_level=ChurnRiskLevel.MEDIUM,
        )

        # Assert
        if len(users) > 1:
            for i in range(len(users) - 1):
                assert users[i].churn_probability >= users[i + 1].churn_probability


class TestChurnAnalytics:
    """Testes de analytics de churn."""

    @pytest.mark.asyncio
    async def test_get_churn_analytics_returns_valid_metrics(
        self,
        churn_predictor,
        feature_store,
        mock_db,
    ):
        """Deve retornar métricas válidas."""
        # Arrange
        feature_store.get_user_features = AsyncMock(return_value={})
        feature_store.get_engagement_features = AsyncMock(return_value={})
        feature_store.get_transaction_features = AsyncMock(return_value={})

        # Act
        analytics = await churn_predictor.get_churn_analytics(mock_db)

        # Assert
        assert isinstance(analytics, ChurnAnalytics)
        assert analytics.total_users > 0
        assert 0 <= analytics.avg_churn_probability <= 1
        assert analytics.risk_distribution is not None

    @pytest.mark.asyncio
    async def test_get_churn_analytics_includes_top_factors(
        self,
        churn_predictor,
        feature_store,
        mock_db,
    ):
        """Deve incluir top fatores de churn."""
        # Arrange
        feature_store.get_user_features = AsyncMock(
            return_value={
                "last_activity_days": 20,
            }
        )
        feature_store.get_engagement_features = AsyncMock(return_value={})
        feature_store.get_transaction_features = AsyncMock(return_value={})

        # Act
        analytics = await churn_predictor.get_churn_analytics(mock_db)

        # Assert
        assert "top_churn_factors" in analytics.__dict__


class TestRetentionActions:
    """Testes de ações de retenção."""

    def test_generate_actions_for_critical_risk(self, churn_predictor):
        """Deve gerar ações urgentes para risco crítico."""
        factors = [{"factor": "last_activity_days", "direction": "negative"}]
        features = {"total_spent": 3000}

        actions = churn_predictor._generate_retention_actions(
            ChurnRiskLevel.CRITICAL,
            factors,
            features,
        )

        assert len(actions) > 0
        assert any(a.priority == 1 for a in actions)

    def test_generate_actions_for_high_value_user(self, churn_predictor):
        """Deve sugerir VIP para usuário de alto valor."""
        factors = []
        features = {"total_spent": 10000}  # Alto valor

        actions = churn_predictor._generate_retention_actions(
            ChurnRiskLevel.HIGH,
            factors,
            features,
        )

        vip_actions = [a for a in actions if a.action_type == RetentionActionType.VIP_UPGRADE]
        assert len(vip_actions) > 0


class TestLTVCalculation:
    """Testes de cálculo de LTV em risco."""

    def test_calculate_ltv_at_risk_high_probability(self, churn_predictor):
        """LTV em risco deve ser proporcional à probabilidade."""
        total_spent = 5000
        high_prob = 0.8
        low_prob = 0.2

        ltv_high = churn_predictor._calculate_ltv_at_risk(high_prob, total_spent)
        ltv_low = churn_predictor._calculate_ltv_at_risk(low_prob, total_spent)

        assert ltv_high > ltv_low
        assert ltv_high > 0


class TestChurnDateEstimation:
    """Testes de estimativa de data de churn."""

    def test_estimate_churn_date_high_probability(self, churn_predictor):
        """Alta probabilidade deve resultar em data próxima."""
        date = churn_predictor._estimate_churn_date(0.9, 30)

        assert date is not None
        assert date > datetime.utcnow()
        assert date < datetime.utcnow() + timedelta(days=60)

    def test_estimate_churn_date_low_probability(self, churn_predictor):
        """Baixa probabilidade não deve estimar data."""
        date = churn_predictor._estimate_churn_date(0.2, 5)

        assert date is None


class TestTrendCalculation:
    """Testes de cálculo de tendência."""

    def test_calculate_trend_improving(self, churn_predictor):
        """Deve identificar tendência de melhora."""
        # Criar predictions com probabilidade decrescente
        predictions = []
        for i in range(20):
            pred = MagicMock()
            pred.churn_probability = 0.5 - i * 0.02  # Diminuindo
            predictions.append(pred)

        trend = churn_predictor._calculate_trend(predictions)
        assert trend == "improving"

    def test_calculate_trend_worsening(self, churn_predictor):
        """Deve identificar tendência de piora."""
        predictions = []
        for i in range(20):
            pred = MagicMock()
            pred.churn_probability = 0.3 + i * 0.02  # Aumentando
            predictions.append(pred)

        trend = churn_predictor._calculate_trend(predictions)
        assert trend == "worsening"

    def test_calculate_trend_stable(self, churn_predictor):
        """Deve identificar tendência estável."""
        predictions = []
        for _i in range(20):
            pred = MagicMock()
            pred.churn_probability = 0.5  # Constante
            predictions.append(pred)

        trend = churn_predictor._calculate_trend(predictions)
        assert trend == "stable"
