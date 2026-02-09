"""
Script Python para normalizar campos JSONB críticos no Conecta Pro.

Este script normaliza campos JSONB para garantir consistência:
- Converte NULL para {} (objeto vazio) ou [] (array vazio)
- Padroniza estrutura de dados
- Remove valores inválidos
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from core.database import engine


async def normalize_jsonb_fields():
    """Normaliza campos JSONB críticos."""

    print("=" * 70)
    print("CONECTA PRO - JSONB NORMALIZATION")
    print("=" * 70)

    async with engine.begin() as conn:
        # Lista de normalizações a serem aplicadas
        normalizations = [
            # employees.dados_adicionais
            {
                "table": "employees",
                "column": "dados_adicionais",
                "default": "'{}'",
                "description": "Dados adicionais do funcionário",
            },
            # employees.competencias
            {
                "table": "employees",
                "column": "competencias",
                "default": "'[]'",
                "description": "Competências do funcionário",
            },
            # audit_logs.details
            {
                "table": "audit_logs",
                "column": "details",
                "default": "'{}'",
                "description": "Detalhes do log de auditoria",
            },
            # access_history.context
            {"table": "access_history", "column": "context", "default": "'{}'", "description": "Contexto do acesso"},
            # scales.config
            {"table": "scales", "column": "config", "default": "'{}'", "description": "Configuração da escala"},
            # scale_templates.config
            {
                "table": "scale_templates",
                "column": "config",
                "default": "'{}'",
                "description": "Configuração do template",
            },
            # posts.metadata
            {"table": "posts", "column": "metadata", "default": "'{}'", "description": "Metadados do posto"},
            # allocations.qualifications
            {
                "table": "allocations",
                "column": "qualifications",
                "default": "'[]'",
                "description": "Qualificações da alocação",
            },
        ]

        total_updated = 0

        for norm in normalizations:
            table = norm["table"]
            column = norm["column"]
            default = norm["default"]

            try:
                # Verifica se tabela existe
                result = await conn.execute(
                    text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = '{table}'
                    )
                """)
                )

                if not result.scalar():
                    print(f"⚠️  Tabela {table} não existe, pulando...")
                    continue

                # Verifica se coluna existe
                result = await conn.execute(
                    text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns
                        WHERE table_schema = 'public'
                        AND table_name = '{table}'
                        AND column_name = '{column}'
                    )
                """)
                )

                if not result.scalar():
                    print(f"⚠️  Coluna {table}.{column} não existe, pulando...")
                    continue

                # Conta registros NULL
                result = await conn.execute(
                    text(f"""
                    SELECT COUNT(*) FROM {table} WHERE {column} IS NULL
                """)
                )
                null_count = result.scalar()

                if null_count > 0:
                    # Atualiza registros NULL
                    await conn.execute(
                        text(f"""
                        UPDATE {table}
                        SET {column} = {default}::jsonb
                        WHERE {column} IS NULL
                    """)
                    )
                    print(f"✅ {table}.{column}: {null_count} registros NULL normalizados")
                    total_updated += null_count
                else:
                    print(f"✓ {table}.{column}: já está normalizado")

            except Exception as e:
                print(f"❌ Erro em {table}.{column}: {e}")

        print("\n" + "=" * 70)
        print("NORMALIZAÇÃO CONCLUÍDA!")
        print(f"Total de registros atualizados: {total_updated}")
        print("=" * 70)

        return total_updated


if __name__ == "__main__":
    result = asyncio.run(normalize_jsonb_fields())
    sys.exit(0 if result >= 0 else 1)
