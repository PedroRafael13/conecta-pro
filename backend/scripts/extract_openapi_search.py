#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec APENAS do módulo SEARCH

Extrai endpoints da tag: "Search - Busca Global"
Total: 1 endpoint
- GET /api/v1/search/ - Busca global no sistema

Uso:
    python scripts/extract_openapi_search.py

Saída:
    openapi-search.json (apenas módulo SEARCH)
"""

import json
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.openapi.utils import get_openapi

from main_production import app


def extract_search_openapi():
    """Extrai OpenAPI spec apenas do módulo SEARCH."""

    # Gerar spec completo
    full_spec = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    # Tags do módulo SEARCH
    search_tags = {"Search - Busca Global"}

    # Filtrar apenas paths do módulo SEARCH
    filtered_paths = {}
    for path, path_item in full_spec.get("paths", {}).items():
        for method, operation in path_item.items():
            if method in ["get", "post", "put", "patch", "delete"]:
                tags = operation.get("tags", [])
                if any(tag in search_tags for tag in tags):
                    if path not in filtered_paths:
                        filtered_paths[path] = {}
                    filtered_paths[path][method] = operation

    # Coletar schemas referenciados
    all_refs = set()

    def collect_refs(obj):
        """Coleta todas as referências $ref recursivamente."""
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                if ref.startswith("#/components/schemas/"):
                    schema_name = ref.split("/")[-1]
                    all_refs.add(schema_name)
            for value in obj.values():
                collect_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                collect_refs(item)

    # Coletar refs dos paths filtrados
    collect_refs(filtered_paths)

    # Expandir refs recursivamente
    expanded_refs = set(all_refs)
    last_size = 0
    while len(expanded_refs) != last_size:
        last_size = len(expanded_refs)
        for ref in list(expanded_refs):
            if ref in full_spec.get("components", {}).get("schemas", {}):
                schema = full_spec["components"]["schemas"][ref]
                collect_refs(schema)
        expanded_refs = all_refs.copy()

    # Filtrar schemas necessários
    filtered_schemas = {}
    for schema_name in expanded_refs:
        if schema_name in full_spec.get("components", {}).get("schemas", {}):
            filtered_schemas[schema_name] = full_spec["components"]["schemas"][schema_name]

    # Construir spec filtrado
    search_spec = {
        "openapi": full_spec["openapi"],
        "info": {
            "title": "Conecta PRO - API SEARCH",
            "version": full_spec["info"]["version"],
            "description": "OpenAPI spec do módulo SEARCH - Busca Global (1 endpoint)",
        },
        "paths": filtered_paths,
        "components": {"schemas": filtered_schemas},
    }

    # Salvar arquivo
    output_file = Path(__file__).parent.parent / "openapi-search.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(search_spec, f, indent=2, ensure_ascii=False)

    # Estatísticas
    total_endpoints = sum(len(methods) for methods in filtered_paths.values())
    print("✓ OpenAPI SEARCH extraído com sucesso!")
    print(f"  - Arquivo: {output_file}")
    print(f"  - Endpoints: {total_endpoints}")
    print(f"  - Schemas: {len(filtered_schemas)}")
    print(f"  - Tags: {', '.join(sorted(search_tags))}")

    return search_spec


if __name__ == "__main__":
    try:
        extract_search_openapi()
    except Exception as e:
        print(f"✗ Erro ao extrair OpenAPI: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
