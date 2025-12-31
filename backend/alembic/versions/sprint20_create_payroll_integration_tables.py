"""Sprint 20: Cria tabelas de integração com folha de pagamento.

Revision ID: sprint20_payroll
Revises: sprint19_analytics
Create Date: 2024-12-31

Tabelas criadas:
- hr_payroll_periods: Períodos de folha
- hr_payroll_events: Eventos/rubricas de folha
- hr_payroll_integrations: Configurações de integração
- hr_payroll_exports: Exportações de folha
- hr_employee_payroll_configs: Configurações por funcionário
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "sprint20_payroll"
down_revision = "sprint19_analytics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas de integração com folha de pagamento."""

    # =========================================================================
    # Tabela: hr_payroll_periods
    # Períodos de folha de pagamento (mensal, quinzenal, etc.)
    # =========================================================================
    op.create_table(
        "hr_payroll_periods",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Tipo e status
        sa.Column(
            "period_type",
            sa.String(20),
            nullable=False,
            server_default="monthly",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="draft",
        ),
        # Datas do período
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("month", sa.Integer, nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("payment_date", sa.Date, nullable=True),
        # Datas de controle
        sa.Column("calculation_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closing_date", sa.DateTime(timezone=True), nullable=True),
        # Totais
        sa.Column("total_employees", sa.Integer, server_default="0"),
        sa.Column(
            "total_earnings",
            sa.Numeric(15, 2),
            server_default="0",
        ),
        sa.Column(
            "total_deductions",
            sa.Numeric(15, 2),
            server_default="0",
        ),
        sa.Column(
            "total_net",
            sa.Numeric(15, 2),
            server_default="0",
        ),
        sa.Column(
            "total_employer_costs",
            sa.Numeric(15, 2),
            server_default="0",
        ),
        # Configurações
        sa.Column(
            "config",
            postgresql.JSONB,
            server_default="{}",
        ),
        # Responsáveis
        sa.Column("calculated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("closed_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Audit
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    # Índices para hr_payroll_periods
    op.create_index(
        "ix_hr_payroll_periods_year_month",
        "hr_payroll_periods",
        ["condominio_id", "year", "month"],
    )
    op.create_index(
        "ix_hr_payroll_periods_status",
        "hr_payroll_periods",
        ["condominio_id", "status"],
    )
    op.create_index(
        "ix_hr_payroll_periods_code",
        "hr_payroll_periods",
        ["condominio_id", "code"],
        unique=True,
    )

    # =========================================================================
    # Tabela: hr_payroll_events
    # Eventos/rubricas de folha de pagamento
    # =========================================================================
    op.create_table(
        "hr_payroll_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("hr_payroll_periods.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Identificação do evento
        sa.Column("event_code", sa.String(20), nullable=False),
        sa.Column("event_name", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(20), nullable=False),
        sa.Column("event_category", sa.String(50), nullable=False),
        # Valores
        sa.Column("reference", sa.Numeric(10, 4), nullable=True),
        sa.Column("value", sa.Numeric(15, 2), nullable=False),
        sa.Column("original_value", sa.Numeric(15, 2), nullable=True),
        # Incidências (INSS, IRRF, FGTS)
        sa.Column(
            "esocial_incidences",
            postgresql.JSONB,
            server_default='{"inss": true, "irrf": true, "fgts": true}',
        ),
        sa.Column("esocial_code", sa.String(20), nullable=True),
        # Status e controle
        sa.Column(
            "status",
            sa.String(20),
            server_default="active",
        ),
        sa.Column("is_automatic", sa.Boolean, server_default="true"),
        sa.Column("is_proportional", sa.Boolean, server_default="false"),
        sa.Column("proportional_days", sa.Integer, nullable=True),
        # Ajustes
        sa.Column("adjustment_reason", sa.Text, nullable=True),
        sa.Column("adjusted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("adjusted_at", sa.DateTime(timezone=True), nullable=True),
        # Metadata
        sa.Column(
            "metadata",
            postgresql.JSONB,
            server_default="{}",
        ),
        # Audit
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    # Índices para hr_payroll_events
    op.create_index(
        "ix_hr_payroll_events_period_employee",
        "hr_payroll_events",
        ["period_id", "employee_id"],
    )
    op.create_index(
        "ix_hr_payroll_events_event_type",
        "hr_payroll_events",
        ["period_id", "event_type"],
    )
    op.create_index(
        "ix_hr_payroll_events_event_category",
        "hr_payroll_events",
        ["period_id", "event_category"],
    )

    # =========================================================================
    # Tabela: hr_payroll_integrations
    # Configurações de integração com sistemas externos
    # =========================================================================
    op.create_table(
        "hr_payroll_integrations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Identificação
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "integration_type",
            sa.String(30),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(20),
            server_default="inactive",
        ),
        # Configurações gerais
        sa.Column(
            "config",
            postgresql.JSONB,
            server_default="{}",
        ),
        sa.Column(
            "credentials",
            postgresql.JSONB,
            server_default="{}",
        ),
        # Mapeamentos
        sa.Column(
            "rubrica_mapping",
            postgresql.JSONB,
            server_default="{}",
        ),
        sa.Column(
            "department_mapping",
            postgresql.JSONB,
            server_default="{}",
        ),
        # eSocial específico
        sa.Column(
            "esocial_config",
            postgresql.JSONB,
            server_default="{}",
        ),
        # Sincronização
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_status", sa.String(20), nullable=True),
        sa.Column("sync_message", sa.Text, nullable=True),
        sa.Column("sync_records", sa.Integer, server_default="0"),
        # Audit
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    # Índice único por tipo de integração
    op.create_index(
        "ix_hr_payroll_integrations_type",
        "hr_payroll_integrations",
        ["condominio_id", "integration_type"],
        unique=True,
    )

    # =========================================================================
    # Tabela: hr_payroll_exports
    # Exportações de folha de pagamento
    # =========================================================================
    op.create_table(
        "hr_payroll_exports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("hr_payroll_periods.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "integration_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("hr_payroll_integrations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Identificação
        sa.Column("export_code", sa.String(30), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Formato e tipo
        sa.Column("export_format", sa.String(20), nullable=False),
        sa.Column("export_type", sa.String(50), nullable=True),
        sa.Column(
            "status",
            sa.String(20),
            server_default="pending",
        ),
        # Arquivo gerado
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("file_name", sa.String(200), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("file_hash", sa.String(64), nullable=True),
        # Configurações do arquivo
        sa.Column(
            "file_config",
            postgresql.JSONB,
            server_default="{}",
        ),
        # Estatísticas
        sa.Column("total_records", sa.Integer, server_default="0"),
        sa.Column("processed_records", sa.Integer, server_default="0"),
        sa.Column("success_records", sa.Integer, server_default="0"),
        sa.Column("error_records", sa.Integer, server_default="0"),
        # Erros e warnings
        sa.Column(
            "errors",
            postgresql.JSONB,
            server_default="[]",
        ),
        sa.Column(
            "warnings",
            postgresql.JSONB,
            server_default="[]",
        ),
        # Datas de controle
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        # Transmissão (eSocial, etc.)
        sa.Column("transmission_id", sa.String(100), nullable=True),
        sa.Column("receipt_number", sa.String(100), nullable=True),
        sa.Column("transmitted_at", sa.DateTime(timezone=True), nullable=True),
        # Downloads
        sa.Column("download_count", sa.Integer, server_default="0"),
        sa.Column("last_download_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    # Índices para hr_payroll_exports
    op.create_index(
        "ix_hr_payroll_exports_status",
        "hr_payroll_exports",
        ["condominio_id", "status"],
    )
    op.create_index(
        "ix_hr_payroll_exports_format",
        "hr_payroll_exports",
        ["condominio_id", "export_format"],
    )

    # =========================================================================
    # Tabela: hr_employee_payroll_configs
    # Configurações de folha por funcionário
    # =========================================================================
    op.create_table(
        "hr_employee_payroll_configs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        # Contrato
        sa.Column(
            "contract_type",
            sa.String(20),
            server_default="clt",
        ),
        sa.Column(
            "work_schedule",
            sa.String(20),
            server_default="standard",
        ),
        sa.Column("monthly_hours", sa.Numeric(6, 2), server_default="220"),
        sa.Column("weekly_hours", sa.Numeric(5, 2), server_default="44"),
        # Salário
        sa.Column("base_salary", sa.Numeric(12, 2), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(10, 4), nullable=True),
        # Banco de horas
        sa.Column("bank_hours_enabled", sa.Boolean, server_default="false"),
        sa.Column(
            "bank_hours_policy",
            sa.String(20),
            server_default="monthly",
        ),
        sa.Column(
            "bank_hours_balance",
            sa.Numeric(8, 2),
            server_default="0",
        ),
        sa.Column(
            "bank_hours_limit",
            sa.Numeric(8, 2),
            server_default="60",
        ),
        # Hora extra
        sa.Column(
            "overtime_rule",
            sa.String(20),
            server_default="standard",
        ),
        sa.Column(
            "overtime_50_rate",
            sa.Numeric(5, 2),
            server_default="1.50",
        ),
        sa.Column(
            "overtime_100_rate",
            sa.Numeric(5, 2),
            server_default="2.00",
        ),
        sa.Column(
            "night_shift_rate",
            sa.Numeric(5, 2),
            server_default="1.20",
        ),
        # Adicional noturno
        sa.Column("night_shift_enabled", sa.Boolean, server_default="true"),
        sa.Column("night_shift_start", sa.Time, nullable=True),
        sa.Column("night_shift_end", sa.Time, nullable=True),
        # Benefícios
        sa.Column(
            "benefits",
            postgresql.JSONB,
            server_default="[]",
        ),
        # Empréstimos e descontos
        sa.Column(
            "loans",
            postgresql.JSONB,
            server_default="[]",
        ),
        # Pensão alimentícia
        sa.Column(
            "alimony",
            postgresql.JSONB,
            server_default="[]",
        ),
        # Dependentes IR
        sa.Column(
            "dependents",
            postgresql.JSONB,
            server_default="[]",
        ),
        sa.Column("dependents_count", sa.Integer, server_default="0"),
        # eSocial
        sa.Column("esocial_matricula", sa.String(30), nullable=True),
        sa.Column("esocial_categoria", sa.String(5), nullable=True),
        # Sincronização
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    # Índice único por funcionário e condomínio
    op.create_index(
        "ix_hr_employee_payroll_configs_employee",
        "hr_employee_payroll_configs",
        ["condominio_id", "employee_id"],
        unique=True,
    )


def downgrade() -> None:
    """Remove tabelas de integração com folha."""
    op.drop_table("hr_employee_payroll_configs")
    op.drop_table("hr_payroll_exports")
    op.drop_table("hr_payroll_integrations")
    op.drop_table("hr_payroll_events")
    op.drop_table("hr_payroll_periods")
