"""
Script para extrair OpenAPI spec do módulo Analytics.
"""

import json
import sys
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Criar app mínima apenas com routers Analytics
app = FastAPI(
    title="Conecta PRO - Analytics Module",
    version="2.0.0",
    description="Módulo de Analytics, BI e Predictive Analytics com Machine Learning",
)

# Importar routers Analytics
from modules.analytics.controllers import (
    executive_dashboard_router,
    analytics_router
)

# Registrar routers no padrão da API
app.include_router(
    executive_dashboard_router,
    prefix="/api/v1/analytics",
    tags=["Analytics - Executive Dashboard"]
)
app.include_router(
    analytics_router,
    prefix="/api/v1",
    tags=["Analytics - Predictive"]
)

# Gerar OpenAPI spec
openapi_spec = get_openapi(
    title=app.title,
    version=app.version,
    openapi_version=app.openapi_version,
    description=app.description,
    routes=app.routes,
)

# Salvar em arquivo
output_file = backend_path / "openapi_specs" / "analytics_openapi.json"
output_file.parent.mkdir(exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

print(f"OpenAPI spec gerado com sucesso: {output_file}")
print(f"Total de endpoints: {len([r for r in app.routes if hasattr(r, 'methods')])}")
