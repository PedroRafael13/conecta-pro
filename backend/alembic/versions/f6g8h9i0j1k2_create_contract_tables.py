"""create_contract_tables

Revision ID: f6g8h9i0j1k2
Revises: e5f7a8b9c0d1
Create Date: 2025-12-30 08:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f6g8h9i0j1k2"
down_revision: str | None = "e5f7a8b9c0d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Tabela de templates de contrato
    op.create_table(
        "contract_templates",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("service_type", sa.String(length=30), nullable=True),
        sa.Column("content_template", sa.Text(), nullable=False),
        sa.Column("clauses", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("variables", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("approved_by_legal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("approved_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contract_templates_name", "contract_templates", ["name"], unique=False)
    op.create_index("ix_contract_templates_service_type", "contract_templates", ["service_type"], unique=False)

    # Tabela principal de contratos
    op.create_table(
        "contracts",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("contract_number", sa.String(length=30), nullable=False),
        sa.Column("client_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("opportunity_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("proposal_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("template_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("contract_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("monthly_value", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("total_value", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("setup_fee", sa.Numeric(precision=10, scale=2), nullable=True, server_default="0"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("grace_period_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notice_period_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("auto_renewal", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("renewal_period_months", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("renewal_notification_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("adjustment_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("adjustment_index", sa.String(length=20), nullable=True),
        sa.Column("adjustment_fixed_percent", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("adjustment_base_date", sa.Date(), nullable=True),
        sa.Column("last_adjustment_date", sa.Date(), nullable=True),
        sa.Column("next_adjustment_date", sa.Date(), nullable=True),
        sa.Column("has_sla", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sla_config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("clauses", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("signature_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("signature_provider", sa.String(length=50), nullable=True),
        sa.Column("signature_document_id", sa.String(length=100), nullable=True),
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        sa.Column("signed_by_client", sa.String(length=200), nullable=True),
        sa.Column("signed_by_company", sa.String(length=200), nullable=True),
        sa.Column("pdf_file_path", sa.String(length=500), nullable=True),
        sa.Column("commercial_manager_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("account_manager_id", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(
            ["opportunity_id"],
            ["opportunities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["proposal_id"],
            ["proposals.id"],
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["contract_templates.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contract_number"),
    )
    op.create_index("ix_contracts_contract_number", "contracts", ["contract_number"], unique=True)
    op.create_index("ix_contracts_client_id", "contracts", ["client_id"], unique=False)
    op.create_index("ix_contracts_status", "contracts", ["status"], unique=False)
    op.create_index("ix_contracts_contract_type", "contracts", ["contract_type"], unique=False)
    op.create_index("ix_contracts_start_date", "contracts", ["start_date"], unique=False)
    op.create_index("ix_contracts_end_date", "contracts", ["end_date"], unique=False)

    # Tabela de itens do contrato
    op.create_table(
        "contract_items",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("contract_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("service_type", sa.String(length=30), nullable=False),
        sa.Column("service_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("total_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contract_items_contract_id", "contract_items", ["contract_id"], unique=False)
    op.create_index("ix_contract_items_service_type", "contract_items", ["service_type"], unique=False)

    # Tabela de aditivos
    op.create_table(
        "contract_addendums",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("contract_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("addendum_number", sa.String(length=30), nullable=False),
        sa.Column("addendum_type", sa.String(length=30), nullable=False),
        sa.Column("previous_value", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("new_value", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("adjustment_percent", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("adjustment_index", sa.String(length=20), nullable=True),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("signed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        sa.Column("signature_document_id", sa.String(length=100), nullable=True),
        sa.Column("pdf_file_path", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contract_addendums_contract_id", "contract_addendums", ["contract_id"], unique=False)
    op.create_index("ix_contract_addendums_addendum_number", "contract_addendums", ["addendum_number"], unique=False)
    op.create_index("ix_contract_addendums_effective_date", "contract_addendums", ["effective_date"], unique=False)

    # Tabela de relatórios SLA
    op.create_table(
        "contract_sla_reports",
        sa.Column("id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("contract_id", sa.UUID(as_uuid=False), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("indicators", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("overall_score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("penalty_applied", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("penalty_percent", sa.Numeric(precision=5, scale=2), nullable=False, server_default="0"),
        sa.Column("penalty_amount", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("generated_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("approved_by", sa.UUID(as_uuid=False), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contract_sla_reports_contract_id", "contract_sla_reports", ["contract_id"], unique=False)
    op.create_index("ix_contract_sla_reports_year_month", "contract_sla_reports", ["year", "month"], unique=False)
    op.create_index("ix_contract_sla_reports_status", "contract_sla_reports", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_contract_sla_reports_status", table_name="contract_sla_reports")
    op.drop_index("ix_contract_sla_reports_year_month", table_name="contract_sla_reports")
    op.drop_index("ix_contract_sla_reports_contract_id", table_name="contract_sla_reports")
    op.drop_table("contract_sla_reports")

    op.drop_index("ix_contract_addendums_effective_date", table_name="contract_addendums")
    op.drop_index("ix_contract_addendums_addendum_number", table_name="contract_addendums")
    op.drop_index("ix_contract_addendums_contract_id", table_name="contract_addendums")
    op.drop_table("contract_addendums")

    op.drop_index("ix_contract_items_service_type", table_name="contract_items")
    op.drop_index("ix_contract_items_contract_id", table_name="contract_items")
    op.drop_table("contract_items")

    op.drop_index("ix_contracts_end_date", table_name="contracts")
    op.drop_index("ix_contracts_start_date", table_name="contracts")
    op.drop_index("ix_contracts_contract_type", table_name="contracts")
    op.drop_index("ix_contracts_status", table_name="contracts")
    op.drop_index("ix_contracts_client_id", table_name="contracts")
    op.drop_index("ix_contracts_contract_number", table_name="contracts")
    op.drop_table("contracts")

    op.drop_index("ix_contract_templates_service_type", table_name="contract_templates")
    op.drop_index("ix_contract_templates_name", table_name="contract_templates")
    op.drop_table("contract_templates")
