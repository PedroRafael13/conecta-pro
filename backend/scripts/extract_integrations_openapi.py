#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo Integrations
Sprint 33: Integration Framework
"""

import json
import sys
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from fastapi.openapi.utils import get_openapi  # noqa: E402

from main_production import app  # noqa: E402


def extract_integrations_openapi():
    """Extrai OpenAPI spec apenas do módulo Integrations."""

    # Gerar OpenAPI completo
    openapi_schema = get_openapi(
        title="Conecta Plus API - Integrations Module",
        version="1.0.0",
        description="API de Integrações com sistemas externos (não governamentais)",
        routes=app.routes,
    )

    # Filtrar apenas rotas de integrations
    filtered_paths = {}
    for path, methods in openapi_schema.get("paths", {}).items():
        if "/api/v1/integrations" in path:
            filtered_paths[path] = methods

    openapi_schema["paths"] = filtered_paths

    # Tags relacionadas ao módulo
    integration_tags = [
        "Integrações",
        "Conectores Externos",
        "Solides Integration",
        "Integrations - API Gateway",
        "Integrations - Conectores",
        "Integrations - Sólides RH/DP",
    ]

    # Filtrar tags
    if "tags" in openapi_schema:
        openapi_schema["tags"] = [tag for tag in openapi_schema.get("tags", []) if tag.get("name") in integration_tags]

    # Adicionar info sobre o módulo
    openapi_schema["info"]["x-module"] = "integrations"
    openapi_schema["info"]["x-module-description"] = "Integrações com sistemas externos de terceiros"

    return openapi_schema


if __name__ == "__main__":
    try:
        schema = extract_integrations_openapi()

        # Salvar em arquivo
        output_path = backend_path / "openapi" / "integrations.json"
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

        print(f"✓ OpenAPI spec extraído: {output_path}")
        print(f"✓ Total de endpoints: {len(schema.get('paths', {}))}")
        print(f"✓ Schemas: {len(schema.get('components', {}).get('schemas', {}))}")

    except Exception as e:
        print(f"✗ Erro ao extrair OpenAPI: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
