#!/usr/bin/env python3
"""
schema-validator.py — Valida uso de Pydantic schemas nos testes

Uso:
    ./scripts/schema-validator.py --model TenantCreate    # Valida um model
    ./scripts/schema-validator.py --model Tenant --model Invoice  # Múltiplos
    ./scripts/schema-validator.py --scan                  # Escaneia erros nos testes
    ./scripts/schema-validator.py --help                  # Ajuda
"""

import ast
import re
import sys
from pathlib import Path

BACKEND = Path("/opt/conecta-pro/backend")
MODULES_DIR = BACKEND / "modules"
CORE_DIR = BACKEND / "core"
TESTS_DIR = BACKEND / "tests"


def find_model_definition(model_name: str) -> tuple[Path | None, list[dict]]:
    """Encontra onde um model Pydantic/SQLAlchemy é definido e seus campos."""
    search_dirs = [MODULES_DIR, CORE_DIR]

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
                if isinstance(node, ast.ClassDef) and node.name == model_name:
                    fields = extract_fields(node)
                    return py_file, fields

    return None, []


def extract_fields(class_node: ast.ClassDef) -> list[dict]:
    """Extrai campos de uma classe model."""
    fields = []

    for item in class_node.body:
        field = None

        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            name = item.target.id
            if name.startswith("_") or name == "model_config":
                continue

            required = True
            field_type = "?"
            default = None

            # Tipo da anotação
            if isinstance(item.annotation, ast.Name):
                field_type = item.annotation.id
            elif isinstance(item.annotation, ast.Subscript):
                if isinstance(item.annotation.value, ast.Name):
                    outer = item.annotation.value.id
                    if outer == "Optional":
                        required = False
                    field_type = ast.unparse(item.annotation)
            elif isinstance(item.annotation, ast.BinOp):
                field_type = ast.unparse(item.annotation)
                if isinstance(item.annotation.op, ast.BitOr):
                    if isinstance(item.annotation.right, ast.Constant) and item.annotation.right.value is None:
                        required = False

            # Valor default
            if item.value is not None:
                if isinstance(item.value, ast.Constant) and item.value.value is ...:
                    required = True  # Field(...)
                else:
                    required = False
                    try:
                        default = ast.unparse(item.value)
                    except Exception:
                        default = "..."

            field = {"name": name, "type": field_type, "required": required, "default": default}

        elif isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    name = target.id
                    if name in ("__tablename__", "__table_args__", "model_config"):
                        continue

                    required = True
                    field_type = "?"
                    default = None

                    if isinstance(item.value, ast.Call):
                        func_name = ""
                        if isinstance(item.value.func, ast.Name):
                            func_name = item.value.func.id
                        elif isinstance(item.value.func, ast.Attribute):
                            func_name = item.value.func.attr

                        if func_name in ("relationship", "declared_attr"):
                            continue

                        for kw in item.value.keywords:
                            if kw.arg == "nullable" and isinstance(kw.value, ast.Constant):
                                if kw.value.value:
                                    required = False
                            elif kw.arg == "default":
                                required = False
                            elif kw.arg == "primary_key" and isinstance(kw.value, ast.Constant):
                                if kw.value.value:
                                    required = False
                                    default = "auto"
                            elif kw.arg == "server_default":
                                required = False

                    field = {"name": name, "type": field_type, "required": required, "default": default}

        if field:
            fields.append(field)

    return fields


def find_model_usage_in_tests(model_name: str) -> list[dict]:
    """Encontra onde um model é instanciado nos testes."""
    usages = []

    # Pattern: ModelName( com args
    pattern = re.compile(rf'\b{re.escape(model_name)}\s*\(')

    if not TESTS_DIR.exists():
        return usages

    for py_file in TESTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            lines = source.splitlines()
        except (UnicodeDecodeError, OSError):
            continue

        for line_num, line in enumerate(lines, 1):
            if pattern.search(line):
                # Tentar parsear os kwargs passados
                passed_kwargs = set()
                # Simples: extrair nome=valor patterns da linha (e linhas seguintes para multiline)
                # Pegar bloco até fechar parênteses
                block = line
                paren_depth = 0
                for c in line:
                    if c == "(":
                        paren_depth += 1
                    elif c == ")":
                        paren_depth -= 1

                # Se não fechou, pegar linhas seguintes
                if paren_depth > 0:
                    for next_line in lines[line_num:min(line_num + 20, len(lines))]:
                        block += "\n" + next_line
                        for c in next_line:
                            if c == "(":
                                paren_depth += 1
                            elif c == ")":
                                paren_depth -= 1
                        if paren_depth <= 0:
                            break

                # Extrair kwargs
                kwarg_pattern = re.compile(r'(\w+)\s*=')
                for m in kwarg_pattern.finditer(block):
                    passed_kwargs.add(m.group(1))

                usages.append({
                    "file": str(py_file.relative_to(BACKEND)),
                    "line": line_num,
                    "abs_path": str(py_file),
                    "passed_kwargs": passed_kwargs,
                    "line_content": line.strip(),
                })

    return usages


