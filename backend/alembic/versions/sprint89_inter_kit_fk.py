"""add_kit_document_id_to_inter_transactions

Revision ID: sprint89_inter_kit_fk
Revises: sprint88_inter_cat
Create Date: 2026-05-06

INV-2: ADD COLUMN apenas — nunca DROP, nunca ALTER TYPE.
FK nullable ON DELETE SET NULL — preserva histórico de transações se kit_document for deletado.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint89_inter_kit_fk"
down_revision = "sprint88_inter_cat"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "inter_transactions",
        sa.Column(
            "kit_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ged_kit_documents.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_inter_tx_kit_document",
        "inter_transactions",
        ["kit_document_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_inter_tx_kit_document", table_name="inter_transactions")
    op.drop_column("inter_transactions", "kit_document_id")
