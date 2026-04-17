"""sprint82: GEDEON Fase 3 — Onvio Sync tables

Revision ID: sprint82_gedeon_fase3_onvio
Revises: sprint81_ged_client_id_posts
Create Date: 2026-04-17

Cria as 4 tabelas necessárias para o módulo GEDEON Fase 3 — Onvio Sync:
  - onvio_sync_log: log de sincronizações com o Onvio
  - onvio_documents: documentos importados do Onvio
  - fgts_guias: guias FGTS extraídas dos documentos
  - inss_guias: guias INSS extraídas dos documentos
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint82_gedeon_fase3_onvio"
down_revision = "sprint81_ged_client_id_posts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # onvio_sync_log
    op.create_table(
        "onvio_sync_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("mes_ref", sa.String(7), nullable=True),
        sa.Column("status", sa.String(20), nullable=True, server_default="pending"),
        sa.Column("docs_baixados", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("docs_novos", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("docs_erro", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("duracao_s", sa.Float(), nullable=True),
        sa.Column("detalhes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )

    # onvio_documents
    op.create_table(
        "onvio_documents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("onvio_id", sa.String(64), nullable=False),
        sa.Column("onvio_folder_id", sa.String(64), nullable=False),
        sa.Column("nome_arquivo", sa.String(255), nullable=False),
        sa.Column("categoria", sa.String(50), nullable=False),
        sa.Column("mes_ref", sa.String(7), nullable=True),
        sa.Column("caminho_local", sa.String(512), nullable=True),
        sa.Column("tamanho_bytes", sa.Integer(), nullable=True),
        sa.Column("data_onvio", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "data_importado",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("processado", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.UniqueConstraint("onvio_id", name="uq_onvio_documents_onvio_id"),
    )
    op.create_index(
        "ix_onvio_documents_onvio_id",
        "onvio_documents",
        ["onvio_id"],
        unique=True,
    )

    # fgts_guias
    op.create_table(
        "fgts_guias",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("mes_ref", sa.String(7), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=True),
        sa.Column("valor", sa.Float(), nullable=True),
        sa.Column("vencimento", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=True, server_default="pendente"),
        sa.Column("arquivo_pdf", sa.String(512), nullable=True),
        sa.Column("onvio_doc_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )

    # inss_guias
    op.create_table(
        "inss_guias",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("mes_ref", sa.String(7), nullable=False),
        sa.Column("valor", sa.Float(), nullable=True),
        sa.Column("vencimento", sa.DateTime(timezone=True), nullable=True),
        sa.Column("competencia", sa.String(7), nullable=True),
        sa.Column("status", sa.String(20), nullable=True, server_default="pendente"),
        sa.Column("arquivo_pdf", sa.String(512), nullable=True),
        sa.Column("onvio_doc_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("inss_guias")
    op.drop_table("fgts_guias")
    op.drop_index("ix_onvio_documents_onvio_id", "onvio_documents")
    op.drop_table("onvio_documents")
    op.drop_table("onvio_sync_log")
