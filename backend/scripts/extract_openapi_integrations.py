"""
Script para extrair OpenAPI spec do módulo INTEGRATIONS
Inclui: Core, Connectors, Solides, Banking, WhatsApp, Email
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Importa os routers do módulo integrations
from modules.integrations.controllers import (
    integration_router,
    connector_router,
    solides_router,
)

def create_integrations_app() -> FastAPI:
    """Cria app FastAPI com routers de integrations."""
    app = FastAPI(
        title="Conecta PRO - Integrations API",
        description="API de Integrações, Webhooks, Banking, WhatsApp, Email",
        version="1.0.0",
    )

    # Registra routers com prefixo /api/v1/integrations
    app.include_router(integration_router, prefix="/api/v1")
    app.include_router(connector_router, prefix="/api/v1/integrations")
    app.include_router(solides_router, prefix="/api/v1/integrations")

    return app

def extract_openapi():
    """Extrai OpenAPI spec do módulo integrations."""
    print("🔍 Extraindo OpenAPI spec do módulo INTEGRATIONS...")

    app = create_integrations_app()

    # Gera OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Conta endpoints
    paths = openapi_schema.get("paths", {})
    endpoint_count = sum(len(methods) for methods in paths.values())

    print(f"✅ {len(paths)} paths encontrados")
    print(f"✅ {endpoint_count} endpoints encontrados")

    # Salva arquivo
    output_file = backend_dir / "openapi-integrations.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"📝 OpenAPI spec salvo em: {output_file}")

    # Mostra estatísticas
    print("\n📊 Estatísticas:")
    print(f"  - Schemas: {len(openapi_schema.get('components', {}).get('schemas', {}))}")
    print(f"  - Paths: {len(paths)}")
    print(f"  - Endpoints: {endpoint_count}")

    # Lista alguns endpoints principais
    print("\n📋 Exemplos de endpoints:")
    for path, methods in list(paths.items())[:10]:
        for method in methods.keys():
            if method != "parameters":
                print(f"  - {method.upper()} {path}")

    if len(paths) > 10:
        print(f"  ... e mais {len(paths) - 10} paths")

    return output_file

if __name__ == "__main__":
    try:
        output_file = extract_openapi()
        print(f"\n✅ Extração concluída com sucesso!")
        print(f"📁 Arquivo: {output_file}")
    except Exception as e:
        print(f"\n❌ Erro na extração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
