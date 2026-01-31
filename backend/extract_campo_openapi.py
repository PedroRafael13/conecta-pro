#!/usr/bin/env python3
"""
Script de extração OpenAPI para módulo CAMPO v3.0.0
Gera especificação completa com 13 controllers
"""

import json
import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# Import dos routers do módulo CAMPO
from modules.campo.controllers import (
    # Legacy/Guardian controllers
    access_log_router,
    equipment_status_router,
    occurrence_router,
    sync_router,
    # Cyber Security
    security_audit_router,
    ssh_gateway_router,
    campo_service_router,
    # Monitoring
    monitoring_router,
    # Novos CAMPO controllers
    ordem_servico_router,
    visita_router,
    checklist_router,
    roteirizacao_router,
    estoque_router,
)

def create_campo_app() -> FastAPI:
    """Cria app FastAPI temporário apenas para extração OpenAPI."""

    app = FastAPI(
        title="Conecta PRO - Módulo CAMPO",
        description="""
Sistema de Serviço de Campo - Gestão de Equipes Externas, Visitas, OS e Checklists

## Componentes

### Ordens de Serviço (OS)
- Criação, agendamento e execução de OS
- Controle de materiais e tempo
- Avaliação e relatórios

### Visitas Técnicas/Comerciais
- Agendamento e check-in/out
- Conversão de visitas em OS
- Histórico e relatórios

### Checklists Dinâmicos
- Templates personalizáveis
- Preenchimento offline-first
- Validação e alertas automáticos

### Roteirização Inteligente
- Otimização de rotas
- Reotimização em tempo real
- Análise de equipes

### Estoque Campo
- Requisição de materiais
- Baixa automática
- Alertas de estoque

### Monitoramento Equipamentos
- Status em tempo real
- Alertas e relatórios
- Histórico de eventos

### Segurança e Auditoria
- Logs de acesso
- Auditoria de segurança
- SSH Gateway para acesso remoto

### Sincronização Externa
- Integração com sistemas externos
- Logs de sincronização
        """,
        version="3.0.0",
        openapi_tags=[
            {"name": "Access", "description": "Logs de acesso e operações"},
            {"name": "Equip", "description": "Status de equipamentos"},
            {"name": "Events", "description": "Ocorrências e eventos"},
            {"name": "Physical Sync", "description": "Sincronização externa"},
            {"name": "Cyber", "description": "Auditoria de segurança cibernética"},
            {"name": "SSH", "description": "Gateway SSH para acesso remoto"},
            {"name": "Campo", "description": "Serviços de campo (legacy)"},
            {"name": "Monitoring", "description": "Monitoramento de sistemas"},
            {"name": "Campo - Ordens de Servico", "description": "Gestão de Ordens de Serviço"},
            {"name": "Campo - Visitas", "description": "Visitas técnicas e comerciais"},
            {"name": "Campo - Checklists", "description": "Checklists dinâmicos"},
            {"name": "Campo - Roteirizacao", "description": "Roteirização inteligente"},
            {"name": "Campo - Estoque", "description": "Gestão de estoque campo"},
        ]
    )

    # ===================================================================
    # GUARDIAN ROUTERS (Legacy + Cyber Security + Monitoring)
    # ===================================================================

    # Segurança Física (Legacy)
    app.include_router(sync_router, prefix="/api/v1/campo/guardian/sync", tags=["Physical Sync"])
    app.include_router(access_log_router, prefix="/api/v1/campo/guardian/access", tags=["Access"])
    app.include_router(occurrence_router, prefix="/api/v1/campo/guardian/occurrences", tags=["Events"])
    app.include_router(equipment_status_router, prefix="/api/v1/campo/guardian/equipment", tags=["Equip"])

    # Segurança Cibernética
    app.include_router(security_audit_router, prefix="/api/v1/campo/guardian/cyber", tags=["Cyber"])
    app.include_router(ssh_gateway_router, prefix="/api/v1/campo/guardian/cyber", tags=["SSH"])

    # CAMPO Service (legacy)
    app.include_router(campo_service_router, prefix="/api/v1/campo/guardian/campo", tags=["Campo"])

    # System Monitoring
    app.include_router(monitoring_router, prefix="/api/v1/campo", tags=["Monitoring"])

    # ===================================================================
    # CAMPO ROUTERS (OS, Visitas, Checklists, Rotas, Estoque)
    # ===================================================================

    app.include_router(ordem_servico_router, prefix="/api/v1/campo/os", tags=["Campo - Ordens de Servico"])
    app.include_router(visita_router, prefix="/api/v1/campo/visitas", tags=["Campo - Visitas"])
    app.include_router(checklist_router, prefix="/api/v1/campo/checklists", tags=["Campo - Checklists"])
    app.include_router(roteirizacao_router, prefix="/api/v1/campo/rotas", tags=["Campo - Roteirizacao"])
    app.include_router(estoque_router, prefix="/api/v1/campo/estoque", tags=["Campo - Estoque"])

    return app


def extract_openapi_spec(output_path: Path) -> dict:
    """Extrai especificação OpenAPI do módulo CAMPO."""

    print("🔍 Criando app FastAPI temporário para CAMPO...")
    app = create_campo_app()

    print("📝 Gerando especificação OpenAPI...")
    openapi_spec = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    # Adicionar servidor
    openapi_spec["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Backend Conecta PRO - Desenvolvimento"
        }
    ]

    # Salvar spec
    print(f"💾 Salvando em: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

    # Estatísticas
    endpoints = [route for route in app.routes if hasattr(route, 'methods')]
    total_endpoints = sum(len(route.methods) for route in endpoints)

    stats = {
        "endpoints_total": total_endpoints,
        "routes": len(endpoints),
        "schemas": len(openapi_spec.get("components", {}).get("schemas", {})),
        "tags": len(openapi_spec.get("tags", [])),
    }

    print("\n" + "="*60)
    print("✅ EXTRAÇÃO OPENAPI CONCLUÍDA")
    print("="*60)
    print(f"📊 Total de endpoints: {stats['endpoints_total']}")
    print(f"🛣️  Total de rotas: {stats['routes']}")
    print(f"📦 Schemas gerados: {stats['schemas']}")
    print(f"🏷️  Tags: {stats['tags']}")
    print(f"📄 Arquivo: {output_path}")
    print("="*60)

    return stats


def main():
    """Função principal."""

    # Path do arquivo de saída
    backend_root = Path(__file__).parent
    output_file = backend_root / "openapi_specs" / "campo.openapi.json"

    try:
        stats = extract_openapi_spec(output_file)

        # Validar que temos endpoints suficientes
        if stats["endpoints_total"] < 10:
            print("⚠️  AVISO: Número de endpoints muito baixo!")
            sys.exit(1)

        print("\n✅ Processo concluído com sucesso!")
        return 0

    except Exception as e:
        print(f"\n❌ ERRO na extração: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
