#!/usr/bin/env python3
"""
required-fields.py — Mostra campos obrigatórios de models SQLAlchemy/Pydantic

Uso:
    ./scripts/required-fields.py <arquivo.py> <NomeModel>
    ./scripts/required-fields.py modules/config/models/tenant.py Tenant
    ./scripts/required-fields.py modules/config/models/tenant.py  # lista todos os models do arquivo

Exemplos:
    ./scripts/required-fields.py modules/crm/models/client.py Client
    ./scripts/required-fields.py modules/financial/models/invoice.py Invoice
"""

import ast
import sys
from pathlib import Path

BACKEND = Path("/opt/conecta-pro/backend")


def parse_sqlalchemy_field(node: ast.Assign | ast.AnnAssign) -> dict | None:
    """Parseia um campo SQLAlchemy Column()."""
    result = {"name": None, "type": "?", "required": True, "default": None, "nullable": False}

    # Obter nome do campo
    if isinstance(node, ast.Assign) and node.targets:
        target = node.targets[0]
        if isinstance(target, ast.Name):
            result["name"] = target.id
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        result["name"] = node.target.id

    if not result["name"]:
        return None

    # Ignorar campos dunder e métodos
    if result["name"].startswith("_"):
        return None

    # Analisar o valor (Column(...), relationship(...), etc.)
    value = node.value if isinstance(node, ast.Assign) else node.value
    if value is None:
        return None

    source = ast.dump(value)

    # Detectar Column()
    if isinstance(value, ast.Call):
        func_name = ""
        if isinstance(value.func, ast.Name):
            func_name = value.func.id
        elif isinstance(value.func, ast.Attribute):
            func_name = value.func.attr

        if func_name == "relationship":
            return None  # Não é campo de tabela

        if func_name == "Column":
            # Extrair tipo do primeiro argumento posicional
            if value.args:
                first_arg = value.args[0]
                if isinstance(first_arg, ast.Name):
                    result["type"] = first_arg.id
                elif isinstance(first_arg, ast.Call):
                    if isinstance(first_arg.func, ast.Name):
                        result["type"] = first_arg.func.id
                    elif isinstance(first_arg.func, ast.Attribute):
                        result["type"] = first_arg.func.attr

            # Verificar kwargs
            for kw in value.keywords:
                if kw.arg == "nullable":
                    if isinstance(kw.value, ast.Constant):
                        result["nullable"] = kw.value.value
                        if kw.value.value:
                            result["required"] = False
                elif kw.arg == "default":
                    result["required"] = False
                    if isinstance(kw.value, ast.Constant):
                        result["default"] = repr(kw.value.value)
                    elif isinstance(kw.value, ast.Attribute):
                        result["default"] = f"{kw.value.value.id if isinstance(kw.value.value, ast.Name) else '?'}.{kw.value.attr}"
                    elif isinstance(kw.value, ast.Name):
                        result["default"] = kw.value.id
                elif kw.arg == "primary_key":
                    if isinstance(kw.value, ast.Constant) and kw.value.value:
                        result["required"] = False
                        result["default"] = "auto-generated"
                elif kw.arg == "server_default":
                    result["required"] = False
                    result["default"] = "server_default"

        elif func_name == "Field":
            # Pydantic Field()
            for kw in value.keywords:
                if kw.arg == "default":
                    result["required"] = False
                    if isinstance(kw.value, ast.Constant):
                        result["default"] = repr(kw.value.value)

            # Primeiro arg posicional em Field(...) é default se não é ...
            if value.args:
                first = value.args[0]
                if isinstance(first, ast.Constant) and first.value is not ...:
                    result["required"] = False
                    result["default"] = repr(first.value)
                elif isinstance(first, ast.Constant) and first.value is ...:
                    result["required"] = True

    return result


def parse_pydantic_field(node: ast.AnnAssign) -> dict | None:
    """Parseia um campo Pydantic (type hint)."""
    result = {"name": None, "type": "?", "required": True, "default": None, "nullable": False}

    if isinstance(node.target, ast.Name):
        result["name"] = node.target.id

    if not result["name"] or result["name"].startswith("_"):
        return None

    # Obter tipo da anotação
    if isinstance(node.annotation, ast.Name):
        result["type"] = node.annotation.id
    elif isinstance(node.annotation, ast.Subscript):
        if isinstance(node.annotation.value, ast.Name):
            result["type"] = f"{node.annotation.value.id}[...]"
            if node.annotation.value.id == "Optional":
                result["required"] = False
                result["nullable"] = True
    elif isinstance(node.annotation, ast.BinOp):
        # Union type: str | None
        if isinstance(node.annotation.op, ast.BitOr):
            right = node.annotation.right
            if isinstance(right, ast.Constant) and right.value is None:
                result["required"] = False
                result["nullable"] = True
            result["type"] = ast.unparse(node.annotation)

    # Verificar se tem valor default
    if node.value is not None:
        result["required"] = False
        if isinstance(node.value, ast.Constant):
            result["default"] = repr(node.value.value)
        elif isinstance(node.value, ast.Call):
            func_name = ""
            if isinstance(node.value.func, ast.Name):
                func_name = node.value.func.id
            elif isinstance(node.value.func, ast.Attribute):
                func_name = node.value.func.attr
            result["default"] = f"{func_name}(...)"

    return result


