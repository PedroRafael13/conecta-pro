"""Rename guardian columns to external in access_logs and equipment_status.

As part of the Guardian system removal (Conecta PLUS, not PRO),
this migration renames the guardian_* columns to external_*.

The ORM models already map external_id -> guardian_id column name,
so this migration only needs to run when we're ready to fully
cut over the DB column names.

NOTE: This migration renames DB columns. The ORM aliases handle
backwards compatibility, so this can be applied at any time.

Revision ID: sprint71_rename_guardian_columns
Revises: sprint70_cost_by_type_tables
"""

from alembic import op

revision = "sprint71_rename_guardian_columns"
down_revision = "sprint70_cost_by_type_tables"


def upgrade() -> None:
    # === access_logs ===
    # Rename columns
    op.alter_column("access_logs", "guardian_id", new_column_name="external_id")
    op.alter_column("access_logs", "guardian_metadata", new_column_name="external_metadata")

    # Rename index (drop old, create new)
    op.drop_index("ix_access_logs_guardian_id", table_name="access_logs", if_exists=True)
    op.create_index("ix_access_logs_external_id", "access_logs", ["external_id"], unique=True)

    # === equipment_status ===
    # Rename columns
    op.alter_column("equipment_status", "guardian_id", new_column_name="external_id")
    op.alter_column("equipment_status", "guardian_metadata", new_column_name="external_metadata")

    # Rename index (drop old, create new)
    op.drop_index("ix_equipment_status_guardian_id", table_name="equipment_status", if_exists=True)
    op.create_index("ix_equipment_status_external_id", "equipment_status", ["external_id"], unique=True)


def downgrade() -> None:
    # === access_logs ===
    op.alter_column("access_logs", "external_id", new_column_name="guardian_id")
    op.alter_column("access_logs", "external_metadata", new_column_name="guardian_metadata")
    op.drop_index("ix_access_logs_external_id", table_name="access_logs", if_exists=True)
    op.create_index("ix_access_logs_guardian_id", "access_logs", ["guardian_id"], unique=True)

    # === equipment_status ===
    op.alter_column("equipment_status", "external_id", new_column_name="guardian_id")
    op.alter_column("equipment_status", "external_metadata", new_column_name="guardian_metadata")
    op.drop_index("ix_equipment_status_external_id", table_name="equipment_status", if_exists=True)
    op.create_index("ix_equipment_status_guardian_id", "equipment_status", ["guardian_id"], unique=True)
