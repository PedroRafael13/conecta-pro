#!/usr/bin/env python3
"""
validate-enums.py — Detecta enums usados incorretamente nos testes (EN vs PT)

Uso:
    ./scripts/validate-enums.py          # Lista erros
    ./scripts/validate-enums.py --fix    # Corrige automaticamente
    ./scripts/validate-enums.py --help   # Ajuda
"""

import ast
import os
import re
import sys
from pathlib import Path

BACKEND = Path("/opt/conecta-pro/backend")
MODULES_DIR = BACKEND / "modules"
TESTS_DIR = BACKEND / "tests"


def find_enum_definitions() -> dict[str, dict[str, list[str]]]:
    """Varre modules/ e core/ para encontrar todas as definições de Enum.

    Retorna: {arquivo: {NomeEnum: [VALOR1, VALOR2, ...]}}
    """
    enums: dict[str, dict[str, list[str]]] = {}

    search_dirs = [MODULES_DIR, BACKEND / "core"]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for py_file in search_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                source = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue

                # Verificar se herda de Enum, str+Enum, IntEnum, etc.
                is_enum = False
                for base in node.bases:
                    name = ""
                    if isinstance(base, ast.Name):
                        name = base.id
                    elif isinstance(base, ast.Attribute):
                        name = base.attr
                    if name in ("Enum", "IntEnum", "StrEnum"):
                        is_enum = True
                        break

                if not is_enum:
                    continue

                # Extrair valores do enum
                values = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                values.append(target.id)
                    elif isinstance(item, ast.AnnAssign):
                        if isinstance(item.target, ast.Name):
                            values.append(item.target.id)

                if values:
                    rel_path = str(py_file.relative_to(BACKEND))
                    if rel_path not in enums:
                        enums[rel_path] = {}
                    enums[rel_path][node.name] = values

    return enums


def find_enum_usage_in_tests() -> list[dict]:
    """Varre tests/ para encontrar uso de Enum.VALOR.

    Retorna: [{file, line, enum_name, value, full_match}]
    """
    usages = []
    pattern = re.compile(r'(\w+)\.([A-Z][A-Z0-9_]+)')

    if not TESTS_DIR.exists():
        return usages

    for py_file in TESTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            lines = py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except (UnicodeDecodeError, OSError):
            continue

        for line_num, line in enumerate(lines, 1):
            # Ignorar comentários e strings
            stripped = line.strip()
            if stripped.startswith("#"):
                continue

            for match in pattern.finditer(line):
                enum_name = match.group(1)
                value = match.group(2)

                # Filtrar falsos positivos comuns
                if enum_name in ("self", "cls", "os", "sys", "re", "pytest",
                                 "mock", "MagicMock", "patch", "status",
                                 "HTTP", "ASCII", "UUID", "Base", "Column",
                                 "Field", "Path", "datetime", "timedelta",
                                 "response", "result", "client", "app",
                                 "np", "pd", "db", "session"):
                    continue

                # Ignorar se é ALL_CAPS que parece constante de módulo
                if enum_name.isupper():
                    continue

                usages.append({
                    "file": str(py_file.relative_to(BACKEND)),
                    "line": line_num,
                    "enum_name": enum_name,
                    "value": value,
                    "full_match": f"{enum_name}.{value}",
                    "abs_path": str(py_file),
                    "line_content": line,
                })

    return usages


