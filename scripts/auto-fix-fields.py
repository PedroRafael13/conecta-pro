#!/usr/bin/env python3
"""
auto-fix-fields.py — Corrige campos inválidos nos testes automaticamente

Uso:
    # Primeiro, gerar o mapa de correções:
    ./scripts/auto-fix-fields.py --scan           # Analisa e mostra o que precisa corrigir
    ./scripts/auto-fix-fields.py --fix             # Aplica correções
    ./scripts/auto-fix-fields.py --model Client    # Analisa só um model

Corrige:
- TypeError: 'name' is an invalid keyword argument for Client
  → Detecta que Client tem 'legal_name' e substitui nos testes
"""

import ast
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

BACKEND = Path("/opt/conecta-pro/backend")
MODULES_DIR = BACKEND / "modules"
CORE_DIR = BACKEND / "core"
TESTS_DIR = BACKEND / "tests"


def get_model_fields(model_name: str) -> dict[str, list[str]] | None:
    """Encontra um model e retorna seus campos."""
    search_dirs = [MODULES_DIR, CORE_DIR]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for py_file in search_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                source = py_file.read_text(encoding="utf-8", errors="ignore")
                if f"class {model_name}" not in source:
                    continue
                tree = ast.parse(source, filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef) or node.name != model_name:
                    continue

                fields = []
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                                if target.id not in ("__tablename__", "__table_args__", "model_config"):
                                    fields.append(target.id)
                    elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        name = item.target.id
                        if not name.startswith("_") and name not in ("__tablename__", "__table_args__", "model_config"):
                            fields.append(name)

                if fields:
                    return {"fields": fields, "file": str(py_file)}

    return None


def find_invalid_field_errors() -> list[dict]:
    """Roda pytest para capturar TypeError de campos inválidos."""
    errors = []

    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--tb=line", "-q", "--no-header"],
            capture_output=True, text=True, timeout=300,
            cwd=str(BACKEND)
        )
        output = result.stdout + result.stderr
    except (subprocess.TimeoutExpired, OSError):
        # Tentar ler de arquivo salvo
        saved = Path("/tmp/pytest-full-output.txt")
        if saved.exists():
            output = saved.read_text(errors="ignore")
        else:
            print("❌ Não conseguiu rodar pytest. Salve output em /tmp/pytest-full-output.txt")
            return errors

    # Parsear: TypeError: 'X' is an invalid keyword argument for Model
    pattern = re.compile(r"TypeError: '(\w+)' is an invalid keyword argument for (\w+)")

    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            field = match.group(1)
            model = match.group(2)
            errors.append({"field": field, "model": model, "line": line.strip()})

    return errors


