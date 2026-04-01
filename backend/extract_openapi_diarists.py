"""
Script para extrair OpenAPI spec do módulo DIARISTS.
"""

import json

from fastapi import FastAPI

# Criar app FastAPI minimal
app = FastAPI(
    title="Conecta PRO - Diarists Module API",
    version="1.0.0",
    description="API para gestão de diaristas",
)

# Importar routers DIARISTS
try:
    from modules.operacional.diaristas.controllers import (
        fiscal_router,
        notificacao_router,
    )
    from modules.operacional.diaristas.controllers import (
        router as diarist_router,
    )

    # Registrar routers
    app.include_router(diarist_router, prefix="/api/v1/operacional/diaristas", tags=["Operacional - Diaristas"])
    app.include_router(
        notificacao_router,
        prefix="/api/v1/operacional/diaristas/notificacoes",
        tags=["Operacional - Diaristas Notificações"],
    )
    app.include_router(
        fiscal_router, prefix="/api/v1/operacional/diaristas/fiscal", tags=["Operacional - Diaristas Fiscal"]
    )

    # Gerar OpenAPI spec
    openapi_spec = app.openapi()

    # Salvar em arquivo
    output_path = "/opt/conecta-pro/backend/openapi-diarists.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

    print(f"✅ OpenAPI spec gerado com sucesso: {output_path}")

    # Estatísticas
    total_paths = len(openapi_spec.get("paths", {}))
    total_schemas = len(openapi_spec.get("components", {}).get("schemas", {}))

    print("\n📊 Estatísticas:")
    print(f"   - Total de endpoints: {total_paths}")
    print(f"   - Total de schemas: {total_schemas}")
    print("\n📝 Endpoints encontrados:")
    for path in sorted(openapi_spec.get("paths", {}).keys()):
        methods = list(openapi_spec["paths"][path].keys())
        print(f"   {path} [{', '.join(m.upper() for m in methods)}]")

except Exception as e:
    print(f"❌ Erro ao extrair OpenAPI spec: {e}")
    import traceback

    traceback.print_exc()
    exit(1)
