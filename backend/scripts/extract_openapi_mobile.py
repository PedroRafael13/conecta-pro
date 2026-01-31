#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo MOBILE.

Extrai 17 endpoints mobile:
- Health & Config (2)
- Dashboard (1)
- Sync Operations (3)
- Offline Data (1)
- Batch Operations (1)
- Device Registration (2)
- Push Notifications (7)

Uso:
    python scripts/extract_openapi_mobile.py
"""

import json
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))


def extract_mobile_openapi():
    """Extrai especificação OpenAPI do módulo MOBILE."""

    print("Extraindo OpenAPI do módulo MOBILE...")

    # Import dentro da função para evitar erros de inicialização
    try:
        from fastapi.openapi.utils import get_openapi
        from main import app
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        raise

    # Gerar schema OpenAPI completo com tratamento de erros
    try:
        openapi_schema = get_openapi(
            title=app.title or "Conecta PRO API",
            version=app.version or "1.0.0",
            routes=app.routes,
        )
    except Exception as e:
        print(f"⚠️  Erro ao gerar OpenAPI completo, tentando alternativa: {e}")
        # Alternativa: gerar schema vazio e popular manualmente
        openapi_schema = {
            'openapi': '3.1.0',
            'info': {'title': 'Conecta PRO API', 'version': '1.0.0'},
            'paths': {},
            'components': {'schemas': {}, 'securitySchemes': {}}
        }

    # Filtrar apenas paths /mobile
    mobile_paths = {
        path: spec
        for path, spec in openapi_schema.get('paths', {}).items()
        if '/mobile' in path.lower()
    }

    print(f"✓ Encontrados {len(mobile_paths)} endpoints mobile")

    # Identificar schemas relevantes
    all_schemas = openapi_schema.get('components', {}).get('schemas', {})

    # Keywords para identificar schemas mobile
    mobile_keywords = [
        'Mobile', 'Device', 'Batch', 'Offline', 'Sync',
        'Push', 'Notification', 'QuickAction', 'RecentActivity',
        'DashboardSummary', 'HealthCheck', 'BroadcastNotification'
    ]

    mobile_schemas = {
        name: schema
        for name, schema in all_schemas.items()
        if any(keyword in name for keyword in mobile_keywords)
    }

    print(f"✓ Encontrados {len(mobile_schemas)} schemas mobile")

    # Construir OpenAPI spec mobile
    mobile_openapi = {
        'openapi': openapi_schema.get('openapi', '3.1.0'),
        'info': {
            'title': 'Conecta PRO - Mobile API',
            'version': openapi_schema.get('info', {}).get('version', '1.0.0'),
            'description': 'APIs nativas para dispositivos móveis com sync offline e push notifications'
        },
        'paths': mobile_paths,
        'components': {
            'schemas': mobile_schemas,
            'securitySchemes': openapi_schema.get('components', {}).get('securitySchemes', {})
        },
        'security': openapi_schema.get('security', [])
    }

    # Salvar arquivo
    output_file = Path(__file__).parent.parent / 'openapi-mobile.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mobile_openapi, f, indent=2, ensure_ascii=False)

    print(f"✓ OpenAPI salvo em: {output_file}")
    print(f"✓ Tamanho: {output_file.stat().st_size / 1024:.1f} KB")

    # Listar endpoints
    if mobile_paths:
        print("\nEndpoints extraídos:")
        for i, path in enumerate(sorted(mobile_paths.keys()), 1):
            methods = list(mobile_paths[path].keys())
            methods = [m.upper() for m in methods if m != 'parameters']
            print(f"  {i:2d}. {', '.join(methods):8s} {path}")
    else:
        print("\n⚠️  Nenhum endpoint mobile encontrado!")

    return mobile_openapi


if __name__ == '__main__':
    try:
        spec = extract_mobile_openapi()
        print("\n✅ Extração concluída com sucesso!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro na extração: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
