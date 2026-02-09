#!/usr/bin/env python3
"""
Script para extrair OpenAPI spec do módulo CONFIG
Extrai apenas os endpoints relacionados a configurações, tenants, feature flags
"""

import json
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI

from api.v1 import router as api_router


def extract_config_openapi():
    """Extrai OpenAPI spec do módulo CONFIG."""

    # Criar app temporária
    app = FastAPI(
        title="Conecta PRO - CONFIG Module",
        description="API de Configurações, Multi-tenant, Feature Flags e Templates",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
    )

    # Incluir apenas o router da API v1
    app.include_router(api_router)

    # Gerar schema OpenAPI completo
    full_schema = app.openapi()

    # Filtrar apenas endpoints do módulo CONFIG
    config_paths = {}

    for path, methods in full_schema.get("paths", {}).items():
        # Verificar se o path é do módulo config
        if "/api/v1/config" in path:
            config_paths[path] = methods

    # Extrair schemas relacionados
    config_schemas = {}
    all_schemas = full_schema.get("components", {}).get("schemas", {})

    # Lista de schemas do módulo config
    config_schema_prefixes = [
        "Tenant",
        "SystemConfig",
        "FeatureFlag",
        "NotificationTemplate",
        "ConfigDashboard",
        "HTTPValidationError",
        "ValidationError",
    ]

    for schema_name, schema_def in all_schemas.items():
        # Incluir schemas que começam com prefixos do config
        if any(schema_name.startswith(prefix) for prefix in config_schema_prefixes):
            config_schemas[schema_name] = schema_def

    # Montar OpenAPI spec filtrado
    config_spec = {
        "openapi": full_schema["openapi"],
        "info": {
            "title": "Conecta PRO - CONFIG Module API",
            "description": """
API do módulo de Configurações do Conecta PRO.

## Recursos

### Tenants (Multi-tenant)
- Gerenciamento de tenants (condomínios/clientes)
- Controle de planos e status
- Ativação/Suspensão/Cancelamento
- Conversão de trial
- Gestão de features por tenant

### Tenant Settings
- Configurações específicas por tenant
- Valores customizáveis
- Reset de configurações
- Update de valores individuais

### System Config
- Configurações globais do sistema
- Parâmetros de aplicação
- Configurações compartilhadas

### Feature Flags
- Controle de features
- Gradual rollout
- Toggle por tenant
- Avaliação de flags
- Controle percentual

### Notification Templates
- Templates de notificação
- Renderização com variáveis
- Ativação/Desativação
- Clonagem de templates
- Múltiplos canais (email, SMS, push)

### Dashboards
- Dashboard geral de configurações
- Dashboard por tenant
- Métricas e estatísticas
            """.strip(),
            "version": "1.0.0",
        },
        "servers": [
            {"url": "http://localhost:8000", "description": "Desenvolvimento Local"},
            {"url": "https://api.conectapro.com.br", "description": "Produção"},
        ],
        "paths": config_paths,
        "components": {
            "schemas": config_schemas,
            "securitySchemes": full_schema.get("components", {}).get("securitySchemes", {}),
        },
        "tags": [{"name": "Config", "description": "Configurações, Multi-tenant, Feature Flags e Templates"}],
    }

    # Salvar arquivo
    output_file = Path(__file__).parent / "openapi-config.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(config_spec, f, indent=2, ensure_ascii=False)

    print("✅ OpenAPI spec extraído com sucesso!")
    print(f"📄 Arquivo: {output_file}")
    print(f"📊 Endpoints encontrados: {len(config_paths)}")
    print(f"📦 Schemas extraídos: {len(config_schemas)}")

    # Estatísticas por tipo de endpoint
    methods_count = {}
    for _path, methods in config_paths.items():
        for method in methods.keys():
            if method in ["get", "post", "put", "patch", "delete"]:
                methods_count[method.upper()] = methods_count.get(method.upper(), 0) + 1

    print("\n📈 Distribuição por método HTTP:")
    for method, count in sorted(methods_count.items()):
        print(f"   {method}: {count}")


if __name__ == "__main__":
    extract_config_openapi()
