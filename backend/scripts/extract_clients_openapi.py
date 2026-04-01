#!/usr/bin/env python3
"""
Script de Extração OpenAPI - Módulo CLIENTS
Extrai especificação OpenAPI do módulo de Clientes/Condominios
Sprint 30: 51 endpoints identificados
"""

import json
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import APIRouter, FastAPI  # noqa: E402
from fastapi.openapi.utils import get_openapi  # noqa: E402


def extract_clients_openapi():
    """Extrai OpenAPI spec do módulo CLIENTS"""

    # Criar app FastAPI temporária
    app = FastAPI(
        title="Conecta PRO - Módulo CLIENTS", description="API de Gestão de Clientes e Condomínios", version="1.0.0"
    )

    # Importar apenas o router de clients diretamente
    from modules.clients.controllers import router as client_router  # noqa: E402

    # Criar router v1
    v1_router = APIRouter(prefix="/api/v1")
    v1_router.include_router(client_router, prefix="/clients", tags=["Clients - Cadastro"])

    # Incluir no app
    app.include_router(v1_router)

    # Gerar schema OpenAPI completo
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    return openapi_schema


def main():
    """Main execution"""
    print("=" * 80)
    print("EXTRAÇÃO OPENAPI - MÓDULO CLIENTS")
    print("=" * 80)
    print()

    try:
        # Extrair schema
        print("[1/2] Extraindo OpenAPI schema do módulo CLIENTS...")
        schema = extract_clients_openapi()

        endpoint_count = len(schema.get("paths", {}))
        print(f"✓ {endpoint_count} endpoints extraídos")
        print()

        # Salvar arquivo
        output_file = backend_dir / "openapi-clients.json"
        print(f"[2/2] Salvando em: {output_file}")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

        print("✓ Arquivo salvo com sucesso")
        print()

        # Resumo
        print("=" * 80)
        print("RESUMO DA EXTRAÇÃO")
        print("=" * 80)
        print(f"Total de endpoints: {endpoint_count}")
        print(f"Arquivo gerado: {output_file.name}")
        print(f"Tamanho: {output_file.stat().st_size / 1024:.1f} KB")
        print()
        print("Próximo passo:")
        print(f"  cp {output_file} /opt/conecta-pro/frontend/openapi-clients.json")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"✗ ERRO: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
