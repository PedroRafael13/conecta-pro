#!/usr/bin/env python3
"""
diagnose-failures.py — Categoriza TODOS os failures/errors do pytest por tipo

Uso:
    cd /opt/conecta-pro/backend && source venv/bin/activate
    python -m pytest --tb=line -q 2>&1 | python /opt/conecta-pro/scripts/diagnose-failures.py

    # Ou com arquivo salvo:
    python -m pytest --tb=line -q > /tmp/pytest-output.txt 2>&1
    python /opt/conecta-pro/scripts/diagnose-failures.py /tmp/pytest-output.txt

Gera relatório categorizado + arquivo JSON com plano de correção.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPORT_PATH = Path("/tmp/failure-diagnosis.json")


def parse_pytest_output(lines: list[str]) -> tuple[list[dict], list[dict]]:
    """Parseia output do pytest --tb=line -q."""
    failures = []
    errors = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # FAILED test_file.py::test_name - error message
        if line.startswith("FAILED "):
            test_id = ""
            error_msg = ""
            match = re.match(r'FAILED (.+?) - (.+)', line)
            if match:
                test_id = match.group(1)
                error_msg = match.group(2)
            else:
                match = re.match(r'FAILED (.+)', line)
                if match:
                    test_id = match.group(1)

            # Olhar linha anterior para pegar a mensagem de erro real
            if i > 0:
                prev_line = lines[i - 1].strip()
                if prev_line and not prev_line.startswith("FAILED") and not prev_line.startswith("ERROR"):
                    error_msg = prev_line

            failures.append({
                "test": test_id,
                "error": error_msg,
                "type": "FAILED",
            })

        # ERROR test_file.py::test_name
        elif line.startswith("ERROR "):
            test_id = line.replace("ERROR ", "").strip()
            error_msg = ""
            if i > 0:
                prev_line = lines[i - 1].strip()
                if prev_line and not prev_line.startswith("FAILED") and not prev_line.startswith("ERROR"):
                    error_msg = prev_line

            errors.append({
                "test": test_id,
                "error": error_msg,
                "type": "ERROR",
            })

        i += 1

    return failures, errors


def categorize(item: dict) -> str:
    """Categoriza um failure/error por tipo."""
    error = item.get("error", "")
    test = item.get("test", "")

    # Fixture não encontrada
    if "fixture" in error.lower() and "not found" in error.lower():
        return "FIXTURE_MISSING"

    # TypeError: campo inválido
    if "TypeError" in error and ("invalid keyword argument" in error or "unexpected keyword argument" in error):
        return "SCHEMA_INVALID_FIELD"

    # TypeError: campo obrigatório faltando
    if "TypeError" in error and ("required" in error or "missing" in error):
        return "SCHEMA_MISSING_FIELD"

    # ValidationError Pydantic
    if "ValidationError" in error or "validation error" in error.lower():
        return "PYDANTIC_VALIDATION"

    # Enum/Attribute error
    if "AttributeError" in error and any(x in error for x in ["has no attribute", "has no member"]):
        return "ENUM_OR_ATTRIBUTE"

    # ImportError / ModuleNotFoundError
    if "ImportError" in error or "ModuleNotFoundError" in error:
        return "IMPORT_ERROR"

    # AsyncMock issues
    if "coroutine" in error.lower() or "await" in error.lower():
        return "ASYNC_MOCK"

    # KeyError
    if "KeyError" in error:
        return "KEY_ERROR"

    # AssertionError (test logic failure)
    if "AssertionError" in error or "assert " in error.lower():
        return "ASSERTION_FAILURE"

    # Database/SQLAlchemy
    if any(x in error for x in ["sqlalchemy", "IntegrityError", "OperationalError", "ProgrammingError", "MetaData"]):
        return "DATABASE_ERROR"

    # HTTP/API
    if any(x in error for x in ["status_code", "HTTPException", "422", "500", "404"]):
        return "HTTP_ERROR"

    # Collection error
    if "collection" in error.lower() or item["type"] == "ERROR":
        return "COLLECTION_ERROR"

    return "OTHER"


def extract_fixture_name(error: str) -> str | None:
    """Extrai nome da fixture faltante."""
    match = re.search(r"fixture '(\w+)' not found", error)
    return match.group(1) if match else None


def extract_field_info(error: str) -> dict:
    """Extrai info sobre campo inválido/faltante."""
    # TypeError: __init__() got an unexpected keyword argument 'X'
    match = re.search(r"unexpected keyword argument '(\w+)'", error)
    if match:
        return {"field": match.group(1), "issue": "unexpected"}

    # TypeError: X() missing required argument: 'Y'
    match = re.search(r"missing \d+ required .+ argument.* '(\w+)'", error)
    if match:
        return {"field": match.group(1), "issue": "missing"}

    return {}


def main():
    # Ler input
    if len(sys.argv) > 1 and sys.argv[1] != "--help":
        input_path = Path(sys.argv[1])
        if input_path.exists():
            lines = input_path.read_text().splitlines()
        else:
            print(f"❌ Arquivo não encontrado: {sys.argv[1]}")
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print(__doc__)
            sys.exit(0)
        lines = sys.stdin.read().splitlines()

    # Parsear
    failures, errors = parse_pytest_output(lines)
    total = len(failures) + len(errors)

    if total == 0:
        print("✓ Nenhum failure/error encontrado no output!")
        sys.exit(0)

    # Categorizar
    categories: dict[str, list[dict]] = defaultdict(list)
    for item in failures + errors:
        cat = categorize(item)
        item["category"] = cat
        categories[cat].append(item)

    # Extrair detalhes específicos
    missing_fixtures = Counter()
    invalid_fields = Counter()
    for item in categories.get("FIXTURE_MISSING", []):
        name = extract_fixture_name(item["error"])
        if name:
            missing_fixtures[name] += 1

    for item in categories.get("SCHEMA_INVALID_FIELD", []) + categories.get("SCHEMA_MISSING_FIELD", []):
        info = extract_field_info(item["error"])
        if info.get("field"):
            invalid_fields[f"{info['issue']}:{info['field']}"] += 1

    # Imprimir relatório
    print("═══════════════════════════════════════════════════════")
    print(f"DIAGNÓSTICO: {total} problemas ({len(failures)} failed, {len(errors)} errors)")
    print("═══════════════════════════════════════════════════════")
    print("")

    # Ordenar por quantidade
    sorted_cats = sorted(categories.items(), key=lambda x: -len(x[1]))

    for cat, items in sorted_cats:
        pct = len(items) * 100 // total
        automatable = cat in ("FIXTURE_MISSING", "ENUM_OR_ATTRIBUTE", "ASYNC_MOCK", "IMPORT_ERROR")
        auto_tag = " [AUTOMATIZÁVEL]" if automatable else ""
        print(f"  {cat:<25} {len(items):>4} ({pct:>2}%){auto_tag}")

    print("")
    print("═══════════════════════════════════════════════════════")

    # Fixtures faltantes
    if missing_fixtures:
        print("")
        print("FIXTURES FALTANTES (top 10):")
        for name, count in missing_fixtures.most_common(10):
            print(f"  {name:<30} {count} testes afetados")

    # Campos inválidos
    if invalid_fields:
        print("")
        print("CAMPOS PROBLEMÁTICOS (top 10):")
        for field_info, count in invalid_fields.most_common(10):
            issue, field = field_info.split(":", 1)
            label = "não existe" if issue == "unexpected" else "obrigatório faltando"
            print(f"  {field:<30} {label} ({count}x)")

    # Arquivos mais afetados
    file_counts = Counter()
    for item in failures + errors:
        test_file = item["test"].split("::")[0] if "::" in item["test"] else item["test"]
        file_counts[test_file] += 1

    print("")
    print("ARQUIVOS MAIS AFETADOS (top 15):")
    for file_path, count in file_counts.most_common(15):
        print(f"  {count:>4}  {file_path}")

    # Salvar relatório JSON
    report = {
        "summary": {
            "total": total,
            "failures": len(failures),
            "errors": len(errors),
        },
        "by_category": {cat: len(items) for cat, items in sorted_cats},
        "missing_fixtures": dict(missing_fixtures.most_common(20)),
        "problematic_fields": dict(invalid_fields.most_common(20)),
        "most_affected_files": dict(file_counts.most_common(30)),
        "details": failures + errors,
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print("")
    print(f"═══════════════════════════════════════════════════════")
    print(f"Relatório JSON salvo em: {REPORT_PATH}")
    print(f"═══════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
