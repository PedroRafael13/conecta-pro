"""Modelo KPIDefinition - Definições de KPIs de RH."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class KPICategory(str, Enum):
    """Categoria do KPI."""
    ATTENDANCE = "attendance"        # Frequência
    PUNCTUALITY = "punctuality"      # Pontualidade
    OVERTIME = "overtime"            # Horas extras
    PRODUCTIVITY = "productivity"    # Produtividade
    COMPLIANCE = "compliance"        # Conformidade CLT
    COST = "cost"                    # Custos
    TURNOVER = "turnover"            # Rotatividade
    SATISFACTION = "satisfaction"    # Satisfação
    CUSTOM = "custom"                # Personalizado


class KPIUnit(str, Enum):
    """Unidade de medida do KPI."""
    PERCENTAGE = "percentage"
    HOURS = "hours"
    MINUTES = "minutes"
    DAYS = "days"
    COUNT = "count"
    CURRENCY = "currency"
    RATIO = "ratio"
    SCORE = "score"


class KPIDirection(str, Enum):
    """Direção desejada do KPI."""
    UP = "up"              # Maior é melhor
    DOWN = "down"          # Menor é melhor
    TARGET = "target"      # Próximo ao alvo é melhor
    NEUTRAL = "neutral"    # Sem preferência


class KPIFrequency(str, Enum):
    """Frequência de cálculo."""
    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class KPIDefinition(Base):
    """Modelo de definição de KPI."""

    __tablename__ = "kpi_definitions"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    condominio_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True,
    )  # None = KPI global/padrão

    # Informações básicas
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(
        String(20),
        default=KPICategory.ATTENDANCE.value,
        index=True,
    )

    # Unidade e formato
    unit: Mapped[str] = mapped_column(
        String(20),
        default=KPIUnit.PERCENTAGE.value,
    )
    decimal_places: Mapped[int] = mapped_column(Integer, default=2)
    format_pattern: Mapped[Optional[str]] = mapped_column(String(50))
    prefix: Mapped[Optional[str]] = mapped_column(String(10))
    suffix: Mapped[Optional[str]] = mapped_column(String(10))

    # Direção e metas
    direction: Mapped[str] = mapped_column(
        String(10),
        default=KPIDirection.UP.value,
    )
    target_value: Mapped[Optional[float]] = mapped_column(Float)
    min_value: Mapped[Optional[float]] = mapped_column(Float)
    max_value: Mapped[Optional[float]] = mapped_column(Float)

    # Thresholds (% do target ou valores absolutos)
    threshold_critical: Mapped[Optional[float]] = mapped_column(Float)
    threshold_warning: Mapped[Optional[float]] = mapped_column(Float)
    threshold_good: Mapped[Optional[float]] = mapped_column(Float)
    threshold_excellent: Mapped[Optional[float]] = mapped_column(Float)

    # Cálculo
    calculation_formula: Mapped[Optional[str]] = mapped_column(Text)
    calculation_query: Mapped[Optional[str]] = mapped_column(Text)
    calculation_params: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    frequency: Mapped[str] = mapped_column(
        String(20),
        default=KPIFrequency.DAILY.value,
    )

    # Comparações
    enable_comparison: Mapped[bool] = mapped_column(Boolean, default=True)
    comparison_periods: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=lambda: ["previous_period", "same_period_last_year"],
    )

    # Benchmark
    industry_benchmark: Mapped[Optional[float]] = mapped_column(Float)
    benchmark_source: Mapped[Optional[str]] = mapped_column(String(200))

    # Alertas
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_recipients: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    alert_conditions: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Visualização
    default_chart_type: Mapped[str] = mapped_column(String(30), default="line_chart")
    color_scheme: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    icon: Mapped[Optional[str]] = mapped_column(String(50))

    # Drill-down
    drill_down_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    drill_down_dimensions: Mapped[Optional[list]] = mapped_column(
        JSONB,
        default=lambda: ["department", "employee", "date"],
    )

    # Metadados
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Ordenação e visibilidade
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    # Auditoria
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Índices
    __table_args__ = (
        Index("ix_kpi_definitions_condominio_category", "condominio_id", "category"),
        Index("ix_kpi_definitions_code", "code"),
    )

    def evaluate_status(self, value: float) -> str:
        """Avalia status do KPI baseado nos thresholds."""
        if self.direction == KPIDirection.UP.value:
            if self.threshold_excellent and value >= self.threshold_excellent:
                return "excellent"
            if self.threshold_good and value >= self.threshold_good:
                return "good"
            if self.threshold_warning and value >= self.threshold_warning:
                return "warning"
            return "critical"

        elif self.direction == KPIDirection.DOWN.value:
            if self.threshold_excellent and value <= self.threshold_excellent:
                return "excellent"
            if self.threshold_good and value <= self.threshold_good:
                return "good"
            if self.threshold_warning and value <= self.threshold_warning:
                return "warning"
            return "critical"

        elif self.direction == KPIDirection.TARGET.value:
            if not self.target_value:
                return "neutral"
            deviation = abs(value - self.target_value) / self.target_value * 100
            if deviation <= 5:
                return "excellent"
            if deviation <= 10:
                return "good"
            if deviation <= 20:
                return "warning"
            return "critical"

        return "neutral"

    def calculate_trend(self, current: float, previous: float) -> dict:
        """Calcula tendência entre valores."""
        if previous == 0:
            return {"direction": "neutral", "percentage": 0, "is_positive": True}

        change = ((current - previous) / previous) * 100
        is_positive = (
            (change > 0 and self.direction == KPIDirection.UP.value)
            or (change < 0 and self.direction == KPIDirection.DOWN.value)
        )

        return {
            "direction": "up" if change > 0 else "down" if change < 0 else "neutral",
            "percentage": round(abs(change), 2),
            "is_positive": is_positive,
        }

    def format_value(self, value: float) -> str:
        """Formata valor para exibição."""
        formatted = f"{value:.{self.decimal_places}f}"

        if self.format_pattern:
            try:
                formatted = self.format_pattern.format(value=value)
            except (ValueError, KeyError):
                pass

        result = f"{self.prefix or ''}{formatted}{self.suffix or ''}"

        if self.unit == KPIUnit.PERCENTAGE.value and not self.suffix:
            result += "%"

        return result

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "unit": self.unit,
            "direction": self.direction,
            "target_value": self.target_value,
            "is_featured": self.is_featured,
        }


# KPIs padrão de RH
DEFAULT_KPIS = [
    {
        "code": "ABSENTEEISM_RATE",
        "name": "Taxa de Absenteísmo",
        "description": "Percentual de faltas em relação aos dias úteis",
        "category": KPICategory.ATTENDANCE.value,
        "unit": KPIUnit.PERCENTAGE.value,
        "direction": KPIDirection.DOWN.value,
        "target_value": 3.0,
        "threshold_excellent": 2.0,
        "threshold_good": 3.0,
        "threshold_warning": 5.0,
        "threshold_critical": 8.0,
        "industry_benchmark": 4.5,
    },
    {
        "code": "PUNCTUALITY_RATE",
        "name": "Taxa de Pontualidade",
        "description": "Percentual de entradas no horário",
        "category": KPICategory.PUNCTUALITY.value,
        "unit": KPIUnit.PERCENTAGE.value,
        "direction": KPIDirection.UP.value,
        "target_value": 95.0,
        "threshold_excellent": 98.0,
        "threshold_good": 95.0,
        "threshold_warning": 90.0,
        "threshold_critical": 85.0,
    },
    {
        "code": "OVERTIME_HOURS",
        "name": "Horas Extras Médias",
        "description": "Média de horas extras por funcionário",
        "category": KPICategory.OVERTIME.value,
        "unit": KPIUnit.HOURS.value,
        "direction": KPIDirection.TARGET.value,
        "target_value": 10.0,
        "threshold_excellent": 8.0,
        "threshold_good": 12.0,
        "threshold_warning": 20.0,
        "threshold_critical": 30.0,
    },
    {
        "code": "BANK_HOURS_BALANCE",
        "name": "Saldo Banco de Horas",
        "description": "Saldo total do banco de horas",
        "category": KPICategory.OVERTIME.value,
        "unit": KPIUnit.HOURS.value,
        "direction": KPIDirection.NEUTRAL.value,
    },
    {
        "code": "CLT_COMPLIANCE",
        "name": "Conformidade CLT",
        "description": "Percentual de conformidade com regras trabalhistas",
        "category": KPICategory.COMPLIANCE.value,
        "unit": KPIUnit.PERCENTAGE.value,
        "direction": KPIDirection.UP.value,
        "target_value": 100.0,
        "threshold_excellent": 100.0,
        "threshold_good": 98.0,
        "threshold_warning": 95.0,
        "threshold_critical": 90.0,
    },
    {
        "code": "OVERTIME_COST",
        "name": "Custo de Horas Extras",
        "description": "Custo total com horas extras no período",
        "category": KPICategory.COST.value,
        "unit": KPIUnit.CURRENCY.value,
        "direction": KPIDirection.DOWN.value,
        "prefix": "R$ ",
    },
    {
        "code": "WORKED_HOURS_EFFICIENCY",
        "name": "Eficiência de Horas Trabalhadas",
        "description": "Horas trabalhadas vs horas contratadas",
        "category": KPICategory.PRODUCTIVITY.value,
        "unit": KPIUnit.PERCENTAGE.value,
        "direction": KPIDirection.TARGET.value,
        "target_value": 100.0,
        "threshold_excellent": 100.0,
        "threshold_good": 98.0,
        "threshold_warning": 95.0,
        "threshold_critical": 90.0,
    },
]
