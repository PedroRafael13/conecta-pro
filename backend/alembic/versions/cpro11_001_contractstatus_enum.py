"""cpro11_001: cria PG enum types para contratos CRM

Revision ID: cpro11_001_contractstatus_enum
Revises: sprint84_bloco1_condominios
Create Date: 2026-04-20

CPRO11-T4 P0.1 — Cria os tipos enum nativos do PostgreSQL para o módulo CRM:
  - contractstatus (draft, pending_signature, active, suspended, cancelled, terminated)
  - contracttype   (recurring, one_time)
  - adjustmentindex (igpm, ipca, inpc, fixed, custom)
  - addendumtype   (adjustment, scope_change, term_change, team_change, equipment_change, other)

Normaliza dados existentes de UPPERCASE para lowercase antes de alterar os tipos.
"""

import sqlalchemy as sa

from alembic import op

revision = "cpro11_001_contractstatus_enum"
down_revision = "sprint84_bloco1_condominios"
branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Valores dos enums (lowercase — idênticos aos valores da classe Python)
# ---------------------------------------------------------------------------
_CONTRACT_STATUS = ("draft", "pending_signature", "active", "suspended", "cancelled", "terminated")
_CONTRACT_TYPE = ("recurring", "one_time")
_ADJUSTMENT_INDEX = ("igpm", "ipca", "inpc", "fixed", "custom")
_ADDENDUM_TYPE = (
    "adjustment",
    "scope_change",
    "term_change",
    "team_change",
    "equipment_change",
    "other",
)


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Normalizar dados existentes para lowercase
    # ------------------------------------------------------------------
    conn.execute(sa.text("UPDATE contracts SET status = LOWER(status)"))
    conn.execute(sa.text("UPDATE contracts SET contract_type = LOWER(contract_type)"))

    # ------------------------------------------------------------------
    # 2. Criar tipos enum nativos (IF NOT EXISTS via DO block)
    # ------------------------------------------------------------------
    conn.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contractstatus') THEN
                    CREATE TYPE contractstatus AS ENUM
                        ('draft', 'pending_signature', 'active', 'suspended', 'cancelled', 'terminated');
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contracttype') THEN
                    CREATE TYPE contracttype AS ENUM ('recurring', 'one_time');
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'adjustmentindex') THEN
                    CREATE TYPE adjustmentindex AS ENUM ('igpm', 'ipca', 'inpc', 'fixed', 'custom');
                END IF;
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'addendumtype') THEN
                    CREATE TYPE addendumtype AS ENUM
                        ('adjustment', 'scope_change', 'term_change',
                         'team_change', 'equipment_change', 'other');
                END IF;
            END$$;
            """
        )
    )

    # ------------------------------------------------------------------
    # 3. Alterar colunas: varchar → enum nativo
    #    (drop default primeiro para evitar DatatypeMismatch no ALTER)
    # ------------------------------------------------------------------
    conn.execute(sa.text("ALTER TABLE contracts ALTER COLUMN status DROP DEFAULT"))
    conn.execute(sa.text("ALTER TABLE contracts ALTER COLUMN contract_type DROP DEFAULT"))

    conn.execute(
        sa.text(
            "ALTER TABLE contracts "
            "ALTER COLUMN status TYPE contractstatus USING status::contractstatus, "
            "ALTER COLUMN contract_type TYPE contracttype USING contract_type::contracttype"
        )
    )
    conn.execute(
        sa.text(
            "ALTER TABLE contracts "
            "ALTER COLUMN status SET DEFAULT 'draft'::contractstatus, "
            "ALTER COLUMN contract_type SET DEFAULT 'recurring'::contracttype"
        )
    )
    conn.execute(
        sa.text(
            "ALTER TABLE contracts "
            "ALTER COLUMN adjustment_index TYPE adjustmentindex "
            "USING adjustment_index::adjustmentindex"
        )
    )
    conn.execute(
        sa.text(
            "ALTER TABLE contract_addendums "
            "ALTER COLUMN addendum_type TYPE addendumtype "
            "USING addendum_type::addendumtype, "
            "ALTER COLUMN adjustment_index TYPE adjustmentindex "
            "USING adjustment_index::adjustmentindex"
        )
    )


def downgrade() -> None:
    conn = op.get_bind()

    # Reverter colunas para varchar
    conn.execute(
        sa.text(
            "ALTER TABLE contract_addendums "
            "ALTER COLUMN addendum_type TYPE varchar(30) USING addendum_type::text, "
            "ALTER COLUMN adjustment_index TYPE varchar(20) USING adjustment_index::text"
        )
    )
    conn.execute(
        sa.text("ALTER TABLE contracts ALTER COLUMN adjustment_index TYPE varchar(20) USING adjustment_index::text")
    )
    conn.execute(sa.text("ALTER TABLE contracts ALTER COLUMN status DROP DEFAULT"))
    conn.execute(sa.text("ALTER TABLE contracts ALTER COLUMN contract_type DROP DEFAULT"))
    conn.execute(
        sa.text(
            "ALTER TABLE contracts "
            "ALTER COLUMN status TYPE varchar(20) USING status::text, "
            "ALTER COLUMN contract_type TYPE varchar(20) USING contract_type::text"
        )
    )
    conn.execute(
        sa.text(
            "ALTER TABLE contracts "
            "ALTER COLUMN status SET DEFAULT 'draft', "
            "ALTER COLUMN contract_type SET DEFAULT 'recurring'"
        )
    )

    # Remover tipos enum
    conn.execute(
        sa.text(
            """
            DROP TYPE IF EXISTS contractstatus;
            DROP TYPE IF EXISTS contracttype;
            DROP TYPE IF EXISTS adjustmentindex;
            DROP TYPE IF EXISTS addendumtype;
            """
        )
    )
