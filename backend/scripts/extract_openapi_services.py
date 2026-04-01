#!/usr/bin/env python3
"""
Script para extrair endpoints do módulo SERVICES do OpenAPI spec completo.
Gera um arquivo openapi-services.json filtrado com 63 endpoints de gestão de serviços.
"""

import json
import sys
from pathlib import Path


def extract_services_spec(input_file: str, output_file: str):
    """Extrai apenas os endpoints do módulo SERVICES."""

    print(f"Carregando OpenAPI spec de: {input_file}")
    with open(input_file, encoding="utf-8") as f:
        full_spec = json.load(f)

    # Filtrar apenas paths do SERVICES (todos os endpoints /services/)
    services_paths = {
        k: v for k, v in full_spec["paths"].items() if "/services/" in k or k.startswith("/api/v1/services")
    }

    # Coletar todos os schemas referenciados
    referenced_schemas = set()

    def extract_refs(obj):
        """Extrai recursivamente todas as referências de schemas."""
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                if ref.startswith("#/components/schemas/"):
                    schema_name = ref.split("/")[-1]
                    referenced_schemas.add(schema_name)
            for value in obj.values():
                extract_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                extract_refs(item)

    # Extrair refs dos paths
    extract_refs(services_paths)

    # Adicionar schemas relacionados recursivamente
    all_schemas = full_spec.get("components", {}).get("schemas", {})
    schemas_to_add = referenced_schemas.copy()

    while True:
        new_schemas = set()
        for schema_name in schemas_to_add:
            if schema_name in all_schemas:
                extract_refs(all_schemas[schema_name])

        new_schemas = referenced_schemas - schemas_to_add
        if not new_schemas:
            break
        schemas_to_add.update(new_schemas)

    # Construir spec filtrado
    filtered_schemas = {k: v for k, v in all_schemas.items() if k in referenced_schemas}

    # Criar spec filtrado
    services_spec = {
        "openapi": full_spec["openapi"],
        "info": {
            "title": "Conecta PRO - Services API",
            "description": "API de Gestão de Serviços: Catálogo, Ordens, Execuções, Relatórios, SLA e AI",
            "version": full_spec["info"]["version"],
        },
        "paths": services_paths,
        "components": {
            "schemas": filtered_schemas,
            "securitySchemes": full_spec.get("components", {}).get("securitySchemes", {}),
        },
    }

    # Adicionar security global se existir
    if "security" in full_spec:
        services_spec["security"] = full_spec["security"]

    # Salvar
    print(f"Salvando spec filtrado em: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(services_spec, f, indent=2, ensure_ascii=False)

    print("\n✅ Spec extraído com sucesso!")
    print(f"📊 Endpoints extraídos: {len(services_paths)}")
    print(f"📦 Schemas incluídos: {len(filtered_schemas)}")

    return services_spec


if __name__ == "__main__":
    backend_root = Path(__file__).parent.parent

    # Tentar encontrar openapi.json ou openapi_full.json
    input_path = backend_root / "openapi_full.json"
    if not input_path.exists():
        input_path = backend_root / "openapi.json"

    output_path = backend_root / "openapi-services.json"

    if not input_path.exists():
        print("❌ Erro: arquivo OpenAPI não encontrado")
        print("Execute primeiro: python scripts/generate_openapi.py")
        sys.exit(1)

    extract_services_spec(str(input_path), str(output_path))
