# T2-C CPRO12 — Sync gedeon + financial/tasks + health_occupational/tasks
**Data:** 2026-05-05
**Sessão:** tmux-t2 | **Módulo:** gedeon, financial, health_occupational
**Branch:** feature/people-management-reorganization

---

## Objetivo

Deploy sync puro: copiar gedeon/, financial/tasks.py e health_occupational/tasks/
para os workers que estavam sem eles. Zero alteração de código.

---

## STEP 1 — Ausência confirmada (Chesterton)

| Container | gedeon/ | financial/tasks.py | health_occupational/tasks/ |
|-----------|---------|-------------------|---------------------------|
| celery-operacional | ❌ dir vazio | ❌ ausente | ❌ dir vazio |
| celery-integrations | ❌ dir vazio | ❌ ausente | N/A |
| celery-priority | ❌ dir vazio | ❌ ausente | ❌ dir vazio |
| celery-nfse | ❌ dir vazio | ❌ ausente | ❌ dir vazio |
| celery-sefaz | ❌ dir vazio | ❌ ausente | ❌ dir vazio |
| celery-beat | ✅ presente | ✅ presente | ✅ + leftover aninhado |
| celery-batch | ✅ presente | ✅ presente | N/A |

**Diagnóstico:** Diretórios existiam nos containers mas estavam **vazios**.
Docker cp com diretório destino já existente cria subdirectório em vez de sobrescrever.
Fix: `rm -rf` no container → recopy do HOST.

---

## Hipóteses Validadas

| Hipótese | Resultado |
|----------|-----------|
| H1: gedeon/ ausente em 5 workers | ✅ dir existia mas vazio — importação falhava |
| H2: financial/tasks.py ausente em 5 workers | ✅ confirmado |
| H3: health_occupational/ ausente em 4 workers | ✅ dir existia, tasks/ existia mas vazia |
| H4: beat com diretório aninhado duplicado | ✅ health_occupational/health_occupational/ removido |
| H5: após cp gedeon, import kronos_tasks funciona | ✅ OK em 5/5 workers |
| H6: financial/tasks.py tem tasks válidas | ✅ sync_cashflow_entries_task, gedeon_risk_monitor_task |
| H7: após sync, workers healthy | ✅ 5/5 passaram para (healthy) |
| H8: py_compile health_occupational OK | ✅ |

---

## Módulos sincronizados

### health_occupational/tasks/ → 4 workers
```
operacional, priority, nfse, sefaz
```
**Arquivos copiados:** `__init__.py`, `sst_alerts_tasks.py`
**Import:** `verificar_asos_vencendo`, `verificar_epis_vencendo`, `verificar_exames_pendentes` — OK

### gedeon/ → 5 workers
```
operacional, integrations, priority, nfse, sefaz
```
**Método:** rm -rf diretório vazio + docker cp backend/modules/gedeon
**Import:** `gedeon.kronos_tasks` — OK em 5/5

### financial/tasks.py → 5 workers
```
operacional, integrations, priority, nfse, sefaz
```
**INV-9 respeitado:** apenas `tasks.py`, não o diretório `financial/` inteiro (zona proibida)
**Import:** `sync_cashflow_entries_task` — OK em 5/5

---

## Limpeza Beat

Diretório aninhado `health_occupational/health_occupational/` removido do celery-beat
(leftover de docker cp anterior que criou subdirectório duplicado).

---

## Aviso INV-10 — Não corrigido

`health_occupational/__init__.py` emite durante import em priority/sefaz:
```
Health Occupational: falha ao registrar subscribers: No module named 'modules.health_occupational.integrations'
```
Bug pré-existente. INV-10: documentado, NÃO corrigido (§13.4 escopo).

---

## Status Final

```
conecta-pro-celery-integrations     (healthy)  ✅
34bbe0bcda76_celery-priority        (healthy)  ✅
a853a3056bf9_celery-sefaz           (healthy)  ✅
8f30da3e29ad_celery-nfse            (healthy)  ✅
297439d0453a_celery-operacional     (healthy)  ✅
conecta-pro-celery-batch            (healthy)  ✅
conecta-pro-celery-beat             (unhealthy) ⚠️  BUG-2 punch_controller (T1 — fora do escopo)
```

---

## Incidente de Deploy — Overwrite acidental + Recovery

Durante cópia de `health_occupational/tasks/`, o comando:
```bash
docker cp backend/modules/health_occupational/tasks/__init__.py $CONTAINER:/app/modules/health_occupational/
```
sobrescreveu o `__init__.py` do módulo raiz com o `__init__.py` do tasks/.
**Recovery imediato:** restaurado via `docker cp backend/modules/health_occupational/__init__.py` em todos os 4 containers.
**Verificação:** import `verificar_asos_vencendo` OK em 4/4 após recovery.

---

## STEP 7 — Imports validados pós-SIGHUP

| Container | gedeon.kronos_tasks | financial.tasks | health_occupational.tasks |
|-----------|---------------------|-----------------|--------------------------|
| celery-operacional | ✅ OK | ✅ OK | ✅ OK |
| celery-integrations | ✅ OK | ✅ OK | N/A |
| celery-priority | ✅ OK | ✅ OK | ✅ OK |
| celery-nfse | ✅ OK | ✅ OK | ✅ OK |
| celery-sefaz | ✅ OK | ✅ OK | ✅ OK |

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|----------|
| docs | `5fc425f5` | `docs(contracts): §68 — Sync gedeon/financial/health_occupational workers (CPRO12 T2-C)` |
| deploy | `3da0d7c4` | `chore(deploy): gedeon+financial/tasks+health_occupational/tasks→5 workers (§68) [CPRO12 T2-C]` |

---

## Cenário: A

Todos os imports OK. 5/5 workers (healthy). Tasks KRONOS/THEMIS, financeiras e SST
disponíveis em todos os workers que as precisam. beat ainda unhealthy por BUG-2 (T1).
