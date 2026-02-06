#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo CAMPO
Gera campo.openapi.json com todos os 147 endpoints
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Import CAMPO routers
from modules.campo.controllers import (
    campo_service_router,
    access_log_router,
    occurrence_router,
    equipment_status_router,
    sync_router,
    security_audit_router,
    monitoring_router,
    ordem_servico_router,
    visita_router,
    checklist_router,
    roteirizacao_router,
    estoque_router
)

def extract_campo_openapi():
    """Extrai OpenAPI spec completo do módulo CAMPO."""

    # Create temporary FastAPI app
    app = FastAPI(
        title="Conecta PRO - CAMPO API",
        description="API completa do módulo CAMPO - Serviço de Campo",
        version="3.0.0",
    )

    # Include all CAMPO routers
    routers = [
        (campo_service_router, "/api/v1/campo", ["Campo Service"]),
        (access_log_router, "/api/v1/campo/guardian/access-logs", ["Guardian Access Logs"]),
        (occurrence_router, "/api/v1/campo/guardian/occurrences", ["Guardian Occurrences"]),
        (equipment_status_router, "/api/v1/campo/guardian/equipment-status", ["Guardian Equipment"]),
        (sync_router, "/api/v1/campo/guardian/sync", ["Guardian Sync"]),
        (security_audit_router, "/api/v1/campo/security-audit", ["Security Audit"]),
        (monitoring_router, "/api/v1/campo/monitoring", ["Monitoring"]),
        (ordem_servico_router, "/api/v1/campo/ordens-servico", ["Ordens de Serviço"]),
        (visita_router, "/api/v1/campo/visitas", ["Visitas"]),
        (checklist_router, "/api/v1/campo/checklists", ["Checklists"]),
        (roteirizacao_router, "/api/v1/campo/roteirizacao", ["Roteirização"]),
        (estoque_router, "/api/v1/campo/estoque", ["Estoque"]),
    ]

    for router, prefix, tags in routers:
        app.include_router(router, prefix=prefix, tags=tags)

    # Generate OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add servers
    openapi_schema["servers"] = [
        {"url": "https://api.conectapro.com.br", "description": "Produção"},
        {"url": "https://staging-api.conectapro.com.br", "description": "Staging"},
        {"url": "http://localhost:8000", "description": "Desenvolvimento"},
    ]

    # Count endpoints
    total_endpoints = sum(len(methods) for methods in openapi_schema.get("paths", {}).values())
    print(f"✅ OpenAPI spec gerado com sucesso!")
    print(f"📊 Total de paths: {len(openapi_schema.get('paths', {}))}")
    print(f"📊 Total de endpoints: {total_endpoints}")

    # Save to file
    output_path = Path(__file__).parent.parent / "campo.openapi.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"💾 Arquivo salvo: {output_path}")

    # List all paths
    print("\n📋 Endpoints por categoria:")
    paths = openapi_schema.get("paths", {})

    categories = {
        "Campo Service": [],
        "Ordens de Serviço": [],
        "Visitas": [],
        "Checklists": [],
        "Roteirização": [],
        "Estoque": [],
        "Guardian Access Logs": [],
        "Guardian Occurrences": [],
        "Guardian Equipment": [],
        "Guardian Sync": [],
        "Security Audit": [],
        "Monitoring": [],
    }

    for path, methods in sorted(paths.items()):
        # Categorize by path
        if "/ordens-servico" in path:
            categories["Ordens de Serviço"].append((path, list(methods.keys())))
        elif "/visitas" in path:
            categories["Visitas"].append((path, list(methods.keys())))
        elif "/checklists" in path:
            categories["Checklists"].append((path, list(methods.keys())))
        elif "/roteirizacao" in path:
            categories["Roteirização"].append((path, list(methods.keys())))
        elif "/estoque" in path:
            categories["Estoque"].append((path, list(methods.keys())))
        elif "/access-logs" in path:
            categories["Guardian Access Logs"].append((path, list(methods.keys())))
        elif "/occurrences" in path:
            categories["Guardian Occurrences"].append((path, list(methods.keys())))
        elif "/equipment-status" in path:
            categories["Guardian Equipment"].append((path, list(methods.keys())))
        elif "/sync" in path:
            categories["Guardian Sync"].append((path, list(methods.keys())))
        elif "/security-audit" in path:
            categories["Security Audit"].append((path, list(methods.keys())))
        elif "/monitoring" in path:
            categories["Monitoring"].append((path, list(methods.keys())))
        else:
            categories["Campo Service"].append((path, list(methods.keys())))

    for category, endpoints in categories.items():
        if endpoints:
            print(f"\n  {category} ({len(endpoints)} paths):")
            for path, methods in endpoints[:3]:  # Show first 3
                print(f"    {path}: {methods}")
            if len(endpoints) > 3:
                print(f"    ... e mais {len(endpoints) - 3} endpoints")

    return openapi_schema

if __name__ == "__main__":
    try:
        extract_campo_openapi()
        print("\n✅ Script executado com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
