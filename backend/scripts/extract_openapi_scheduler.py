#!/usr/bin/env python3
"""Extrator OpenAPI - Módulo SCHEDULER.

Sprint 35 - Task Scheduler.

Extrai spec OpenAPI do módulo scheduler com 26 endpoints:
- Tasks (9 endpoints)
- Executions (4 endpoints)
- Queue (4 endpoints)
- Workers (3 endpoints)
- Locks (4 endpoints)
- Operations (2 endpoints)
"""

import json
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from modules.scheduler.controllers.scheduler_controller import router as scheduler_router


def extract_scheduler_openapi():
    """Extrai OpenAPI spec do módulo scheduler."""
    # Criar app temporária
    app = FastAPI(
        title="Conecta PRO - Scheduler API",
        description="API de Agendamento e Background Jobs",
        version="1.0.0",
    )

    # Registrar router scheduler
    app.include_router(scheduler_router, prefix="/api/v1")

    # Gerar OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Salvar spec
    output_path = Path(__file__).parent.parent / "openapi-scheduler.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    # Estatísticas
    total_endpoints = len(openapi_schema.get("paths", {}))
    total_schemas = len(openapi_schema.get("components", {}).get("schemas", {}))

    print("✅ OpenAPI Scheduler extraído com sucesso!")
    print(f"   • Endpoints: {total_endpoints}")
    print(f"   • Schemas: {total_schemas}")
    print(f"   • Arquivo: {output_path}")

    # Detalhar endpoints por categoria
    endpoints_by_tag = {}
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, spec in methods.items():
            if method in ["get", "post", "put", "patch", "delete"]:
                tags = spec.get("tags", ["Scheduler"])
                for tag in tags:
                    if tag not in endpoints_by_tag:
                        endpoints_by_tag[tag] = []
                    endpoints_by_tag[tag].append(f"{method.upper()} {path}")

    print("\n📋 Endpoints por categoria:")
    for tag, endpoints in sorted(endpoints_by_tag.items()):
        print(f"   {tag}: {len(endpoints)} endpoints")

    return output_path


if __name__ == "__main__":
    try:
        output = extract_scheduler_openapi()
        print("\n🎯 Próximos passos:")
        print("   1. Copiar para frontend")
        print("   2. Criar orval.config.scheduler.ts")
        print("   3. npm run orval:scheduler")
    except Exception as e:
        print(f"❌ Erro ao extrair OpenAPI: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
