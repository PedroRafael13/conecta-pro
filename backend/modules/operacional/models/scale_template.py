"""
Modelo ScaleTemplate para armazenamento de templates de escalas.

Templates permitem reutilizar estruturas de escalas bem-sucedidas,
salvando padrões de alocação e configurações.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class ScaleTemplate(Base):
    """
    Modelo de Template de Escala.

    Armazena estruturas de escalas que podem ser reutilizadas em diferentes períodos,
    permitindo criar novas escalas rapidamente baseadas em padrões comprovados.

    Attributes:
        id: Identificador único
        tenant_id: ID do tenant (condomínio)
        name: Nome do template
        description: Descrição detalhada
        template_data: Estrutura da escala em formato JSON
        created_by: ID do usuário criador
        created_at: Data de criação
        updated_at: Data de atualização
        is_active: Se o template está ativo
        times_used: Quantas vezes foi utilizado
        last_used: Data da última utilização
    """

    __tablename__ = "scale_templates"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Tenant para isolamento multi-tenant
    tenant_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Informações do template
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Dados do template (estrutura da escala)
    template_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )
    """
    Estrutura esperada do template_data:
    {
        "scale_type": "12x36",
        "posts": ["post_id_1", "post_id_2"],
        "shifts_pattern": [
            {
                "employee_id": "emp_1",
                "post_id": "post_1",
                "days_of_week": [0, 1, 2],  # 0=segunda, 6=domingo
                "start_time": "08:00",
                "end_time": "17:00",
                "shift_type": "12x36",
                "is_night_shift": false,
                "break_minutes": 60
            }
        ],
        "config": {
            "shift_duration_hours": 12,
            "rest_duration_hours": 36,
            "night_shift_start": "19:00",
            "day_shift_start": "07:00",
            "consider_holidays": true,
            "holiday_multiplier": 2.0
        },
        "metadata": {
            "total_employees": 10,
            "coverage_percentage": 100,
            "total_shifts_per_month": 60,
            "avg_hours_per_employee": 180
        }
    }
    """

    # Controle de uso
    times_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_used: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    # Auditoria
    created_by: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Soft delete
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ScaleTemplate {self.name} (usado {self.times_used}x)>"

    @property
    def is_popular(self) -> bool:
        """Verifica se o template é popular (usado 5+ vezes)."""
        return self.times_used >= 5

    @property
    def total_employees(self) -> int:
        """Retorna total de funcionários no template."""
        metadata = self.template_data.get("metadata", {})
        return metadata.get("total_employees", 0)

    @property
    def coverage_percentage(self) -> float:
        """Retorna percentual de cobertura do template."""
        metadata = self.template_data.get("metadata", {})
        return metadata.get("coverage_percentage", 0.0)
