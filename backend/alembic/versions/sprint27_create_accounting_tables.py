"""Create accounting tables for Sprint 27 - Contabilidade module.

Revision ID: sprint27_accounting
Revises: sprint26_inventory
Create Date: 2024-12-31

Tables:
- fin_charts_of_accounts: Planos de Contas
- fin_accounting_accounts: Contas Contabeis
- fin_cost_centers: Centros de Custo
- fin_accounting_periods: Periodos Contabeis
- fin_journal_entries: Lancamentos Contabeis
- fin_journal_entry_lines: Partidas dos Lancamentos
- fin_trial_balances: Balancetes
- fin_trial_balance_items: Itens dos Balancetes
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint27_accounting"
down_revision: Union[str, None] = "sprint26_inventory"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create accounting tables."""
    # ==========================================================================
    # ENUMS
    # ==========================================================================

    # ChartOfAccounts enums
    chart_type_enum = postgresql.ENUM(
        "STANDARD",
        "SIMPLIFIED",
        "CUSTOM",
        name="charttype",
        create_type=False,
    )
    chart_type_enum.create(op.get_bind(), checkfirst=True)

    chart_status_enum = postgresql.ENUM(
        "DRAFT",
        "ACTIVE",
        "INACTIVE",
        "ARCHIVED",
        name="chartstatus",
        create_type=False,
    )
    chart_status_enum.create(op.get_bind(), checkfirst=True)

    chart_standard_enum = postgresql.ENUM(
        "SPED_ECD",
        "SPED_ECF",
        "CPC",
        "IFRS",
        "US_GAAP",
        "CUSTOM",
        name="chartstandard",
        create_type=False,
    )
    chart_standard_enum.create(op.get_bind(), checkfirst=True)

    # AccountingAccount enums
    account_type_enum = postgresql.ENUM(
        "ASSET",
        "LIABILITY",
        "EQUITY",
        "REVENUE",
        "EXPENSE",
        "COST",
        name="accounttype",
        create_type=False,
    )
    account_type_enum.create(op.get_bind(), checkfirst=True)

    account_nature_enum = postgresql.ENUM(
        "DEBIT",
        "CREDIT",
        name="accountnature",
        create_type=False,
    )
    account_nature_enum.create(op.get_bind(), checkfirst=True)

    account_classification_enum = postgresql.ENUM(
        "SYNTHETIC",
        "ANALYTICAL",
        name="accountclassification",
        create_type=False,
    )
    account_classification_enum.create(op.get_bind(), checkfirst=True)

    account_status_enum = postgresql.ENUM(
        "ACTIVE",
        "INACTIVE",
        "BLOCKED",
        "PENDING",
        name="accountstatus",
        create_type=False,
    )
    account_status_enum.create(op.get_bind(), checkfirst=True)

    sped_account_nature_enum = postgresql.ENUM(
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        name="spedaccountnature",
        create_type=False,
    )
    sped_account_nature_enum.create(op.get_bind(), checkfirst=True)

    # CostCenter enums
    cost_center_type_enum = postgresql.ENUM(
        "OPERATIONAL",
        "ADMINISTRATIVE",
        "COMMERCIAL",
        "PRODUCTION",
        "SUPPORT",
        "PROJECT",
        "DEPARTMENT",
        "BRANCH",
        "OTHER",
        name="costcentertype",
        create_type=False,
    )
    cost_center_type_enum.create(op.get_bind(), checkfirst=True)

    cost_center_status_enum = postgresql.ENUM(
        "ACTIVE",
        "INACTIVE",
        "BLOCKED",
        "PENDING",
        name="costcenterstatus",
        create_type=False,
    )
    cost_center_status_enum.create(op.get_bind(), checkfirst=True)

    allocation_method_enum = postgresql.ENUM(
        "DIRECT",
        "PROPORTIONAL",
        "HEADCOUNT",
        "AREA",
        "REVENUE",
        "COST",
        "CUSTOM",
        name="allocationmethod",
        create_type=False,
    )
    allocation_method_enum.create(op.get_bind(), checkfirst=True)

    # AccountingPeriod enums
    period_type_enum = postgresql.ENUM(
        "MONTHLY",
        "QUARTERLY",
        "SEMIANNUAL",
        "ANNUAL",
        "CUSTOM",
        name="periodtype",
        create_type=False,
    )
    period_type_enum.create(op.get_bind(), checkfirst=True)

    period_status_enum = postgresql.ENUM(
        "PENDING",
        "OPEN",
        "CLOSING",
        "CLOSED",
        "REOPENED",
        "ARCHIVED",
        name="periodstatus",
        create_type=False,
    )
    period_status_enum.create(op.get_bind(), checkfirst=True)

    closing_type_enum = postgresql.ENUM(
        "MONTHLY",
        "ANNUAL",
        "SPECIAL",
        name="closingtype",
        create_type=False,
    )
    closing_type_enum.create(op.get_bind(), checkfirst=True)

    # JournalEntry enums
    entry_type_enum = postgresql.ENUM(
        "MANUAL",
        "AUTOMATIC",
        "IMPORT",
        "ADJUSTMENT",
        "OPENING",
        "CLOSING",
        "REVERSAL",
        "PROVISION",
        "DEPRECIATION",
        "RECLASSIFICATION",
        name="entrytype",
        create_type=False,
    )
    entry_type_enum.create(op.get_bind(), checkfirst=True)

    entry_status_enum = postgresql.ENUM(
        "DRAFT",
        "PENDING",
        "APPROVED",
        "POSTED",
        "REVERSED",
        "CANCELLED",
        name="entrystatus",
        create_type=False,
    )
    entry_status_enum.create(op.get_bind(), checkfirst=True)

    entry_origin_enum = postgresql.ENUM(
        "ACCOUNTS_PAYABLE",
        "ACCOUNTS_RECEIVABLE",
        "CASH_FLOW",
        "INVENTORY",
        "PURCHASE",
        "SALES",
        "PAYROLL",
        "FIXED_ASSETS",
        "TAX",
        "MANUAL",
        "OTHER",
        name="entryorigin",
        create_type=False,
    )
    entry_origin_enum.create(op.get_bind(), checkfirst=True)

    # TrialBalance enums
    balance_type_enum = postgresql.ENUM(
        "VERIFICATION",
        "ANALYTICAL",
        "SYNTHETIC",
        "COMPARISON",
        "CONSOLIDATED",
        name="balancetype",
        create_type=False,
    )
    balance_type_enum.create(op.get_bind(), checkfirst=True)

    balance_status_enum = postgresql.ENUM(
        "DRAFT",
        "GENERATED",
        "APPROVED",
        "PUBLISHED",
        "ARCHIVED",
        name="balancestatus",
        create_type=False,
    )
    balance_status_enum.create(op.get_bind(), checkfirst=True)

    balance_period_enum = postgresql.ENUM(
        "MONTHLY",
        "QUARTERLY",
        "SEMIANNUAL",
        "ANNUAL",
        "CUSTOM",
        name="balanceperiod",
        create_type=False,
    )
    balance_period_enum.create(op.get_bind(), checkfirst=True)

    # ==========================================================================
    # TABLE: fin_charts_of_accounts
    # ==========================================================================
    op.create_table(
        "fin_charts_of_accounts",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identification
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Type and Status
        sa.Column("chart_type", chart_type_enum, server_default="STANDARD", nullable=False),
        sa.Column("status", chart_status_enum, server_default="DRAFT", nullable=False),
        sa.Column("standard", chart_standard_enum, server_default="SPED_ECD", nullable=False),
        # Version
        sa.Column("version", sa.String(20), nullable=True),
        sa.Column("base_version", sa.String(20), nullable=True),
        # Validity
        sa.Column("valid_from", sa.Date, nullable=True),
        sa.Column("valid_until", sa.Date, nullable=True),
        # SPED
        sa.Column("sped_layout", sa.String(10), nullable=True),
        sa.Column("sped_nature", sa.String(10), nullable=True),
        # Stats
        sa.Column("total_accounts", sa.Integer, server_default="0", nullable=False),
        sa.Column("total_analytical", sa.Integer, server_default="0", nullable=False),
        sa.Column("total_synthetic", sa.Integer, server_default="0", nullable=False),
        sa.Column("max_level", sa.Integer, server_default="5", nullable=False),
        # Activation
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Integration
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Flags
        sa.Column("active", sa.Boolean, server_default="true", nullable=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes for fin_charts_of_accounts
    op.create_index("ix_fin_charts_condominio", "fin_charts_of_accounts", ["condominio_id"])
    op.create_index("ix_fin_charts_code", "fin_charts_of_accounts", ["code"])
    op.create_index("ix_fin_charts_status", "fin_charts_of_accounts", ["status"])
    op.create_index("ix_fin_charts_active", "fin_charts_of_accounts", ["active"])
    op.create_unique_constraint(
        "uq_fin_charts_code_condo",
        "fin_charts_of_accounts",
        ["condominio_id", "code"],
    )

    # ==========================================================================
    # TABLE: fin_accounting_accounts
    # ==========================================================================
    op.create_table(
        "fin_accounting_accounts",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Reference to Chart
        sa.Column("chart_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Hierarchy
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Identification
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Type and Classification
        sa.Column("account_type", account_type_enum, nullable=False),
        sa.Column("nature", account_nature_enum, nullable=False),
        sa.Column("classification", account_classification_enum, nullable=False),
        sa.Column("status", account_status_enum, server_default="ACTIVE", nullable=False),
        # Hierarchy Info
        sa.Column("level", sa.Integer, nullable=False),
        sa.Column("full_path", sa.String(500), nullable=True),
        sa.Column("path_codes", sa.String(200), nullable=True),
        # SPED
        sa.Column("sped_nature", sped_account_nature_enum, nullable=True),
        sa.Column("sped_referential_code", sa.String(30), nullable=True),
        sa.Column("sped_start_date", sa.Date, nullable=True),
        sa.Column("sped_end_date", sa.Date, nullable=True),
        # Reports
        sa.Column("balance_sheet_group", sa.String(50), nullable=True),
        sa.Column("dre_group", sa.String(50), nullable=True),
        sa.Column("cash_flow_group", sa.String(50), nullable=True),
        # Balance
        sa.Column("opening_balance", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("current_balance", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("debit_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("credit_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Budget
        sa.Column("budget_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("budget_alert_percent", sa.Numeric(5, 2), nullable=True),
        # Integration
        sa.Column("external_code", sa.String(50), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Flags
        sa.Column("accepts_entries", sa.Boolean, server_default="true", nullable=False),
        sa.Column("requires_cost_center", sa.Boolean, server_default="false", nullable=False),
        sa.Column("requires_project", sa.Boolean, server_default="false", nullable=False),
        sa.Column("is_cash_account", sa.Boolean, server_default="false", nullable=False),
        sa.Column("is_bank_account", sa.Boolean, server_default="false", nullable=False),
        sa.Column("active", sa.Boolean, server_default="true", nullable=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["chart_id"],
            ["fin_charts_of_accounts.id"],
            name="fk_account_chart",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["fin_accounting_accounts.id"],
            name="fk_account_parent",
        ),
    )

    # Indexes for fin_accounting_accounts
    op.create_index("ix_fin_accounts_condominio", "fin_accounting_accounts", ["condominio_id"])
    op.create_index("ix_fin_accounts_chart", "fin_accounting_accounts", ["chart_id"])
    op.create_index("ix_fin_accounts_parent", "fin_accounting_accounts", ["parent_id"])
    op.create_index("ix_fin_accounts_code", "fin_accounting_accounts", ["code"])
    op.create_index("ix_fin_accounts_type", "fin_accounting_accounts", ["account_type"])
    op.create_index("ix_fin_accounts_nature", "fin_accounting_accounts", ["nature"])
    op.create_index("ix_fin_accounts_classification", "fin_accounting_accounts", ["classification"])
    op.create_index("ix_fin_accounts_status", "fin_accounting_accounts", ["status"])
    op.create_index("ix_fin_accounts_level", "fin_accounting_accounts", ["level"])
    op.create_index("ix_fin_accounts_active", "fin_accounting_accounts", ["active"])
    op.create_unique_constraint(
        "uq_fin_accounts_chart_code",
        "fin_accounting_accounts",
        ["chart_id", "code"],
    )

    # ==========================================================================
    # TABLE: fin_cost_centers
    # ==========================================================================
    op.create_table(
        "fin_cost_centers",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Hierarchy
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Identification
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Type and Status
        sa.Column(
            "center_type", cost_center_type_enum, server_default="OPERATIONAL", nullable=False
        ),
        sa.Column("status", cost_center_status_enum, server_default="ACTIVE", nullable=False),
        sa.Column(
            "allocation_method", allocation_method_enum, server_default="DIRECT", nullable=False
        ),
        # Hierarchy Info
        sa.Column("level", sa.Integer, server_default="1", nullable=False),
        sa.Column("full_path", sa.String(500), nullable=True),
        # Manager
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        # Budget
        sa.Column("budget_amount", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("actual_amount", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("budget_year", sa.Integer, nullable=True),
        sa.Column("budget_alert_percent", sa.Numeric(5, 2), nullable=True),
        # Allocation
        sa.Column("allocation_basis", sa.String(50), nullable=True),
        sa.Column("allocation_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("allocation_value", sa.Numeric(18, 2), nullable=True),
        # Validity
        sa.Column("valid_from", sa.Date, nullable=True),
        sa.Column("valid_until", sa.Date, nullable=True),
        # Integration
        sa.Column("external_code", sa.String(50), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Flags
        sa.Column("accepts_entries", sa.Boolean, server_default="true", nullable=False),
        sa.Column("is_productive", sa.Boolean, server_default="true", nullable=False),
        sa.Column("is_allocatable", sa.Boolean, server_default="true", nullable=False),
        sa.Column("active", sa.Boolean, server_default="true", nullable=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["fin_cost_centers.id"],
            name="fk_cost_center_parent",
        ),
    )

    # Indexes for fin_cost_centers
    op.create_index("ix_fin_cost_centers_condominio", "fin_cost_centers", ["condominio_id"])
    op.create_index("ix_fin_cost_centers_parent", "fin_cost_centers", ["parent_id"])
    op.create_index("ix_fin_cost_centers_code", "fin_cost_centers", ["code"])
    op.create_index("ix_fin_cost_centers_type", "fin_cost_centers", ["center_type"])
    op.create_index("ix_fin_cost_centers_status", "fin_cost_centers", ["status"])
    op.create_index("ix_fin_cost_centers_active", "fin_cost_centers", ["active"])
    op.create_unique_constraint(
        "uq_fin_cost_centers_code_condo",
        "fin_cost_centers",
        ["condominio_id", "code"],
    )

    # ==========================================================================
    # TABLE: fin_accounting_periods
    # ==========================================================================
    op.create_table(
        "fin_accounting_periods",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identification
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Type and Status
        sa.Column("period_type", period_type_enum, server_default="MONTHLY", nullable=False),
        sa.Column("status", period_status_enum, server_default="PENDING", nullable=False),
        # Dates
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("month", sa.Integer, nullable=True),
        sa.Column("quarter", sa.Integer, nullable=True),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        # Opening
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opened_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Closing
        sa.Column("closing_type", closing_type_enum, nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("closing_notes", sa.Text, nullable=True),
        # Reopen
        sa.Column("reopened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reopened_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reopen_reason", sa.Text, nullable=True),
        sa.Column("reopen_count", sa.Integer, server_default="0", nullable=False),
        # Stats
        sa.Column("total_entries", sa.Integer, server_default="0", nullable=False),
        sa.Column("total_debit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_credit", sa.Numeric(18, 2), server_default="0", nullable=False),
        # SPED
        sa.Column("sped_transmitted", sa.Boolean, server_default="false", nullable=False),
        sa.Column("sped_transmission_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sped_receipt", sa.String(100), nullable=True),
        # Integration
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Flags
        sa.Column("is_adjustment", sa.Boolean, server_default="false", nullable=False),
        sa.Column("is_opening", sa.Boolean, server_default="false", nullable=False),
        sa.Column("is_closing", sa.Boolean, server_default="false", nullable=False),
        sa.Column("allow_posting", sa.Boolean, server_default="true", nullable=False),
        sa.Column("active", sa.Boolean, server_default="true", nullable=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes for fin_accounting_periods
    op.create_index("ix_fin_periods_condominio", "fin_accounting_periods", ["condominio_id"])
    op.create_index("ix_fin_periods_code", "fin_accounting_periods", ["code"])
    op.create_index("ix_fin_periods_type", "fin_accounting_periods", ["period_type"])
    op.create_index("ix_fin_periods_status", "fin_accounting_periods", ["status"])
    op.create_index("ix_fin_periods_year", "fin_accounting_periods", ["year"])
    op.create_index("ix_fin_periods_dates", "fin_accounting_periods", ["start_date", "end_date"])
    op.create_index("ix_fin_periods_active", "fin_accounting_periods", ["active"])
    op.create_unique_constraint(
        "uq_fin_periods_code_condo",
        "fin_accounting_periods",
        ["condominio_id", "code"],
    )

    # ==========================================================================
    # TABLE: fin_journal_entries
    # ==========================================================================
    op.create_table(
        "fin_journal_entries",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Period Reference
        sa.Column("period_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Identification
        sa.Column("entry_number", sa.String(30), nullable=False),
        sa.Column("batch_number", sa.String(30), nullable=True),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("complement", sa.Text, nullable=True),
        # Type and Status
        sa.Column("entry_type", entry_type_enum, server_default="MANUAL", nullable=False),
        sa.Column("status", entry_status_enum, server_default="DRAFT", nullable=False),
        sa.Column("origin", entry_origin_enum, server_default="MANUAL", nullable=False),
        # Dates
        sa.Column("entry_date", sa.Date, nullable=False),
        sa.Column("competence_date", sa.Date, nullable=False),
        sa.Column("posting_date", sa.DateTime(timezone=True), nullable=True),
        # Totals
        sa.Column("total_debit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_credit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("line_count", sa.Integer, server_default="0", nullable=False),
        # Source Document
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_number", sa.String(50), nullable=True),
        # Reversal
        sa.Column("is_reversal", sa.Boolean, server_default="false", nullable=False),
        sa.Column("reversed_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reversal_entry_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reversal_reason", sa.String(200), nullable=True),
        sa.Column("reversal_date", sa.DateTime(timezone=True), nullable=True),
        # Approval
        sa.Column("requires_approval", sa.Boolean, server_default="false", nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        sa.Column("rejected_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Posting
        sa.Column("posted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # SPED
        sa.Column("sped_included", sa.Boolean, server_default="false", nullable=False),
        sa.Column("sped_record_type", sa.String(10), nullable=True),
        # Integration
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Attachments
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        # Flags
        sa.Column("is_template", sa.Boolean, server_default="false", nullable=False),
        sa.Column("is_recurring", sa.Boolean, server_default="false", nullable=False),
        sa.Column("is_balanced", sa.Boolean, server_default="true", nullable=False),
        sa.Column("active", sa.Boolean, server_default="true", nullable=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["period_id"],
            ["fin_accounting_periods.id"],
            name="fk_entry_period",
        ),
        sa.ForeignKeyConstraint(
            ["reversed_entry_id"],
            ["fin_journal_entries.id"],
            name="fk_entry_reversed",
        ),
    )

    # Indexes for fin_journal_entries
    op.create_index("ix_fin_entries_condominio", "fin_journal_entries", ["condominio_id"])
    op.create_index("ix_fin_entries_period", "fin_journal_entries", ["period_id"])
    op.create_index("ix_fin_entries_number", "fin_journal_entries", ["entry_number"])
    op.create_index("ix_fin_entries_type", "fin_journal_entries", ["entry_type"])
    op.create_index("ix_fin_entries_status", "fin_journal_entries", ["status"])
    op.create_index("ix_fin_entries_origin", "fin_journal_entries", ["origin"])
    op.create_index("ix_fin_entries_date", "fin_journal_entries", ["entry_date"])
    op.create_index("ix_fin_entries_source", "fin_journal_entries", ["source_type", "source_id"])
    op.create_index("ix_fin_entries_active", "fin_journal_entries", ["active"])
    op.create_unique_constraint(
        "uq_fin_entries_number_condo",
        "fin_journal_entries",
        ["condominio_id", "entry_number"],
    )

    # ==========================================================================
    # TABLE: fin_journal_entry_lines
    # ==========================================================================
    op.create_table(
        "fin_journal_entry_lines",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # References
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cost_center_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Line Number
        sa.Column("line_number", sa.Integer, nullable=False),
        # Values
        sa.Column("debit_amount", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("credit_amount", sa.Numeric(18, 2), server_default="0", nullable=False),
        # History
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("history_code", sa.String(10), nullable=True),
        # Document
        sa.Column("document_type", sa.String(30), nullable=True),
        sa.Column("document_number", sa.String(50), nullable=True),
        sa.Column("document_date", sa.Date, nullable=True),
        # Counterpart
        sa.Column("counterpart_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("counterpart_account_code", sa.String(30), nullable=True),
        # Allocation
        sa.Column("allocation_key", sa.String(50), nullable=True),
        sa.Column("allocation_percentage", sa.Numeric(5, 2), nullable=True),
        # Project
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("project_code", sa.String(30), nullable=True),
        # Reconciliation
        sa.Column("is_reconciled", sa.Boolean, server_default="false", nullable=False),
        sa.Column("reconciliation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reconciliation_date", sa.DateTime(timezone=True), nullable=True),
        # SPED
        sa.Column("sped_account_code", sa.String(30), nullable=True),
        sa.Column("sped_cost_center_code", sa.String(30), nullable=True),
        # Integration
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"],
            ["fin_journal_entries.id"],
            name="fk_line_entry",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["fin_accounting_accounts.id"],
            name="fk_line_account",
        ),
        sa.ForeignKeyConstraint(
            ["cost_center_id"],
            ["fin_cost_centers.id"],
            name="fk_line_cost_center",
        ),
    )

    # Indexes for fin_journal_entry_lines
    op.create_index("ix_fin_lines_entry", "fin_journal_entry_lines", ["journal_entry_id"])
    op.create_index("ix_fin_lines_account", "fin_journal_entry_lines", ["account_id"])
    op.create_index("ix_fin_lines_cost_center", "fin_journal_entry_lines", ["cost_center_id"])
    op.create_index("ix_fin_lines_reconciled", "fin_journal_entry_lines", ["is_reconciled"])

    # ==========================================================================
    # TABLE: fin_trial_balances
    # ==========================================================================
    op.create_table(
        "fin_trial_balances",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # Multi-tenant
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False),
        # References
        sa.Column("chart_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Identification
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        # Type and Status
        sa.Column("balance_type", balance_type_enum, server_default="VERIFICATION", nullable=False),
        sa.Column("status", balance_status_enum, server_default="DRAFT", nullable=False),
        sa.Column("balance_period", balance_period_enum, server_default="MONTHLY", nullable=False),
        # Period Reference
        sa.Column("reference_date", sa.Date, nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("month", sa.Integer, nullable=True),
        # Totals
        sa.Column("total_accounts", sa.Integer, server_default="0", nullable=False),
        sa.Column("total_analytical", sa.Integer, server_default="0", nullable=False),
        # Previous Balances
        sa.Column("previous_debit_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("previous_credit_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("previous_balance_debit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("previous_balance_credit", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Period Movements
        sa.Column("period_debit_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("period_credit_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Current Balances
        sa.Column("current_debit_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("current_credit_total", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("current_balance_debit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("current_balance_credit", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Verification
        sa.Column("is_balanced", sa.Boolean, server_default="true", nullable=False),
        sa.Column("difference_amount", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Result
        sa.Column("total_revenue", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_expenses", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("period_result", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Equity
        sa.Column("total_assets", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_liabilities", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("total_equity", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Generation
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("generated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("generation_time_ms", sa.Integer, nullable=True),
        # Approval
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        # Publication
        sa.Column("published_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        # Comparison
        sa.Column("comparison_balance_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("variation_absolute", sa.Numeric(18, 2), nullable=True),
        sa.Column("variation_percentage", sa.Numeric(8, 4), nullable=True),
        # Filters
        sa.Column("filter_account_types", postgresql.JSONB, nullable=True),
        sa.Column("filter_levels", postgresql.JSONB, nullable=True),
        sa.Column("filter_cost_centers", postgresql.JSONB, nullable=True),
        # Integration
        sa.Column("external_reference", sa.String(100), nullable=True),
        sa.Column("integration_data", postgresql.JSONB, nullable=True),
        # Exports
        sa.Column("exported_pdf", sa.Boolean, server_default="false", nullable=False),
        sa.Column("exported_excel", sa.Boolean, server_default="false", nullable=False),
        sa.Column("exported_sped", sa.Boolean, server_default="false", nullable=False),
        sa.Column("last_export_date", sa.DateTime(timezone=True), nullable=True),
        # Flags
        sa.Column("include_zero_balance", sa.Boolean, server_default="false", nullable=False),
        sa.Column("include_inactive", sa.Boolean, server_default="false", nullable=False),
        sa.Column("show_cost_centers", sa.Boolean, server_default="false", nullable=False),
        sa.Column("active", sa.Boolean, server_default="true", nullable=False),
        # Notes
        sa.Column("notes", sa.Text, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        # Audit
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["chart_id"],
            ["fin_charts_of_accounts.id"],
            name="fk_balance_chart",
        ),
        sa.ForeignKeyConstraint(
            ["period_id"],
            ["fin_accounting_periods.id"],
            name="fk_balance_period",
        ),
    )

    # Indexes for fin_trial_balances
    op.create_index("ix_fin_balances_condominio", "fin_trial_balances", ["condominio_id"])
    op.create_index("ix_fin_balances_chart", "fin_trial_balances", ["chart_id"])
    op.create_index("ix_fin_balances_period", "fin_trial_balances", ["period_id"])
    op.create_index("ix_fin_balances_code", "fin_trial_balances", ["code"])
    op.create_index("ix_fin_balances_type", "fin_trial_balances", ["balance_type"])
    op.create_index("ix_fin_balances_status", "fin_trial_balances", ["status"])
    op.create_index("ix_fin_balances_year", "fin_trial_balances", ["year"])
    op.create_index("ix_fin_balances_date", "fin_trial_balances", ["reference_date"])
    op.create_index("ix_fin_balances_active", "fin_trial_balances", ["active"])
    op.create_unique_constraint(
        "uq_fin_balances_code_condo",
        "fin_trial_balances",
        ["condominio_id", "code"],
    )

    # ==========================================================================
    # TABLE: fin_trial_balance_items
    # ==========================================================================
    op.create_table(
        "fin_trial_balance_items",
        # Primary Key
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        # References
        sa.Column("trial_balance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Account Snapshot
        sa.Column("account_code", sa.String(30), nullable=False),
        sa.Column("account_name", sa.String(150), nullable=False),
        sa.Column("account_type", sa.String(20), nullable=False),
        sa.Column("account_nature", sa.String(10), nullable=False),
        sa.Column("account_level", sa.Integer, nullable=False),
        sa.Column("is_analytical", sa.Boolean, nullable=False),
        # Cost Center (optional)
        sa.Column("cost_center_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cost_center_code", sa.String(20), nullable=True),
        sa.Column("cost_center_name", sa.String(100), nullable=True),
        # Previous Balance
        sa.Column("previous_debit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("previous_credit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("previous_balance", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Period Movement
        sa.Column("period_debit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("period_credit", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Current Balance
        sa.Column("current_debit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("current_credit", sa.Numeric(18, 2), server_default="0", nullable=False),
        sa.Column("current_balance", sa.Numeric(18, 2), server_default="0", nullable=False),
        # Variation
        sa.Column("variation_absolute", sa.Numeric(18, 2), nullable=True),
        sa.Column("variation_percentage", sa.Numeric(8, 4), nullable=True),
        # Display
        sa.Column("display_order", sa.Integer, nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["trial_balance_id"],
            ["fin_trial_balances.id"],
            name="fk_balance_item_balance",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["fin_accounting_accounts.id"],
            name="fk_balance_item_account",
        ),
    )

    # Indexes for fin_trial_balance_items
    op.create_index("ix_fin_balance_items_balance", "fin_trial_balance_items", ["trial_balance_id"])
    op.create_index("ix_fin_balance_items_account", "fin_trial_balance_items", ["account_id"])
    op.create_index("ix_fin_balance_items_code", "fin_trial_balance_items", ["account_code"])
    op.create_index("ix_fin_balance_items_type", "fin_trial_balance_items", ["account_type"])


def downgrade() -> None:
    """Drop accounting tables."""
    # Drop tables in reverse order
    op.drop_table("fin_trial_balance_items")
    op.drop_table("fin_trial_balances")
    op.drop_table("fin_journal_entry_lines")
    op.drop_table("fin_journal_entries")
    op.drop_table("fin_accounting_periods")
    op.drop_table("fin_cost_centers")
    op.drop_table("fin_accounting_accounts")
    op.drop_table("fin_charts_of_accounts")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS balanceperiod")
    op.execute("DROP TYPE IF EXISTS balancestatus")
    op.execute("DROP TYPE IF EXISTS balancetype")
    op.execute("DROP TYPE IF EXISTS entryorigin")
    op.execute("DROP TYPE IF EXISTS entrystatus")
    op.execute("DROP TYPE IF EXISTS entrytype")
    op.execute("DROP TYPE IF EXISTS closingtype")
    op.execute("DROP TYPE IF EXISTS periodstatus")
    op.execute("DROP TYPE IF EXISTS periodtype")
    op.execute("DROP TYPE IF EXISTS allocationmethod")
    op.execute("DROP TYPE IF EXISTS costcenterstatus")
    op.execute("DROP TYPE IF EXISTS costcentertype")
    op.execute("DROP TYPE IF EXISTS spedaccountnature")
    op.execute("DROP TYPE IF EXISTS accountstatus")
    op.execute("DROP TYPE IF EXISTS accountclassification")
    op.execute("DROP TYPE IF EXISTS accountnature")
    op.execute("DROP TYPE IF EXISTS accounttype")
    op.execute("DROP TYPE IF EXISTS chartstandard")
    op.execute("DROP TYPE IF EXISTS chartstatus")
    op.execute("DROP TYPE IF EXISTS charttype")
