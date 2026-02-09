"""Sprint 48: Create data quality tables

Revision ID: sprint48_data_quality
Revises: sprint47_report_gen
Create Date: 2026-01-06

Cria tabelas para o módulo AI Data Quality:
- ai_data_quality_rules: Regras de validação
- ai_data_quality_checks: Execuções de verificação
- ai_data_quality_issues: Problemas encontrados
- ai_duplicate_records: Registros duplicados
- ai_data_profiles: Perfis estatísticos de dados
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "sprint48_data_quality"
down_revision = "sprint47_report_gen"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============== ENUMS ==============

    # Rule Type Enum
    rule_type_enum = postgresql.ENUM(
        "REQUIRED",
        "UNIQUE",
        "FORMAT",
        "RANGE",
        "LENGTH",
        "PATTERN",
        "CUSTOM",
        "REFERENCE",
        "CONSISTENCY",
        "COMPLETENESS",
        "CPF_VALID",
        "CNPJ_VALID",
        "EMAIL_VALID",
        "PHONE_VALID",
        "CEP_VALID",
        "DATE_VALID",
        "NUMERIC_RANGE",
        "STRING_LENGTH",
        "ENUM_VALUE",
        "REGEX_MATCH",
        "NOT_NULL",
        "NOT_EMPTY",
        "POSITIVE_NUMBER",
        "NON_NEGATIVE",
        "PAST_DATE",
        "FUTURE_DATE",
        "DATE_RANGE",
        "VALUE_LIST",
        "FOREIGN_KEY",
        "CROSS_FIELD",
        "CONDITIONAL",
        "AGGREGATE",
        "STATISTICAL",
        name="ruletype_enum",
        create_type=False,
    )

    # Rule Severity Enum
    rule_severity_enum = postgresql.ENUM(
        "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", name="ruleseverity_enum", create_type=False
    )

    # Rule Status Enum
    rule_status_enum = postgresql.ENUM(
        "ACTIVE", "INACTIVE", "DRAFT", "DEPRECATED", "TESTING", name="rulestatus_enum", create_type=False
    )

    # Rule Category Enum
    rule_category_enum = postgresql.ENUM(
        "COMPLETENESS",
        "ACCURACY",
        "CONSISTENCY",
        "VALIDITY",
        "UNIQUENESS",
        "TIMELINESS",
        "STANDARDIZATION",
        name="rulecategory_enum",
        create_type=False,
    )

    # Check Status Enum
    check_status_enum = postgresql.ENUM(
        "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED", "PARTIAL", name="checkstatus_enum", create_type=False
    )

    # Check Scope Enum
    check_scope_enum = postgresql.ENUM(
        "FULL", "INCREMENTAL", "SAMPLE", "SINGLE_RECORD", "BATCH", name="checkscope_enum", create_type=False
    )

    # Issue Type Enum
    issue_type_enum = postgresql.ENUM(
        "MISSING_VALUE",
        "INVALID_VALUE",
        "DUPLICATE_RECORD",
        "INCONSISTENT_DATA",
        "FORMAT_ERROR",
        "RANGE_VIOLATION",
        "REFERENCE_ERROR",
        "PATTERN_MISMATCH",
        "LENGTH_VIOLATION",
        "TYPE_MISMATCH",
        "ENCODING_ERROR",
        "COMPLETENESS_ERROR",
        "ACCURACY_ERROR",
        "TIMELINESS_ERROR",
        "STANDARDIZATION_ERROR",
        "OUTLIER_DETECTED",
        "ANOMALY_DETECTED",
        "CROSS_FIELD_ERROR",
        "BUSINESS_RULE_VIOLATION",
        "CUSTOM_ERROR",
        name="issuetype_enum",
        create_type=False,
    )

    # Issue Status Enum
    issue_status_enum = postgresql.ENUM(
        "OPEN",
        "ACKNOWLEDGED",
        "IN_PROGRESS",
        "FIXED",
        "IGNORED",
        "FALSE_POSITIVE",
        "WONT_FIX",
        name="issuestatus_enum",
        create_type=False,
    )

    # Issue Resolution Enum
    issue_resolution_enum = postgresql.ENUM(
        "MANUAL_FIX",
        "AUTO_FIX",
        "DATA_CORRECTION",
        "RECORD_DELETION",
        "MERGE_RECORDS",
        "IGNORE",
        "FALSE_POSITIVE",
        "DEFERRED",
        name="issueresolution_enum",
        create_type=False,
    )

    # Duplicate Type Enum
    duplicate_type_enum = postgresql.ENUM(
        "EXACT", "FUZZY", "PARTIAL", "PHONETIC", "SEMANTIC", name="duplicatetype_enum", create_type=False
    )

    # Duplicate Status Enum
    duplicate_status_enum = postgresql.ENUM(
        "DETECTED",
        "REVIEWING",
        "CONFIRMED",
        "MERGED",
        "REJECTED",
        "DEFERRED",
        "AUTO_MERGED",
        name="duplicatestatus_enum",
        create_type=False,
    )

    # Merge Strategy Enum
    merge_strategy_enum = postgresql.ENUM(
        "KEEP_FIRST",
        "KEEP_LAST",
        "KEEP_MOST_COMPLETE",
        "MERGE_FIELDS",
        "MANUAL",
        name="mergestrategy_enum",
        create_type=False,
    )

    # Profile Status Enum
    profile_status_enum = postgresql.ENUM(
        "PENDING", "RUNNING", "COMPLETED", "FAILED", name="profilestatus_enum", create_type=False
    )

    # Data Type Enum
    data_type_enum = postgresql.ENUM(
        "STRING",
        "INTEGER",
        "FLOAT",
        "BOOLEAN",
        "DATE",
        "DATETIME",
        "EMAIL",
        "CPF",
        "CNPJ",
        "PHONE",
        "CEP",
        "URL",
        "UUID",
        "JSON",
        "ARRAY",
        "CURRENCY",
        "PERCENTAGE",
        "UNKNOWN",
        name="datatype_enum",
        create_type=False,
    )

    # Create all enums
    rule_type_enum.create(op.get_bind(), checkfirst=True)
    rule_severity_enum.create(op.get_bind(), checkfirst=True)
    rule_status_enum.create(op.get_bind(), checkfirst=True)
    rule_category_enum.create(op.get_bind(), checkfirst=True)
    check_status_enum.create(op.get_bind(), checkfirst=True)
    check_scope_enum.create(op.get_bind(), checkfirst=True)
    issue_type_enum.create(op.get_bind(), checkfirst=True)
    issue_status_enum.create(op.get_bind(), checkfirst=True)
    issue_resolution_enum.create(op.get_bind(), checkfirst=True)
    duplicate_type_enum.create(op.get_bind(), checkfirst=True)
    duplicate_status_enum.create(op.get_bind(), checkfirst=True)
    merge_strategy_enum.create(op.get_bind(), checkfirst=True)
    profile_status_enum.create(op.get_bind(), checkfirst=True)
    data_type_enum.create(op.get_bind(), checkfirst=True)

    # ============== TABLES ==============

    # 1. ai_data_quality_rules
    op.create_table(
        "ai_data_quality_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("rule_code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column(
            "rule_type",
            postgresql.ENUM(
                "REQUIRED",
                "UNIQUE",
                "FORMAT",
                "RANGE",
                "LENGTH",
                "PATTERN",
                "CUSTOM",
                "REFERENCE",
                "CONSISTENCY",
                "COMPLETENESS",
                "CPF_VALID",
                "CNPJ_VALID",
                "EMAIL_VALID",
                "PHONE_VALID",
                "CEP_VALID",
                "DATE_VALID",
                "NUMERIC_RANGE",
                "STRING_LENGTH",
                "ENUM_VALUE",
                "REGEX_MATCH",
                "NOT_NULL",
                "NOT_EMPTY",
                "POSITIVE_NUMBER",
                "NON_NEGATIVE",
                "PAST_DATE",
                "FUTURE_DATE",
                "DATE_RANGE",
                "VALUE_LIST",
                "FOREIGN_KEY",
                "CROSS_FIELD",
                "CONDITIONAL",
                "AGGREGATE",
                "STATISTICAL",
                name="ruletype_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            postgresql.ENUM("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", name="ruleseverity_enum", create_type=False),
            nullable=False,
            server_default="MEDIUM",
        ),
        sa.Column(
            "category",
            postgresql.ENUM(
                "COMPLETENESS",
                "ACCURACY",
                "CONSISTENCY",
                "VALIDITY",
                "UNIQUENESS",
                "TIMELINESS",
                "STANDARDIZATION",
                name="rulecategory_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "ACTIVE", "INACTIVE", "DRAFT", "DEPRECATED", "TESTING", name="rulestatus_enum", create_type=False
            ),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("field_name", sa.String(100)),
        sa.Column("validation_expression", sa.Text),
        sa.Column("error_message", sa.String(500)),
        sa.Column("fix_suggestion", sa.Text),
        sa.Column("auto_fix_enabled", sa.Boolean, server_default="false"),
        sa.Column("auto_fix_expression", sa.Text),
        sa.Column("parameters", postgresql.JSONB, server_default="{}"),
        sa.Column("conditions", postgresql.JSONB, server_default="{}"),
        sa.Column("priority", sa.Integer, server_default="50"),
        sa.Column("execution_order", sa.Integer, server_default="100"),
        sa.Column("is_system_rule", sa.Boolean, server_default="false"),
        sa.Column("tags", postgresql.ARRAY(sa.String(50)), server_default="{}"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    op.create_index("ix_dq_rules_entity_type", "ai_data_quality_rules", ["entity_type"])
    op.create_index("ix_dq_rules_status", "ai_data_quality_rules", ["status"])
    op.create_index("ix_dq_rules_category", "ai_data_quality_rules", ["category"])
    op.create_index("ix_dq_rules_rule_type", "ai_data_quality_rules", ["rule_type"])

    # 2. ai_data_quality_checks
    op.create_table(
        "ai_data_quality_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("check_code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column(
            "scope",
            postgresql.ENUM(
                "FULL", "INCREMENTAL", "SAMPLE", "SINGLE_RECORD", "BATCH", name="checkscope_enum", create_type=False
            ),
            nullable=False,
            server_default="FULL",
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING",
                "RUNNING",
                "COMPLETED",
                "FAILED",
                "CANCELLED",
                "PARTIAL",
                name="checkstatus_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("rule_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default="{}"),
        sa.Column("filter_criteria", postgresql.JSONB, server_default="{}"),
        sa.Column("sample_size", sa.Integer),
        sa.Column("sample_percentage", sa.Float),
        sa.Column("total_records", sa.Integer, server_default="0"),
        sa.Column("processed_records", sa.Integer, server_default="0"),
        sa.Column("passed_records", sa.Integer, server_default="0"),
        sa.Column("failed_records", sa.Integer, server_default="0"),
        sa.Column("issues_found", sa.Integer, server_default="0"),
        sa.Column("issues_fixed", sa.Integer, server_default="0"),
        sa.Column("quality_score", sa.Float),
        sa.Column("progress_percentage", sa.Float, server_default="0"),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("duration_seconds", sa.Float),
        sa.Column("error_message", sa.Text),
        sa.Column("statistics", postgresql.JSONB, server_default="{}"),
        sa.Column("results_summary", postgresql.JSONB, server_default="{}"),
        sa.Column("rule_results", postgresql.JSONB, server_default="{}"),
        sa.Column("scheduled", sa.Boolean, server_default="false"),
        sa.Column("schedule_cron", sa.String(100)),
        sa.Column("last_run_at", sa.DateTime),
        sa.Column("next_run_at", sa.DateTime),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    op.create_index("ix_dq_checks_entity_type", "ai_data_quality_checks", ["entity_type"])
    op.create_index("ix_dq_checks_status", "ai_data_quality_checks", ["status"])
    op.create_index("ix_dq_checks_created_at", "ai_data_quality_checks", ["created_at"])

    # 3. ai_data_quality_issues
    op.create_table(
        "ai_data_quality_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("issue_code", sa.String(50), nullable=False, unique=True),
        sa.Column("check_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_data_quality_checks.id")),
        sa.Column("rule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_data_quality_rules.id")),
        sa.Column(
            "issue_type",
            postgresql.ENUM(
                "MISSING_VALUE",
                "INVALID_VALUE",
                "DUPLICATE_RECORD",
                "INCONSISTENT_DATA",
                "FORMAT_ERROR",
                "RANGE_VIOLATION",
                "REFERENCE_ERROR",
                "PATTERN_MISMATCH",
                "LENGTH_VIOLATION",
                "TYPE_MISMATCH",
                "ENCODING_ERROR",
                "COMPLETENESS_ERROR",
                "ACCURACY_ERROR",
                "TIMELINESS_ERROR",
                "STANDARDIZATION_ERROR",
                "OUTLIER_DETECTED",
                "ANOMALY_DETECTED",
                "CROSS_FIELD_ERROR",
                "BUSINESS_RULE_VIOLATION",
                "CUSTOM_ERROR",
                name="issuetype_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            postgresql.ENUM("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", name="ruleseverity_enum", create_type=False),
            nullable=False,
            server_default="MEDIUM",
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "OPEN",
                "ACKNOWLEDGED",
                "IN_PROGRESS",
                "FIXED",
                "IGNORED",
                "FALSE_POSITIVE",
                "WONT_FIX",
                name="issuestatus_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="OPEN",
        ),
        sa.Column(
            "resolution",
            postgresql.ENUM(
                "MANUAL_FIX",
                "AUTO_FIX",
                "DATA_CORRECTION",
                "RECORD_DELETION",
                "MERGE_RECORDS",
                "IGNORE",
                "FALSE_POSITIVE",
                "DEFERRED",
                name="issueresolution_enum",
                create_type=False,
            ),
        ),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("record_id", sa.String(100), nullable=False),
        sa.Column("field_name", sa.String(100)),
        sa.Column("current_value", sa.Text),
        sa.Column("expected_value", sa.Text),
        sa.Column("suggested_value", sa.Text),
        sa.Column("error_message", sa.Text),
        sa.Column("fix_suggestion", sa.Text),
        sa.Column("can_auto_fix", sa.Boolean, server_default="false"),
        sa.Column("auto_fixed", sa.Boolean, server_default="false"),
        sa.Column("auto_fix_value", sa.Text),
        sa.Column("context_data", postgresql.JSONB, server_default="{}"),
        sa.Column("related_issues", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), server_default="{}"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True)),
        sa.Column("acknowledged_by", postgresql.UUID(as_uuid=True)),
        sa.Column("acknowledged_at", sa.DateTime),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True)),
        sa.Column("resolved_at", sa.DateTime),
        sa.Column("resolution_notes", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    op.create_index("ix_dq_issues_check_id", "ai_data_quality_issues", ["check_id"])
    op.create_index("ix_dq_issues_rule_id", "ai_data_quality_issues", ["rule_id"])
    op.create_index("ix_dq_issues_status", "ai_data_quality_issues", ["status"])
    op.create_index("ix_dq_issues_entity_record", "ai_data_quality_issues", ["entity_type", "record_id"])
    op.create_index("ix_dq_issues_severity", "ai_data_quality_issues", ["severity"])

    # 4. ai_duplicate_records
    op.create_table(
        "ai_duplicate_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "DETECTED",
                "REVIEWING",
                "CONFIRMED",
                "MERGED",
                "REJECTED",
                "DEFERRED",
                "AUTO_MERGED",
                name="duplicatestatus_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="DETECTED",
        ),
        sa.Column(
            "duplicate_type",
            postgresql.ENUM(
                "EXACT", "FUZZY", "PARTIAL", "PHONETIC", "SEMANTIC", name="duplicatetype_enum", create_type=False
            ),
            nullable=False,
            server_default="FUZZY",
        ),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("record_ids", postgresql.ARRAY(sa.String(100)), nullable=False),
        sa.Column("record_count", sa.Integer, nullable=False, server_default="2"),
        sa.Column("master_record_id", sa.String(100)),
        sa.Column("matching_fields", postgresql.ARRAY(sa.String(100)), server_default="{}"),
        sa.Column("conflicting_fields", postgresql.ARRAY(sa.String(100)), server_default="{}"),
        sa.Column("similarity_score", sa.Float, nullable=False),
        sa.Column("confidence_score", sa.Float),
        sa.Column("field_scores", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "merge_strategy",
            postgresql.ENUM(
                "KEEP_FIRST",
                "KEEP_LAST",
                "KEEP_MOST_COMPLETE",
                "MERGE_FIELDS",
                "MANUAL",
                name="mergestrategy_enum",
                create_type=False,
            ),
        ),
        sa.Column("merge_rules", postgresql.JSONB, server_default="{}"),
        sa.Column("merged_record_data", postgresql.JSONB),
        sa.Column("can_auto_merge", sa.Boolean, server_default="false"),
        sa.Column("auto_merged", sa.Boolean, server_default="false"),
        sa.Column("merged_at", sa.DateTime),
        sa.Column("merged_by", postgresql.UUID(as_uuid=True)),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True)),
        sa.Column("reviewed_at", sa.DateTime),
        sa.Column("review_notes", sa.Text),
        sa.Column("detection_method", sa.String(100)),
        sa.Column("check_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_data_quality_checks.id")),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    op.create_index("ix_duplicate_records_group_id", "ai_duplicate_records", ["group_id"])
    op.create_index("ix_duplicate_records_entity_type", "ai_duplicate_records", ["entity_type"])
    op.create_index("ix_duplicate_records_status", "ai_duplicate_records", ["status"])
    op.create_index("ix_duplicate_records_similarity", "ai_duplicate_records", ["similarity_score"])

    # 5. ai_data_profiles
    op.create_table(
        "ai_data_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("profile_code", sa.String(50), nullable=False, unique=True),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("field_name", sa.String(100)),
        sa.Column("is_entity_profile", sa.Boolean, server_default="false"),
        sa.Column(
            "status",
            postgresql.ENUM("PENDING", "RUNNING", "COMPLETED", "FAILED", name="profilestatus_enum", create_type=False),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "detected_type",
            postgresql.ENUM(
                "STRING",
                "INTEGER",
                "FLOAT",
                "BOOLEAN",
                "DATE",
                "DATETIME",
                "EMAIL",
                "CPF",
                "CNPJ",
                "PHONE",
                "CEP",
                "URL",
                "UUID",
                "JSON",
                "ARRAY",
                "CURRENCY",
                "PERCENTAGE",
                "UNKNOWN",
                name="datatype_enum",
                create_type=False,
            ),
        ),
        sa.Column("total_records", sa.Integer, server_default="0"),
        sa.Column("null_count", sa.Integer, server_default="0"),
        sa.Column("null_percentage", sa.Float, server_default="0"),
        sa.Column("empty_count", sa.Integer, server_default="0"),
        sa.Column("empty_percentage", sa.Float, server_default="0"),
        sa.Column("distinct_count", sa.Integer, server_default="0"),
        sa.Column("distinct_percentage", sa.Float, server_default="0"),
        sa.Column("duplicate_count", sa.Integer, server_default="0"),
        sa.Column("completeness_score", sa.Float, server_default="0"),
        # Numeric stats
        sa.Column("min_value", sa.Float),
        sa.Column("max_value", sa.Float),
        sa.Column("mean_value", sa.Float),
        sa.Column("median_value", sa.Float),
        sa.Column("std_deviation", sa.Float),
        sa.Column("variance", sa.Float),
        sa.Column("sum_value", sa.Float),
        sa.Column("percentiles", postgresql.JSONB, server_default="{}"),
        # String stats
        sa.Column("min_length", sa.Integer),
        sa.Column("max_length", sa.Integer),
        sa.Column("avg_length", sa.Float),
        sa.Column("common_patterns", postgresql.ARRAY(sa.String(200)), server_default="{}"),
        # Date stats
        sa.Column("date_range_start", sa.DateTime),
        sa.Column("date_range_end", sa.DateTime),
        sa.Column("future_dates_count", sa.Integer, server_default="0"),
        # Distribution
        sa.Column("value_distribution", postgresql.JSONB, server_default="{}"),
        sa.Column("histogram_data", postgresql.JSONB, server_default="{}"),
        # Outliers
        sa.Column("outlier_count", sa.Integer, server_default="0"),
        sa.Column("outlier_percentage", sa.Float, server_default="0"),
        sa.Column("outliers", postgresql.JSONB, server_default="[]"),
        # Quality
        sa.Column("quality_score", sa.Float),
        sa.Column("recommendations", postgresql.JSONB, server_default="[]"),
        # Metadata
        sa.Column("profiled_at", sa.DateTime),
        sa.Column("profiling_duration_seconds", sa.Float),
        sa.Column("error_message", sa.Text),
        sa.Column("extra_metadata", postgresql.JSONB, server_default="{}"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("ativo", sa.Boolean, server_default="true"),
    )

    op.create_index("ix_data_profiles_entity_type", "ai_data_profiles", ["entity_type"])
    op.create_index("ix_data_profiles_field_name", "ai_data_profiles", ["field_name"])
    op.create_index("ix_data_profiles_status", "ai_data_profiles", ["status"])
    op.create_index("ix_data_profiles_profiled_at", "ai_data_profiles", ["profiled_at"])


def downgrade() -> None:
    # Drop tables
    op.drop_table("ai_data_profiles")
    op.drop_table("ai_duplicate_records")
    op.drop_table("ai_data_quality_issues")
    op.drop_table("ai_data_quality_checks")
    op.drop_table("ai_data_quality_rules")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS datatype_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS profilestatus_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS mergestrategy_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS duplicatestatus_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS duplicatetype_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS issueresolution_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS issuestatus_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS issuetype_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS checkscope_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS checkstatus_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS rulecategory_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS rulestatus_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS ruleseverity_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS ruletype_enum CASCADE")
