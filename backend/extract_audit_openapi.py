#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo AUDIT
Sprint 33: Auditoria e Compliance
"""

import json
import sys
from pathlib import Path

# Ajustar sys.path para importar módulos do backend
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from fastapi.openapi.utils import get_openapi
    from main_production import app

    # Gerar schema OpenAPI completo
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    # Filtrar apenas rotas do módulo audit
    audit_paths = {
        k: v for k, v in openapi_schema['paths'].items()
        if k.startswith('/api/v1/audit')
    }

    # Extrair componentes/schemas usados no módulo audit
    if not audit_paths:
        print("ERRO: Nenhum endpoint /api/v1/audit encontrado!", file=sys.stderr)
        sys.exit(1)

    # Criar schema filtrado
    audit_schema = {
        'openapi': openapi_schema['openapi'],
        'info': {
            'title': 'Conecta PRO - Módulo AUDIT',
            'description': 'API de Auditoria e Compliance - 31 endpoints',
            'version': openapi_schema['info']['version']
        },
        'paths': audit_paths,
        'components': openapi_schema.get('components', {}),
        'tags': [
            {
                'name': 'Auditoria e Compliance',
                'description': 'Endpoints de auditoria, logs, compliance e retenção de dados'
            }
        ]
    }

    # Salvar em arquivo
    output_file = backend_dir / 'openapi-audit.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(audit_schema, f, indent=2, ensure_ascii=False)

    # Estatísticas
    total_endpoints = len(audit_paths)
    methods = {}
    for path, operations in audit_paths.items():
        for method in operations.keys():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                methods[method.upper()] = methods.get(method.upper(), 0) + 1

    print(f"✓ OpenAPI extraído com sucesso!")
    print(f"  Arquivo: {output_file}")
    print(f"  Endpoints: {total_endpoints}")
    print(f"  Métodos: {', '.join(f'{m}={c}' for m, c in sorted(methods.items()))}")

    # Listar endpoints
    print("\n  Rotas extraídas:")
    for path in sorted(audit_paths.keys()):
        print(f"    - {path}")

except ImportError as e:
    print(f"ERRO: Falha ao importar módulos: {e}", file=sys.stderr)
    print("Execute este script do diretório /opt/conecta-pro/backend", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERRO: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
