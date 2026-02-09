"""
Script para extrair OpenAPI spec do módulo GED (Gestão Eletrônica de Documentos).
"""

import json

from fastapi import FastAPI

# Criar app FastAPI minimal
app = FastAPI(
    title="Conecta PRO - GED Module API",
    version="1.0.0",
    description="""
    API completa para Gestão Eletrônica de Documentos (GED).

    Funcionalidades:
    - Gestão de pastas hierárquicas
    - Upload e controle de documentos
    - Controle de versões
    - Compartilhamento seguro com links e permissões
    - Sistema de tags e categorização
    - Assinaturas digitais e workflow
    - Classificação automática com IA
    - OCR e extração de dados
    - Estatísticas e relatórios

    Total: 133 endpoints organizados em 7 controllers
    """,
)

# Importar routers GED
try:
    from modules.ged.controllers import (
        document_router,
        folder_router,
        share_router,
        signature_router,
        stats_router,
        tag_router,
        version_router,
    )

    # Registrar routers
    app.include_router(folder_router, prefix="/api/v1/ged", tags=["GED - Pastas"])
    app.include_router(document_router, prefix="/api/v1/ged", tags=["GED - Documentos"])
    app.include_router(version_router, prefix="/api/v1/ged", tags=["GED - Versões"])
    app.include_router(share_router, prefix="/api/v1/ged", tags=["GED - Compartilhamento"])
    app.include_router(tag_router, prefix="/api/v1/ged", tags=["GED - Tags"])
    app.include_router(signature_router, prefix="/api/v1/ged", tags=["GED - Assinaturas"])
    app.include_router(stats_router, prefix="/api/v1/ged", tags=["GED - Estatísticas"])

    # Gerar OpenAPI spec
    openapi_spec = app.openapi()

    # Salvar em arquivo no backend
    output_path_backend = "/opt/conecta-pro/backend/openapi-ged.json"
    with open(output_path_backend, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

    # Salvar também no frontend
    output_path_frontend = "/opt/conecta-pro/frontend/openapi/ged-openapi.json"
    with open(output_path_frontend, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

    print("✅ OpenAPI spec gerado com sucesso!")
    print(f"   📁 Backend:  {output_path_backend}")
    print(f"   📁 Frontend: {output_path_frontend}")

    # Estatísticas
    total_paths = len(openapi_spec.get("paths", {}))
    total_schemas = len(openapi_spec.get("components", {}).get("schemas", {}))

    print("\n📊 Estatísticas GED:")
    print(f"   - Total de endpoints: {total_paths}")
    print(f"   - Total de schemas: {total_schemas}")

    # Contar por tag
    tags_count = {}
    for _path, methods in openapi_spec.get("paths", {}).items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                for tag in details.get("tags", []):
                    tags_count[tag] = tags_count.get(tag, 0) + 1

    print("\n📝 Endpoints por controller:")
    for tag, count in sorted(tags_count.items()):
        print(f"   {tag}: {count} endpoints")

    print("\n📋 Lista de endpoints:")
    for path in sorted(openapi_spec.get("paths", {}).keys()):
        methods = list(openapi_spec["paths"][path].keys())
        print(f"   {path} [{', '.join(m.upper() for m in methods if m != 'parameters')}]")

except Exception as e:
    print(f"❌ Erro ao extrair OpenAPI spec: {e}")
    import traceback

    traceback.print_exc()
    exit(1)
