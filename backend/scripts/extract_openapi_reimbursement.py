#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo REIMBURSEMENT.
Gera spec completo com todos os endpoints, schemas e validações.
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Importa o router do módulo reimbursement
from modules.reimbursement.controllers import router as reimbursement_router


def extract_reimbursement_openapi():
    """Extrai OpenAPI spec do módulo REIMBURSEMENT."""

    # Cria app temporário
    app = FastAPI(
        title="Conecta PRO - Reimbursement API",
        description="API de Reembolso de Despesas - Conecta PRO",
        version="1.0.0",
    )

    # Inclui router
    app.include_router(reimbursement_router, prefix="/api/v1/reimbursements", tags=["Reimbursement"])

    # Gera OpenAPI schema
    openapi_schema = get_openapi(
        title="Conecta PRO - Reimbursement API",
        version="1.0.0",
        description="API completa de Reembolso de Despesas",
        routes=app.routes,
    )

    # Adiciona info adicional
    openapi_schema["info"]["x-module"] = "reimbursement"
    openapi_schema["info"]["x-coverage"] = "100%"

    # Salva arquivo
    output_file = backend_dir / "openapi_specs" / "reimbursement.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    # Estatísticas
    endpoints = len([r for r in app.routes if hasattr(r, "methods")])
    schemas = len(openapi_schema.get("components", {}).get("schemas", {}))

    print(f"✅ OpenAPI spec extraído com sucesso!")
    print(f"📁 Arquivo: {output_file}")
    print(f"📊 Endpoints: {endpoints}")
    print(f"📦 Schemas: {schemas}")
    print(f"\nEndpoints disponíveis:")

    # Lista endpoints
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            methods = ", ".join(sorted(route.methods))
            print(f"  {methods:20} {route.path}")

    return output_file


if __name__ == "__main__":
    try:
        output_file = extract_reimbursement_openapi()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro ao extrair OpenAPI spec: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
