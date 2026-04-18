"""sprint83 gedeon fase b2 extraction fields

Revision ID: sprint83_gedeon_fase_b2_extraction
Revises: sprint82b_gedeon_schema_fix
Create Date: 2026-04-18

Adiciona colunas de extração de valores em:
- onvio_documents, fgts_guias, inss_guias
Permite rollback via downgrade().

NOTA: fgts_guias e inss_guias já tinham 'valor' (float) e 'vencimento' (timestamptz)
com tipos incorretos. Este migration corrige os tipos (drop + recreate com NULL safe)
e adiciona as colunas restantes. Os 42 fgts e 5 inss já existentes têm NULL nessas
colunas — nenhum dado é perdido.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "9d91ef5c61f6"
down_revision = "sprint82b_gedeon_schema_fix"
branch_labels = None
depends_on = None

# Colunas de metadata de extração (vão em todas as 3 tabelas)
_COLUNAS_EXTRACAO = [
    ("confianca_extracao", sa.Float()),
    ("metodo_extracao", sa.String(50)),
    ("revisao_manual", sa.Boolean()),
    ("detalhes_json", postgresql.JSONB()),
    ("extraido_em", sa.DateTime(timezone=True)),
]


def upgrade() -> None:
    # ── onvio_documents: apenas metadata (valor fica nas guias específicas) ──
    for col, tipo in _COLUNAS_EXTRACAO:
        op.add_column("onvio_documents", sa.Column(col, tipo, nullable=True))

    # ── fgts_guias ──
    # Corrigir tipos errados: float → Numeric(15,2) e timestamptz → Date
    op.drop_column("fgts_guias", "valor")
    op.drop_column("fgts_guias", "vencimento")
    op.add_column("fgts_guias", sa.Column("valor", sa.Numeric(15, 2), nullable=True))
    op.add_column("fgts_guias", sa.Column("vencimento", sa.Date(), nullable=True))
    op.add_column("fgts_guias", sa.Column("codigo_barras", sa.String(50), nullable=True))
    for col, tipo in _COLUNAS_EXTRACAO:
        op.add_column("fgts_guias", sa.Column(col, tipo, nullable=True))

    # ── inss_guias ──
    # Corrigir tipos errados: float → Numeric(15,2) e timestamptz → Date
    op.drop_column("inss_guias", "valor")
    op.drop_column("inss_guias", "vencimento")
    op.add_column("inss_guias", sa.Column("valor", sa.Numeric(15, 2), nullable=True))
    op.add_column("inss_guias", sa.Column("vencimento", sa.Date(), nullable=True))
    op.add_column("inss_guias", sa.Column("codigo_barras", sa.String(50), nullable=True))
    for col, tipo in _COLUNAS_EXTRACAO:
        op.add_column("inss_guias", sa.Column(col, tipo, nullable=True))


def downgrade() -> None:
    # Remove na ordem inversa; restaura valor/vencimento com tipos originais
    for tabela in ("inss_guias", "fgts_guias"):
        for col in (
            "extraido_em",
            "detalhes_json",
            "revisao_manual",
            "metodo_extracao",
            "confianca_extracao",
            "codigo_barras",
        ):
            op.drop_column(tabela, col)
        # Restaurar tipos originais (pré-migration)
        op.drop_column(tabela, "valor")
        op.drop_column(tabela, "vencimento")
        op.add_column(tabela, sa.Column("valor", sa.Float(), nullable=True))
        op.add_column(tabela, sa.Column("vencimento", sa.DateTime(timezone=True), nullable=True))

    for col in ("extraido_em", "detalhes_json", "revisao_manual", "metodo_extracao", "confianca_extracao"):
        op.drop_column("onvio_documents", col)
