# T3-B CPRO12 — Fix get_sync_session → get_sync_db
**Data:** 2026-05-05
**Terminal:** T3
**Branch:** feature/people-management-reorganization

---

## Ocorrências substituídas

| Arquivo | Ocorrências | Módulo |
|---|---|---|
| `backend/modules/health_occupational/tasks/sst_alerts_tasks.py` | 3 imports + 3 usos | health_occupational ✅ corrigido |
| `backend/modules/health_occupational/integrations/hr_events.py` | 1 import + 1 uso | health_occupational ✅ corrigido |
| `backend/modules/people_management/sst/tasks/afastamento_tasks.py` | 2 imports + 2 usos | people_management ⚠️ listado, §13.4 |
| `backend/modules/notifications/anti_procrastination/integration/module_integrator.py` | 1 import + 1 uso | notifications ⚠️ listado, §13.4 |

---

## Hipóteses

| # | Hipótese | Resultado |
|---|---|---|
| H1 | 3 ocorrências (34,164,246) | ✅ CONFIRMADO — 6 ocorrências (3 imports + 3 usos em linhas 34/41, 164/170, 246/252) |
| H2 | get_sync_db existe | ✅ CONFIRMADO — `backend/core/database/session.py:111` |
| H3 | assinatura compatível | ✅ CONFIRMADO — `@contextmanager`, `with get_sync_db() as db:` idêntico ao uso |
| H4 | outros arquivos afetados | ✅ 2 arquivos mesmo módulo (hr_events.py) + 2 módulos externos (people_management, notifications) |
| H5 | containers tinham health_occupational/tasks/ | ✅ celery-batch ✅ celery-beat ✅ backend |
| H6 | py_compile OK | ✅ COMPILE OK (sst_alerts_tasks + hr_events) |
| H7 | import 3 tasks OK | ✅ "3 tasks SST importadas com sucesso" em celery-batch e celery-beat |
| H8 | get_sync_session não existe em core.database | ✅ CONFIRMADO — zero ocorrências em session.py |

---

## Descoberta crítica — get_sync_db não exportado em __init__.py

`get_sync_db` existe em `session.py` mas NÃO está em `core.database/__init__.py`.
Import `from core.database import get_sync_db` FALHARIA igualmente.
Solução: importar direto de `from core.database.session import get_sync_db`.

---

## Teste vermelho

```
docker exec conecta-pro-celery-batch python3 -c "
from modules.health_occupational.tasks.sst_alerts_tasks import (
    verificar_asos_vencendo,
    verificar_epis_vencendo,
    verificar_exames_pendentes,
)
print('3 tasks SST importadas com sucesso')
"
→ 3 tasks SST importadas com sucesso ✅

docker exec conecta-pro-celery-beat → 3 tasks SST importadas com sucesso (beat) ✅
```

---

## Commits

| # | Hash | Mensagem |
|---|---|---|
| docs | `0996e1a7` (via T2-B) | `docs(contracts): §64 — Fix TenantStatus...` inclui §65 |
| code | `075f2fb8` | `fix(sst): get_sync_session→get_sync_db — destravar tasks ASO/EPI/exames (§65)` |

Push: `0a41c5f7..075f2fb8` ✅

---

## SELF-CHECK — 13 itens

```
[x] STEP 0 — contrato lido, §63 confirmado, §13.1 citado, 3 linhas respondidas
[x] STEP 1.1 — sst_alerts_tasks.py lido INTEIRO (Chesterton)
[x] STEP 1.3 — assinatura get_sync_db verificada: @contextmanager, compatível
[x] STEP 1.4 — outros arquivos: hr_events.py (corrigido), people_management/ e notifications/ (listados)
[x] STEP 2 — backups criados (.bak.t3cpro12b)
[x] STEP 3 — get_sync_session substituído em TODAS as 8 ocorrências (2 arquivos)
[x] STEP 5 — py_compile OK (ambos arquivos)
[x] STEP 6 — §65 no CONTRACTS_GEDEON ANTES do commit de código
[x] STEP 7 — hot-copy para backend + celery-beat + celery-batch; pyc limpos; integrations/ criado nos containers
[x] STEP 8 — teste vermelho: 3 tasks importadas OK (celery-batch + celery-beat)
[x] STEP 9 — 2 commits separados + push + backups removidos
[x] INV-3 — apenas imports substituídos, lógica de negócio intacta
[x] INV-6 — hot-copy para TODOS os 3 containers com health_occupational
```

---

## Cenário: A

INSERT OK — 3 tasks desbloqueadas, import verificado em ambos workers.

---

## T3-B CPRO12 — STATUS

**Tasks SST desbloqueadas:** `verificar_asos_vencendo`, `verificar_epis_vencendo`, `verificar_exames_pendentes` podem executar via Celery Beat.

**⚠️ Pendente (outros módulos — §13.4):**
- `people_management/sst/tasks/afastamento_tasks.py` — mesmo bug (get_sync_session)
- `notifications/anti_procrastination/integration/module_integrator.py` — mesmo bug
