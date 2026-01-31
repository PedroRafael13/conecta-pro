#!/usr/bin/env python3
"""
Script para extrair endpoints do módulo BIDDING (Licitações) do OpenAPI spec completo.
Gera um arquivo openapi-bidding.json filtrado com ~64 endpoints de licitações.

Módulos incluídos:
- Tenders (Editais)
- Proposals (Propostas)
- Contracts (Contratos Públicos)
- Certificates (Certidões)
- Documents (Documentação)
- PNCP (Integração Portal Nacional)
"""

import json
import sys
from pathlib import Path

def extract_bidding_spec(input_file: str, output_file: str):
    """Extrai apenas os endpoints do módulo BIDDING."""

    print(f"Carregando OpenAPI spec de: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        full_spec = json.load(f)

    # Filtrar apenas paths do BIDDING (licitações)
    bidding_paths = {
        k: v for k, v in full_spec['paths'].items()
        if any([
            '/tenders' in k,
            '/proposals' in k,
            '/contracts' in k and '/bidding' in k,
            '/certificates' in k,
            '/bidding/documents' in k,
            '/pncp' in k,
            k.startswith('/api/v1/bidding')
        ])
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
    extract_refs(bidding_paths)

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
    bidding_spec = {
        'openapi': full_spec['openapi'],
        'info': {
            'title': 'Conecta PRO - Bidding/Licitações API',
            'description': 'API de Licitações Públicas: Editais, Propostas, Contratos, Certidões, Integração PNCP (Lei 14.133/2021)',
            'version': full_spec['info']['version']
        },
        'paths': bidding_paths,
        'components': {
            'schemas': filtered_schemas,
            'securitySchemes': full_spec.get('components', {}).get('securitySchemes', {})
        }
    }

    # Adicionar security global se existir
    if 'security' in full_spec:
        bidding_spec['security'] = full_spec['security']

    # Salvar
    print(f"Salvando spec filtrado em: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bidding_spec, f, indent=2, ensure_ascii=False)

    print(f"\nEstatísticas:")
    print(f"  - Endpoints Bidding: {len(bidding_paths)}")
    print(f"  - Schemas: {len(filtered_schemas)}")
    print(f"  - Tamanho: {Path(output_file).stat().st_size / 1024:.1f} KB")

    # Listar endpoints por módulo
    modules = {}
    for path in bidding_paths.keys():
        if '/tenders' in path:
            modules['Tenders (Editais)'] = modules.get('Tenders (Editais)', 0) + 1
        elif '/proposals' in path:
            modules['Proposals (Propostas)'] = modules.get('Proposals (Propostas)', 0) + 1
        elif '/contracts' in path:
            modules['Contracts (Contratos)'] = modules.get('Contracts (Contratos)', 0) + 1
        elif '/certificates' in path:
            modules['Certificates (Certidões)'] = modules.get('Certificates (Certidões)', 0) + 1
        elif '/documents' in path or '/pncp' in path:
            modules['Documents/PNCP'] = modules.get('Documents/PNCP', 0) + 1

    print(f"\nMódulos Bidding extraídos:")
    for module, count in sorted(modules.items()):
        print(f"  - {module}: {count} endpoints")

    return bidding_spec

if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / 'openapi_full.json'
    output_file = base_dir / 'openapi-bidding.json'

    if not input_file.exists():
        print(f"ERRO: Arquivo {input_file} não encontrado!")
        print("Execute: curl -s http://localhost:8080/openapi.json > openapi_full.json")
        sys.exit(1)

    extract_bidding_spec(str(input_file), str(output_file))
    print("\n✓ OpenAPI spec BIDDING extraído com sucesso!")