def find_field_mapping(invalid_field: str, valid_fields: list[str]) -> str | None:
    """Tenta mapear um campo inválido para o campo correto."""
    # Mapeamentos conhecidos EN→PT e vice-versa
    known_mappings = {
        # EN → campo real (pode ser PT ou EN diferente)
        "name": ["nome", "legal_name", "trade_name"],
        "title": ["titulo", "nome"],
        "description": ["descricao", "description"],
        "status": ["status"],
        "type": ["type", "tipo"],
        "email": ["email"],
        "phone": ["phone", "telefone"],
        "address": ["endereco", "address_street"],
        "city": ["cidade", "address_city"],
        "state": ["estado", "address_state"],
        "country": ["pais", "address_country"],
        "zipcode": ["cep", "address_zipcode"],
        "created_at": ["created_at"],
        "updated_at": ["updated_at"],
        "active": ["ativo", "is_active"],
        "is_active": ["is_active", "ativo"],
        "value": ["valor", "value"],
        "amount": ["valor", "amount"],
        "price": ["preco", "price"],
        "quantity": ["quantidade", "quantity"],
        "date": ["data", "date"],
        "start_date": ["data_inicio", "start_date"],
        "end_date": ["data_fim", "end_date"],
        "code": ["codigo", "code"],
        "codigo": ["codigo", "code"],
        "category": ["categoria", "category"],
        "priority": ["prioridade", "priority"],
        "user_id": ["user_id", "usuario_id"],
        "tenant_id": ["tenant_id"],
        "notes": ["observacoes", "notes"],
        "balance": ["saldo", "balance", "current_balance"],
        "account_type": ["tipo", "type", "account_type"],
        "document": ["documento", "document_number"],
        "number": ["numero", "number"],
        "account_number": ["numero_conta", "account_number"],
        "bank_code": ["codigo_banco", "bank_code"],
        "agency": ["agencia", "agency"],
        "owner_name": ["titular", "owner_name"],
        "owner_document": ["documento_titular", "owner_document"],
        "is_default": ["is_default", "padrao"],
        "month": ["mes", "month"],
        "year": ["ano", "year"],
        "period": ["periodo", "period"],
        "label": ["rotulo", "label"],
        "dashboard_type": ["tipo", "type"],
        "widgets": ["widgets"],
        "layout": ["layout"],
        "is_public": ["is_public", "publico"],
        "refresh_interval": ["intervalo_atualizacao", "refresh_interval"],
        "filters": ["filtros", "filters"],
        "color": ["cor", "color"],
        "icon": ["icone", "icon"],
        "order": ["ordem", "order"],
        "slug": ["slug"],
    }

    # 1. Mapeamento direto
    if invalid_field in known_mappings:
        for candidate in known_mappings[invalid_field]:
            if candidate in valid_fields:
                return candidate

    # 2. Fuzzy match - campo similar
    invalid_lower = invalid_field.lower()
    for valid in valid_fields:
        valid_lower = valid.lower()
        # Exato com case diferente
        if invalid_lower == valid_lower:
            return valid
        # Contém
        if invalid_lower in valid_lower or valid_lower in invalid_lower:
            return valid

    # 3. Tradução PT↔EN
    pt_en = {
        "nome": "name", "descricao": "description", "titulo": "title",
        "tipo": "type", "valor": "value", "preco": "price",
        "quantidade": "quantity", "data": "date", "codigo": "code",
        "categoria": "category", "prioridade": "priority",
        "saldo": "balance", "numero": "number", "mes": "month",
        "ano": "year", "periodo": "period", "rotulo": "label",
        "cor": "color", "icone": "icon", "ordem": "order",
        "ativo": "active", "observacoes": "notes",
    }

    # Se o campo inválido é inglês, procurar equivalente português
    for pt, en in pt_en.items():
        if invalid_lower == en and pt in valid_fields:
            return pt
        if invalid_lower == pt and en in valid_fields:
            return en

    return None


def scan_and_build_fixes() -> dict:
    """Escaneia todos os erros e constrói mapa de correções."""
    print("Escaneando erros de campo inválido...")

    errors = find_invalid_field_errors()
    if not errors:
        print("✓ Nenhum erro de campo inválido encontrado!")
        return {}

    # Agrupar por model
    by_model: dict[str, set] = defaultdict(set)
    for err in errors:
        by_model[err["model"]].add(err["field"])

    print(f"Encontrados: {len(errors)} erros em {len(by_model)} models")
    print("")

    fixes: dict[str, dict] = {}  # model -> {invalid_field: correct_field}
    unfixable: dict[str, list] = defaultdict(list)

    for model_name, invalid_fields in sorted(by_model.items()):
        model_info = get_model_fields(model_name)
        if not model_info:
            print(f"  ⚠️  {model_name}: Model não encontrado em modules/")
            for f in invalid_fields:
                unfixable[model_name].append(f)
            continue

        valid_fields = model_info["fields"]
        model_fixes = {}

        for invalid_field in sorted(invalid_fields):
            mapping = find_field_mapping(invalid_field, valid_fields)
            if mapping:
                model_fixes[invalid_field] = mapping
                print(f"  🔧 {model_name}.{invalid_field} → {mapping}")
            else:
                unfixable[model_name].append(invalid_field)
                print(f"  ❌ {model_name}.{invalid_field} → ? (campos: {', '.join(valid_fields[:5])}...)")

        if model_fixes:
            fixes[model_name] = {
                "mappings": model_fixes,
                "file": model_info["file"],
            }

    return {"fixes": fixes, "unfixable": unfixable}


