"""Add missing cnae column to suppliers table.

Revision ID: sprint61_add_supplier_cnae
Revises: sprint60_fix_financial_schema
Create Date: 2026-03-08

"""

from alembic import op

revision = "sprint61_add_supplier_cnae"
down_revision = "sprint60_fix_financial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing cnae column to suppliers
    op.execute("ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS cnae VARCHAR(10)")


def downgrade() -> None:
    op.execute("ALTER TABLE suppliers DROP COLUMN IF EXISTS cnae")
