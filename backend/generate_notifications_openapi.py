"""Script para gerar OpenAPI spec do módulo Notifications."""

import json

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Criar app temporário
app = FastAPI(
    title="Conecta PRO - Notifications Module",
    version="2.0.0",
    description="API de Notificações Multi-Canal com IA",
)

# Importar routers
try:
    from modules.notifications.controllers.intelligent_notification_controller import router as intelligent_router
    from modules.notifications.controllers.notification_controller import router as notification_router
    from modules.notifications.push.controllers.push_controller import router as push_router

    # Adicionar routers (sem duplicar prefix já definido nos routers)
    app.include_router(notification_router, prefix="/api/v1", tags=["Notifications"])
    app.include_router(intelligent_router, prefix="/api/v1/notifications", tags=["Intelligent Notifications"])
    app.include_router(push_router, prefix="/api/v1/notifications", tags=["Push Notifications"])

    # Gerar OpenAPI
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Adicionar info de servers
    openapi_schema["servers"] = [
        {"url": "http://localhost:8080", "description": "Development"},
        {"url": "https://api.conectapro.com.br", "description": "Production"},
    ]

    # Salvar
    with open("openapi-notifications.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print("✅ OpenAPI spec gerado com sucesso!")
    print(f"📊 Total de endpoints: {len(openapi_schema['paths'])}")
    print(f"🏷️  Tags: {[t['name'] for t in openapi_schema.get('tags', [])]}")

except Exception as e:
    print(f"❌ Erro ao gerar OpenAPI: {e}")
    import traceback

    traceback.print_exc()
