#!/usr/bin/env python3
"""
Script para extrair apenas os endpoints do módulo Government Integrations do OpenAPI completo.
Filtro: /api/v1/government/

Uso:
    python3 extract-government-spec.py
"""

import json
import sys
from pathlib import Path

def extract_government_spec(
    input_file: str,
    output_file: str,
    path_filter: str = "/api/v1/government/"
):
    """Extrai apenas os endpoints do módulo Government Integrations."""

    print(f"📖 Lendo OpenAPI spec completo: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        full_spec = json.load(f)

    print(f"📊 Total de endpoints no spec completo: {len(full_spec['paths'])}")

    # Criar novo spec apenas com endpoints do Government
    gov_spec = {
        "openapi": full_spec["openapi"],
        "info": {
            "title": "Conecta PRO - Módulo Government Integrations",
            "description": "API do módulo Government Integrations: NFS-e, eSocial, SEFAZ, SPED, FGTS, e outras integrações governamentais",
            "version": full_spec["info"]["version"]
        },
        "servers": full_spec.get("servers", []),
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": full_spec.get("components", {}).get("securitySchemes", {})
        }
    }

    # Filtrar apenas paths do módulo Government
    gov_paths = {
        path: data
        for path, data in full_spec["paths"].items()
        if path_filter in path
    }

    gov_spec["paths"] = gov_paths

    print(f"✅ Endpoints do módulo Government: {len(gov_paths)}")

    # Coletar schemas referenciados pelos endpoints do Government
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

    collect_refs(gov_paths)

    print(f"📦 Schemas referenciados: {len(referenced_schemas)}")

    # Copiar apenas os schemas referenciados
    all_schemas = full_spec.get("components", {}).get("schemas", {})
    # Converter para lista para evitar "Set changed size during iteration"
    initial_schemas = list(referenced_schemas)
    for schema_name in initial_schemas:
        if schema_name in all_schemas:
            gov_spec["components"]["schemas"][schema_name] = all_schemas[schema_name]
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
        if schema_name in all_schemas and schema_name not in gov_spec["components"]["schemas"]:
            gov_spec["components"]["schemas"][schema_name] = all_schemas[schema_name]

    print(f"📦 Total de schemas copiados: {len(gov_spec['components']['schemas'])}")

    # Salvar spec do módulo Government
    print(f"💾 Salvando spec do módulo Government: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(gov_spec, f, indent=2, ensure_ascii=False)

    # Estatísticas
    size_before = Path(input_file).stat().st_size / 1024 / 1024  # MB
    size_after = Path(output_file).stat().st_size / 1024 / 1024  # MB
    reduction = ((size_before - size_after) / size_before) * 100

    print("\n✨ EXTRAÇÃO CONCLUÍDA!")
    print(f"   Tamanho original: {size_before:.2f} MB")
    print(f"   Tamanho otimizado: {size_after:.2f} MB")
    print(f"   Redução: {reduction:.1f}%")
    print(f"\n📄 Arquivo gerado: {output_file}")
    print(f"   Endpoints: {len(gov_paths)}")
    print(f"   Schemas: {len(gov_spec['components']['schemas'])}")

    # Estatísticas por controller (baseado nos tags)
    print("\n📊 ENDPOINTS POR CONTROLLER:")
    endpoints_by_tag = {}
    for path, data in gov_paths.items():
        for method, details in data.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                tags = details.get('tags', ['Outros'])
                tag = tags[0] if tags else 'Outros'
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = 0
                endpoints_by_tag[tag] += 1

    for tag in sorted(endpoints_by_tag.keys()):
        count = endpoints_by_tag[tag]
        print(f"   {tag}: {count} endpoints")

    print(f"\n✅ TOTAL: {sum(endpoints_by_tag.values())} endpoints")

if __name__ == "__main__":
    # Caminhos padrão
    docs_dir = Path("/opt/conecta-pro/docs/expansao-orval-28-01-2026")
    input_file = docs_dir / "openapi-conecta-pro.json"
    output_file = docs_dir / "openapi-government.json"

    # Se não existir no docs, tentar /tmp
    if not input_file.exists():
        input_file = Path("/tmp/openapi-conecta-pro.json")

    if not input_file.exists():
        print(f"❌ ERRO: Arquivo não encontrado: {input_file}")
        print("\nExecute primeiro:")
        print("  curl -s http://localhost:8080/openapi.json -o /opt/conecta-pro/docs/expansao-orval-28-01-2026/openapi-conecta-pro.json")
        print("\nOu:")
        print("  curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json")
        sys.exit(1)

    try:
        extract_government_spec(str(input_file), str(output_file))
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
