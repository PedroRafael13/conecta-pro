# 📊 RELATÓRIO DE ANÁLISE DE API E ENDPOINTS

**Projeto:** Conecta PRO (FastAPI Backend)
**Diretório:** `/opt/conecta-pro/backend/`
**Data:** 2026-02-05

---

## 📈 Resumo Geral

| Métrica | Valor |
|---------|-------|
| Total de controllers/routers | 209 arquivos |
| Endpoints GET identificados | 183+ endpoints |
| Módulos analisados | 35+ módulos |
| Endpoints sem cache | 15+ críticos |
| Operações síncronas pesadas | 12+ |

---

## 🔴 Endpoints Sem Cache (Oportunidades)

### Dados de Referência (Cache Recomendado: 24h)

| Endpoint | Cache TTL | Prioridade | Justificativa |
|----------|-----------|------------|---------------|
| `GET /api/v1/config/tenants` | 24h | 🔴 Alta | Raramente muda |
| `GET /api/v1/config/flags` | 1h | 🔴 Alta | Feature flags |
| `GET /api/v1/config/system` | 24h | 🟡 Média | Configurações |
| `GET /api/v1/clients/` | 5min | 🔴 Alta | Lista paginada |
| `GET /api/v1/clients/{id}` | 5min | 🟡 Média | Dados cliente |
| `GET /api/v1/clients/stats` | 5min | 🔴 Alta | Estatísticas |
| `GET /api/v1/operacional/postos` | 5min | 🔴 Alta | Postos ativos |
| `GET /api/v1/crm/leads` | 5min | 🟡 Média | Leads |
| `GET /api/v1/crm/opportunities` | 5min | 🟡 Média | Oportunidades |

### Dashboards/Relatórios (Cache Recomendado: 1-5min)

| Endpoint | Cache TTL | Prioridade |
|----------|-----------|------------|
| `GET /api/v1/operacional/dashboard` | 1min | 🔴 Crítica |
| `GET /api/v1/operacional/metricas` | 5min | 🔴 Crítica |
| `GET /api/v1/operacional/ocupacao` | 1min | 🔴 Crítica |
| `GET /api/v1/operacional/kpis` | 5min | 🔴 Crítica |
| `GET /api/v1/operacional/kpi-trends` | 5min | 🔴 Alta |
| `GET /api/v1/operacional/resumo-dia` | 1min | 🔴 Crítica |
| `GET /api/v1/operacional/reports/coverage` | 5min | 🟡 Alta |
| `GET /api/v1/operacional/reports/hours` | 5min | 🟡 Alta |
| `GET /api/v1/financial/cashflow` | 5min | 🟡 Alta |

### Já Com Cache ✅

| Endpoint | TTL | Status |
|----------|-----|--------|
| `GET /api/v1/operacional/escalas` | 180s | ✅ Cacheado |
| `GET /api/v1/operacional/turnos` | 180s | ✅ Cacheado |

---

## ⚠️ Operações Síncronas → Async/Celery

### Geração de PDF/Excel/Documentos

| Endpoint | Operação | Sugestão | Prioridade |
|----------|----------|----------|------------|
| `POST /api/v1/operacional/reports/*/export` | Exportação Excel/PDF | Celery + notificação | 🔴 Alta |
| `POST /api/v1/financial/fiscal/nfe/{id}/emitir` | Emissão NFe | Celery + webhook | 🔴 Crítica |
| `POST /api/v1/financial/fiscal/nfse/{id}/emitir` | Emissão NFSe | Celery + webhook | 🔴 Crítica |
| `POST /api/v1/financial/fiscal/sped/gerar` | Geração SPED | Celery | 🟡 Média |
| `POST /api/v1/hr/portal/payslip/{id}/download` | Geração holerite | Async | 🟡 Média |
| `POST /api/v1/ai/reports/generate` | Geração relatório IA | Celery (já deve estar) | ✅ OK |

**Exemplo de implementação:**

