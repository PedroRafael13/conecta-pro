"""
Risk Profile Model - AI Fraud Detection

Modelo para perfis de risco de entidades.
"""

import enum
import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    Float,
    DateTime,
    Date,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from core.database import Base


class EntityType(str, enum.Enum):
    """Tipo de entidade."""

    USER = "user"
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    EMPLOYEE = "employee"
    DEVICE = "device"
    IP_ADDRESS = "ip_address"
    ACCOUNT = "account"
    CARD = "card"
    TRANSACTION = "transaction"
    SESSION = "session"
    EMAIL = "email"
    PHONE = "phone"
    DOCUMENT = "document"
    OTHER = "other"


class RiskLevel(str, enum.Enum):
    """Nivel de risco."""

    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    BLOCKED = "blocked"


class RiskProfile(Base):
    """
    Modelo de perfil de risco.

    Armazena o perfil de risco de uma entidade (usuario,
    dispositivo, conta, etc) baseado em historico e comportamento.
    """

    __tablename__ = "fraud_risk_profiles"

    # Identificacao
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Entidade
    entity_type = Column(
        Enum(EntityType),
        nullable=False,
        index=True,
    )
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    entity_identifier = Column(String(200), index=True)
    entity_name = Column(String(300))

    # Nivel de risco
    risk_level = Column(
        Enum(RiskLevel),
        default=RiskLevel.LOW,
        nullable=False,
        index=True,
    )
    risk_score = Column(Float, default=0, nullable=False)
    previous_risk_score = Column(Float)
    risk_score_change = Column(Float, default=0)

    # Scores detalhados
    behavior_score = Column(Float, default=0)
    transaction_score = Column(Float, default=0)
    velocity_score = Column(Float, default=0)
    identity_score = Column(Float, default=0)
    network_score = Column(Float, default=0)
    historical_score = Column(Float, default=0)

    # Fatores de risco
    risk_factors = Column(JSONB, default=[])
    """
    [
        {"factor": "high_transaction_volume", "weight": 0.3, "score": 25},
        {"factor": "unusual_login_location", "weight": 0.2, "score": 15},
        {"factor": "multiple_failed_logins", "weight": 0.1, "score": 10}
    ]
    """

    # Indicadores positivos
    trust_indicators = Column(JSONB, default=[])
    """
    [
        {"indicator": "verified_identity", "bonus": -10},
        {"indicator": "long_account_age", "bonus": -5}
    ]
    """

    # Historico de alertas
    total_alerts = Column(Integer, default=0)
    confirmed_frauds = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    last_alert_at = Column(DateTime)
    last_fraud_at = Column(DateTime)

    # Historico de transacoes
    total_transactions = Column(Integer, default=0)
    total_transaction_value = Column(Float, default=0)
    avg_transaction_value = Column(Float, default=0)
    max_transaction_value = Column(Float, default=0)
    suspicious_transactions = Column(Integer, default=0)

    # Comportamento de acesso
    total_logins = Column(Integer, default=0)
    failed_logins = Column(Integer, default=0)
    unique_ips = Column(Integer, default=0)
    unique_devices = Column(Integer, default=0)
    unique_locations = Column(Integer, default=0)
    last_login_at = Column(DateTime)
    last_ip = Column(String(45))
    last_device = Column(String(200))
    last_location = Column(String(200))

    # Padroes conhecidos
    known_ips = Column(ARRAY(String), default=[])
    known_devices = Column(ARRAY(String), default=[])
    known_locations = Column(ARRAY(String), default=[])
    typical_hours = Column(JSONB, default={})
    typical_days = Column(ARRAY(Integer), default=[])

    # Restricoes
    is_blocked = Column(Boolean, default=False)
    blocked_at = Column(DateTime)
    blocked_by = Column(UUID(as_uuid=True))
    blocked_reason = Column(Text)
    unblock_at = Column(DateTime)

    is_whitelisted = Column(Boolean, default=False)
    whitelisted_at = Column(DateTime)
    whitelisted_by = Column(UUID(as_uuid=True))
    whitelist_reason = Column(Text)

    is_watchlisted = Column(Boolean, default=False)
    watchlist_reason = Column(Text)
    watchlist_expires = Column(DateTime)

    # Limites
    transaction_limit_daily = Column(Float)
    transaction_limit_monthly = Column(Float)
    transaction_count_limit_daily = Column(Integer)
    requires_approval_above = Column(Float)

    # Verificacao
    identity_verified = Column(Boolean, default=False)
    identity_verified_at = Column(DateTime)
    document_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    address_verified = Column(Boolean, default=False)

    # ML
    ml_risk_score = Column(Float)
    ml_confidence = Column(Float)
    ml_model_version = Column(String(50))
    ml_last_scored = Column(DateTime)
    ml_features = Column(JSONB, default={})

    # Relacionamentos externos
    linked_profiles = Column(ARRAY(UUID(as_uuid=True)), default=[])
    shared_attributes = Column(JSONB, default={})

    # Periodo de analise
    analysis_start_date = Column(Date)
    analysis_end_date = Column(Date)
    days_analyzed = Column(Integer, default=0)

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_calculated_at = Column(DateTime)

    # Flags
    is_active = Column(Boolean, default=True, nullable=False)
    needs_review = Column(Boolean, default=False)
    auto_updated = Column(Boolean, default=True)

    # Notas
    notes = Column(Text)
    review_notes = Column(Text)
    tags = Column(ARRAY(String), default=[])

    def __repr__(self) -> str:
        return f"<RiskProfile {self.entity_type.value}:{self.entity_id} [{self.risk_level.value}]>"

    @property
    def fraud_rate(self) -> float:
        """Taxa de fraudes confirmadas."""
        if self.total_alerts == 0:
            return 0.0
        return (self.confirmed_frauds / self.total_alerts) * 100

    @property
    def false_positive_rate(self) -> float:
        """Taxa de falsos positivos."""
        if self.total_alerts == 0:
            return 0.0
        return (self.false_positives / self.total_alerts) * 100

    @property
    def is_high_risk(self) -> bool:
        """Verifica se e alto risco."""
        return self.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.BLOCKED)

    @property
    def is_restricted(self) -> bool:
        """Verifica se tem restricoes."""
        return self.is_blocked or self.is_watchlisted

    @property
    def verification_level(self) -> int:
        """Nivel de verificacao (0-5)."""
        level = 0
        if self.email_verified:
            level += 1
        if self.phone_verified:
            level += 1
        if self.document_verified:
            level += 1
        if self.identity_verified:
            level += 1
        if self.address_verified:
            level += 1
        return level

    def calculate_risk_score(self) -> float:
        """
        Calcula score de risco baseado nos fatores.

        Returns:
            Score de 0 a 100
        """
        # Guardar score anterior
        self.previous_risk_score = self.risk_score

        # Score base dos componentes
        base_score = (
            self.behavior_score * 0.25
            + self.transaction_score * 0.25
            + self.velocity_score * 0.15
            + self.identity_score * 0.15
            + self.network_score * 0.10
            + self.historical_score * 0.10
        )

        # Adicionar fatores de risco
        for factor in self.risk_factors:
            base_score += factor.get("score", 0) * factor.get("weight", 0.1)

        # Subtrair indicadores de confianca
        for indicator in self.trust_indicators:
            base_score += indicator.get("bonus", 0)

        # Ajuste por historico de fraude
        if self.confirmed_frauds > 0:
            base_score += min(self.confirmed_frauds * 10, 30)

        # Ajuste por verificacao
        base_score -= self.verification_level * 3

        # Normalizar
        self.risk_score = max(0, min(100, base_score))
        self.risk_score_change = self.risk_score - (self.previous_risk_score or 0)

        # Atualizar nivel
        self._update_risk_level()

        self.last_calculated_at = datetime.utcnow()
        return self.risk_score

    def _update_risk_level(self) -> None:
        """Atualiza nivel de risco baseado no score."""
        if self.is_blocked:
            self.risk_level = RiskLevel.BLOCKED
        elif self.risk_score >= 80:
            self.risk_level = RiskLevel.CRITICAL
        elif self.risk_score >= 60:
            self.risk_level = RiskLevel.HIGH
        elif self.risk_score >= 40:
            self.risk_level = RiskLevel.MEDIUM
        elif self.risk_score >= 20:
            self.risk_level = RiskLevel.LOW
        else:
            self.risk_level = RiskLevel.MINIMAL

    def add_risk_factor(
        self,
        factor: str,
        weight: float = 0.1,
        score: float = 10,
    ) -> None:
        """Adiciona fator de risco."""
        self.risk_factors = [
            f for f in self.risk_factors if f.get("factor") != factor
        ]
        self.risk_factors.append({
            "factor": factor,
            "weight": weight,
            "score": score,
            "added_at": datetime.utcnow().isoformat(),
        })

    def add_trust_indicator(self, indicator: str, bonus: float = -5) -> None:
        """Adiciona indicador de confianca."""
        self.trust_indicators = [
            i for i in self.trust_indicators if i.get("indicator") != indicator
        ]
        self.trust_indicators.append({
            "indicator": indicator,
            "bonus": bonus,
            "added_at": datetime.utcnow().isoformat(),
        })

    def record_login(
        self,
        ip: str,
        device: str,
        location: Optional[str] = None,
        success: bool = True,
    ) -> None:
        """Registra login."""
        self.total_logins += 1
        if not success:
            self.failed_logins += 1

        self.last_login_at = datetime.utcnow()
        self.last_ip = ip
        self.last_device = device
        if location:
            self.last_location = location

        # Atualizar conhecidos
        if ip and ip not in (self.known_ips or []):
            self.known_ips = (self.known_ips or []) + [ip]
            self.unique_ips = len(self.known_ips)

        if device and device not in (self.known_devices or []):
            self.known_devices = (self.known_devices or []) + [device]
            self.unique_devices = len(self.known_devices)

        if location and location not in (self.known_locations or []):
            self.known_locations = (self.known_locations or []) + [location]
            self.unique_locations = len(self.known_locations)

    def record_transaction(self, value: float, suspicious: bool = False) -> None:
        """Registra transacao."""
        self.total_transactions += 1
        self.total_transaction_value += value

        if value > (self.max_transaction_value or 0):
            self.max_transaction_value = value

        self.avg_transaction_value = (
            self.total_transaction_value / self.total_transactions
        )

        if suspicious:
            self.suspicious_transactions += 1

    def block(self, user_id: uuid.UUID, reason: str) -> None:
        """Bloqueia entidade."""
        self.is_blocked = True
        self.blocked_at = datetime.utcnow()
        self.blocked_by = user_id
        self.blocked_reason = reason
        self.risk_level = RiskLevel.BLOCKED

    def unblock(self) -> None:
        """Desbloqueia entidade."""
        self.is_blocked = False
        self.blocked_at = None
        self.blocked_by = None
        self.blocked_reason = None
        self._update_risk_level()
