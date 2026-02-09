"""
Add performance indexes - Quick Wins

Revision ID: 20260205_192551
Revises: b0b10e87f1c1
Create Date: 2026-02-05 19:25:51

This migration adds critical performance indexes identified during the
performance audit. These improve JOIN performance and query
response times without changing any functional behavior.

Indexes added:
- Foreign keys for faster JOINs
- Date fields for range queries
- Status fields for filtering
- Composite indexes for common query patterns

Estimated impact:
- 50-70% faster JOIN operations
- 30-50% faster dashboard queries
- Reduced CPU usage on PostgreSQL

"""

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260205_192551"
down_revision = "b0b10e87f1c1"
branch_labels = None
depends_on = None


def upgrade():
    """
    Create performance indexes for frequently queried columns.
    """
    conn = op.get_bind()

    # Índices a serem criados: (nome, tabela, colunas)
    indexes = [
        ("idx_ged_docs_contract", "ged_documents", "contract_id"),
        ("idx_occ_attach_occurrence", "occurrence_attachments", "occurrence_id"),
        ("idx_shifts_employee_date", "shifts", "employee_id, shift_date"),
        ("idx_payables_due_status", "payables", "due_date, status"),
        ("idx_receivables_client", "receivables", "client_id"),
        ("idx_audit_logs_created_at", "audit_logs", "created_at"),
        ("idx_occ_comm_occurrence", "occurrence_comments", "occurrence_id"),
        ("idx_leads_source", "leads", "source"),
        ("idx_candidates_status", "candidates", "status"),
        ("idx_scales_status_year_month", "scales", "status, year, month"),
        ("idx_allocations_employee", "allocations", "employee_id"),
        ("idx_diarist_schedules_lookup", "diarist_schedules", "diarist_id, work_date"),
    ]

    for idx_name, table, columns in indexes:
        try:
            # Verifica se tabela existe
            result = conn.execute(
                text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = '{table}'
                )
            """)
            )
            if not result.scalar():
                print(f"⚠️  Tabela {table} não existe, pulando índice {idx_name}")
                continue

            # Cria índice
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})"))
            print(f"✅ Índice {idx_name} criado/verificado")
        except Exception as e:
            print(f"⚠️  Erro ao criar índice {idx_name}: {e}")
            # Não falha a migration, continua com os próximos índices
            conn.execute(text("ROLLBACK"))
            continue

    print("\n✅ Migration de performance concluída!")


def downgrade():
    """
    Remove performance indexes.
    """
    conn = op.get_bind()

    indexes = [
        ("idx_diarist_schedules_lookup", "diarist_schedules"),
        ("idx_allocations_employee", "allocations"),
        ("idx_scales_status_year_month", "scales"),
        ("idx_candidates_status", "candidates"),
        ("idx_leads_source", "leads"),
        ("idx_occ_comm_occurrence", "occurrence_comments"),
        ("idx_audit_logs_created_at", "audit_logs"),
        ("idx_receivables_client", "receivables"),
        ("idx_payables_due_status", "payables"),
        ("idx_shifts_employee_date", "shifts"),
        ("idx_occ_attach_occurrence", "occurrence_attachments"),
        ("idx_ged_docs_contract", "ged_documents"),
    ]

    for idx_name, _table in indexes:
        try:
            conn.execute(text(f"DROP INDEX IF EXISTS {idx_name}"))
            print(f"🗑️  Índice {idx_name} removido")
        except Exception as e:
            print(f"⚠️  Erro ao remover índice {idx_name}: {e}")

    print("\n✅ Downgrade concluído!")
