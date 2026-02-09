#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo WORKFLOWS.

Extrai automaticamente as rotas do módulo automation/workflow
e gera arquivo openapi-workflows.json.
"""

import json
import sys
from pathlib import Path

# Adiciona backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI  # noqa: E402
from fastapi.openapi.utils import get_openapi  # noqa: E402


def extract_workflows_openapi():
    """Extrai OpenAPI spec do módulo WORKFLOWS."""

    print("🔍 Extraindo OpenAPI spec do módulo WORKFLOWS...")

    # Cria app FastAPI temporária
    app = FastAPI(
        title="Conecta PRO - Workflows API",
        description="API de Workflows e Automações",
        version="1.0.0",
    )

    # Importa e registra router de workflows
    try:
        from modules.automation.workflow.controllers.workflow_controller import router  # noqa: E402

        app.include_router(router, prefix="/api/v1/workflows", tags=["Automation - Workflows"])

        print(f"✅ Router importado: {len(router.routes)} rotas encontradas")

    except Exception as e:
        print(f"❌ Erro ao importar router: {e}")
        return None

    # Gera OpenAPI spec
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Adiciona metadata
    openapi_schema["info"]["x-module"] = "workflows"
    openapi_schema["info"]["x-category"] = "automation"
    openapi_schema["info"]["x-generated-at"] = "2026-01-28"

    # Remove servidor base (será configurado no frontend)
    if "servers" in openapi_schema:
        del openapi_schema["servers"]

    return openapi_schema


def save_openapi_spec(spec: dict, output_path: Path):
    """Salva spec OpenAPI em arquivo JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    print(f"✅ OpenAPI spec salvo em: {output_path}")


def main():
    """Função principal."""

    # Extrai spec
    spec = extract_workflows_openapi()

    if not spec:
        print("❌ Falha ao extrair OpenAPI spec")
        sys.exit(1)

    # Salva arquivo
    output_path = backend_path / "openapi-workflows.json"
    save_openapi_spec(spec, output_path)

    # Estatísticas
    paths_count = len(spec.get("paths", {}))
    schemas_count = len(spec.get("components", {}).get("schemas", {}))

    print("\n📊 Estatísticas:")
    print(f"   • Endpoints: {paths_count}")
    print(f"   • Schemas: {schemas_count}")
    print(f"   • Tags: {len(spec.get('tags', []))}")

    print("\n✅ Extração concluída com sucesso!")


if __name__ == "__main__":
    main()
