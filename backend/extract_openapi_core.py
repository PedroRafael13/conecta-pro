#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec completo do módulo CORE.
Extrai endpoints de autenticação e gerenciamento de usuários.
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Import CORE routers directly (bypass __init__.py to avoid circular imports)
import importlib.util

def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

auth_module = load_module_from_file("auth", Path(__file__).parent / "api/v1/endpoints/auth.py")
users_module = load_module_from_file("users", Path(__file__).parent / "api/v1/endpoints/users.py")

auth_router = auth_module.router
users_router = users_module.router


def extract_core_openapi():
    """Extrai OpenAPI spec completo do módulo CORE."""

    # Create temporary FastAPI app
    app = FastAPI(
        title="Conecta PRO - Core Module",
        description="Módulo Core - Autenticação, Usuários e Permissões",
        version="1.0.0",
    )

    # Add CORE routers
    print("Registrando routers do módulo CORE...")

    # Authentication (Login, Register, Refresh, Google OAuth)
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

    # User Management (List, Create, Update, Delete)
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])

    # Generate OpenAPI schema
    print("Gerando OpenAPI schema...")
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Count endpoints
    endpoint_count = len([route for route in app.routes if hasattr(route, 'methods')])
    print(f"\n✅ Total de endpoints extraídos: {endpoint_count}")

    # Count by tag
    print("\n📊 Endpoints por submódulo:")
    paths = openapi_schema.get('paths', {})
    tag_counts = {}
    for path_data in paths.values():
        for method_data in path_data.values():
            if isinstance(method_data, dict) and 'tags' in method_data:
                for tag in method_data['tags']:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

    for tag, count in sorted(tag_counts.items()):
        print(f"  - {tag}: {count} endpoints")

    # Save to file
    output_file = Path(__file__).parent / "openapi-core.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"\n✅ OpenAPI spec salvo em: {output_file}")
    print(f"📦 Tamanho: {output_file.stat().st_size / 1024:.1f} KB")

    return openapi_schema


if __name__ == "__main__":
    try:
        extract_core_openapi()
        print("\n✅ Extração concluída com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao extrair OpenAPI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
