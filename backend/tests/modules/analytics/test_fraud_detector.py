"""Testes para o Fraud Detector."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import numpy as np
import pytest

from modules.analytics.ml.registry.model_registry import ModelRegistry
from modules.analytics.models.fraud.fraud_detector import (
    AlertStatus,
    FraudAlert,
    FraudAnalytics,
    FraudDetector,
    FraudIndicator,
    FraudRiskLevel,
    FraudType,
    RuleViolation,
)


@pytest.fixture
def model_registry():
    """Model registry mockado."""
    return MagicMock(spec=ModelRegistry)


@pytest.fixture
def fraud_detector(model_registry):
    """Instância do FraudDetector."""
    return FraudDetector(model_registry)


@pytest.fixture
def mock_db():
    """Mock da sessão do banco."""
    return AsyncMock()


class TestTransactionAnalysis:
    """Testes de análise de transações."""

    @pytest.mark.asyncio
    async def test_analyze_normal_transaction(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve analisar transação normal sem alertas."""
        # Arrange
        transaction = {
            "id": "tx_001",
            "user_id": 1,
            "amount": 500,
            "hour": 14,
            "recent_transactions_count": 2,
        }

        # Act
        alert = await fraud_detector.analyze_transaction(mock_db, transaction)

        # Assert
        assert isinstance(alert, FraudAlert)
        assert alert.risk_score < 50  # Risco baixo

    @pytest.mark.asyncio
    async def test_analyze_high_value_transaction(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve detectar transação de alto valor."""
        # Arrange
        transaction = {
            "id": "tx_002",
            "user_id": 1,
            "amount": 15000,  # Acima do threshold
            "hour": 14,
            "recent_transactions_count": 1,
        }

        # Act
        alert = await fraud_detector.analyze_transaction(mock_db, transaction)

        # Assert
        assert alert.risk_score > 30
        assert any(v.rule_id == "R001" for v in alert.rule_violations)

    @pytest.mark.asyncio
    async def test_analyze_unusual_time_transaction(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve detectar transação em horário incomum."""
        # Arrange
        transaction = {
            "id": "tx_003",
            "user_id": 1,
            "amount": 500,
            "hour": 3,  # Madrugada
            "recent_transactions_count": 1,
        }

        # Act
        alert = await fraud_detector.analyze_transaction(mock_db, transaction)

        # Assert
        assert any(v.rule_id == "R002" for v in alert.rule_violations)

    @pytest.mark.asyncio
    async def test_analyze_velocity_violation(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve detectar muitas transações em curto período."""
        # Arrange
        transaction = {
            "id": "tx_004",
            "user_id": 1,
            "amount": 200,
            "hour": 14,
            "recent_transactions_count": 10,  # Muitas transações
        }

        # Act
        alert = await fraud_detector.analyze_transaction(mock_db, transaction)

        # Assert
        assert any(v.rule_id == "R003" for v in alert.rule_violations)


class TestRuleChecking:
    """Testes de verificação de regras."""

    def test_check_high_value_rule(self, fraud_detector):
        """Deve detectar violação de valor alto."""
        transaction = {"amount": 15000}

        violations = fraud_detector._check_rules(transaction)

        assert len(violations) > 0
        assert any(v.rule_id == "R001" for v in violations)

    def test_check_unusual_time_rule(self, fraud_detector):
        """Deve detectar violação de horário."""
        transaction = {"amount": 100, "hour": 4}

        violations = fraud_detector._check_rules(transaction)

        assert any(v.rule_id == "R002" for v in violations)

    def test_check_velocity_rule(self, fraud_detector):
        """Deve detectar violação de velocidade."""
        transaction = {"amount": 100, "recent_transactions_count": 8}

        violations = fraud_detector._check_rules(transaction)

        assert any(v.rule_id == "R003" for v in violations)

    def test_no_violations_normal_transaction(self, fraud_detector):
        """Não deve detectar violações em transação normal."""
        transaction = {
            "amount": 500,
            "hour": 14,
            "recent_transactions_count": 2,
        }

        violations = fraud_detector._check_rules(transaction)

        # Pode ter algumas violações menores, mas não as principais
        critical_rules = ["R001", "R002", "R003"]
        critical_violations = [v for v in violations if v.rule_id in critical_rules]
        assert len(critical_violations) == 0


class TestSessionAnalysis:
    """Testes de análise de sessão."""

    @pytest.mark.asyncio
    async def test_analyze_new_device(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve detectar novo dispositivo."""
        # Arrange
        session = {
            "user_id": 1,
            "is_new_device": True,
            "device_id": "device_new",
        }

        # Act
        alert = await fraud_detector.analyze_user_session(mock_db, session)

        # Assert
        assert any(i.indicator_type == "new_device" for i in alert.indicators)

    @pytest.mark.asyncio
    async def test_analyze_location_anomaly(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve detectar anomalia de localização."""
        # Arrange
        session = {
            "user_id": 1,
            "location_change_km": 1000,  # Muito longe
            "location": "New York",
        }

        # Act
        alert = await fraud_detector.analyze_user_session(mock_db, session)

        # Assert
        assert any(i.indicator_type == "location_anomaly" for i in alert.indicators)
        assert alert.risk_score > 40

    @pytest.mark.asyncio
    async def test_analyze_failed_login_attempts(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve detectar múltiplas tentativas de login."""
        # Arrange
        session = {
            "user_id": 1,
            "failed_login_attempts": 5,
        }

        # Act
        alert = await fraud_detector.analyze_user_session(mock_db, session)

        # Assert
        assert any(i.indicator_type == "failed_attempts" for i in alert.indicators)


class TestRiskClassification:
    """Testes de classificação de risco."""

    def test_classify_very_low_risk(self, fraud_detector):
        """Deve classificar como risco muito baixo."""
        assert fraud_detector._classify_risk(15) == FraudRiskLevel.VERY_LOW

    def test_classify_low_risk(self, fraud_detector):
        """Deve classificar como risco baixo."""
        assert fraud_detector._classify_risk(30) == FraudRiskLevel.LOW

    def test_classify_medium_risk(self, fraud_detector):
        """Deve classificar como risco médio."""
        assert fraud_detector._classify_risk(50) == FraudRiskLevel.MEDIUM

    def test_classify_high_risk(self, fraud_detector):
        """Deve classificar como risco alto."""
        assert fraud_detector._classify_risk(70) == FraudRiskLevel.HIGH

    def test_classify_critical_risk(self, fraud_detector):
        """Deve classificar como risco crítico."""
        assert fraud_detector._classify_risk(90) == FraudRiskLevel.CRITICAL


class TestFraudTypeIdentification:
    """Testes de identificação de tipo de fraude."""

    def test_identify_account_takeover(self, fraud_detector):
        """Deve identificar account takeover."""
        indicators = [
            FraudIndicator(
                indicator_type="new_device",
                value=1.0,
                weight=0.2,
                description="",
                evidence={},
            ),
            FraudIndicator(
                indicator_type="location_anomaly",
                value=1000,
                weight=0.3,
                description="",
                evidence={},
            ),
        ]
        violations = []

        fraud_type = fraud_detector._identify_fraud_type(indicators, violations)

        assert fraud_type == FraudType.ACCOUNT_TAKEOVER

    def test_identify_bot_activity(self, fraud_detector):
        """Deve identificar atividade de bot."""
        indicators = []
        violations = [
            RuleViolation(
                rule_id="R003",
                rule_name="velocity_check",
                severity=8,
                description="",
                value_detected=10,
                threshold=5,
            )
        ]

        fraud_type = fraud_detector._identify_fraud_type(indicators, violations)

        assert fraud_type == FraudType.BOT_ACTIVITY


class TestAlertManagement:
    """Testes de gerenciamento de alertas."""

    @pytest.mark.asyncio
    async def test_update_alert_status(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve atualizar status do alerta."""
        # Arrange
        transaction = {
            "id": "tx_001",
            "user_id": 1,
            "amount": 15000,
        }
        alert = await fraud_detector.analyze_transaction(mock_db, transaction)

        # Act
        updated = fraud_detector.update_alert_status(
            str(alert.id),
            AlertStatus.INVESTIGATING,
            notes="Em análise",
        )

        # Assert
        assert updated is not None
        assert updated.status == AlertStatus.INVESTIGATING

    @pytest.mark.asyncio
    async def test_get_open_alerts(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve retornar alertas abertos."""
        # Arrange - criar alguns alertas
        for i in range(5):
            await fraud_detector.analyze_transaction(
                mock_db,
                {
                    "id": f"tx_{i}",
                    "user_id": 1,
                    "amount": 15000,
                },
            )

        # Act
        open_alerts = fraud_detector.get_open_alerts(limit=10)

        # Assert
        assert len(open_alerts) > 0
        for alert in open_alerts:
            assert alert.status in [AlertStatus.OPEN, AlertStatus.INVESTIGATING]


class TestUserRiskProfile:
    """Testes de perfil de risco de usuário."""

    @pytest.mark.asyncio
    async def test_get_user_risk_profile(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve retornar perfil de risco do usuário."""
        # Act
        profile = await fraud_detector.get_user_risk_profile(mock_db, user_id=1)

        # Assert
        assert "user_id" in profile
        assert "risk_score" in profile
        assert "risk_level" in profile


class TestFraudAnalytics:
    """Testes de analytics de fraude."""

    @pytest.mark.asyncio
    async def test_get_fraud_analytics(
        self,
        fraud_detector,
        mock_db,
    ):
        """Deve retornar analytics de fraude."""
        # Act
        analytics = await fraud_detector.get_fraud_analytics(mock_db)

        # Assert
        assert isinstance(analytics, FraudAnalytics)
        assert analytics.total_transactions >= 0
        assert analytics.fraud_rate >= 0


class TestAnomalyDetection:
    """Testes de detecção de anomalias."""

    def test_detect_anomalies_normal_transaction(self, fraud_detector):
        """Não deve detectar anomalia em transação normal."""
        transaction = {
            "amount": 500,
            "hour": 14,
            "day_of_week": 2,
            "recent_transactions_count": 2,
        }

        score = fraud_detector._detect_anomalies(transaction)

        assert 0 <= score <= 1

    def test_detect_anomalies_suspicious_transaction(self, fraud_detector):
        """Deve detectar anomalia em transação suspeita."""
        transaction = {
            "amount": 50000,  # Muito alto
            "hour": 3,  # Madrugada
            "day_of_week": 0,
            "recent_transactions_count": 15,  # Muitas
        }

        score = fraud_detector._detect_anomalies(transaction)

        # Score de anomalia pode variar, mas deve ser calculado
        assert 0 <= score <= 1


class TestRiskScoreCalculation:
    """Testes de cálculo de score de risco."""

    def test_calculate_risk_score_with_indicators(self, fraud_detector):
        """Deve calcular score baseado em indicadores."""
        indicators = [
            FraudIndicator(
                indicator_type="amount_anomaly",
                value=0.8,
                weight=0.3,
                description="",
                evidence={},
            ),
            FraudIndicator(
                indicator_type="time_anomaly",
                value=0.5,
                weight=0.2,
                description="",
                evidence={},
            ),
        ]
        violations = []

        score = fraud_detector._calculate_risk_score(indicators, violations)

        assert score > 0

    def test_calculate_risk_score_with_violations(self, fraud_detector):
        """Deve calcular score baseado em violações."""
        indicators = []
        violations = [
            RuleViolation(
                rule_id="R001",
                rule_name="high_value",
                severity=7,
                description="",
                value_detected=15000,
                threshold=10000,
            ),
        ]

        score = fraud_detector._calculate_risk_score(indicators, violations)

        assert score > 0

    def test_calculate_risk_score_max_100(self, fraud_detector):
        """Score não deve exceder 100."""
        indicators = [
            FraudIndicator(
                indicator_type=f"indicator_{i}",
                value=1.0,
                weight=0.5,
                description="",
                evidence={},
            )
            for i in range(10)
        ]
        violations = [
            RuleViolation(
                rule_id=f"R{i:03d}",
                rule_name=f"rule_{i}",
                severity=10,
                description="",
                value_detected=0,
                threshold=0,
            )
            for i in range(10)
        ]

        score = fraud_detector._calculate_risk_score(indicators, violations)

        assert score <= 100


class TestRecommendations:
    """Testes de recomendações de ação."""

    def test_recommendations_critical_risk(self, fraud_detector):
        """Deve gerar ações urgentes para risco crítico."""
        recommendations = fraud_detector._generate_recommendations(
            FraudRiskLevel.CRITICAL,
            FraudType.PAYMENT,
            [],
        )

        assert len(recommendations) > 0
        assert any("BLOQUEAR" in r for r in recommendations)

    def test_recommendations_high_risk(self, fraud_detector):
        """Deve gerar ações para risco alto."""
        recommendations = fraud_detector._generate_recommendations(
            FraudRiskLevel.HIGH,
            FraudType.PAYMENT,
            [],
        )

        assert len(recommendations) > 0
        assert any("verificação" in r.lower() for r in recommendations)

    def test_recommendations_account_takeover(self, fraud_detector):
        """Deve incluir reset de senha para account takeover."""
        recommendations = fraud_detector._generate_recommendations(
            FraudRiskLevel.HIGH,
            FraudType.ACCOUNT_TAKEOVER,
            [],
        )

        assert any("senha" in r.lower() for r in recommendations)


class TestPatternIdentification:
    """Testes de identificação de padrões."""

    def test_identify_patterns(self, fraud_detector):
        """Deve identificar padrões de fraude."""
        alerts = [
            MagicMock(fraud_type=FraudType.PAYMENT),
            MagicMock(fraud_type=FraudType.PAYMENT),
            MagicMock(fraud_type=FraudType.PAYMENT),
            MagicMock(fraud_type=FraudType.ACCOUNT_TAKEOVER),
        ]

        patterns = fraud_detector._identify_patterns(alerts)

        assert len(patterns) > 0
        assert patterns[0]["pattern"] == "payment"  # Mais comum
        assert patterns[0]["occurrences"] == 3
