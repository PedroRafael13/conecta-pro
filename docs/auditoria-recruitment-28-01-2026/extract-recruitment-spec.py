#!/usr/bin/env python3
"""
Script para extrair apenas os endpoints do módulo RECRUITMENT do OpenAPI completo.

Baseado em extract-ged-spec.py com ajustes para o módulo de Recrutamento e Seleção.

Uso:
    python3 extract-recruitment-spec.py
"""

import json
import sys
from pathlib import Path


def extract_recruitment_spec(
    input_file: str,
    output_file: str,
    path_filters: list = None
):
    """Extrai apenas os endpoints do módulo RECRUITMENT."""

    if path_filters is None:
        path_filters = [
            "/api/v1/recruitment/job-positions/",
            "/api/v1/recruitment/candidates/",
            "/api/v1/recruitment/applications/",
            "/api/v1/recruitment/interviews/",
        ]

    print(f"📖 Lendo OpenAPI spec completo: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        full_spec = json.load(f)

    print(f"📊 Total de endpoints no spec completo: {len(full_spec['paths'])}")

    # Criar novo spec apenas com endpoints do RECRUITMENT
    recruitment_spec = {
        "openapi": full_spec["openapi"],
        "info": {
            "title": "Conecta PRO - Módulo RECRUITMENT",
            "description": "API do módulo RECRUITMENT (Recrutamento e Seleção): vagas, candidatos, candidaturas, entrevistas",
            "version": full_spec["info"]["version"]
        },
        "servers": full_spec.get("servers", []),
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": full_spec.get("components", {}).get("securitySchemes", {})
        }
    }

    # Filtrar apenas paths do módulo RECRUITMENT
    recruitment_paths = {}
    for path, data in full_spec["paths"].items():
        for filter_path in path_filters:
            if filter_path in path:
                recruitment_paths[path] = data
                break

    recruitment_spec["paths"] = recruitment_paths

    print(f"✅ Endpoints do módulo RECRUITMENT: {len(recruitment_paths)}")

    # Breakdown por submódulo
    job_positions = len([p for p in recruitment_paths.keys() if "/job-positions/" in p])
    candidates = len([p for p in recruitment_paths.keys() if "/candidates/" in p])
    applications = len([p for p in recruitment_paths.keys() if "/applications/" in p])
    interviews = len([p for p in recruitment_paths.keys() if "/interviews/" in p])

    print(f"   - Job Positions (Vagas): {job_positions}")
    print(f"   - Candidates (Candidatos): {candidates}")
    print(f"   - Applications (Candidaturas): {applications}")
    print(f"   - Interviews (Entrevistas): {interviews}")

    # Coletar schemas referenciados pelos endpoints do RECRUITMENT
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

    collect_refs(recruitment_paths)

    print(f"📦 Schemas referenciados: {len(referenced_schemas)}")

    # Copiar apenas os schemas referenciados
    all_schemas = full_spec.get("components", {}).get("schemas", {})

    # Primeira passagem: adicionar schemas diretos
    initial_schemas = list(referenced_schemas)
    for schema_name in initial_schemas:
        if schema_name in all_schemas:
            recruitment_spec["components"]["schemas"][schema_name] = all_schemas[schema_name]
            # Recursivamente adicionar schemas referenciados dentro deste schema
            collect_refs(all_schemas[schema_name])

    # Segunda passagem: adicionar schemas referenciados pelos schemas
    schemas_to_process = list(referenced_schemas)
    for schema_name in schemas_to_process:
        if schema_name in all_schemas:
            collect_refs(all_schemas[schema_name])

    # Terceira passagem: adicionar todos os schemas descobertos
    all_referenced = list(referenced_schemas)
    for schema_name in all_referenced:
        if schema_name in all_schemas and schema_name not in recruitment_spec["components"]["schemas"]:
            recruitment_spec["components"]["schemas"][schema_name] = all_schemas[schema_name]

    print(f"📦 Total de schemas copiados: {len(recruitment_spec['components']['schemas'])}")

    # Salvar spec do módulo RECRUITMENT
    print(f"💾 Salvando spec do módulo RECRUITMENT: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recruitment_spec, f, indent=2, ensure_ascii=False)

    # Estatísticas
    size_before = Path(input_file).stat().st_size / 1024 / 1024  # MB
    size_after = Path(output_file).stat().st_size / 1024 / 1024  # MB
    reduction = ((size_before - size_after) / size_before) * 100

    print("\n✨ EXTRAÇÃO CONCLUÍDA!")
    print(f"   Tamanho original: {size_before:.2f} MB")
    print(f"   Tamanho otimizado: {size_after:.2f} MB")
    print(f"   Redução: {reduction:.1f}%")
    print(f"\n📄 Arquivo gerado: {output_file}")
    print(f"   Endpoints: {len(recruitment_paths)}")
    print(f"   Schemas: {len(recruitment_spec['components']['schemas'])}")
    print(f"\n📋 Breakdown:")
    print(f"   - Job Positions: {job_positions} endpoints")
    print(f"   - Candidates: {candidates} endpoints")
    print(f"   - Applications: {applications} endpoints")
    print(f"   - Interviews: {interviews} endpoints")


if __name__ == "__main__":
    # Caminhos padrão
    docs_dir = Path("/opt/conecta-pro/docs/auditoria-recruitment-28-01-2026")
    input_file = docs_dir / "openapi-conecta-pro.json"
    output_file = docs_dir / "openapi-recruitment.json"

    if not input_file.exists():
        print(f"❌ ERRO: Arquivo não encontrado: {input_file}")
        print("\nExecute primeiro:")
        print(f"  curl -s http://localhost:8080/openapi.json -o {input_file}")
        sys.exit(1)

    try:
        extract_recruitment_spec(str(input_file), str(output_file))
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