def analyze_model(file_path: Path, model_name: str | None = None) -> dict[str, list[dict]]:
    """Analisa um arquivo e retorna campos dos models."""
    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"❌ Erro ao parsear {file_path}: {e}")
        return {}

    results: dict[str, list[dict]] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        if model_name and node.name != model_name:
            continue

        # Verificar se é Model (herda de Base, BaseModel, etc.)
        base_names = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_names.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_names.append(base.attr)

        is_model = any(b in ("Base", "BaseModel", "BaseSchema", "SQLModel")
                      or "Model" in b or "Base" in b or "Schema" in b or "Mixin" in b
                      for b in base_names)

        if not is_model and not model_name:
            continue

        fields = []
        for item in node.body:
            field = None

            if isinstance(item, ast.Assign):
                field = parse_sqlalchemy_field(item)
            elif isinstance(item, ast.AnnAssign):
                # Tentar como SQLAlchemy primeiro, depois Pydantic
                if item.value and isinstance(item.value, ast.Call):
                    func_name = ""
                    if isinstance(item.value.func, ast.Name):
                        func_name = item.value.func.id
                    elif isinstance(item.value.func, ast.Attribute):
                        func_name = item.value.func.attr

                    if func_name in ("Column", "Field", "mapped_column"):
                        field = parse_sqlalchemy_field(item)
                    else:
                        field = parse_pydantic_field(item)
                else:
                    field = parse_pydantic_field(item)

            if field and field["name"]:
                fields.append(field)

        if fields:
            results[node.name] = fields

    return results


def print_model_fields(model_name: str, fields: list[dict]):
    """Imprime campos do model formatados."""
    required = [f for f in fields if f["required"]]
    optional = [f for f in fields if not f["required"]]

    print(f"═══════════════════════════════════════════")
    print(f"{model_name} — Campos")
    print(f"═══════════════════════════════════════════")
    print("")

    if required:
        print(f"OBRIGATÓRIOS ({len(required)}):")
        for f in required:
            default_info = ""
            if f["default"]:
                default_info = f"  default: {f['default']}"
            print(f"  {f['name']:<25} {f['type']:<20} sem default{default_info}")
    else:
        print("OBRIGATÓRIOS (0): nenhum")

    print("")

    if optional:
        print(f"OPCIONAIS ({len(optional)}):")
        for f in optional:
            info = ""
            if f["nullable"]:
                info = "nullable=True"
            elif f["default"]:
                info = f"default={f['default']}"
            else:
                info = "tem default"
            print(f"  {f['name']:<25} {f['type']:<20} {info}")

    print("")

    # Gerar exemplo de uso
    if required:
        args = []
        for f in required:
            if f["type"] in ("str", "String", "Text"):
                args.append(f'{f["name"]}="test"')
            elif f["type"] in ("int", "Integer"):
                args.append(f'{f["name"]}=1')
            elif f["type"] in ("float", "Float", "Numeric"):
                args.append(f'{f["name"]}=0.0')
            elif f["type"] in ("bool", "Boolean"):
                args.append(f'{f["name"]}=True')
            elif f["type"] in ("UUID",):
                args.append(f'{f["name"]}=uuid4()')
            else:
                args.append(f'{f["name"]}=<{f["type"]}>')

        print(f"═══════════════════════════════════════════")
        print(f"Uso correto no teste:")
        print(f"  {model_name}({', '.join(args)})")
        print(f"═══════════════════════════════════════════")


def main():
    if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    file_arg = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else None

    # Resolver path
    file_path = Path(file_arg)
    if not file_path.is_absolute():
        if (BACKEND / file_path).exists():
            file_path = BACKEND / file_path
        elif Path(f"/opt/conecta-pro/{file_arg}").exists():
            file_path = Path(f"/opt/conecta-pro/{file_arg}")

    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_arg}")
        print(f"   Tentei: {file_path}")
        sys.exit(1)

    results = analyze_model(file_path, model_name)

    if not results:
        if model_name:
            print(f"❌ Model '{model_name}' não encontrado em {file_arg}")
        else:
            print(f"⚠️  Nenhum model encontrado em {file_arg}")
        sys.exit(1)

    for name, fields in results.items():
        print_model_fields(name, fields)
        print("")


if __name__ == "__main__":
    main()
