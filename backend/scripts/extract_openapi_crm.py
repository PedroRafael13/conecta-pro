#!/usr/bin/env python3
"""
Script para extrair endpoints do módulo CRM do OpenAPI spec completo.
Gera um arquivo openapi-crm.json filtrado com 100 endpoints de CRM.
"""

import json
import sys
from pathlib import Path

def extract_crm_spec(input_file: str, output_file: str):
    """Extrai apenas os endpoints do módulo CRM."""

    print(f"Carregando OpenAPI spec de: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        full_spec = json.load(f)

    # Filtrar apenas paths do CRM
    crm_paths = {
        k: v for k, v in full_spec['paths'].items()
        if '/crm/' in k or k.startswith('/api/v1/crm')
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
    extract_refs(crm_paths)

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
    crm_spec = {
        'openapi': full_spec['openapi'],
        'info': {
            'title': 'Conecta PRO - CRM API',
            'description': 'API de Gestão de Relacionamento com Cliente: Leads, Opportunities, Contratos, Comissões, Propostas e Dashboard',
            'version': full_spec['info']['version']
        },
        'paths': crm_paths,
        'components': {
            'schemas': filtered_schemas,
            'securitySchemes': full_spec.get('components', {}).get('securitySchemes', {})
        }
    }

    # Adicionar security global se existir
    if 'security' in full_spec:
        crm_spec['security'] = full_spec['security']

    # Salvar
    print(f"Salvando spec filtrado em: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(crm_spec, f, indent=2, ensure_ascii=False)

    print(f"\nEstatísticas:")
    print(f"  - Endpoints CRM: {len(crm_paths)}")
    print(f"  - Schemas: {len(filtered_schemas)}")
    print(f"  - Tamanho: {Path(output_file).stat().st_size / 1024:.1f} KB")

    # Listar endpoints por controller
    controllers = {}
    for path in crm_paths.keys():
        if '/crm/' in path:
            parts = path.split('/crm/')
            if len(parts) > 1:
                controller = parts[1].split('/')[0]
                controllers[controller] = controllers.get(controller, 0) + 1

    print(f"\nControllers CRM extraídos:")
    for controller, count in sorted(controllers.items()):
        print(f"  - {controller}: {count} endpoints")

    return crm_spec

if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / 'openapi_full.json'
    output_file = base_dir / 'openapi-crm.json'

    if not input_file.exists():
        print(f"ERRO: Arquivo {input_file} não encontrado!")
        print("Execute: curl -s http://localhost:8080/openapi.json > openapi_full.json")
        sys.exit(1)

    extract_crm_spec(str(input_file), str(output_file))
    print("\n✓ OpenAPI spec CRM extraído com sucesso!")
