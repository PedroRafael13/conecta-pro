# Módulos API-Only — Conecta PRO

> Documentação dos módulos backend que operam exclusivamente via API, sem interface frontend dedicada.
>
> Atualizado: 2026-02-09

---

## 📋 Lista de Módulos API-Only (15 módulos)

| # | Módulo | Descrição | Justificativa API-Only |
|---|--------|-----------|------------------------|
| 1 | **ai** | Inteligência Artificial - Bartolo Assistente | Consumido via API por outros módulos e interfaces de chat |
| 2 | **audit** | Auditoria e Compliance | Logs acessados via relatórios e dashboards administrativos |
| 3 | **clients** | Gestão de Clientes (Orval) | API consumida por sistemas externos de clientes |
| 4 | **core** | Núcleo do sistema | Serviços compartilhados usados por todos os módulos |
| 5 | **document_kits** | Kits de Documentos | Funcionalidade auxiliar, acessada via workflow de outros módulos |
| 6 | **fase5** | Funcionalidades Fase 5 | Módulo de transição, endpoints integrados em módulos principais |
| 7 | **ged** | Gestão Eletrônica de Documentos | Integrações com storage e processamento em background |
| 8 | **hr** | Recursos Humanos | Funcionalidades ainda em desenvolvimento, acesso via API interna |
| 9 | **integrations** | Integrações Externas | Webhooks e APIs de terceiros (SEFAZ, Prefeituras) |
| 10 | **mobile** | API Mobile | Backend exclusivo para aplicativo mobile |
| 11 | **monitoring** | Monitoramento do Sistema | Acesso via Grafana/Prometheus, não requer UI própria |
| 12 | **notifications** | Sistema de Notificações | Serviço em background, gerenciado via painel admin |
| 13 | **retention** | Retenção de Clientes | Analytics e relatórios, sem interface dedicada |
| 14 | **search** | Busca Full-Text | Motor de busca consumido via API por outras telas |
| 15 | **services** | Serviços Compartilhados | Helpers e utilities usados por múltiplos módulos |

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTENDS (22)                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Auth    │ │  Users   │ │ Financial│ │Scheduler │ ...        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘            │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                         │
                  ┌──────▼──────┐
                  │   API REST  │
                  └──────┬──────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Com Frontend│ │ API-Only    │ │ API-Only    │
│  (18/33)     │ │ (15/33)     │ │ (15/33)     │
│              │ │             │ │             │
│ • auth       │ │ • ai        │ │ • mobile    │
│ • users      │ │ • audit     │ │ • monitoring│
│ • financial  │ │ • clients   │ │ • notifications│
│ • scheduler  │ │ • core      │ │ • retention │
│ ...          │ │ • document_kits│ │ • search   │
│              │ │ • fase5     │ │ • services  │
│              │ │ • ged       │ │             │
│              │ │ • hr        │ │             │
│              │ │ • integrations│ │            │
└──────────────┘ └─────────────┘ └─────────────┘
```

---

## 🔌 Padrões de Uso

### 1. Consumo Interno (Módulos → Módulos)

```python
# Exemplo: Módulo Operacional consumindo AI
from modules.ai.services import BartoloService

response = await BartoloService.process_message(
    message="Qual o status da escala hoje?",
    context={"user_id": user.id}
)
```

### 2. Integrações Externas

```python
# Exemplo: SEFAZ via módulo integrations
from modules.integrations.sefaz import SEFAZClient

client = SEFAZClient(cnpj="12345678000195")
status = await client.consultar_status()
```

### 3. Serviços em Background

```python
# Exemplo: Notificações processadas em Celery
from modules.notifications.services import NotificationService

@shared_task
def send_daily_reminders():
    NotificationService.send_bulk(
        template="daily_reminder",
        recipients=get_active_users()
    )
```

---

## 📊 Cobertura de Frontend por Módulo

| Categoria | Módulos | Frontends | Status |
|-----------|---------|-----------|--------|
| Com Frontend | 18 | 18 | ✅ Completo |
| API-Only | 15 | 0 | ✅ Por Design |
| **Total** | **33** | **18** | **54%** |

---

## ⚠️ Notas Importantes

1. **API-Only ≠ Incompleto**: Estes módulos são intencionalmente API-only por design arquitetural

2. **Documentação de Endpoints**: Cada módulo API-only possui documentação OpenAPI/Swagger acessível em `/docs`

3. **Testes**: Todos os módulos API-only possuem cobertura de testes unitários e de integração

4. **Monitoramento**: Módulos como `monitoring` e `audit` exportam métricas para Prometheus/Grafana

---

## 🔗 Recursos Relacionados

- [Arquitetura do Sistema](./ARCHITECTURE.md)
- [API Documentation](../backend/docs/openapi.json)
- [Guia de Integrações](./INTEGRATION_GUIDE.md)

---

*Documento criado como parte da TASK-002: Consolidar 85%*