```python
# modules/fiscal/controllers/nfe_controller.py

from celery_app import celery_app
from fastapi import BackgroundTasks

@router.post("/nfe/{id}/emitir", response_model=TaskResponse)
async def emitir_nfe(
    id: UUID,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Emite NFe de forma assíncrona.
    Retorna task_id para acompanhar progresso.
    """
    # Validar permissões
    await require_permission(current_user, "fiscal:nfe:emitir")

    # Enviar para Celery
    task = celery_app.send_task(
        'tasks.fiscal.emitir_nfe',
        args=[str(id), str(current_user.id)],
        queue='fiscal',
        countdown=0
    )

    return TaskResponse(
        task_id=task.id,
        status="pending",
        message="Emissão de NFe iniciada",
        status_url=f"/api/v1/tasks/{task.id}/status"
    )

# tasks/fiscal_tasks.py

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue='fiscal'
)
def emitir_nfe(self, nfe_id: str, user_id: str):
    """
    Task Celery para emitir NFe.
    Pode demorar minutos (API SEFAZ).
    """
    try:
        # Operação longa com API externa
        result = nfe_service.emitir(nfe_id)

        # Notificar usuário
        notification_service.send_notification(
            user_id=user_id,
            title="NFe Emitida",
            message=f"NFe {result.numero} emitida com sucesso"
        )

        return {
            "status": "success",
            "nfe_id": nfe_id,
            "numero": result.numero,
            "xml": result.xml_url
        }

    except SefazTimeoutException as exc:
        # Retry com backoff
        logger.warning(f"Timeout SEFAZ, retrying... (attempt {self.request.retries})")
        raise self.retry(exc=exc, countdown=120 * (self.request.retries + 1))

    except Exception as exc:
        logger.error(f"Erro ao emitir NFe: {exc}")
        raise
```

---

### Envio de Email (EmailService)

| Operação | Localização | Sugestão |
|----------|-------------|----------|
| Comunicados massa | `communication/announcement_service.py` | Celery |
| Notificações diaristas | `notificacao_service.py` | Celery |
| Workflow actions | `workflow_engine.py` | Celery |
| Intelligence Hub | `insight_distributor.py` | Celery |

---

### Chamadas API Externas

| Endpoint | Integração | Sugestão |
|----------|------------|----------|
| `POST /api/v1/financial/fiscal/nfe/*` | Provedor NFe | Celery + retry |
| `POST /api/v1/financial/fiscal/nfse/*` | Provedor NFSe | Celery + retry |
| `POST /api/v1/government/sefaz/*` | SEFAZ | Celery + retry |
| `POST /api/v1/government/esocial/*` | eSocial | Celery + retry |
| `POST /api/v1/government/fgts/*` | FGTS Digital | Celery + retry |
| `POST /api/v1/integrations/solides/*` | Sólides | Async + timeout |
| `POST /api/v1/bidding/pncp/*` | PNCP | Async + cache |

---

## 📦 Endpoints com Payload Grande

### Clientes (50+ campos)

| Endpoint | Campos | Sugestão |
|----------|--------|----------|
| `GET /api/v1/clients/` | ~30 campos | ✅ Usa ClientListResponse |
| `GET /api/v1/clients/{id}` | ~50 campos | Criar ClientMinimalResponse |
| `GET /api/v1/clients/{id}/full` | 50+ campos | Manter completo |

**Sugestão:** Implementar field selection:

```python
@router.get("/clients/{id}", response_model=ClientResponse)
async def get_client(
    id: UUID,
    fields: Optional[str] = Query(None, description="Campos desejados: id,name,email"),
    current_user: CurrentUser = Depends(get_current_user)
):
    client = await client_service.get_by_id(id)

    if fields:
        # Filtrar apenas campos solicitados
        field_list = fields.split(',')
        return {k: v for k, v in client.dict().items() if k in field_list}

    return client

# Uso: GET /api/v1/clients/123?fields=id,name,email
```

### Dashboards Complexos

| Endpoint | Payload | Sugestão |
|----------|---------|----------|
| `GET /api/v1/operacional/dashboard` | Múltiplos objetos | Cache + compressão |
| `GET /api/v1/operacional/metricas` | Dados consolidados | Field selection |
| `GET /api/v1/config/tenants/{id}/dashboard` | Estatísticas | Paginar/compactar |

---

## 🔐 Autenticação e Rate Limiting

### JWT Validation ✅

**Implementado corretamente:**
- Todos os endpoints protegidos usam `CurrentActiveUser`
- `require_permission()` para permissões granulares
- `require_operacional_permission()` para módulo operacional

### Rate Limiting ✅

**Configurado (slowapi + Redis):**

```python
# Configuração atual (main.py)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    default_limits=["1000/hour"],  # Global
)

# Limites específicos:
limits_public = ["10/minute"]           # Endpoints públicos
limits_auth = ["5/minute"]              # Login, refresh
limits_read = ["100/minute"]            # GET endpoints
limits_write = ["30/minute"]            # POST/PUT/DELETE
limits_critical = ["10/minute"]         # Geração escalas
limits_bulk = ["5/minute"]              # Operações bulk
limits_export = ["3/minute"]            # Exportações
```

