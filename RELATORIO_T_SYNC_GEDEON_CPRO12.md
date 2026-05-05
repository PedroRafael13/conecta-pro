# T_SYNC CPRO12 — Sync gedeon/ + plano enterprise
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Duração:** ~10min
**Tipo:** Deploy sync (zero alteração de código)

---

## RESULTADO — CENÁRIO C

> gedeon/ já estava nos containers (copiado em T1 CPRO12). SKIP para ambos.
> celery-batch: Up 25+ min **healthy**. Nenhum module copy necessário.

---

## Hipóteses validadas

| Hipótese | Resultado |
|----------|-----------|
| H1 gedeon/ existe no HOST | ✅ SIM — 13 subpastas, tasks/kronos_tasks.py presente |
| H2 batch sem gedeon antes | ❌ FALSO — já tinha gedeon/ (copiado em T1) |
| H3 beat sem gedeon antes | ❌ FALSO — já tinha gedeon/ (copiado em T1) |
| H4 batch em loop antes | ❌ FALSO — Up 25+ min healthy quando verificado |
| H5 gedeon tem tasks | ✅ SIM — gedeon/tasks/kronos_tasks.py |
| H6 import OK após cp | ✅ gedeon.tasks OK em beat e batch |
| H7 batch subiu | ✅ Up 25 min (healthy) |
| H8 inventário diff HOST vs batch | ✅ Executado — ver abaixo |

---

## Inventário diferencial HOST vs containers (P4 antecipado)

### Módulos presentes nos containers mas AUSENTES no HOST
| Módulo | Observação |
|--------|-----------|
| `cadastros` | Presente em beat + batch, não no HOST |
| `core` | Presente em beat + batch, não no HOST (provavelmente builtin da imagem) |

### Módulos presentes no HOST mas AUSENTES nos containers
| Módulo | Observação |
|--------|-----------|
| `gdrive` | Apenas no HOST — nunca copiado para celery workers |
| `juridico` | Apenas no HOST — nunca copiado para celery workers |
| `search` | Apenas no HOST — nunca copiado para celery workers |

**Ação:** APENAS LISTADO — §13.4 proíbe cópia não autorizada. Jordan decide se/quando sincronizar.

---

## Ações executadas

| # | Ação | Resultado |
|---|------|-----------|
| 1 | Verificar gedeon/ no HOST | ✅ Completo (13 entries) |
| 2 | Verificar gedeon/ em celery-batch | ✅ Já presente — SKIP |
| 3 | Verificar gedeon/ em celery-beat | ✅ Já presente — SKIP |
| 4 | Inventário diff HOST vs batch | ✅ Executado (ver acima) |
| 5 | tenant plano 'free' → 'enterprise' | ✅ UPDATE 1 confirmado |
| 6 | Import gedeon.tasks validado | ✅ OK em beat e batch |
| 7 | §63 CONTRACTS_GEDEON.md | ✅ Adicionado |
| 8 | 2 commits + push | ✅ docs=f49fd84a, chore=4bc88b47 |
| 9 | sync_celery_workers.sh criado | ✅ scripts/deploy/ |

---

## STEP 3 — tenant plano

```sql
UPDATE tenants SET plano = 'enterprise', updated_at = NOW()
WHERE documento = '35710481000103'
RETURNING id, nome, plano, status;
-- id: 841a3906-5410-4047-a076-bc7bce95ffd2
-- nome: CONECTAMAIS ELETRONICA LTDA
-- plano: enterprise | status: active
-- UPDATE 1 ✅
```

---

## Status pós-sync

```
conecta-pro-celery-integrations    Up 2 weeks  (healthy)
conecta-pro-celery-beat            Up 26 min   (unhealthy*)
conecta-pro-celery-batch           Up 25 min   (healthy)
conecta-pro-celery-priority        Up 2 weeks  (healthy)
conecta-pro-celery-sefaz           Up 2 weeks  (healthy)
conecta-pro-celery-nfse            Up 2 weeks  (healthy)
conecta-pro-celery-operacional     Up 2 weeks  (healthy)
```

*celery-beat `unhealthy` = healthcheck usa `ps` que não existe no container (bug pré-existente).
O scheduler está funcionando — foi observado enviando 10+ tasks em T1 CPRO12.

---

## Próximo erro (celery-batch)

**Nenhum.** celery-batch está healthy e processando tasks:
```
Task government_integrations.tasks.monitoring.verificar_disponibilidade succeeded in 15.46s
```
O erro de Redis `localhost:6379` nos logs é do publisher de eventos (pré-existente, out of scope).

---

## Script criado — scripts/deploy/sync_celery_workers.sh

```bash
# Uso: ./sync_celery_workers.sh nome_do_modulo
# Ex: ./sync_celery_workers.sh gedeon
# Copia para: backend, celery-beat, celery-batch, operacional, integrations, priority
# Limpa pyc stale antes de cada cp
# Envia HUP ao backend no final
```

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|---------|
| docs | `f49fd84a` | docs(contracts): §63 — Sync gedeon containers + plano enterprise |
| chore | `4bc88b47` | chore(deploy): script sync_celery_workers.sh |

Push: `8fab2f42..4bc88b47 → feature/people-management-reorganization`

---

## SELF-CHECK

| Item | Status |
|------|--------|
| STEP 0 — §62 confirmado, §13.1 citado | ✅ |
| STEP 1 — HOST vs containers verificado antes do cp | ✅ |
| STEP 1.3 — inventário diff executado e documentado | ✅ |
| STEP 2 — gedeon já presente → SKIP (lógica condicional respeitada) | ✅ |
| STEP 2 — pyc limpo (N/A — cp não executado pois já existia) | ✅ |
| STEP 3 — tenant plano atualizado free → enterprise | ✅ |
| STEP 4 — import gedeon.tasks validado em cada container | ✅ |
| STEP 5 — status dos containers verificado | ✅ |
| STEP 6 — §63 no CONTRACTS_GEDEON antes do commit | ✅ |
| STEP 7 — 2 commits + script sync salvo + push | ✅ |
| INV-3 — apenas gedeon escopo; outros ausentes apenas listados | ✅ |
| INV-11 — nenhum novo erro (batch healthy) | ✅ |

---

**T_SYNC CPRO12 OK — gedeon já sincronizado desde T1. Batch: healthy (25 min). Beat: running (26 min, healthcheck bug pré-existente).**
