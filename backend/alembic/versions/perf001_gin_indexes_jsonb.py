"""
Migration: Adicionar índices GIN para colunas JSONB

Performance optimization - Fase 3
Cria índices GIN nas colunas JSONB mais consultadas.

Índices GIN (Generalized Inverted Index) são otimizados para:
- Operações de contenção (@>, <@)
- Operações de existência de chave (?)
- Queries em documentos JSON

Recomendação: Executar em horário de baixo tráfego.
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers
revision = "perf001_gin_indexes_jsonb"
down_revision = "20260205_192551"  # Performance indexes quick wins
branch_labels = None
depends_on = None

# Colunas JSONB prioritárias para indexação
# Format: (table_name, column_name, schema)
JSONB_COLUMNS_PRIORITY = [
    # Audit e Logs (alta cardinalidade, frequentemente consultados)
    ("audit_logs", "details", "public"),
    ("audit_logs", "changes", "public"),
    ("access_history", "context", "public"),
    ("integration_logs", "request_data", "public"),
    ("integration_logs", "response_data", "public"),
    # Configurações e Metadados
    ("report_templates", "config", "public"),
    ("report_sections", "config", "public"),
    ("workflows", "config", "public"),
    ("workflow_definitions", "steps_config", "public"),
    # Dados de Integração
    ("integration_sync_queue", "payload", "public"),
    ("integration_id_map", "metadata", "public"),
    # Dados de IA
    ("ai_predictions", "input_data", "public"),
    ("ai_predictions", "output_data", "public"),
    ("ai_conversations", "context", "public"),
    # Dados Operacionais
    ("employees", "dados_adicionais", "public"),
    ("employees", "competencias", "public"),
    ("diaristas", "referencias", "public"),
    # Fiscal e Documentos
    ("documentos_fiscais", "dados_evento", "public"),
    ("documentos_fiscais", "historico_alteracoes", "public"),
]


def upgrade() -> None:
    """Adiciona índices GIN nas colunas JSONB prioritárias."""
    conn = op.get_bind()

    for table, column, schema in JSONB_COLUMNS_PRIORITY:
        index_name = f"idx_{table}_{column}_gin"

        # Verificar se tabela existe
        result = conn.execute(
            sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = '{schema}'
                AND table_name = '{table}'
            )
        """)
        )
        table_exists = result.scalar()

        if not table_exists:
            print(f"⚠️  Tabela {schema}.{table} não existe, pulando...")
            continue

        # Verificar se coluna existe
        result = conn.execute(
            sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = '{schema}'
                AND table_name = '{table}'
                AND column_name = '{column}'
            )
        """)
        )
        column_exists = result.scalar()

        if not column_exists:
            print(f"⚠️  Coluna {schema}.{table}.{column} não existe, pulando...")
            continue

        # Verificar se índice já existe
        result = conn.execute(
            sa.text(f"""
            SELECT EXISTS (
                SELECT FROM pg_indexes
                WHERE schemaname = '{schema}'
                AND tablename = '{table}'
                AND indexname = '{index_name}'
            )
        """)
        )
        index_exists = result.scalar()

        if index_exists:
            print(f"✓ Índice {index_name} já existe")
            continue

        # Criar índice GIN
        print(f"📝 Criando índice {index_name}...")
        conn.execute(
            sa.text(f"""
            CREATE INDEX IF NOT EXISTS {index_name}
            ON {schema}.{table} USING GIN ({column})
        """)
        )
        print(f"✅ Índice {index_name} criado com sucesso")

    print("\n✅ Migration concluída!")


def downgrade() -> None:
    """Remove índices GIN criados."""
    conn = op.get_bind()

    for table, column, schema in JSONB_COLUMNS_PRIORITY:
        index_name = f"idx_{table}_{column}_gin"

        print(f"🗑️  Removendo índice {index_name}...")
        conn.execute(
            sa.text(f"""
            DROP INDEX IF EXISTS {schema}.{index_name}
        """)
        )

    print("\n✅ Downgrade concluído!")


if __name__ == "__main__":
    # Para teste manual
    print("JSONB GIN Index Migration")
    print(f"Colunas prioritárias: {len(JSONB_COLUMNS_PRIORITY)}")
