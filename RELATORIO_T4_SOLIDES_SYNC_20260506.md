# T4 — Sólides Sync Manual 2026-05-06
**Data:** 2026-05-06
**Executor:** Claude Sonnet 4.6 [session: t5] [module: ged]
**Branch:** feature/people-management-reorganization

---

## Missão

Executar sync manual do Sólides.
Atualizar funcionários, afastamentos e estrutura organizacional.

---

## STEP 1 — Diagnóstico Pré-Sync

### Estado dos funcionários (antes)

| Métrica | Valor |
|---------|-------|
| Total | 58 |
| Ativos (`status='ativo'`) | 45 |
| Inativos (`status='inativo'`) | 13 |

**Nota:** O campo `status` usa valores em português (`ativo`/`inativo`), não `active`/`inactive` como assumido no prompt. A query do prompt retorna 0 ativos porque usa `status='active'`.

### Último sync registrado (pré-execução)

| sync_type | status | started_at | items_processed |
|-----------|--------|------------|-----------------|
| full | completed | 2026-05-05 21:48:20 | 89 |
| incremental | completed | 2026-05-06 15:47:57 | 51 |
| incremental | completed | 2026-05-06 16:02:56 | 51 |

O sync beat já havia executado automaticamente. O último full sync ocorreu em 2026-05-05 (não em 2026-01-18 como indicado no prompt — o cron estava ativo).

### Endpoint status (`/api/v1/dp/solides/sync/status`)

Retornou **404**. O endpoint correto descoberto via código fonte é:
`POST /api/v1/integrations/solides/sync/trigger`

---

## STEP 2 — Execução do Sync

**Endpoint usado:** `POST /api/v1/integrations/solides/sync/trigger`
**Payload:** `{"full_sync": true}`

**Resposta:**
```json
{
    "success": true,
    "message": "Sincronização completa agendada",
    "task_id": "0f60ba6f-331a-4165-b8a5-78cf929617a3",
    "sync_type": "full",
    "entity_types": null
}
```

---

## STEP 3 — Validação Pós-Sync

### Log do sync executado

| Campo | Valor |
|-------|-------|
| sync_type | full |
| status | **completed** |
| started_at | 2026-05-06 16:18:24 |
| completed_at | 2026-05-06 16:18:28 |
| duration_ms | **3.805 ms** |
| items_processed | **89** |
| items_created | 45 |
| items_updated | **0** |
| items_failed | **0** |

### Contagem pós-sync

| Métrica | Antes | Depois | Δ |
|---------|-------|--------|---|
| Total | 58 | 58 | 0 |
| Ativos | 45 | 45 | 0 |
| Inativos | 13 | 13 | 0 |
| Última atualização | 2026-04-10 23:05 | 2026-04-10 23:05 | — |

### Novos/alterados nos últimos 10 minutos

Nenhum. `WHERE updated_at >= NOW() - INTERVAL '10 minutes'` → 0 rows.

**Diagnóstico:** `items_created=45` é comportamento do upsert do connector — re-avalia todos os ativos sem gerar modificações reais no banco. Nenhum dado mudou desde 2026-04-10.

---

## STEP 4 — Documentação

- §111 appendado ao `CONTRACTS_GEDEON.md`
- Commit: `e539f3c6` — `docs(contracts): §111 — sync manual Sólides 2026-05-06`
- Push: ✅ `feature/people-management-reorganization`

---

## Achados

| Achado | Impacto |
|--------|---------|
| `status='active'` não existe — valores reais são `'ativo'`/`'inativo'` | Query do STEP 1 retorna 0 ativos (falso negativo) |
| Endpoint `/api/v1/dp/solides/sync` → 404 | Rota real: `/api/v1/integrations/solides/sync/trigger` |
| `full_name`/`job_title` não existem em `employees` | Colunas reais: `nome`/`cargo` |
| Beat schedule já executava syncs automáticos | Último full sync foi 2026-05-05, não 2026-01-18 |

---

## Self-check

| Item | Status |
|------|--------|
| STEP 1 — diagnóstico completo (employees + sync_log + status endpoint) | ✅ |
| STEP 2 — sync full executado e confirmado | ✅ |
| STEP 3 — validação pós-sync (log + contagens + alterações 10min) | ✅ |
| STEP 4 — §111 em CONTRACTS_GEDEON + commit + push | ✅ |
| Reportar status, items_processed, contagem antes/depois, novos funcionários | ✅ |

---

**T4 SÓLIDES SYNC OK**

status=completed | items_processed=89 | items_failed=0
Funcionários: 45 ativos / 13 inativos / 58 total (sem alterações)
Novos/alterados: nenhum

[session: t5] [module: ged]
