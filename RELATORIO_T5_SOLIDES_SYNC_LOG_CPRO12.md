# T5 Sólides Sync Logging — CPRO12
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization

---

## Problema
`solides_sync_log` sempre com 0 linhas apesar de syncs ocorrendo regularmente.

## Diagnóstico (STEP 1–2)

**Root cause:** `sync_solides_full` e `sync_solides_incremental` (tasks.py) chamam
`SolidesConnector` diretamente, bypassando `SolidesSyncService` que contém o `log_sync_operation`.

**Último sync real (solides_employees):** 2026-01-18 23:34:19

**Webhook:** `SOLIDES_WEBHOOK_SECRET` configurado no container. `POST /webhook` existe e recebe
eventos. `/webhook/configure` e `/webhook/status` retornam 404 — não implementados.

## Fix (STEP 3)

**tasks.py** — adicionados helpers com raw SQL:
- `_log_sync_start()`: INSERT em `solides_sync_log` com `status='running'` antes do sync
- `_log_sync_end()`: UPDATE com `status='completed'/'failed'`, `duration_ms`, `items_processed`, `items_created`
- Integrados em `sync_solides_full` e `sync_solides_incremental`

**sync_service.py** — corrigidos nomes de colunas (7 erros em `full_sync`, 7 erros em `incremental_sync`, 1 em except):
| Errado | Correto |
|--------|---------|
| `duration_seconds` | `duration_ms` (×1000) |
| `total_processed` | `items_processed` |
| `created_count` | `items_created` |
| `updated_count` | `items_updated` |
| `skipped_count` | `items_skipped` |
| `conflict_count` | `conflicts_detected` |
| `error_count` | `items_failed` |
| `errors` | `error_details` |

## Webhook (STEP 4)
`POST /integrations/solides/webhook/configure` → HTTP 404 (endpoint não existe).
Documentado como pendência futura. `SOLIDES_WEBHOOK_SECRET` já está configurado no container.

## Validação (STEP 5)
```
POST /api/v1/integrations/solides/sync/trigger → HTTP 200 (task agendada)
solides_sync_log após sync:
  status=completed | duration_ms=3853 | items_processed=89 | items_created=45 | triggered_by=manual
```

## Commits
| Hash | Descrição |
|------|-----------|
| `a3a24fcc` | docs(solides): §107 — logging ativado em solides_sync_log |
| `04e95789` | fix(solides): ativar logging via _log_sync_start/_log_sync_end |
| `5a2f7f65` | fix(solides): corrigir colunas incremental_sync + errors→error_details (auditoria) |
| `(este)` | docs(solides): §107 corrigido + relatório T5 |

Push: `feature/people-management-reorganization` → remoto OK

---

## SELF-CHECK
- [x] STEP 1 — connector Sólides lido inteiro
- [x] STEP 2 — status webhook verificado (404 documentado)
- [x] STEP 3 — logging adicionado, py_compile OK
- [x] STEP 4 — webhook documentado como pendência
- [x] STEP 5 — sync manual → solides_sync_log tem registro
- [x] STEP 6 — §107 + commits + push