def apply_fixes(fixes: dict) -> int:
    """Aplica as correções nos arquivos de teste."""
    fixed = 0

    if not TESTS_DIR.exists():
        return 0

    for py_file in TESTS_DIR.rglob("test_*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        original = content
        file_fixed = 0

        for model_name, model_data in fixes.get("fixes", {}).items():
            mappings = model_data["mappings"]

            for old_field, new_field in mappings.items():
                # Pattern 1: Model(old_field=value)
                pattern = rf'(\b{model_name}\s*\([^)]*)\b{old_field}\s*='
                replacement = rf'\g<1>{new_field}='
                new_content = re.sub(pattern, replacement, content)

                # Pattern 2: dict com old_field como key
                # "old_field": value  ou  'old_field': value
                data_pattern = rf'(["\']){old_field}\1(\s*:\s*)'
                # Só substituir se está perto de um Model() context
                # Para segurança, usar substituição mais conservadora

                # Pattern 3: sample_data["old_field"] = value
                access_pattern = rf'(\[[\"\']){old_field}([\"\']\])'
                access_replacement = rf'\g<1>{new_field}\g<2>'

                if new_content != content:
                    content = new_content
                    file_fixed += 1

                # Também substituir em dicts de dados de teste
                # Padrão: "old_field": "value" em fixtures/dicts
                dict_pattern = rf'"{old_field}"(\s*:)'
                dict_replacement = f'"{new_field}"\\1'
                new_content2 = re.sub(dict_pattern, dict_replacement, content)
                if new_content2 != content:
                    content = new_content2
                    file_fixed += 1

        if content != original:
            py_file.write_text(content, encoding="utf-8")
            rel_path = str(py_file.relative_to(BACKEND))
            print(f"  ✓ {rel_path}: {file_fixed} correções")
            fixed += file_fixed

    return fixed


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    fix_mode = "--fix" in sys.argv
    specific_model = None
    for i, arg in enumerate(sys.argv):
        if arg == "--model" and i + 1 < len(sys.argv):
            specific_model = sys.argv[i + 1]

    print("═══════════════════════════════════════════")
    print("AUTO-FIX FIELDS — Campos Inválidos nos Testes")
    print("═══════════════════════════════════════════")
    print("")

    result = scan_and_build_fixes()

    fixes = result.get("fixes", {})
    unfixable = result.get("unfixable", {})

    total_fixable = sum(len(f["mappings"]) for f in fixes.values())
    total_unfixable = sum(len(f) for f in unfixable.values())

    print("")
    print(f"═══════════════════════════════════════════")
    print(f"Mapeamentos encontrados: {total_fixable} auto-fixáveis, {total_unfixable} manuais")
    print(f"═══════════════════════════════════════════")

    if unfixable:
        print("")
        print("CAMPOS SEM MAPEAMENTO (precisam revisão manual):")
        for model, fields in unfixable.items():
            print(f"  {model}: {', '.join(fields)}")

    if fix_mode and fixes:
        print("")
        print("Aplicando correções...")
        fixed = apply_fixes(result)
        print(f"")
        print(f"═══════════════════════════════════════════")
        print(f"✓ {fixed} correções aplicadas")
        print(f"Rode verify-instant para confirmar.")
        print(f"═══════════════════════════════════════════")
    elif fixes:
        print("")
        print("═══════════════════════════════════════════")
        print("Para aplicar: ./scripts/auto-fix-fields.py --fix")
        print("═══════════════════════════════════════════")


if __name__ == "__main__":
    main()