def validate(enums: dict, usages: list) -> list[dict]:
    """Compara uso nos testes com definições reais dos enums."""
    errors = []

    # Criar mapa: NomeEnum → [valores válidos]
    enum_map: dict[str, list[str]] = {}
    enum_locations: dict[str, str] = {}

    for file_path, file_enums in enums.items():
        for enum_name, values in file_enums.items():
            enum_map[enum_name] = values
            enum_locations[enum_name] = file_path

    for usage in usages:
        enum_name = usage["enum_name"]
        value = usage["value"]

        # Só validar enums que conhecemos
        if enum_name not in enum_map:
            continue

        valid_values = enum_map[enum_name]

        if value not in valid_values:
            # Tentar encontrar sugestão (fuzzy)
            suggestion = None
            value_lower = value.lower()
            for valid in valid_values:
                if valid.lower() == value_lower:
                    suggestion = valid
                    break

            # Traduções comuns EN→PT
            translations = {
                "ACTIVE": ["ATIVO", "ATIVA"],
                "INACTIVE": ["INATIVO", "INATIVA"],
                "PENDING": ["PENDENTE"],
                "COMPLETED": ["CONCLUIDO", "CONCLUIDA", "COMPLETO"],
                "CANCELLED": ["CANCELADO", "CANCELADA"],
                "PUBLISHED": ["PUBLICADO", "PUBLICADA"],
                "DRAFT": ["RASCUNHO"],
                "ARCHIVED": ["ARQUIVADO", "ARQUIVADA"],
                "SUSPENDED": ["SUSPENSO", "SUSPENSA"],
                "NOTIFICATIONS": ["NOTIFICACAO", "NOTIFICACOES"],
                "APPROVED": ["APROVADO", "APROVADA"],
                "REJECTED": ["REJEITADO", "REJEITADA"],
                "PROCESSING": ["PROCESSANDO"],
                "EXPIRED": ["EXPIRADO", "EXPIRADA"],
                "DELETED": ["EXCLUIDO", "EXCLUIDA", "DELETADO"],
            }

            if not suggestion and value in translations:
                for pt_val in translations[value]:
                    if pt_val in valid_values:
                        suggestion = pt_val
                        break

            if not suggestion:
                # Último recurso: mostrar valores válidos
                suggestion = valid_values[0] if valid_values else None

            errors.append({
                **usage,
                "valid_values": valid_values,
                "suggestion": suggestion,
                "definition_file": enum_locations.get(enum_name, "?"),
            })

    return errors


def fix_errors(errors: list) -> int:
    """Aplica correções automáticas nos arquivos de teste."""
    fixed = 0
    files_to_fix: dict[str, list] = {}

    for error in errors:
        if not error.get("suggestion"):
            continue
        abs_path = error["abs_path"]
        if abs_path not in files_to_fix:
            files_to_fix[abs_path] = []
        files_to_fix[abs_path].append(error)

    for file_path, file_errors in files_to_fix.items():
        try:
            content = Path(file_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        for error in file_errors:
            old = f"{error['enum_name']}.{error['value']}"
            new = f"{error['enum_name']}.{error['suggestion']}"
            content = content.replace(old, new)
            fixed += 1

        Path(file_path).write_text(content, encoding="utf-8")

    return fixed


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    fix_mode = "--fix" in sys.argv

    print("═══════════════════════════════════════════")
    print("VALIDAÇÃO DE ENUMS — Detectando EN vs PT")
    print("═══════════════════════════════════════════")
    print("")

    # 1. Encontrar definições
    print("Escaneando definições de enums em modules/...")
    enums = find_enum_definitions()
    total_enums = sum(len(v) for v in enums.values())
    print(f"  Encontrados: {total_enums} enums em {len(enums)} arquivos")
    print("")

    # 2. Encontrar uso nos testes
    print("Escaneando uso de enums em tests/...")
    usages = find_enum_usage_in_tests()
    print(f"  Encontrados: {len(usages)} referências a enums")
    print("")

    # 3. Validar
    errors = validate(enums, usages)

    if not errors:
        print("═══════════════════════════════════════════")
        print("✓ NENHUM erro de enum encontrado!")
        print("═══════════════════════════════════════════")
        sys.exit(0)

    print(f"═══════════════════════════════════════════")
    print(f"{'❌' if not fix_mode else '🔧'} {len(errors)} erro(s) encontrado(s)")
    print(f"═══════════════════════════════════════════")
    print("")

    for i, error in enumerate(errors, 1):
        print(f"{'❌' if not fix_mode else '🔧'} {error['file']}:{error['line']}")
        print(f"   Enum: {error['full_match']}")
        if error.get("suggestion"):
            print(f"   Erro: '{error['value']}' não existe. Use: '{error['suggestion']}'")
        else:
            print(f"   Erro: '{error['value']}' não existe.")
            print(f"   Valores válidos: {', '.join(error['valid_values'][:5])}")
        print(f"   Definido em: {error['definition_file']}")
        print("")

    if fix_mode:
        print("═══════════════════════════════════════════")
        print("Aplicando correções...")
        fixed = fix_errors(errors)
        print(f"✓ {fixed} correção(ões) aplicada(s)")
        print("")
        print("Rode 'verify-instant' para verificar.")
        print("═══════════════════════════════════════════")
    else:
        print("═══════════════════════════════════════════")
        print("CORREÇÃO AUTOMÁTICA disponível:")
        print("  ./scripts/validate-enums.py --fix")
        print("═══════════════════════════════════════════")

    sys.exit(1 if not fix_mode else 0)


if __name__ == "__main__":
    main()