**Endpoints críticos com rate limit:**
- `POST /api/v1/operations/scales/generate` → 10/min
- `POST /api/v1/operations/scales/auto-generate` → 10/min
- Bulk operations → 5/min
- Exportações → 3/min

---

## 🎯 Implementação de Cache

### Exemplo: Cache em Dashboards

```python
# modules/operacional/controllers/dashboard_controller.py

from core.cache import cache_response

class DashboardController:

    @cache_response(ttl=60, prefix="api:dashboard:main")
    async def get_dashboard_main(
        self,
        client_id: UUID,
        date: date,
        current_user: User = Depends(get_current_user)
    ):
        """
        Dashboard principal - cache de 1 minuto.
        Dados que mudam frequentemente.
        """
        return {
            "escalas_ativas": await self.get_escalas_ativas(client_id),
            "ocorrencias_hoje": await self.get_ocorrencias_hoje(client_id, date),
            "ocupacao": await self.get_ocupacao(client_id),
        }

    @cache_response(ttl=300, prefix="api:dashboard:kpis")  # 5 minutos
    async def get_kpis(
        self,
        client_id: UUID,
        current_user: User = Depends(get_current_user)
    ):
        """
        KPIs - cache de 5 minutos.
        Dados mais estáveis.
        """
        return {
            "total_employees": await self.count_employees(client_id),
            "total_posts": await self.count_posts(client_id),
            "monthly_stats": await self.get_monthly_stats(client_id),
        }
```

### Exemplo: Cache em Configurações

```python
# modules/config/controllers/config_controller.py

@cache_response(ttl=3600, prefix="api:config:system")  # 1 hora
async def get_system_config(
    key: str,
    current_user: User = Depends(get_current_user)
):
    """
    Configurações do sistema - cache de 1 hora.
    Mudam muito raramente.
    """
    return await config_service.get_system_config_value(key)

@cache_response(ttl=300, prefix="api:config:flags")  # 5 minutos
async def get_feature_flags(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Feature flags - cache de 5 minutos.
    """
    return await config_service.evaluate_flags(tenant_id)
```

---

## 🎯 Recomendações Prioritárias

### Prioridade 1 (Impacto Alto/Esforço Baixo)

1. **Adicionar cache nos dashboards** (`/operacional/dashboard`, `/operacional/kpis`)
   - Tempo: 30 minutos
   - Impacto: -90% tempo de resposta

2. **Adicionar cache em listas de referência** (`/config/*`, `/clients/` paginado)
   - Tempo: 1 hora
   - Impacto: -80% consultas repetidas

3. **Verificar timeout em operações fiscais** (NFe/NFSe)
   - Tempo: 2 horas
   - Impacto: Elimina timeouts

### Prioridade 2 (Impacto Alto)

1. **Mover emissão de notas fiscais para Celery**
   - Tempo: 4 horas
   - Impacto: UX melhorada, sem timeouts

2. **Mover exportações PDF/Excel para Celery**
   - Tempo: 3 horas
   - Impacto: Elimina bloqueio de requests

3. **Criar response_model minimal para listagens**
   - Tempo: 2 horas
   - Impacto: -50% payload

### Prioridade 3 (Médio Prazo)

1. Implementar field selection (`?fields=id,name,email`)
2. Adicionar compressão gzip para payloads grandes
3. Cache distribuído Redis para multi-instância

---

## ✅ Checklist de Implementação

### Cache
- [ ] Adicionar `@cache_response` em `/operacional/dashboard`
- [ ] Adicionar `@cache_response` em `/operacional/kpis`
- [ ] Adicionar `@cache_response` em `/config/system`
- [ ] Adicionar `@cache_response` em `/config/flags`
- [ ] Adicionar `@cache_response` em `/clients` (listagem)

### Celery
- [ ] Criar task `emitir_nfe` em `tasks/fiscal_tasks.py`
- [ ] Criar task `emitir_nfse` em `tasks/fiscal_tasks.py`
- [ ] Criar task `generate_export` em `tasks/reports_tasks.py`
- [ ] Atualizar controllers para usar Celery
- [ ] Criar endpoint `/tasks/{id}/status` para acompanhar progresso

### Payload
- [ ] Criar `ClientMinimalResponse` schema
- [ ] Criar `CondominiumMinimalResponse` schema
- [ ] Implementar field selection nos endpoints grandes

---

**Relatório gerado:** 2026-02-05
**Status:** Aguardando implementação
