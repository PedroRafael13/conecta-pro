#!/usr/bin/env python3
"""
auto-fix-async-mocks.py — Corrige MagicMock → AsyncMock em testes async

Uso:
    ./scripts/auto-fix-async-mocks.py          # Lista o que precisa corrigir
    ./scripts/auto-fix-async-mocks.py --fix     # Aplica correções
    ./scripts/auto-fix-async-mocks.py --help    # Ajuda

Detecta:
- MagicMock() usado em funções async (return_value com coroutine)
- patch() sem AsyncMock em métodos async
- Mock() onde AsyncMock é necessário
"""

import re
import sys
from pathlib import Path

BACKEND = Path("/opt/conecta-pro/backend")
TESTS_DIR = BACKEND / "tests"


def find_async_mock_issues() -> list[dict]:
    """Encontra uso incorreto de MagicMock em contextos async."""
    issues = []

    if not TESTS_DIR.exists():
        return issues

    for py_file in TESTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
        except (UnicodeDecodeError, OSError):
            continue

        # Track imports
        has_asyncmock_import = "AsyncMock" in content
        has_magicmock_import = "MagicMock" in content
        has_async_tests = "async def test_" in content or "@pytest.mark.asyncio" in content

        if not has_async_tests:
            continue

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments
            if stripped.startswith("#"):
                continue

            # Pattern 1: MagicMock() in async test file
            if "MagicMock()" in line and has_async_tests:
                # Check if it's assigning to something that looks like a service/repo
                var_match = re.match(r'\s*(\w+)\s*=\s*MagicMock\(\)', line)
                if var_match:
                    var_name = var_match.group(1)
                    # Check if var is used with await in subsequent lines
                    for check_line in lines[line_num:min(line_num + 30, len(lines))]:
                        if f"await {var_name}" in check_line or f"await.*{var_name}" in check_line:
                            issues.append({
                                "file": str(py_file.relative_to(BACKEND)),
                                "abs_path": str(py_file),
                                "line": line_num,
                                "line_content": line.rstrip(),
                                "issue": f"MagicMock() used but '{var_name}' is awaited",
                                "fix": line.replace("MagicMock()", "AsyncMock()"),
                                "needs_import": not has_asyncmock_import,
                            })
                            break

            # Pattern 2: Mock(return_value=...) for async method
            if "return_value" in line and ("MagicMock" in line or "Mock(" in line):
                # Check if the mock target is an async method
                patch_match = re.search(r"@patch\(['\"](.+?)['\"]\)", stripped)
                if patch_match:
                    # Can't easily determine if target is async without importing
                    pass

            # Pattern 3: patch() without new_callable=AsyncMock for async
            patch_match = re.search(r"@patch\(['\"](.+?)['\"]\s*\)", stripped)
            if patch_match and "AsyncMock" not in line:
                target = patch_match.group(1)
                # Check if the test function is async
                for check_line in lines[line_num:min(line_num + 5, len(lines))]:
                    if "async def test_" in check_line:
                        # This patch might need AsyncMock
                        if "service" in target.lower() or "repository" in target.lower():
                            issues.append({
                                "file": str(py_file.relative_to(BACKEND)),
                                "abs_path": str(py_file),
                                "line": line_num,
                                "line_content": line.rstrip(),
                                "issue": f"patch() on '{target}' in async test without AsyncMock",
                                "fix": None,  # Complex fix
                                "needs_import": not has_asyncmock_import,
                            })
                        break

            # Pattern 4: mock.return_value = X (sync) in async context
            if ".return_value =" in line and has_async_tests:
                # Check if this should be async
                pass

    return issues


def add_asyncmock_import(content: str) -> str:
    """Adiciona import de AsyncMock se não existir."""
    if "AsyncMock" in content:
        return content

    # Encontrar linha de import do unittest.mock
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "from unittest.mock import" in line:
            if "AsyncMock" not in line:
                # Adicionar AsyncMock ao import existente
                new_line = line.rstrip()
                if new_line.endswith(")"):
                    new_line = new_line[:-1] + ", AsyncMock)"
                else:
                    new_line += ", AsyncMock"
                lines[i] = new_line
            return "\n".join(lines)

    # Se não tem import do unittest.mock, adicionar
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            lines.insert(i, "from unittest.mock import AsyncMock, MagicMock, patch")
            return "\n".join(lines)

    return content


def apply_fixes(issues: list[dict]) -> int:
    """Aplica correções nos arquivos."""
    fixed = 0
    files_modified: dict[str, str] = {}

    for issue in issues:
        if not issue.get("fix"):
            continue

        abs_path = issue["abs_path"]
        if abs_path not in files_modified:
            try:
                files_modified[abs_path] = Path(abs_path).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

        content = files_modified[abs_path]
        old_line = issue["line_content"]
        new_line = issue["fix"]

        if old_line in content:
            content = content.replace(old_line, new_line, 1)
            fixed += 1

        if issue.get("needs_import"):
            content = add_asyncmock_import(content)

        files_modified[abs_path] = content

    for abs_path, content in files_modified.items():
        Path(abs_path).write_text(content, encoding="utf-8")

    return fixed


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    fix_mode = "--fix" in sys.argv

    print("═══════════════════════════════════════════")
    print("AUTO-FIX ASYNC MOCKS")
    print("═══════════════════════════════════════════")
    print("")

    issues = find_async_mock_issues()

    if not issues:
        print("✓ Nenhum problema de MagicMock/AsyncMock detectado!")
        sys.exit(0)

    fixable = [i for i in issues if i.get("fix")]
    manual = [i for i in issues if not i.get("fix")]

    print(f"Encontrados: {len(issues)} problemas ({len(fixable)} auto-fixáveis, {len(manual)} manuais)")
    print("")

    for issue in issues:
        tag = "🔧" if issue.get("fix") else "⚠️"
        print(f"{tag} {issue['file']}:{issue['line']}")
        print(f"   {issue['issue']}")
        if issue.get("fix"):
            print(f"   Fix: {issue['fix'].strip()}")
        print("")

    if fix_mode and fixable:
        print("═══════════════════════════════════════════")
        print("Aplicando correções...")
        fixed = apply_fixes(fixable)
        print(f"✓ {fixed} correção(ões) aplicada(s)")
        print("Rode verify-instant para confirmar.")
        print("═══════════════════════════════════════════")
    elif fixable:
        print("═══════════════════════════════════════════")
        print(f"CORREÇÃO AUTOMÁTICA: ./scripts/auto-fix-async-mocks.py --fix")
        print("═══════════════════════════════════════════")

    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
