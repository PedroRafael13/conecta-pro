#!/usr/bin/env python3
"""
Script de migração Pydantic v1 → v2: class Config → model_config
Parte do plano de melhoria de qualidade: Score 90 → 94

Substituições:
- class Config: from_attributes = True → model_config = ConfigDict(from_attributes=True)
- Adiciona import ConfigDict se necessário
"""

import re
from pathlib import Path

# Padrões de Config para substituição
CONFIG_PATTERNS = [
    # from_attributes = True (mais comum)
    (
        r"    class Config:\s*\n        from_attributes\s*=\s*True\s*\n",
        "    model_config = ConfigDict(from_attributes=True)\n",
    ),
    # orm_mode = True (legado)
    (
        r"    class Config:\s*\n        orm_mode\s*=\s*True\s*\n",
        "    model_config = ConfigDict(from_attributes=True)\n",
    ),
    # Variação com espaçamento diferente
    (
        r"    class Config:\n        from_attributes = True\n\n",
        "    model_config = ConfigDict(from_attributes=True)\n\n",
    ),
    # Com comentário pylint e docstring
    (
        r'    class Config:  # pylint: disable=too-few-public-methods\s*\n        """[^"]*"""\s*\n\s*\n        from_attributes = True\s*\n',
        "    model_config = ConfigDict(from_attributes=True)\n",
    ),
    # Com comentário pylint sem docstring
    (
        r"    class Config:  # pylint: disable=too-few-public-methods\s*\n        from_attributes = True\s*\n",
        "    model_config = ConfigDict(from_attributes=True)\n",
    ),
    # Com docstring simples (sem pylint)
    (
        r'    class Config:\s*\n        """[^"]*"""\s*\n        from_attributes = True\s*\n',
        "    model_config = ConfigDict(from_attributes=True)\n",
    ),
]


def fix_file(filepath: Path) -> tuple[int, list[str]]:
    """Corrige um arquivo e retorna o número de substituições feitas."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return 0, [f"Erro ao ler {filepath}: {e}"]

    original = content
    changes = []
    total_fixes = 0

    # Contar class Config antes
    count_before = len(re.findall(r"class Config:", content))

    if count_before == 0:
        return 0, []

    # Aplicar substituições
    for pattern, replacement in CONFIG_PATTERNS:
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, replacement, content)
            total_fixes += matches

    # Verificar se precisa adicionar import ConfigDict
    if total_fixes > 0:
        has_configdict_import = bool(re.search(r"from pydantic import.*ConfigDict", content))

        if not has_configdict_import:
            # Tentar adicionar ConfigDict ao import existente de pydantic
            pydantic_import_pattern = r"(from pydantic import\s+)([^\n]+)"
            match = re.search(pydantic_import_pattern, content)

            if match:
                imports = match.group(2).strip()
                if "ConfigDict" not in imports:
                    # Adicionar ConfigDict ao import existente
                    new_imports = imports.rstrip(",") + ", ConfigDict"
                    content = re.sub(pydantic_import_pattern, rf"\g<1>{new_imports}", content, count=1)
                    changes.append("  + Adicionado ConfigDict ao import")

        changes.append(f"  class Config → model_config ({total_fixes}x)")

    if content != original:
        try:
            filepath.write_text(content, encoding="utf-8")
            return total_fixes, changes
        except Exception as e:
            return 0, [f"Erro ao escrever {filepath}: {e}"]

    return 0, []


def main():
    """Executa a correção em todos os arquivos Python."""
    base_dir = Path(".")

    # Diretórios a processar
    dirs_to_process = ["modules", "core", "api"]

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
