"""Model para previsoes de fluxo de caixa."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class ForecastPeriodType(str, Enum):
    """Tipo de periodo da previsao."""

    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"


class ForecastStatus(str, Enum):
    """Status da previsao."""

    RASCUNHO = "rascunho"
    ATIVA = "ativa"
    REVISADA = "revisada"
    CONCLUIDA = "concluida"
    ARQUIVADA = "arquivada"


class ForecastConfidence(str, Enum):
    """Nivel de confianca da previsao."""

    MUITO_BAIXA = "muito_baixa"  # < 40%
    BAIXA = "baixa"  # 40-60%
    MEDIA = "media"  # 60-75%
    ALTA = "alta"  # 75-90%
    MUITO_ALTA = "muito_alta"  # > 90%


class CashFlowForecast(Base):
    """Previsao de fluxo de caixa."""

    __tablename__ = "cashflow_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    reference = Column(String(50), nullable=True)  # Ex: "2025/Q1"

    # Periodo
    period_type = Column(String(20), nullable=False, default=ForecastPeriodType.MENSAL.value)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    forecast_date = Column(Date, nullable=False)  # Data para a qual a previsao foi feita

    # Status
    status = Column(String(20), nullable=False, default=ForecastStatus.RASCUNHO.value)

    # === PREVISOES (valores esperados) ===
    # Entradas previstas
    expected_inflows = Column(Numeric(15, 2), default=Decimal("0"))
    expected_receivables = Column(Numeric(15, 2), default=Decimal("0"))  # De contas a receber
    expected_other_income = Column(Numeric(15, 2), default=Decimal("0"))  # Outros

    # Saidas previstas
    expected_outflows = Column(Numeric(15, 2), default=Decimal("0"))
    expected_payables = Column(Numeric(15, 2), default=Decimal("0"))  # De contas a pagar
    expected_other_expenses = Column(Numeric(15, 2), default=Decimal("0"))  # Outros

    # Saldos previstos
    expected_opening_balance = Column(Numeric(15, 2), default=Decimal("0"))
    expected_closing_balance = Column(Numeric(15, 2), default=Decimal("0"))
    expected_net_flow = Column(Numeric(15, 2), default=Decimal("0"))  # Fluxo liquido

    # === REALIZADOS (valores efetivos) ===
    actual_inflows = Column(Numeric(15, 2), nullable=True)
    actual_outflows = Column(Numeric(15, 2), nullable=True)
    actual_opening_balance = Column(Numeric(15, 2), nullable=True)
    actual_closing_balance = Column(Numeric(15, 2), nullable=True)
    actual_net_flow = Column(Numeric(15, 2), nullable=True)

    # === VARIACOES ===
    inflows_variance = Column(Numeric(15, 2), nullable=True)
    outflows_variance = Column(Numeric(15, 2), nullable=True)
    balance_variance = Column(Numeric(15, 2), nullable=True)
    inflows_variance_pct = Column(Numeric(8, 2), nullable=True)  # Percentual
    outflows_variance_pct = Column(Numeric(8, 2), nullable=True)
    balance_variance_pct = Column(Numeric(8, 2), nullable=True)

    # === IA E CONFIANCA ===
    # Nivel de confianca da previsao
    confidence_level = Column(Integer, default=50)  # 0-100
    confidence_category = Column(
        String(20),
        default=ForecastConfidence.MEDIA.value,
    )

    # Gerado por IA
    ai_generated = Column(Boolean, default=False)
    ai_model_version = Column(String(50), nullable=True)
    ai_generated_at = Column(DateTime, nullable=True)

    # Fatores considerados pela IA
    ai_factors = Column(JSONB, default=dict)
    # {"historico_pagamento": 0.85, "sazonalidade": 0.72, "inadimplencia": 0.15, ...}

    # Riscos identificados
    risks = Column(JSONB, default=list)
    # [{"type": "inadimplencia", "probability": 0.3, "impact": 5000, "mitigation": "..."}]

    # Oportunidades identificadas
    opportunities = Column(JSONB, default=list)
    # [{"type": "economia", "probability": 0.6, "value": 2000, "action": "..."}]

    # === DETALHAMENTO ===
    # Breakdown por categoria
    inflows_breakdown = Column(JSONB, default=dict)
    # {"taxa_condominial": 50000, "reservas": 5000, "multas": 1000, ...}

    outflows_breakdown = Column(JSONB, default=dict)
    # {"folha": 30000, "manutencao": 10000, "energia": 5000, ...}

    # Previsao diaria/semanal dentro do periodo
    daily_forecast = Column(JSONB, default=list)
    # [{"date": "2025-01-01", "inflows": 1000, "outflows": 500, "balance": 500}, ...]

    # Cenarios
    scenarios = Column(JSONB, default=dict)
    # {
    #   "pessimista": {"inflows": 45000, "outflows": 55000, "balance": -10000},
    #   "realista": {"inflows": 50000, "outflows": 50000, "balance": 0},
    #   "otimista": {"inflows": 55000, "outflows": 45000, "balance": 10000}
    # }

    # === PREMISSAS ===
    assumptions = Column(JSONB, default=list)
    # ["Inadimplencia de 5%", "Aumento de 3% na energia", ...]

    # === ALERTAS ===
    alerts = Column(JSONB, default=list)
    # [{"type": "saldo_negativo", "date": "2025-01-15", "amount": -5000, "severity": "high"}]

    has_negative_balance_alert = Column(Boolean, default=False)
    has_high_outflow_alert = Column(Boolean, default=False)
    has_low_inflow_alert = Column(Boolean, default=False)

    # === METAS ===
    target_balance = Column(Numeric(15, 2), nullable=True)
    target_achieved = Column(Boolean, nullable=True)

    # Observacoes
    notes = Column(Text, nullable=True)
    review_notes = Column(Text, nullable=True)

    # Revisao
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Controle
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_cashflow_forecasts_condominio", "condominio_id"),
        Index("ix_cashflow_forecasts_period", "period_start", "period_end"),
        Index("ix_cashflow_forecasts_date", "forecast_date"),
        Index("ix_cashflow_forecasts_status", "status"),
        Index(
            "ix_cashflow_forecasts_condominio_date",
            "condominio_id",
            "forecast_date",
        ),
    )

    def __repr__(self) -> str:
        return f"<CashFlowForecast {self.name} - {self.forecast_date}>"

    @property
    def is_active(self) -> bool:
        """Verifica se esta ativa."""
        return self.status == ForecastStatus.ATIVA.value

    @property
    def is_past(self) -> bool:
        """Verifica se o periodo ja passou."""
        return self.period_end < date.today()

    @property
    def is_current(self) -> bool:
        """Verifica se e o periodo atual."""
        today = date.today()
        return self.period_start <= today <= self.period_end

    @property
    def is_future(self) -> bool:
        """Verifica se e periodo futuro."""
        return self.period_start > date.today()

    @property
    def has_actuals(self) -> bool:
        """Verifica se tem valores realizados."""
        return self.actual_closing_balance is not None

    @property
    def accuracy(self) -> Optional[float]:
        """Calcula precisao da previsao (para periodos passados)."""
        if not self.has_actuals or self.expected_closing_balance == 0:
            return None
        variance = abs(self.balance_variance or Decimal("0"))
        expected = abs(self.expected_closing_balance)
        if expected == 0:
            return 100.0 if variance == 0 else 0.0
        return max(0, 100 - float(variance / expected * 100))

    def calculate_expected_values(self) -> None:
        """Calcula valores esperados."""
        self.expected_inflows = (self.expected_receivables or Decimal("0")) + (
            self.expected_other_income or Decimal("0")
        )
        self.expected_outflows = (self.expected_payables or Decimal("0")) + (
            self.expected_other_expenses or Decimal("0")
        )
        self.expected_net_flow = self.expected_inflows - self.expected_outflows
        self.expected_closing_balance = (
            self.expected_opening_balance or Decimal("0")
        ) + self.expected_net_flow

    def calculate_variances(self) -> None:
        """Calcula variacoes entre previsto e realizado."""
        if self.actual_inflows is not None:
            self.inflows_variance = self.actual_inflows - self.expected_inflows
            if self.expected_inflows != 0:
                self.inflows_variance_pct = Decimal(
                    str(float(self.inflows_variance / self.expected_inflows * 100))
                )

        if self.actual_outflows is not None:
            self.outflows_variance = self.actual_outflows - self.expected_outflows
            if self.expected_outflows != 0:
                self.outflows_variance_pct = Decimal(
                    str(float(self.outflows_variance / self.expected_outflows * 100))
                )

        if self.actual_closing_balance is not None:
            self.balance_variance = self.actual_closing_balance - self.expected_closing_balance
            if self.expected_closing_balance != 0:
                self.balance_variance_pct = Decimal(
                    str(float(self.balance_variance / self.expected_closing_balance * 100))
                )

        # Calcula fluxo liquido realizado
        if self.actual_inflows is not None and self.actual_outflows is not None:
            self.actual_net_flow = self.actual_inflows - self.actual_outflows

    def update_confidence(self, level: int) -> None:
        """Atualiza nivel de confianca."""
        self.confidence_level = max(0, min(100, level))

        # Define categoria
        if level < 40:
            self.confidence_category = ForecastConfidence.MUITO_BAIXA.value
        elif level < 60:
            self.confidence_category = ForecastConfidence.BAIXA.value
        elif level < 75:
            self.confidence_category = ForecastConfidence.MEDIA.value
        elif level < 90:
            self.confidence_category = ForecastConfidence.ALTA.value
        else:
            self.confidence_category = ForecastConfidence.MUITO_ALTA.value

    def add_risk(
        self,
        risk_type: str,
        probability: float,
        impact: Decimal,
        mitigation: str,
    ) -> None:
        """Adiciona risco identificado."""
        if self.risks is None:
            self.risks = []

        self.risks.append(
            {
                "id": str(uuid.uuid4()),
                "type": risk_type,
                "probability": probability,
                "impact": float(impact),
                "mitigation": mitigation,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    def add_opportunity(
        self,
        opportunity_type: str,
        probability: float,
        value: Decimal,
        action: str,
    ) -> None:
        """Adiciona oportunidade identificada."""
        if self.opportunities is None:
            self.opportunities = []

        self.opportunities.append(
            {
                "id": str(uuid.uuid4()),
                "type": opportunity_type,
                "probability": probability,
                "value": float(value),
                "action": action,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    def add_alert(
        self,
        alert_type: str,
        alert_date: date,
        amount: Decimal,
        severity: str,
        message: str,
    ) -> None:
        """Adiciona alerta."""
        if self.alerts is None:
            self.alerts = []

        self.alerts.append(
            {
                "id": str(uuid.uuid4()),
                "type": alert_type,
                "date": alert_date.isoformat(),
                "amount": float(amount),
                "severity": severity,
                "message": message,
            }
        )

        # Atualiza flags
        if alert_type == "saldo_negativo":
            self.has_negative_balance_alert = True
        elif alert_type == "saida_alta":
            self.has_high_outflow_alert = True
        elif alert_type == "entrada_baixa":
            self.has_low_inflow_alert = True

    def activate(self) -> None:
        """Ativa a previsao."""
        self.status = ForecastStatus.ATIVA.value

    def complete(self) -> None:
        """Conclui a previsao (apos periodo passar)."""
        self.status = ForecastStatus.CONCLUIDA.value

    def archive(self) -> None:
        """Arquiva a previsao."""
        self.status = ForecastStatus.ARQUIVADA.value

    def review(self, user_id: uuid.UUID, notes: Optional[str] = None) -> None:
        """Marca como revisada."""
        self.status = ForecastStatus.REVISADA.value
        self.reviewed_at = datetime.utcnow()
        self.reviewed_by = user_id
        self.review_notes = notes

    def mark_as_ai_generated(self, model_version: str) -> None:
        """Marca como gerada por IA."""
        self.ai_generated = True
        self.ai_model_version = model_version
        self.ai_generated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte para dicionario."""
        return {
            "id": str(self.id),
            "condominio_id": str(self.condominio_id),
            "name": self.name,
            "description": self.description,
            "reference": self.reference,
            "period_type": self.period_type,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "forecast_date": self.forecast_date.isoformat(),
            "status": self.status,
            "expected_inflows": float(self.expected_inflows or 0),
            "expected_outflows": float(self.expected_outflows or 0),
            "expected_opening_balance": float(self.expected_opening_balance or 0),
            "expected_closing_balance": float(self.expected_closing_balance or 0),
            "expected_net_flow": float(self.expected_net_flow or 0),
            "actual_inflows": float(self.actual_inflows) if self.actual_inflows else None,
            "actual_outflows": float(self.actual_outflows) if self.actual_outflows else None,
            "actual_closing_balance": (
                float(self.actual_closing_balance) if self.actual_closing_balance else None
            ),
            "balance_variance": float(self.balance_variance) if self.balance_variance else None,
            "confidence_level": self.confidence_level,
            "confidence_category": self.confidence_category,
            "ai_generated": self.ai_generated,
            "has_actuals": self.has_actuals,
            "accuracy": self.accuracy,
            "is_current": self.is_current,
            "has_negative_balance_alert": self.has_negative_balance_alert,
            "risks_count": len(self.risks or []),
            "opportunities_count": len(self.opportunities or []),
            "alerts_count": len(self.alerts or []),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
