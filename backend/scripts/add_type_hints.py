#!/usr/bin/env python3
"""
Script para adicionar type hints automaticamente em controllers.

Uso:
    python scripts/add_type_hints.py <caminho_do_arquivo>

Exemplo:
    python scripts/add_type_hints.py modules/operacional/controllers/employee_controller.py
"""

import argparse
import re
import sys
from pathlib import Path


def get_return_type(func_name: str, args: list) -> str | None:
    """Infere o tipo de retorno baseado no nome da função e argumentos."""
    func_lower = func_name.lower()

    if any(x in func_lower for x in ["list", "get_all", "search", "filter"]):
        return "list[dict]"  # Simplificado - idealmente seria o schema específico
    elif any(x in func_lower for x in ["get", "find", "retrieve", "by_id"]):
        return "dict"  # Simplificado
    elif any(x in func_lower for x in ["create", "update", "upsert"]):
        return "dict"
    elif any(x in func_lower for x in ["delete", "remove"]):
        return "None"
    elif func_lower.startswith("health") or func_lower.startswith("check"):
        return "dict[str, Any]"
    return "dict"


def add_type_hints_to_file(filepath: str) -> bool:
    """Adiciona type hints em um arquivo Python."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Arquivo não encontrado: {filepath}")
        return False

    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False

    # Padrão para encontrar funções sem type hints
    pattern = r"^(async def|def)\s+(\w+)\s*\(([^)]*)\)\s*:(?![^\n]*->)"

    def replace_func(match):
        prefix = match.group(1)
        func_name = match.group(2)
        args = match.group(3)

        return_type = get_return_type(func_name, [])
        if return_type:
            return f"{prefix} {func_name}({args}) -> {return_type}:"
        return match.group(0)

    new_content = re.sub(pattern, replace_func, content, flags=re.MULTILINE)

    if new_content == content:
        print(f"ℹ️  Nenhuma alteração necessária em {filepath}")
        return True

    # Backup
    backup_path = path.with_suffix(".py.backup")
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Write new content
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Type hints adicionados em {filepath}")
    print(f"   Backup salvo em {backup_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Adiciona type hints em controllers")
    parser.add_argument("filepath", help="Caminho do arquivo para processar")
    args = parser.parse_args()

    success = add_type_hints_to_file(args.filepath)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
