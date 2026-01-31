#!/usr/bin/env python3
"""
Script para extrair endpoints do módulo RECRUITMENT do OpenAPI spec completo.
Gera um arquivo openapi.recruitment.json filtrado.
"""

import json
import sys
from pathlib import Path

def extract_recruitment_spec(input_file: str, output_file: str):
    """Extrai apenas os endpoints do módulo Recruitment."""

    print(f"Carregando OpenAPI spec de: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        full_spec = json.load(f)

    # Filtrar apenas paths do recruitment
    recruitment_paths = {
        k: v for k, v in full_spec['paths'].items()
        if '/recruitment' in k
    }

    # Coletar todos os schemas referenciados
    referenced_schemas = set()

    def extract_refs(obj):
        """Extrai recursivamente todas as referências de schemas."""
        if isinstance(obj, dict):
            if '$ref' in obj:
                ref = obj['$ref']
                if ref.startswith('#/components/schemas/'):
                    schema_name = ref.split('/')[-1]
                    referenced_schemas.add(schema_name)
            for value in obj.values():
                extract_refs(value)
        elif isinstance(obj, list):
            for item in obj:
                extract_refs(item)

    # Extrair refs dos paths
    extract_refs(recruitment_paths)

    # Adicionar schemas relacionados recursivamente
    all_schemas = full_spec.get('components', {}).get('schemas', {})
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
    filtered_schemas = {
        k: v for k, v in all_schemas.items()
        if k in referenced_schemas
    }

    # Criar spec filtrado
    recruitment_spec = {
        'openapi': full_spec['openapi'],
        'info': {
            'title': 'Conecta PRO - Recruitment API',
            'description': 'API de Recrutamento e Seleção',
            'version': full_spec['info']['version']
        },
        'paths': recruitment_paths,
        'components': {
            'schemas': filtered_schemas,
            'securitySchemes': full_spec.get('components', {}).get('securitySchemes', {})
        }
    }

    # Adicionar security global se existir
    if 'security' in full_spec:
        recruitment_spec['security'] = full_spec['security']

    # Salvar
    print(f"Salvando spec filtrado em: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recruitment_spec, f, indent=2, ensure_ascii=False)

    print(f"\nEstatísticas:")
    print(f"  - Endpoints: {len(recruitment_paths)}")
    print(f"  - Schemas: {len(filtered_schemas)}")
    print(f"  - Tamanho: {Path(output_file).stat().st_size / 1024:.1f} KB")

    return recruitment_spec

if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / 'openapi_full.json'
    output_file = base_dir / 'openapi.recruitment.json'

    if not input_file.exists():
        print(f"ERRO: Arquivo {input_file} não encontrado!")
        print("Execute: curl -s http://localhost:8080/openapi.json > openapi_full.json")
        sys.exit(1)

    extract_recruitment_spec(str(input_file), str(output_file))
    print("\n✓ OpenAPI spec recruitment extraído com sucesso!")
