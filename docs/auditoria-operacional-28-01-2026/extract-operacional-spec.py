#!/usr/bin/env python3
"""
Script para extrair apenas os endpoints do módulo OPERACIONAL do OpenAPI completo.
Isso evita que o Orval tente processar 1.246 endpoints de uma vez.

Uso:
    python3 extract-operacional-spec.py
"""

import json
import sys
from pathlib import Path

def extract_operacional_spec(
    input_file: str,
    output_file: str,
    path_filter: str = "/api/v1/operacional/"
):
    """Extrai apenas os endpoints do módulo operacional."""

    print(f"📖 Lendo OpenAPI spec completo: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        full_spec = json.load(f)

    print(f"📊 Total de endpoints no spec completo: {len(full_spec['paths'])}")

    # Criar novo spec apenas com endpoints operacionais
    operacional_spec = {
        "openapi": full_spec["openapi"],
        "info": {
            "title": "Conecta PRO - Módulo OPERACIONAL",
            "description": "API do módulo operacional (postos, escalas, turnos, ocorrências, etc.)",
            "version": full_spec["info"]["version"]
        },
        "servers": full_spec.get("servers", []),
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": full_spec.get("components", {}).get("securitySchemes", {})
        }
    }

    # Filtrar apenas paths do módulo operacional
    operacional_paths = {
        path: data
        for path, data in full_spec["paths"].items()
        if path_filter in path
    }

    operacional_spec["paths"] = operacional_paths

    print(f"✅ Endpoints do módulo OPERACIONAL: {len(operacional_paths)}")

    # Coletar schemas referenciados pelos endpoints operacionais
    print("🔍 Coletando schemas referenciados...")
    referenced_schemas = set()

    def collect_refs(obj):
        """Recursivamente coleta todas as referências $ref."""
        if isinstance(obj, dict):
            if "$ref" in obj:
                # Extrair nome do schema: #/components/schemas/User -> User
                ref_path = obj["$ref"]
                if "/schemas/" in ref_path:
                    schema_name = ref_path.split("/schemas/")[-1]
                    referenced_schemas.add(schema_name)
            for value in obj.values():
                collect_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                collect_refs(item)

    collect_refs(operacional_paths)

    print(f"📦 Schemas referenciados: {len(referenced_schemas)}")

    # Copiar apenas os schemas referenciados
    all_schemas = full_spec.get("components", {}).get("schemas", {})
    # Converter para lista para evitar "Set changed size during iteration"
    initial_schemas = list(referenced_schemas)
    for schema_name in initial_schemas:
        if schema_name in all_schemas:
            operacional_spec["components"]["schemas"][schema_name] = all_schemas[schema_name]
            # Recursivamente adicionar schemas referenciados dentro deste schema
            collect_refs(all_schemas[schema_name])

    # Segunda passagem para pegar schemas referenciados pelos schemas
    # Converter para lista para evitar "Set changed size during iteration"
    schemas_to_process = list(referenced_schemas)
    for schema_name in schemas_to_process:
        if schema_name in all_schemas:
            collect_refs(all_schemas[schema_name])

    # Adicionar schemas que foram descobertos na segunda passagem
    # Converter para lista novamente
    all_referenced = list(referenced_schemas)
    for schema_name in all_referenced:
        if schema_name in all_schemas and schema_name not in operacional_spec["components"]["schemas"]:
            operacional_spec["components"]["schemas"][schema_name] = all_schemas[schema_name]

    print(f"📦 Total de schemas copiados: {len(operacional_spec['components']['schemas'])}")

    # Salvar spec do módulo operacional
    print(f"💾 Salvando spec do módulo OPERACIONAL: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(operacional_spec, f, indent=2, ensure_ascii=False)

    # Estatísticas
    size_before = Path(input_file).stat().st_size / 1024 / 1024  # MB
    size_after = Path(output_file).stat().st_size / 1024 / 1024  # MB
    reduction = ((size_before - size_after) / size_before) * 100

    print("\n✨ EXTRAÇÃO CONCLUÍDA!")
    print(f"   Tamanho original: {size_before:.2f} MB")
    print(f"   Tamanho otimizado: {size_after:.2f} MB")
    print(f"   Redução: {reduction:.1f}%")
    print(f"\n📄 Arquivo gerado: {output_file}")
    print(f"   Endpoints: {len(operacional_paths)}")
    print(f"   Schemas: {len(operacional_spec['components']['schemas'])}")

if __name__ == "__main__":
    # Caminhos padrão
    scratchpad = Path("/tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad")
    input_file = scratchpad / "openapi-conecta-pro.json"
    output_file = scratchpad / "openapi-operacional.json"

    if not input_file.exists():
        print(f"❌ ERRO: Arquivo não encontrado: {input_file}")
        print("\nExecute primeiro:")
        print("  curl -s http://localhost:8080/openapi.json -o", input_file)
        sys.exit(1)

    try:
        extract_operacional_spec(str(input_file), str(output_file))
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
