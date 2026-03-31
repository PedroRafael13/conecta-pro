"""Altera gp_justifications.employee_id de Integer para String(36) (UUID)

Revision ID: sprint79_justification_employee_uuid
Revises: sprint78_cct_db_001
Create Date: 2026-03-30
"""

import sqlalchemy as sa

from alembic import op

revision = "sprint79_just_uuid"
down_revision = "sprint78_cct_db_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop index that references the column
    op.drop_index("ix_gp_justification_status", table_name="gp_justifications")
    op.drop_index("ix_gp_justifications_employee_id", table_name="gp_justifications")

    # Alter column type from Integer to VARCHAR(36)
    op.alter_column(
        "gp_justifications",
        "employee_id",
        type_=sa.String(36),
        existing_type=sa.Integer(),
        nullable=False,
        postgresql_using="employee_id::varchar",
    )

    # Recreate indexes
    op.create_index("ix_gp_justifications_employee_id", "gp_justifications", ["employee_id"])
    op.create_index("ix_gp_justification_status", "gp_justifications", ["status", "employee_id"])


def downgrade() -> None:
    op.drop_index("ix_gp_justification_status", table_name="gp_justifications")
    op.drop_index("ix_gp_justifications_employee_id", table_name="gp_justifications")

    op.alter_column(
        "gp_justifications",
        "employee_id",
        type_=sa.Integer(),
        existing_type=sa.String(36),
        nullable=False,
        postgresql_using="employee_id::integer",
    )

    op.create_index("ix_gp_justifications_employee_id", "gp_justifications", ["employee_id"])
    op.create_index("ix_gp_justification_status", "gp_justifications", ["status", "employee_id"])
