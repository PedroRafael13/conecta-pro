#!/usr/bin/env python3
"""
Script para extrair endpoints do módulo AI (Inteligência Artificial) do OpenAPI spec completo.
Gera um arquivo openapi-ai.json filtrado com 25 endpoints de IA.
"""

import json
import sys
from pathlib import Path


def extract_ai_spec(input_file: str, output_file: str):
    """Extrai apenas os endpoints do módulo AI/Bartolo."""

    print(f"Carregando OpenAPI spec de: {input_file}")
    with open(input_file, encoding="utf-8") as f:
        full_spec = json.load(f)

    # Filtrar apenas paths do AI (todos os endpoints /ai/)
    ai_paths = {k: v for k, v in full_spec["paths"].items() if "/ai/" in k or k.startswith("/api/v1/ai")}

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
    extract_refs(ai_paths)

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
    ai_spec = {
        "openapi": full_spec["openapi"],
        "info": {
            "title": "Conecta PRO - AI/Bartolo API",
            "description": "API de Inteligência Artificial: OCR, Análise de Contratos, Detecção de Fraude, Assistente Bartolo e mais",
            "version": full_spec["info"]["version"],
        },
        "paths": ai_paths,
        "components": {
            "schemas": filtered_schemas,
            "securitySchemes": full_spec.get("components", {}).get("securitySchemes", {}),
        },
    }

    # Adicionar security global se existir
    if "security" in full_spec:
        ai_spec["security"] = full_spec["security"]

    # Salvar
    print(f"Salvando spec filtrado em: {output_file}")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ai_spec, f, indent=2, ensure_ascii=False)

    print("\nEstatísticas:")
    print(f"  - Endpoints AI: {len(ai_paths)}")
    print(f"  - Schemas: {len(filtered_schemas)}")
    print(f"  - Tamanho: {Path(output_file).stat().st_size / 1024:.1f} KB")

    # Listar endpoints por módulo
    modules = {}
    for path in ai_paths.keys():
        if "/ai/" in path:
            parts = path.split("/ai/")
            if len(parts) > 1:
                module = parts[1].split("/")[0]
                modules[module] = modules.get(module, 0) + 1

    print("\nMódulos AI extraídos:")
    for module, count in sorted(modules.items()):
        print(f"  - {module}: {count} endpoints")

    return ai_spec


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "openapi_full.json"
    output_file = base_dir / "openapi-ai.json"

    if not input_file.exists():
        print(f"ERRO: Arquivo {input_file} não encontrado!")
        print("Execute: curl -s http://localhost:8080/openapi.json > openapi_full.json")
        sys.exit(1)

    extract_ai_spec(str(input_file), str(output_file))
    print("\n✓ OpenAPI spec AI extraído com sucesso!")
