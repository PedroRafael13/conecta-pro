"""Sprint 31: Create services tables

Revision ID: sprint31_services
Revises:
Create Date: 2026-01-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint31_services"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create services module tables."""
    # Create service_catalog table
    op.create_table(
        "service_catalog",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("short_description", sa.String(500), nullable=True),
        sa.Column(
            "category",
            sa.Enum(
                "manutencao_predial",
                "limpeza",
                "seguranca",
                "jardinagem",
                "piscina",
                "elevadores",
                "portaria",
                "administracao",
                "consultoria",
                "tecnologia",
                "eventos",
                "outros",
                name="servicecategory",
            ),
            nullable=False,
            server_default="outros",
        ),
        sa.Column(
            "service_type",
            sa.Enum(
                "pontual",
                "recorrente",
                "emergencia",
                "preventivo",
                "corretivo",
                "consultivo",
                "projeto",
                name="servicetype",
            ),
            nullable=False,
            server_default="recorrente",
        ),
        sa.Column(
            "status",
            sa.Enum("ativo", "inativo", "suspenso", "descontinuado", name="servicestatus"),
            nullable=False,
            server_default="ativo",
        ),
        sa.Column("base_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("price_unit", sa.String(50), nullable=True),
        sa.Column("min_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("max_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("estimated_duration_hours", sa.Numeric(8, 2), nullable=True),
        sa.Column("min_team_size", sa.Integer, nullable=True),
        sa.Column("max_team_size", sa.Integer, nullable=True),
        sa.Column("required_skills", postgresql.JSONB, nullable=True),
        sa.Column("required_equipment", postgresql.JSONB, nullable=True),
        sa.Column("required_materials", postgresql.JSONB, nullable=True),
        sa.Column("requires_scheduling", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("requires_approval", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("allows_remote", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_emergency_available", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("emergency_surcharge_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("default_sla_response_hours", sa.Integer, nullable=True),
        sa.Column("default_sla_resolution_hours", sa.Integer, nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("total_orders", sa.Integer, nullable=False, server_default="0"),
        sa.Column("completed_orders", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cancelled_orders", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_rating", sa.Numeric(3, 2), nullable=True),
        sa.Column("total_revenue", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("is_available", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("availability_schedule", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create service_orders table
    op.create_table(
        "service_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("order_number", sa.String(30), nullable=False, unique=True),
        sa.Column(
            "service_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_catalog.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condominium_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parent_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("requirements", sa.Text, nullable=True),
        sa.Column("special_instructions", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "rascunho",
                "pendente",
                "aprovada",
                "agendada",
                "em_andamento",
                "pausada",
                "concluida",
                "cancelada",
                "rejeitada",
                name="orderstatus",
            ),
            nullable=False,
            server_default="rascunho",
        ),
        sa.Column(
            "priority",
            sa.Enum("baixa", "normal", "alta", "urgente", "critica", name="orderpriority"),
            nullable=False,
            server_default="normal",
        ),
        sa.Column("requester_name", sa.String(200), nullable=True),
        sa.Column("requester_email", sa.String(255), nullable=True),
        sa.Column("requester_phone", sa.String(20), nullable=True),
        sa.Column("requester_unit", sa.String(50), nullable=True),
        sa.Column("location_address", sa.String(500), nullable=True),
        sa.Column("location_details", sa.String(500), nullable=True),
        sa.Column("location_coordinates", postgresql.JSONB, nullable=True),
        sa.Column("requested_date", sa.Date, nullable=True),
        sa.Column("requested_time_start", sa.String(5), nullable=True),
        sa.Column("requested_time_end", sa.String(5), nullable=True),
        sa.Column("is_flexible_schedule", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("scheduled_date", sa.Date, nullable=True),
        sa.Column("scheduled_time_start", sa.String(5), nullable=True),
        sa.Column("scheduled_time_end", sa.String(5), nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("paused_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("cancelled_at", sa.DateTime, nullable=True),
        sa.Column("estimated_duration_hours", sa.Numeric(8, 2), nullable=True),
        sa.Column("actual_duration_hours", sa.Numeric(8, 2), nullable=True),
        sa.Column("estimated_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("final_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("discount_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("discount_reason", sa.String(500), nullable=True),
        sa.Column("additional_charges", sa.Numeric(12, 2), nullable=True),
        sa.Column("additional_charges_description", sa.Text, nullable=True),
        sa.Column("assigned_technician_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_technician_name", sa.String(200), nullable=True),
        sa.Column("assigned_team", postgresql.JSONB, nullable=True),
        sa.Column("rating", sa.Integer, nullable=True),
        sa.Column("rating_feedback", sa.Text, nullable=True),
        sa.Column("rated_at", sa.DateTime, nullable=True),
        sa.Column("internal_notes", sa.Text, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        sa.Column("pause_reason", sa.Text, nullable=True),
        sa.Column("completion_notes", sa.Text, nullable=True),
        sa.Column("sla_response_deadline", sa.DateTime, nullable=True),
        sa.Column("sla_resolution_deadline", sa.DateTime, nullable=True),
        sa.Column("sla_response_met", sa.Boolean, nullable=True),
        sa.Column("sla_resolution_met", sa.Boolean, nullable=True),
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create service_executions table
    op.create_table(
        "service_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("execution_number", sa.String(30), nullable=False, unique=True),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer, nullable=False, server_default="1"),
        sa.Column("technician_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("technician_name", sa.String(200), nullable=True),
        sa.Column("team_members", postgresql.JSONB, nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "agendada",
                "em_deslocamento",
                "no_local",
                "em_execucao",
                "pausada",
                "aguardando_material",
                "aguardando_aprovacao",
                "concluida",
                "cancelada",
                name="executionstatus",
            ),
            nullable=False,
            server_default="agendada",
        ),
        sa.Column("scheduled_start", sa.DateTime, nullable=True),
        sa.Column("scheduled_end", sa.DateTime, nullable=True),
        sa.Column("travel_start", sa.DateTime, nullable=True),
        sa.Column("arrival_at_location", sa.DateTime, nullable=True),
        sa.Column("actual_start", sa.DateTime, nullable=True),
        sa.Column("actual_end", sa.DateTime, nullable=True),
        sa.Column("paused_at", sa.DateTime, nullable=True),
        sa.Column("resumed_at", sa.DateTime, nullable=True),
        sa.Column("travel_duration_minutes", sa.Integer, nullable=True),
        sa.Column("execution_duration_minutes", sa.Integer, nullable=True),
        sa.Column("pause_duration_minutes", sa.Integer, nullable=True),
        sa.Column("total_duration_minutes", sa.Integer, nullable=True),
        sa.Column("work_description", sa.Text, nullable=True),
        sa.Column("findings", sa.Text, nullable=True),
        sa.Column("recommendations", sa.Text, nullable=True),
        sa.Column("internal_notes", sa.Text, nullable=True),
        sa.Column("client_notes", sa.Text, nullable=True),
        sa.Column("pause_reason", sa.Text, nullable=True),
        sa.Column("checklist_items", postgresql.JSONB, nullable=True),
        sa.Column("checklist_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("checklist_completion_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("materials_used", postgresql.JSONB, nullable=True),
        sa.Column("materials_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("labor_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("travel_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("additional_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("photos", postgresql.JSONB, nullable=True),
        sa.Column("documents", postgresql.JSONB, nullable=True),
        sa.Column("signatures", postgresql.JSONB, nullable=True),
        sa.Column("gps_tracking", postgresql.JSONB, nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create service_reports table
    op.create_table(
        "service_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_number", sa.String(30), nullable=False, unique=True),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_executions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "report_type",
            sa.Enum(
                "execucao",
                "inspecao",
                "auditoria",
                "tecnico",
                "orcamento",
                "laudo",
                "vistoria",
                "preventivo",
                "corretivo",
                "final",
                name="reporttype",
            ),
            nullable=False,
            server_default="execucao",
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("introduction", sa.Text, nullable=True),
        sa.Column("methodology", sa.Text, nullable=True),
        sa.Column("findings", sa.Text, nullable=True),
        sa.Column("analysis", sa.Text, nullable=True),
        sa.Column("conclusions", sa.Text, nullable=True),
        sa.Column("recommendations", sa.Text, nullable=True),
        sa.Column("sections", postgresql.JSONB, nullable=True),
        sa.Column("photos", postgresql.JSONB, nullable=True),
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        sa.Column("non_conformities", postgresql.JSONB, nullable=True),
        sa.Column("measurements", postgresql.JSONB, nullable=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("author_name", sa.String(200), nullable=True),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewer_name", sa.String(200), nullable=True),
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approver_name", sa.String(200), nullable=True),
        sa.Column("is_draft", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_reviewed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_approved", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_sent", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("sent_at", sa.DateTime, nullable=True),
        sa.Column("sent_to", postgresql.JSONB, nullable=True),
        sa.Column("review_notes", sa.Text, nullable=True),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("previous_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("pdf_url", sa.String(500), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create sla_configs table
    op.create_table(
        "sla_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(30), nullable=True),
        sa.Column(
            "service_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_catalog.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "metric_type",
            sa.Enum(
                "tempo_resposta",
                "tempo_resolucao",
                "disponibilidade",
                "uptime",
                "qualidade",
                "satisfacao",
                "primeiro_contato",
                "reincidencia",
                name="slametrictype",
            ),
            nullable=False,
            server_default="tempo_resolucao",
        ),
        sa.Column("response_time_minutes", sa.Integer, nullable=True),
        sa.Column("resolution_time_minutes", sa.Integer, nullable=True),
        sa.Column("first_contact_time_minutes", sa.Integer, nullable=True),
        sa.Column("target_availability_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("target_quality_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("target_satisfaction_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("max_incidents_month", sa.Integer, nullable=True),
        sa.Column("max_reopen_count", sa.Integer, nullable=True),
        sa.Column("max_escalation_count", sa.Integer, nullable=True),
        sa.Column("penalty_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("penalty_percent_per_breach", sa.Numeric(5, 2), nullable=True),
        sa.Column("max_penalty_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("penalty_calculation_method", sa.String(50), nullable=True),
        sa.Column("bonus_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("bonus_percent_on_exceed", sa.Numeric(5, 2), nullable=True),
        sa.Column("max_bonus_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("escalation_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("escalation_levels", postgresql.JSONB, nullable=True),
        sa.Column("business_hours_only", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("business_hours_start", sa.String(5), nullable=True),
        sa.Column("business_hours_end", sa.String(5), nullable=True),
        sa.Column("business_days", postgresql.JSONB, nullable=True),
        sa.Column("holiday_calendar_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("priority_multipliers", postgresql.JSONB, nullable=True),
        sa.Column("notification_enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notification_thresholds", postgresql.JSONB, nullable=True),
        sa.Column("notification_recipients", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("valid_from", sa.DateTime, nullable=True),
        sa.Column("valid_until", sa.DateTime, nullable=True),
        sa.Column("total_orders", sa.Integer, nullable=False, server_default="0"),
        sa.Column("orders_within_sla", sa.Integer, nullable=False, server_default="0"),
        sa.Column("orders_breached", sa.Integer, nullable=False, server_default="0"),
        sa.Column("current_compliance_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create indexes for service_catalog
    op.create_index("ix_service_catalog_code", "service_catalog", ["code"])
    op.create_index("ix_service_catalog_category", "service_catalog", ["category"])
    op.create_index("ix_service_catalog_service_type", "service_catalog", ["service_type"])
    op.create_index("ix_service_catalog_status", "service_catalog", ["status"])
    op.create_index("ix_service_catalog_is_available", "service_catalog", ["is_available"])
    op.create_index("ix_service_catalog_ativo", "service_catalog", ["ativo"])

    # Create indexes for service_orders
    op.create_index("ix_service_orders_order_number", "service_orders", ["order_number"])
    op.create_index("ix_service_orders_service_id", "service_orders", ["service_id"])
    op.create_index("ix_service_orders_client_id", "service_orders", ["client_id"])
    op.create_index("ix_service_orders_condominium_id", "service_orders", ["condominium_id"])
    op.create_index("ix_service_orders_status", "service_orders", ["status"])
    op.create_index("ix_service_orders_priority", "service_orders", ["priority"])
    op.create_index("ix_service_orders_scheduled_date", "service_orders", ["scheduled_date"])
    op.create_index("ix_service_orders_technician", "service_orders", ["assigned_technician_id"])
    op.create_index("ix_service_orders_ativo", "service_orders", ["ativo"])
    op.create_index("ix_service_orders_created_at", "service_orders", ["created_at"])

    # Create indexes for service_executions
    op.create_index("ix_service_executions_number", "service_executions", ["execution_number"])
    op.create_index("ix_service_executions_order_id", "service_executions", ["order_id"])
    op.create_index("ix_service_executions_technician", "service_executions", ["technician_id"])
    op.create_index("ix_service_executions_status", "service_executions", ["status"])
    op.create_index("ix_service_executions_ativo", "service_executions", ["ativo"])

    # Create indexes for service_reports
    op.create_index("ix_service_reports_number", "service_reports", ["report_number"])
    op.create_index("ix_service_reports_order_id", "service_reports", ["order_id"])
    op.create_index("ix_service_reports_execution_id", "service_reports", ["execution_id"])
    op.create_index("ix_service_reports_type", "service_reports", ["report_type"])
    op.create_index("ix_service_reports_is_approved", "service_reports", ["is_approved"])
    op.create_index("ix_service_reports_ativo", "service_reports", ["ativo"])

    # Create indexes for sla_configs
    op.create_index("ix_sla_configs_service_id", "sla_configs", ["service_id"])
    op.create_index("ix_sla_configs_client_id", "sla_configs", ["client_id"])
    op.create_index("ix_sla_configs_contract_id", "sla_configs", ["contract_id"])
    op.create_index("ix_sla_configs_metric_type", "sla_configs", ["metric_type"])
    op.create_index("ix_sla_configs_is_active", "sla_configs", ["is_active"])
    op.create_index("ix_sla_configs_is_default", "sla_configs", ["is_default"])
    op.create_index("ix_sla_configs_ativo", "sla_configs", ["ativo"])


def downgrade() -> None:
    """Drop services module tables."""
    # Drop indexes
    op.drop_index("ix_sla_configs_ativo", table_name="sla_configs")
    op.drop_index("ix_sla_configs_is_default", table_name="sla_configs")
    op.drop_index("ix_sla_configs_is_active", table_name="sla_configs")
    op.drop_index("ix_sla_configs_metric_type", table_name="sla_configs")
    op.drop_index("ix_sla_configs_contract_id", table_name="sla_configs")
    op.drop_index("ix_sla_configs_client_id", table_name="sla_configs")
    op.drop_index("ix_sla_configs_service_id", table_name="sla_configs")

    op.drop_index("ix_service_reports_ativo", table_name="service_reports")
    op.drop_index("ix_service_reports_is_approved", table_name="service_reports")
    op.drop_index("ix_service_reports_type", table_name="service_reports")
    op.drop_index("ix_service_reports_execution_id", table_name="service_reports")
    op.drop_index("ix_service_reports_order_id", table_name="service_reports")
    op.drop_index("ix_service_reports_number", table_name="service_reports")

    op.drop_index("ix_service_executions_ativo", table_name="service_executions")
    op.drop_index("ix_service_executions_status", table_name="service_executions")
    op.drop_index("ix_service_executions_technician", table_name="service_executions")
    op.drop_index("ix_service_executions_order_id", table_name="service_executions")
    op.drop_index("ix_service_executions_number", table_name="service_executions")

    op.drop_index("ix_service_orders_created_at", table_name="service_orders")
    op.drop_index("ix_service_orders_ativo", table_name="service_orders")
    op.drop_index("ix_service_orders_technician", table_name="service_orders")
    op.drop_index("ix_service_orders_scheduled_date", table_name="service_orders")
    op.drop_index("ix_service_orders_priority", table_name="service_orders")
    op.drop_index("ix_service_orders_status", table_name="service_orders")
    op.drop_index("ix_service_orders_condominium_id", table_name="service_orders")
    op.drop_index("ix_service_orders_client_id", table_name="service_orders")
    op.drop_index("ix_service_orders_service_id", table_name="service_orders")
    op.drop_index("ix_service_orders_order_number", table_name="service_orders")

    op.drop_index("ix_service_catalog_ativo", table_name="service_catalog")
    op.drop_index("ix_service_catalog_is_available", table_name="service_catalog")
    op.drop_index("ix_service_catalog_status", table_name="service_catalog")
    op.drop_index("ix_service_catalog_service_type", table_name="service_catalog")
    op.drop_index("ix_service_catalog_category", table_name="service_catalog")
    op.drop_index("ix_service_catalog_code", table_name="service_catalog")

    # Drop tables
    op.drop_table("sla_configs")
    op.drop_table("service_reports")
    op.drop_table("service_executions")
    op.drop_table("service_orders")
    op.drop_table("service_catalog")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS slametrictype")
    op.execute("DROP TYPE IF EXISTS reporttype")
    op.execute("DROP TYPE IF EXISTS executionstatus")
    op.execute("DROP TYPE IF EXISTS orderpriority")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS servicestatus")
    op.execute("DROP TYPE IF EXISTS servicetype")
    op.execute("DROP TYPE IF EXISTS servicecategory")
