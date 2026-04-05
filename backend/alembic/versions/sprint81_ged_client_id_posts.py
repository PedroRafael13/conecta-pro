"""add ged_client_id to posts

Revision ID: sprint81_ged_client_id_posts
Revises: sprint80b_fin_cols_sync
Create Date: 2026-04-05

Adiciona coluna ged_client_id (UUID, nullable) na tabela posts para
vincular explicitamente um posto ao seu cliente GED, eliminando a
dependência de fuzzy match por nome.
"""

import sqlalchemy as sa

from alembic import op

revision = "sprint81_ged_client_id_posts"
down_revision = "sprint80b_fin_cols_sync"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column(
            "ged_client_id",
            sa.dialects.postgresql.UUID(as_uuid=False),
            nullable=True,
            comment="FK para ged_clients.id — vincula posto ao cliente GED diretamente",
        ),
    )
    op.create_index(
        "ix_posts_ged_client_id",
        "posts",
        ["ged_client_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_posts_ged_client_id", table_name="posts")
    op.drop_column("posts", "ged_client_id")