def validate_model(model_name: str) -> list[dict]:
    """Valida uso de um model nos testes."""
    file_path, fields = find_model_definition(model_name)

    if not file_path:
        print(f"⚠️  Model '{model_name}' não encontrado em modules/ ou core/")
        return []

    required_fields = [f for f in fields if f["required"]]
    optional_fields = [f for f in fields if not f["required"]]

    rel_path = str(file_path.relative_to(BACKEND))

    print(f"═══════════════════════════════════════════")
    print(f"Schema Validator: {model_name}")
    print(f"Definido em: {rel_path}")
    print(f"═══════════════════════════════════════════")
    print("")

    if not required_fields:
        print("  Nenhum campo obrigatório detectado.")
        print("")
        return []

    usages = find_model_usage_in_tests(model_name)

    if not usages:
        print(f"  ⚠️  Nenhum uso encontrado em tests/")
        print("")
        print(f"  Campos obrigatórios ({len(required_fields)}):")
        for f in required_fields:
            print(f"    - {f['name']}: {f['type']}")
        print("")
        return []

    errors = []

    print(f"Campos obrigatórios ({len(required_fields)}):")

    for field in required_fields:
        missing_in = []
        present_in = 0

        for usage in usages:
            if field["name"] in usage["passed_kwargs"]:
                present_in += 1
            else:
                missing_in.append(usage)

        if not missing_in:
            print(f"  ✓ {field['name']:<20} presente em todos os {present_in} usos")
        else:
            print(f"  ⚠️  {field['name']:<20} FALTANDO em:")
            for m in missing_in[:5]:  # Limitar a 5
                print(f"      - {m['file']}:{m['line']}")
                errors.append({
                    "model": model_name,
                    "field": field["name"],
                    "file": m["file"],
                    "line": m["line"],
                })
            if len(missing_in) > 5:
                print(f"      ... e mais {len(missing_in) - 5} ocorrência(s)")

    print("")

    # Gerar exemplo de uso correto
    if required_fields:
        args = []
        for f in required_fields:
            t = f["type"]
            if "str" in t.lower() or t in ("String", "Text"):
                args.append(f'{f["name"]}="test"')
            elif "int" in t.lower() or t == "Integer":
                args.append(f'{f["name"]}=1')
            elif "float" in t.lower() or t in ("Float", "Numeric", "Decimal"):
                args.append(f'{f["name"]}=0.0')
            elif "bool" in t.lower() or t == "Boolean":
                args.append(f'{f["name"]}=True')
            elif "uuid" in t.lower() or t == "UUID":
                args.append(f'{f["name"]}=uuid4()')
            elif "date" in t.lower():
                args.append(f'{f["name"]}=datetime.now()')
            else:
                args.append(f'{f["name"]}=<{f["type"]}>')

        print(f"═══════════════════════════════════════════")
        print(f"CORREÇÃO SUGERIDA:")
        if len(args) <= 3:
            print(f"  {model_name}({', '.join(args)})")
        else:
            print(f"  {model_name}(")
            for arg in args:
                print(f"    {arg},")
            print(f"  )")
        print(f"═══════════════════════════════════════════")

    return errors


def scan_test_errors() -> list[dict]:
    """Escaneia todos os testes buscando instanciações que podem faltar campos."""
    print("═══════════════════════════════════════════")
    print("SCAN: Procurando schemas com campos faltando")
    print("═══════════════════════════════════════════")
    print("")

    # Encontrar todos os models usados nos testes
    models_in_tests = set()
    model_pattern = re.compile(r'\b([A-Z][a-zA-Z]+(?:Create|Update|Response|Schema|Model|Config|Settings))\s*\(')

    if not TESTS_DIR.exists():
        print("❌ Diretório tests/ não encontrado")
        return []

    for py_file in TESTS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except (UnicodeDecodeError, OSError):
            continue

        for match in model_pattern.finditer(content):
            models_in_tests.add(match.group(1))

    print(f"Models encontrados nos testes: {len(models_in_tests)}")
    print("")

    all_errors = []
    for model_name in sorted(models_in_tests):
        errors = validate_model(model_name)
        all_errors.extend(errors)
        if errors:
            print("")

    print("")
    print(f"═══════════════════════════════════════════")
    print(f"TOTAL: {len(all_errors)} campo(s) faltando em testes")
    print(f"═══════════════════════════════════════════")

    return all_errors


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    if "--scan" in sys.argv:
        errors = scan_test_errors()
        sys.exit(1 if errors else 0)

    models = []
    for i, arg in enumerate(sys.argv):
        if arg == "--model" and i + 1 < len(sys.argv):
            models.append(sys.argv[i + 1])

    if not models:
        print("Uso: ./scripts/schema-validator.py --model NomeModel")
        print("     ./scripts/schema-validator.py --scan")
        sys.exit(1)

    all_errors = []
    for model_name in models:
        errors = validate_model(model_name)
        all_errors.extend(errors)
        print("")

    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()
