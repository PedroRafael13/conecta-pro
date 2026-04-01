"""Fix schema alignment between bidding models and migrations.

Add extra columns that models define but sprint71 migration did not create:
- bidding_pricing: assessment_id (UUID FK), raw_pricing (JSONB)
- bidding_price_history: metadata_extra (JSONB)
- bidding_disputes: updated_at (TIMESTAMP)

Revision ID: sprint72_fix_bidding_schema
Revises: sprint71_bidding_ai_agents
Create Date: 2026-03-12

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint72_fix_bidding_schema"
down_revision = "sprint71_bidding_ai_agents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # bidding_pricing: add assessment_id FK and raw_pricing
    op.add_column(
        "bidding_pricing",
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_pricing_assessment_id",
        "bidding_pricing",
        "bidding_assessments",
        ["assessment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("idx_pricing_assessment", "bidding_pricing", ["assessment_id"])
    op.add_column(
        "bidding_pricing",
        sa.Column("raw_pricing", postgresql.JSONB, nullable=True),
    )

    # bidding_price_history: add metadata_extra
    op.add_column(
        "bidding_price_history",
        sa.Column("metadata_extra", postgresql.JSONB, nullable=True),
    )

    # bidding_disputes: add updated_at
    op.add_column(
        "bidding_disputes",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    # bidding_disputes: drop updated_at
    op.drop_column("bidding_disputes", "updated_at")

    # bidding_price_history: drop metadata_extra
    op.drop_column("bidding_price_history", "metadata_extra")

    # bidding_pricing: drop raw_pricing and assessment_id
    op.drop_column("bidding_pricing", "raw_pricing")
    op.drop_index("idx_pricing_assessment", table_name="bidding_pricing")
    op.drop_constraint("fk_pricing_assessment_id", "bidding_pricing", type_="foreignkey")
    op.drop_column("bidding_pricing", "assessment_id")
