#!/usr/bin/env python3
"""
Script direto para extrair OpenAPI spec do módulo CONFIG
Extrai apenas o router de config sem carregar outros módulos
"""

import json
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI


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

    # Importar apenas o router de config
    try:
        from modules.config.controllers import router as config_router

        # Incluir router com prefix correto
        app.include_router(config_router, prefix="/api/v1", tags=["Config"])

    except Exception as e:
        print(f"❌ Erro ao importar router de config: {e}")
        sys.exit(1)

    # Gerar schema OpenAPI completo
    full_schema = app.openapi()

    # Ajustar info
    full_schema["info"] = {
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
    }

    # Adicionar servers
    full_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Desenvolvimento Local"},
        {"url": "https://api.conectapro.com.br", "description": "Produção"},
    ]

    # Salvar arquivo
    output_file = Path(__file__).parent / "openapi-config.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(full_schema, f, indent=2, ensure_ascii=False)

    print("✅ OpenAPI spec extraído com sucesso!")
    print(f"📄 Arquivo: {output_file}")
    print(f"📊 Endpoints encontrados: {len(full_schema.get('paths', {}))}")
    print(f"📦 Schemas extraídos: {len(full_schema.get('components', {}).get('schemas', {}))}")

    # Estatísticas por tipo de endpoint
    methods_count = {}
    for _path, methods in full_schema.get("paths", {}).items():
        for method in methods.keys():
            if method in ["get", "post", "put", "patch", "delete"]:
                methods_count[method.upper()] = methods_count.get(method.upper(), 0) + 1

    print("\n📈 Distribuição por método HTTP:")
    for method, count in sorted(methods_count.items()):
        print(f"   {method}: {count}")

    # Listar endpoints
    print("\n📋 Endpoints extraídos:")
    for path in sorted(full_schema.get("paths", {}).keys()):
        methods = list(full_schema["paths"][path].keys())
        methods = [m.upper() for m in methods if m in ["get", "post", "put", "patch", "delete"]]
        print(f"   {', '.join(methods):20} {path}")


if __name__ == "__main__":
    extract_config_openapi()
