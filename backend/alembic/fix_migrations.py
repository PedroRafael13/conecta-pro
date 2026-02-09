#!/usr/bin/env python3
"""Script para corrigir migrations com CREATE TYPE sem verificação."""

import glob
import os
import re

MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__)) + "/versions"

# Função helper que será adicionada
HELPER_FUNCTION = '''
def create_enum_safe(name: str, values: list):
    """Cria enum de forma segura (ignora se já existir)."""
    values_str = ", ".join([f"'{v}'" for v in values])
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({values_str});
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

'''


def fix_migration(filepath):
    """Corrige uma migration individual."""
    with open(filepath) as f:
        content = f.read()

    # Verifica se tem CREATE TYPE sem DO $$ BEGIN
    if "CREATE TYPE" not in content:
        return False

    if "DO $$ BEGIN" in content and "create_enum_safe" in content:
        print(f"  Já corrigido: {os.path.basename(filepath)}")
        return False

    # Padrão para encontrar CREATE TYPE inline
    pattern = r'op\.execute\s*\(\s*["\'][\s\S]*?CREATE\s+TYPE\s+(\w+)\s+AS\s+ENUM\s*\(([\s\S]*?)\)[\s\S]*?["\']\s*\)'

    matches = re.findall(pattern, content)
    if not matches:
        print(f"  Sem padrão encontrado: {os.path.basename(filepath)}")
        return False

    print(f"  Corrigindo: {os.path.basename(filepath)} ({len(matches)} ENUMs)")

    # Adiciona a função helper se não existir
    if "def create_enum_safe" not in content:
        # Encontra onde adicionar (após os imports, antes de upgrade())
        upgrade_match = re.search(r"\ndef upgrade\(\)", content)
        if upgrade_match:
            insert_pos = upgrade_match.start()
            content = content[:insert_pos] + HELPER_FUNCTION + content[insert_pos:]

    # Substitui cada CREATE TYPE
    for enum_name, enum_values in matches:
        # Limpa os valores
        values_clean = [v.strip().strip("'\"") for v in enum_values.replace("\n", " ").split(",")]
        values_list = str(values_clean)

        # Padrão específico para este enum
        specific_pattern = (
            rf'op\.execute\s*\(\s*["\'][\s\S]*?CREATE\s+TYPE\s+{enum_name}\s+AS\s+ENUM\s*\([^)]+\)[\s\S]*?["\']\s*\)'
        )

        replacement = f'create_enum_safe("{enum_name}", {values_list})'
        content = re.sub(specific_pattern, replacement, content)

    with open(filepath, "w") as f:
        f.write(content)

    return True


def main():
    """Corrige todas as migrations."""
    print("Corrigindo migrations com CREATE TYPE...\n")

    fixed = 0
    for filepath in glob.glob(f"{MIGRATIONS_DIR}/*.py"):
        if fix_migration(filepath):
            fixed += 1

    print(f"\n{fixed} migrations corrigidas.")


if __name__ == "__main__":
    main()
