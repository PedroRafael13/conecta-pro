#!/usr/bin/env python3
"""
Script de correção em massa de datetime.utcnow() deprecado.
Parte do plano de melhoria de qualidade: Score 90 → 94

Substituições:
- datetime.utcnow() → datetime.now(UTC)
- Adiciona import UTC se necessário
"""

import re
from pathlib import Path


def fix_file(filepath: Path) -> tuple[int, list[str]]:
    """Corrige um arquivo e retorna o número de substituições feitas."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return 0, [f"Erro ao ler {filepath}: {e}"]

    original = content
    changes = []

    # Contar ocorrências antes
    count_utcnow = len(re.findall(r"datetime\.utcnow\(\)", content))

    if count_utcnow == 0:
        return 0, []

    # Substituir datetime.utcnow() por datetime.now(UTC)
    content = re.sub(r"datetime\.utcnow\(\)", "datetime.now(UTC)", content)

    # Verificar se precisa adicionar import de UTC
    has_utc_import = bool(re.search(r"from datetime import.*UTC", content))
    has_datetime_utc = bool(re.search(r"datetime\.UTC", content))

    if not has_utc_import and not has_datetime_utc:
        # Tentar adicionar UTC ao import existente de datetime
        # Padrão: from datetime import datetime, ...
        datetime_import_pattern = r"(from datetime import\s+)([^(\n]+)"
        match = re.search(datetime_import_pattern, content)

        if match:
            imports = match.group(2).strip()
            if "UTC" not in imports:
                # Adicionar UTC ao import existente
                new_imports = imports.rstrip(",") + ", UTC"
                content = re.sub(datetime_import_pattern, rf"\g<1>{new_imports}", content, count=1)
                changes.append("  + Adicionado UTC ao import de datetime")
        else:
            # Verificar import simples: import datetime
            if re.search(r"^import datetime\s*$", content, re.MULTILINE):
                # Substituir datetime.now(UTC) por datetime.datetime.now(datetime.UTC)
                content = re.sub(r"datetime\.now\(UTC\)", "datetime.datetime.now(datetime.UTC)", content)
                changes.append("  ! Usando datetime.datetime.now(datetime.UTC)")

    changes.append(f"  datetime.utcnow() → datetime.now(UTC) ({count_utcnow}x)")

    if content != original:
        try:
            filepath.write_text(content, encoding="utf-8")
            return count_utcnow, changes
        except Exception as e:
            return 0, [f"Erro ao escrever {filepath}: {e}"]

    return 0, []


def main():
    """Executa a correção em todos os arquivos Python."""
    base_dir = Path(".")

    # Diretórios a processar
    dirs_to_process = ["modules", "core", "tests", "api"]

    total_fixes = 0
    files_fixed = 0
    all_changes = []

    for dir_name in dirs_to_process:
        dir_path = base_dir / dir_name
        if not dir_path.exists():
            continue

        py_files = list(dir_path.rglob("*.py"))

        for filepath in sorted(py_files):
            # Ignorar diretórios obsoletos
            if "_obsolete" in str(filepath):
                continue

            fixes, changes = fix_file(filepath)
            if fixes > 0:
                files_fixed += 1
                total_fixes += fixes
                print(f"✅ {filepath}: {fixes} correções")
                all_changes.extend(changes)

    print()
    print("=" * 60)
    print("RESUMO:")
    print(f"  Arquivos corrigidos: {files_fixed}")
    print(f"  Total de correções: {total_fixes}")
    print("=" * 60)


if __name__ == "__main__":
    main()
