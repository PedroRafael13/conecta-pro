"""sprint82b: GEDEON Fase 3 — corrige schema das tabelas Onvio

Revision ID: sprint82b_gedeon_schema_fix
Revises: sprint82_gedeon_fase3_onvio
Create Date: 2026-04-17

Problema: tabelas criadas anteriormente com schema divergente do modelo Python.
  - fgts_guias: faltam onvio_doc_id (UUID) e vencimento (timestamp); tem data_vencimento (varchar)
  - inss_guias: faltam onvio_doc_id (UUID), competencia (varchar) e vencimento (timestamp)
  - onvio_documents: data_onvio criado como varchar em vez de timestamp

Correções:
  - Renomear data_vencimento → vencimento + ALTER TYPE para timestamp
  - Adicionar onvio_doc_id UUID nullable em fgts_guias e inss_guias
  - Adicionar competencia VARCHAR(7) em inss_guias
  - ALTER data_onvio para timestamp em onvio_documents
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint82b_gedeon_schema_fix"
down_revision = "sprint82_gedeon_fase3_onvio"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── fgts_guias ──────────────────────────────────────────────────────────
    # Renomear data_vencimento → vencimento e converter para timestamp
    op.execute("ALTER TABLE fgts_guias RENAME COLUMN data_vencimento TO vencimento")
    op.execute(
        """ALTER TABLE fgts_guias
           ALTER COLUMN vencimento TYPE TIMESTAMP WITH TIME ZONE
           USING CASE WHEN vencimento IS NULL OR vencimento = '' THEN NULL
                      ELSE vencimento::TIMESTAMP WITH TIME ZONE END"""
    )
    # Adicionar onvio_doc_id
    op.add_column(
        "fgts_guias",
        sa.Column("onvio_doc_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # ── inss_guias ───────────────────────────────────────────────────────────
    # Renomear data_vencimento → vencimento e converter para timestamp
    op.execute("ALTER TABLE inss_guias RENAME COLUMN data_vencimento TO vencimento")
    op.execute(
        """ALTER TABLE inss_guias
           ALTER COLUMN vencimento TYPE TIMESTAMP WITH TIME ZONE
           USING CASE WHEN vencimento IS NULL OR vencimento = '' THEN NULL
                      ELSE vencimento::TIMESTAMP WITH TIME ZONE END"""
    )
    # Adicionar onvio_doc_id e competencia
    op.add_column(
        "inss_guias",
        sa.Column("onvio_doc_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "inss_guias",
        sa.Column("competencia", sa.String(7), nullable=True),
    )

    # ── onvio_documents ──────────────────────────────────────────────────────
    # data_onvio foi criado como varchar — converter para timestamp
    op.execute(
        """ALTER TABLE onvio_documents
           ALTER COLUMN data_onvio TYPE TIMESTAMP WITH TIME ZONE
           USING CASE WHEN data_onvio IS NULL OR data_onvio = '' THEN NULL
                      ELSE data_onvio::TIMESTAMP WITH TIME ZONE END"""
    )


def downgrade() -> None:
    # onvio_documents
    op.execute("ALTER TABLE onvio_documents ALTER COLUMN data_onvio TYPE VARCHAR(255)")

    # inss_guias
    op.drop_column("inss_guias", "competencia")
    op.drop_column("inss_guias", "onvio_doc_id")
    op.execute("ALTER TABLE inss_guias ALTER COLUMN vencimento TYPE VARCHAR(50)")
    op.execute("ALTER TABLE inss_guias RENAME COLUMN vencimento TO data_vencimento")

    # fgts_guias
    op.drop_column("fgts_guias", "onvio_doc_id")
    op.execute("ALTER TABLE fgts_guias ALTER COLUMN vencimento TYPE VARCHAR(50)")
    op.execute("ALTER TABLE fgts_guias RENAME COLUMN vencimento TO data_vencimento")
