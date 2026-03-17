"""
Script para popular solides_entity_mapping com os 44 employees existentes.

Os 44 employees já existem em ambas tabelas (solides_employees e employees),
mas a tabela de mapeamento está vazia. Este script cria os mapeamentos
baseado no solides_id presente em ambas tabelas.
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

import psycopg2


def main():
    """Popula entity_mapping cruzando employees.solides_id com solides_employees.solides_id."""
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        dbname="conecta_pro",
        user="postgres",
        password=os.environ.get("DB_PASSWORD", "changeme"),  # pragma: allowlist secret
    )
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # Buscar employees que têm solides_id e sync_source='solides'
        cur.execute("""
            SELECT e.id, e.solides_id, e.cpf, e.nome
            FROM employees e
            WHERE e.solides_id IS NOT NULL
              AND e.sync_source = 'solides'
            ORDER BY e.nome
        """)
        employees = cur.fetchall()
        print(f"Encontrados {len(employees)} employees com solides_id")

        # Buscar condominio_id da config (ou do primeiro solides_employee)
        cur.execute("""
            SELECT DISTINCT condominio_id FROM solides_employees LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            print("ERRO: Nenhum registro em solides_employees")
            return 1
        condominio_id = row[0]
        print(f"Condominio ID: {condominio_id}")

        # Verificar mapeamentos existentes
        cur.execute("SELECT COUNT(*) FROM solides_entity_mapping")
        existing = cur.fetchone()[0]
        print(f"Mapeamentos existentes: {existing}")

        created = 0
        skipped = 0

        for emp_id, solides_id, _cpf, _nome in employees:
            # Verificar se já existe mapeamento
            cur.execute(
                """
                SELECT id FROM solides_entity_mapping
                WHERE entity_type = 'colaboradores'
                  AND solides_id = %s
                  AND condominio_id = %s
            """,
                (str(solides_id), condominio_id),
            )

            if cur.fetchone():
                skipped += 1
                continue

            # Criar mapeamento
            mapping_id = uuid4()
            now = datetime.utcnow()

            cur.execute(
                """
                INSERT INTO solides_entity_mapping
                (id, condominio_id, entity_type, solides_id, conecta_id,
                 last_sync_source, first_synced_at, last_synced_at,
                 is_active, sync_enabled, ativo, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s,
                        'solides', %s, %s,
                        true, true, true, %s, %s)
            """,
                (
                    str(mapping_id),
                    condominio_id,
                    "colaboradores",
                    str(solides_id),
                    emp_id,
                    now,
                    now,
                    now,
                    now,
                ),
            )
            created += 1

        conn.commit()
        print(f"\nResultado: {created} mapeamentos criados, {skipped} ignorados (já existiam)")
        print(f"Total entity_mapping agora: {created + existing}")

        # Verificação final
        cur.execute("SELECT COUNT(*) FROM solides_entity_mapping WHERE entity_type = 'colaboradores'")
        total = cur.fetchone()[0]
        print(f"Verificação: {total} mapeamentos de colaboradores na tabela")

        return 0

    except Exception as e:
        conn.rollback()
        print(f"ERRO: {e}")
        return 1
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
