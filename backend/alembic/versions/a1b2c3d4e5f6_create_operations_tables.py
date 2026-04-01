"""Create operations tables (posts, scales, shifts, allocations, substitutions, time_bank).

Revision ID: a1b2c3d4e5f6
Revises: f6g8h9i0j1k2
Create Date: 2024-12-30 06:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "f6g8h9i0j1k2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create operations module tables."""

    # ====================
    # Table: posts (Postos de Trabalho)
    # ====================
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "post_type",
            sa.String(50),
            nullable=False,
            server_default="vigilancia",
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "shift_type",
            sa.String(50),
            nullable=False,
            server_default="12x36",
        ),
        # Localização
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("zip_code", sa.String(10), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        # Relacionamentos
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Requisitos
        sa.Column("required_headcount", sa.Integer, nullable=False, server_default="1"),
        sa.Column("current_headcount", sa.Integer, nullable=False, server_default="0"),
        sa.Column("requires_armed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("requires_vehicle", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("requires_experience_months", sa.Integer, nullable=False, server_default="0"),
        sa.Column("required_certifications", postgresql.JSONB, nullable=True),
        # Configurações
        sa.Column("shift_start_time", sa.Time, nullable=True),
        sa.Column("shift_end_time", sa.Time, nullable=True),
        sa.Column("break_duration_minutes", sa.Integer, nullable=False, server_default="60"),
        sa.Column("night_shift_bonus_percent", sa.Float, nullable=False, server_default="20.0"),
        sa.Column("hazard_pay_percent", sa.Float, nullable=False, server_default="0.0"),
        # Valores
        sa.Column("hourly_rate", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("monthly_cost", sa.Float, nullable=False, server_default="0.0"),
        # Contato
        sa.Column("supervisor_name", sa.String(200), nullable=True),
        sa.Column("supervisor_phone", sa.String(20), nullable=True),
        sa.Column("emergency_contact", sa.String(200), nullable=True),
        sa.Column("emergency_phone", sa.String(20), nullable=True),
        # Metadados
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_posts_code", "posts", ["code"])
    op.create_index("ix_posts_status", "posts", ["status"])
    op.create_index("ix_posts_contract_id", "posts", ["contract_id"])
    op.create_index("ix_posts_client_id", "posts", ["client_id"])
    op.create_index("ix_posts_city_state", "posts", ["city", "state"])

    # ====================
    # Table: scales (Escalas)
    # ====================
    op.create_table(
        "scales",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "scale_type",
            sa.String(50),
            nullable=False,
            server_default="12x36",
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("month", sa.Integer, nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        # Datas
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        # Métricas
        sa.Column("total_shifts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("filled_shifts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_hours", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("overtime_hours", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("estimated_cost", sa.Float, nullable=False, server_default="0.0"),
        # Configuração
        sa.Column("config", postgresql.JSONB, nullable=True),
        # Aprovação
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        # Publicação
        sa.Column("published_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("published_at", sa.DateTime, nullable=True),
        # Metadados
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Foreign keys
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_scales_post_id", "scales", ["post_id"])
    op.create_index("ix_scales_status", "scales", ["status"])
    op.create_index("ix_scales_month_year", "scales", ["month", "year"])
    op.create_unique_constraint(
        "uq_scales_post_month_year",
        "scales",
        ["post_id", "month", "year"],
    )

    # ====================
    # Table: shifts (Turnos)
    # ====================
    op.create_table(
        "shifts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scale_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="scheduled",
        ),
        # Data/Hora planejados
        sa.Column("shift_date", sa.Date, nullable=False),
        sa.Column("planned_start_time", sa.Time, nullable=False),
        sa.Column("planned_end_time", sa.Time, nullable=False),
        sa.Column("planned_break_minutes", sa.Integer, nullable=False, server_default="60"),
        # Data/Hora reais
        sa.Column("actual_start_time", sa.DateTime, nullable=True),
        sa.Column("actual_end_time", sa.DateTime, nullable=True),
        sa.Column("actual_break_minutes", sa.Integer, nullable=True),
        # Horas calculadas
        sa.Column("planned_hours", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("actual_hours", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("overtime_hours", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("night_hours", sa.Float, nullable=False, server_default="0.0"),
        # Flags
        sa.Column("is_holiday", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_night_shift", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_overtime", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_off_day", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("needs_substitution", sa.Boolean, nullable=False, server_default="false"),
        # Valores
        sa.Column("base_pay", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("overtime_pay", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("night_bonus", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("holiday_bonus", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("total_pay", sa.Float, nullable=False, server_default="0.0"),
        # Metadados
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Foreign keys
        sa.ForeignKeyConstraint(["scale_id"], ["scales.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_shifts_scale_id", "shifts", ["scale_id"])
    op.create_index("ix_shifts_post_id", "shifts", ["post_id"])
    op.create_index("ix_shifts_employee_id", "shifts", ["employee_id"])
    op.create_index("ix_shifts_shift_date", "shifts", ["shift_date"])
    op.create_index("ix_shifts_status", "shifts", ["status"])

    # ====================
    # Table: allocations (Alocações Funcionário-Posto)
    # ====================
    op.create_table(
        "allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="active",
        ),
        # Período
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=True),
        # Tipo
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_temporary", sa.Boolean, nullable=False, server_default="false"),
        # Valores
        sa.Column("hourly_rate", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("monthly_salary", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("additional_benefits", sa.Float, nullable=False, server_default="0.0"),
        # Detalhes
        sa.Column("role", sa.String(100), nullable=True),
        sa.Column("qualifications", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("termination_reason", sa.String(255), nullable=True),
        # Metadados
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Foreign keys
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_allocations_post_id", "allocations", ["post_id"])
    op.create_index("ix_allocations_employee_id", "allocations", ["employee_id"])
    op.create_index("ix_allocations_status", "allocations", ["status"])
    op.create_index("ix_allocations_dates", "allocations", ["start_date", "end_date"])

    # ====================
    # Table: substitutions (Substituições)
    # ====================
    op.create_table(
        "substitutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("shift_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("substitute_employee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "reason",
            sa.String(50),
            nullable=False,
            server_default="falta",
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="pending",
        ),
        # Datas
        sa.Column("substitution_date", sa.Date, nullable=False),
        sa.Column("requested_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        # Valores
        sa.Column("additional_cost", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("overtime_hours", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("is_overtime", sa.Boolean, nullable=False, server_default="false"),
        # Detalhes
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("reason_details", sa.String(500), nullable=True),
        sa.Column("rejection_reason", sa.String(255), nullable=True),
        # Notificação
        sa.Column("notification_sent", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("notification_sent_at", sa.DateTime, nullable=True),
        # Responsáveis
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Metadados
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Foreign keys
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_substitutions_shift_id", "substitutions", ["shift_id"])
    op.create_index("ix_substitutions_post_id", "substitutions", ["post_id"])
    op.create_index("ix_substitutions_original_employee_id", "substitutions", ["original_employee_id"])
    op.create_index("ix_substitutions_substitute_employee_id", "substitutions", ["substitute_employee_id"])
    op.create_index("ix_substitutions_status", "substitutions", ["status"])
    op.create_index("ix_substitutions_date", "substitutions", ["substitution_date"])

    # ====================
    # Table: time_bank (Banco de Horas)
    # ====================
    op.create_table(
        "time_bank",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "entry_type",
            sa.String(50),
            nullable=False,
            server_default="credit",
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="pending",
        ),
        # Valores
        sa.Column("hours", sa.Float, nullable=False),
        sa.Column("balance_before", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("balance_after", sa.Float, nullable=False, server_default="0.0"),
        # Datas
        sa.Column("reference_date", sa.Date, nullable=False),
        sa.Column("expiration_date", sa.Date, nullable=True),
        # Relacionamentos
        sa.Column("shift_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Detalhes
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("reason", sa.String(255), nullable=True),
        # Aprovação
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("rejection_reason", sa.String(255), nullable=True),
        # Compensação
        sa.Column("compensated_at", sa.DateTime, nullable=True),
        sa.Column("compensation_shift_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Metadados
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        # Foreign keys
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="SET NULL"),
    )

    op.create_index("ix_time_bank_employee_id", "time_bank", ["employee_id"])
    op.create_index("ix_time_bank_entry_type", "time_bank", ["entry_type"])
    op.create_index("ix_time_bank_status", "time_bank", ["status"])
    op.create_index("ix_time_bank_reference_date", "time_bank", ["reference_date"])
    op.create_index("ix_time_bank_expiration_date", "time_bank", ["expiration_date"])


def downgrade() -> None:
    """Drop operations module tables."""
    op.drop_table("time_bank")
    op.drop_table("substitutions")
    op.drop_table("allocations")
    op.drop_table("shifts")
    op.drop_table("scales")
    op.drop_table("posts")
