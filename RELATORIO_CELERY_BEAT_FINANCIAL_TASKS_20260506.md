# Fix celery-beat: ModuleNotFoundError modules.financial.tasks
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** BUGFIX — celery-beat operacional
**Módulo:** modules/financial/tasks.py

---

## RESULTADO — SUCESSO

> `celery-beat` inicializando limpo: **10/10 módulos importam OK**.
> `Scheduler: Sending due task` em todos os schedules esperados.

---

## DIAGNÓSTICO

### Erro no celery-beat (antes do fix)

```
ModuleNotFoundError: No module named 'modules.financial.tasks'
  File ".../celery/loaders/base.py", line 88, in import_module
    return importlib.import_module(module, package=package)
```

O beat crashava no `init_loader` → `import_default_modules` ao tentar carregar
`modules.financial.tasks` que estava declarado em `celery_app.py` `include=[]`.

### Estado dos containers

| Container | tasks.py | nested financial/financial/ |
|-----------|----------|-----------------------------|
| celery-beat | ❌ AUSENTE | ✅ presente (inofensivo) |
| conecta-pro-backend | ❌ AUSENTE | ✅ presente (inofensivo) |
| celery-batch | ✅ presente | ✅ presente |
| celery-operacional | ✅ presente | ✅ presente |
| celery-integrations | ✅ presente | ✅ presente |
| celery-priority | ✅ presente | ✅ presente |
| celery-nfse | ✅ presente | ✅ presente |
| celery-sefaz | ✅ presente | ✅ presente |

### Root cause

`tasks.py` existia no disco (`/opt/conecta-pro/backend/modules/financial/tasks.py`)
mas nunca foi copiado para os containers `celery-beat` e `backend` em algum
hot-copy anterior. Os outros containers receberam o módulo normalmente.

O `financial/financial/` nested é resquício de um `docker cp` malformado anterior
— não afeta imports (Python resolve `modules.financial.tasks` para o `tasks.py` correto).

---

## FIX APLICADO (hot-copy operacional)

```bash
# 1. Limpar pyc stale
docker exec conecta-pro-celery-beat find /app/modules/financial/__pycache__ -name "*.pyc" -delete
docker exec conecta-pro-backend find /app/modules/financial/__pycache__ -name "*.pyc" -delete

# 2. Copiar tasks.py (syntax OK validado: python3 -c "import ast; ast.parse(...)")
docker cp backend/modules/financial/tasks.py conecta-pro-celery-beat:/app/modules/financial/tasks.py
docker cp backend/modules/financial/tasks.py conecta-pro-backend:/app/modules/financial/tasks.py

# 3. Remover nested dir do beat
docker exec conecta-pro-celery-beat rm -rf /app/modules/financial/financial/

# 4. Reload
docker exec conecta-pro-celery-beat python3 -c "import os, signal; os.kill(1, signal.SIGHUP)"
docker exec conecta-pro-backend kill -HUP 1
```

---

## VALIDAÇÃO

### Import test (celery-beat container)

```
OK: modules.government_integrations.jobs.sync_tasks
OK: modules.government_integrations.jobs.monitoring_tasks
OK: modules.integrations.connectors.solides.tasks
OK: modules.operacional.tasks
OK: modules.bidding.tasks
OK: modules.people_management.sst.tasks
OK: modules.people_management.ged.tasks
OK: modules.health_occupational.tasks
OK: modules.gedeon.tasks.kronos_tasks
OK: modules.financial.tasks          ← era o que falhava
```

### Beat logs após fix

```
Scheduler: Sending due task solides-process-webhooks
Scheduler: Sending due task sync-work-schedules-solides
Scheduler: Sending due task gedeon-risk-monitor-5min
Scheduler: Sending due task check-endpoints-5min
...
```

Container status: `Up 4 minutes (healthy)` ✅

### Outros achados do diagnóstico

| Achado | Detalhe |
|--------|---------|
| `conecta-pro-celery-worker` não existe | Container não existe — fallback do prompt retornou vazio (esperado) |
| Redis `localhost:6379` refused (celery-batch, 2026-05-05) | Erro pontual do dia 05/05, não recorrente — worker tenta localhost em evento pontual |
| TenantStatus enum | Definido em `modules/config/models/tenant.py:17`, usado em config_repository.py — OK |
| `health_occupational` | Sem PunchService — módulo registrado em main_production.py, tasks.py presente |

---

## SELF-CHECK

| Item | Status |
|------|--------|
| Diagnóstico: docker ps workers | ✅ |
| Diagnóstico: celery-beat logs --tail 30 | ✅ |
| Diagnóstico: celery-worker logs (fallback — container não existe) | ✅ |
| Diagnóstico: python3 subprocess beat logs | ✅ |
| Diagnóstico: grep TenantStatus | ✅ |
| Diagnóstico: grep health_occupational/PunchService | ✅ |
| Fix: tasks.py copiado para beat + backend | ✅ |
| Fix: pyc stale limpos | ✅ |
| Fix: nested financial/financial/ removido do beat | ✅ |
| Validação: 10/10 módulos importam no beat | ✅ |
| Validação: beat healthy e dispatching tasks | ✅ |

---

**celery-beat OK — modules.financial.tasks importando corretamente. Beat schedulando 25+ tasks sem erros.**
