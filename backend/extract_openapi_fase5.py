"""
Script para extrair OpenAPI spec completo do módulo FASE5.
Extrai endpoints de CCT Compliance, Email Intelligence e Quality Framework.
"""
import json

from fastapi import FastAPI

# Criar app FastAPI minimal
app = FastAPI(
    title="Conecta PRO - Fase 5 Module API",
    version="1.0.0",
    description="""
    API completa para Fase 5 - Grand Finale.

    Funcionalidades:
    - CCT Compliance: Validação de cargos, salários e propostas comerciais (SINDCOND 2026)
    - Email Intelligence: Análise e classificação de emails com IA
    - Quality Framework: Validação de qualidade do sistema (target 99+/100)

    Total: 11 endpoints organizados em:
    - 6 endpoints CCT Compliance
    - 2 endpoints Email Intelligence
    - 1 endpoint Quality Framework
    - 2 endpoints System Status
    """,
)

# Importar router FASE5
try:
    from modules.fase5.controllers.fase5_controller import router as fase5_router

    # Registrar router
    app.include_router(
        fase5_router,
        prefix="/api/v1",
        tags=["Fase 5 - Grand Finale"]
    )

    # Gerar OpenAPI spec
    openapi_spec = app.openapi()

    # Salvar em arquivo no backend
    output_path_backend = "/opt/conecta-pro/backend/openapi-fase5.json"
    with open(output_path_backend, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

    # Salvar também no frontend
    output_path_frontend = "/opt/conecta-pro/frontend/openapi/fase5-openapi.json"
    with open(output_path_frontend, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

    print(f"✅ OpenAPI spec gerado com sucesso!")
    print(f"   📁 Backend:  {output_path_backend}")
    print(f"   📁 Frontend: {output_path_frontend}")

    # Estatísticas
    total_paths = len(openapi_spec.get("paths", {}))
    total_schemas = len(openapi_spec.get("components", {}).get("schemas", {}))

    print(f"\n📊 Estatísticas FASE5:")
    print(f"   - Total de endpoints: {total_paths}")
    print(f"   - Total de schemas: {total_schemas}")

    # Contar por tag
    tags_count = {}
    for path, methods in openapi_spec.get("paths", {}).items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                for tag in details.get('tags', []):
                    tags_count[tag] = tags_count.get(tag, 0) + 1

    print(f"\n📝 Endpoints por controller:")
    for tag, count in sorted(tags_count.items()):
        print(f"   {tag}: {count} endpoints")

    print(f"\n📋 Lista de endpoints:")
    for path in sorted(openapi_spec.get("paths", {}).keys()):
        methods = list(openapi_spec["paths"][path].keys())
        print(f"   {path} [{', '.join(m.upper() for m in methods if m != 'parameters')}]")

except Exception as e:
    print(f"❌ Erro ao extrair OpenAPI spec: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
