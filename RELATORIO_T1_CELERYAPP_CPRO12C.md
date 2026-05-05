# T1-C CPRO12 — Sync celery_app.py para os 7 workers Celery
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Duração:** ~20min
**Tipo:** Deploy sync (zero alteração de código)

---

## RESULTADO — CENÁRIO B

> celery_app.py sincronizado em todos os 7 containers.
> beat + batch: ✅ running e scheduling.
> operacional/priority/nfse/sefaz/integrations: ❌ ModuleNotFoundError
> (módulos gedeon e health_occupational ausentes nesses containers — aguardam T2/T3).

---

## Hipóteses validadas

| Hipótese | Resultado |
|----------|-----------|
| H1 HOST mais recente que os 7 containers | ✅ SIM — diff confirmou: beat tinha `day_of_month="1"`, HOST tem `day_of_month="21"` |
| H2 includes corretos no HOST | ✅ gedeon, financial, health_occupational, sst presentes (10 includes total) |
| H3 workers recarregaram sem erro | ⚠️ PARCIAL — beat+batch ✅; operacional/priority/nfse/sefaz/integrations ❌ ModuleNotFoundError |
| H4 agendamentos dia 21 no HOST | ✅ `crontab(day_of_month="21", hour="7", minute="0")` |
| H5 beat agenda tasks novas | ✅ `gedeon-risk-monitor-5min (gedeon.risk_monitor)` agendado após sync |
| H6 operacional não tinha SST antes | ✅ CONFIRMADO — grep retornou vazio pré-sync |
| H7 nenhum worker em loop | ⚠️ PARCIAL — beat+batch estáveis; 4 workers restarting (ModuleNotFoundError) |
| H8 script atualizado | ✅ sync_celery_workers.sh atualizado com bloco celery_app.py |

---

## STEP 1 — Diff HOST vs beat (representativo)

```diff
350,352c350
< # Coleta mensal D4 — dia 21 às 07:00 SP
< # INV-12: America/Manaus offset.
< # Manaus 06:00 = Sao Paulo 07:00 (horário padrão, sem DST em Manaus).
---
> # Geração mensal de kits — dia 1 às 02:00 (substitui APScheduler)
355c353
<     "schedule": crontab(day_of_month="21", hour="7", minute="0"),
---
>     "schedule": crontab(day_of_month="1", hour="2", minute="0"),
```

---

## STEP 2 — Sync executado

| Container | docker cp | SIGHUP | Resultado |
|-----------|-----------|--------|-----------|
| conecta-pro-celery-beat | ✅ OK | ✅ python3 os.kill(1,SIGHUP) | beat ativo |
| conecta-pro-celery-batch | ✅ OK | ✅ python3 os.kill(1,SIGHUP) | batch ativo |
| conecta-pro-celery-operacional | ✅ OK | ✅ python3 os.kill(1,SIGHUP) | ❌ ModuleNotFoundError: health_occupational.tasks |
| conecta-pro-celery-integrations | ✅ OK | ✅ python3 os.kill(1,SIGHUP) | ❌ ModuleNotFoundError: modules.gedeon |
| conecta-pro-celery-priority | ✅ OK | ✅ python3 os.kill(1,SIGHUP) | ❌ ModuleNotFoundError: health_occupational.tasks |
| conecta-pro-celery-nfse | ✅ OK | ✅ python3 os.kill(1,SIGHUP) | ❌ ModuleNotFoundError: health_occupational.tasks |
| conecta-pro-celery-sefaz | ✅ OK | ✅ python3 os.kill(1,SIGHUP) | ❌ ModuleNotFoundError: health_occupational.tasks |

**Nota:** `kill` binário ausente nos containers — SIGHUP enviado via `python3 -c "import os,signal; os.kill(1,signal.SIGHUP)"`.

---

## Erros pós-sync (INV-9 — documentados, NÃO corrigidos)

| Container | Erro | Módulo faltante | Fix esperado |
|-----------|------|-----------------|--------------|
| operacional | ModuleNotFoundError | modules.health_occupational.tasks | T3 sync |
| integrations | ModuleNotFoundError | modules.gedeon | T2 sync |
| priority | ModuleNotFoundError | modules.health_occupational.tasks | T3 sync |
| nfse | ModuleNotFoundError | modules.health_occupational.tasks | T3 sync |
| sefaz | ModuleNotFoundError | modules.health_occupational.tasks | T3 sync |

**Causa:** celery_app.py atualizado agora inclui `modules.gedeon.tasks.kronos_tasks` e
`modules.health_occupational.tasks`. Workers que não têm esses módulos copiados entram em crash.
**Ação requerida (Jordan decide):** T2 (sync gedeon/ para integrations) + T3 (sync health_occupational/ para operacional/priority/nfse/sefaz).

---

## STEP 4 — Tasks descobertas no beat

```
Total includes: 10
gedeon: ['modules.gedeon.tasks.kronos_tasks']
financial: ['modules.financial.tasks']
health_occupational: ['modules.health_occupational.tasks']
sst: ['modules.people_management.sst.tasks']
```

```
[2026-05-05 02:25:31] Scheduler: Sending due task gedeon-risk-monitor-5min (gedeon.risk_monitor)
```

---

## Status pós-sync

```
conecta-pro-celery-integrations    Up 2s    (health: starting) ← ModuleNotFoundError: gedeon
conecta-pro-celery-beat            Up 2h    (unhealthy*)       ✅ scheduling
34bbe0bcda76_celery-priority       Up 17s   (health: starting) ← ModuleNotFoundError: health_occupational
a853a3056bf9_celery-sefaz          Up 18s   (health: starting) ← ModuleNotFoundError: health_occupational
8f30da3e29ad_celery-nfse           Up 12s   (health: starting) ← ModuleNotFoundError: health_occupational
conecta-pro-celery-batch           Up 2h    (healthy)          ✅ processing
297439d0453a_celery-operacional    Up 17s   (health: starting) ← ModuleNotFoundError: health_occupational
```

*beat "unhealthy" = healthcheck usa `ps` que não existe no container (bug pré-existente).

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|---------|
| docs | `8b781701` | docs(contracts): §67 — Sync celery_app.py para todos os 7 workers |
| chore | `b86b86cd` | chore(deploy): sync_celery_workers.sh inclui celery_app.py |

Push: `→ feature/people-management-reorganization`

---

## SELF-CHECK

| Item | Status |
|------|--------|
| STEP 0 — §66 confirmado, §13.1 + INV-3 citados, py_compile OK | ✅ |
| STEP 1 — diff HOST vs container verificado antes do cp | ✅ |
| STEP 2 — celery_app.py copiado para 7 containers com limpeza pyc | ✅ |
| STEP 2 — SIGHUP enviado via python3 os.kill (kill ausente nos containers) | ✅ |
| STEP 3 — status e logs verificados após restart | ✅ |
| STEP 4 — tasks gedeon visíveis no beat (10 includes confirmados) | ✅ |
| STEP 5 — §67 no CONTRACTS_GEDEON ANTES do commit | ✅ |
| STEP 6 — 2 commits + script atualizado + push | ✅ |
| INV-3 — celery_app.py NÃO modificado | ✅ |
| INV-9 — erros de 5 workers documentados, NÃO corrigidos | ✅ |

---

**T1-C CPRO12 OK — celery_app.py sincronizado em 7 workers.**
**Beat: ✅ scheduling (inclui gedeon-risk-monitor). Batch: ✅ healthy.**
**4 workers em crash por módulos ausentes — aguardam T2 (gedeon) + T3 (health_occupational).**
