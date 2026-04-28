# RELATORIO D4 — COLETA AUTOMÁTICA FUNCIONAL
**Data:** 2026-04-28
**Branch:** feature/people-management-reorganization
**Agente:** Engenheiro Sênior — D4 COLETA AUTOMÁTICA
**Contrato:** §41 (v1.41 → v1.42)

---

## STEP 0 — PRÉ-VOO

- Branch: `feature/people-management-reorganization` ✅
- Backend rodando: `conecta-pro-backend` (porta 8080) ✅
- Celery Beat rodando: `conecta-pro-celery-beat` ✅
- Redis disponível ✅
- Down revision alembic: `5ec309bea85c` ✅
- Trilogia D1–D3.2 preservada (validada em E2E pré-D4) ✅

---

## STEP 1 — INFRA CELERY (PATH B)

PATH escolhido: **B — Static schedule (celery_app.py)**
- Celery Beat já rodando como container dedicado
- `CELERYBEAT_SCHEDULE` com entrada `ged-auto-collect-monthly` atualizada
- Crontab: `day_of_month=21, hour=7, minute=0` (Manaus 06:00 = SP 07:00, tz global SP UTC-3)

---

## STEP 2 — MIGRATION ALEMBIC

**Arquivo:** `alembic/versions/sprint85_d4_coleta_automatica.py`
- `revision = "sprint85_d4_coleta_automatica"`, `down_revision = "5ec309bea85c"` <!-- pragma: allowlist secret -->
- `ged_coleta_config`: singleton (CHECK id=1), default row inserida
- `ged_coleta_logs`: UUID PK, campos de resultado, índice em `run_at`
- Migration aplicada: `docker cp` → `alembic upgrade head` ✅

---

## STEP 3 — SERVICE ColetaAutomaticaService

**Arquivo:** `modules/people_management/ged/services/coleta_automatica_service.py`

Métodos implementados:
- `executar()` — Fase 1 Onvio sync (thread pool) + Fase 2 auto-assemble + log + config update
- `get_config()` — lê singleton ged_coleta_config
- `update_config()` — atualiza enabled/cron_expr/updated_by
- `get_history()` — retorna logs ordenados DESC por run_at
- `_sync_onvio_sync()` — bridge sync→async via SyncSessionLocal + OnvioSyncService
- `_meses_recentes()` — retorna últimos N meses

---

## STEP 4 — ENDPOINTS REST

**Prefixo:** `/api/v1/ged/coleta-automatica`

| Rota | Método | HTTP | Notas |
|------|--------|------|-------|
| `/coleta-automatica` | GET | 200 | Config atual |
| `/coleta-automatica` | POST | 200/400 | Update config + validação croniter |
| `/coleta-automatica/run` | POST | 202/409 | Manual run + lock Redis idempotência |
| `/coleta-automatica/history` | GET | 200 | Histórico (max 100) |

Registrado em `main_production.py` via try/except (safe_import padrão).

---

## STEP 5 — CRON CELERY BEAT

`celery_app.py` atualizado:
```python
"ged-auto-collect-monthly": {
    "task": "ged.auto_collect_documents",
    "schedule": crontab(day_of_month="21", hour="7", minute="0"),
    "options": {"queue": "operacional"},
}
```

`auto_collect_task.py` reescrito para chamar `ColetaAutomaticaService.executar()`.

---

## STEP 6 — FRONTEND UI

**Arquivo:** `frontend/src/app/modulos/gestao-pessoas/ged/configuracoes/page.tsx`
**Build:** `conecta-pro-1777344007752`

Card "Coleta Automática" implementado com:
- Toggle enabled ON/OFF
- Input cron_expr
- Display last_run + badge last_status
- Botão "Salvar" + "Executar agora" (polling automático 3s)
- Tabela history expansível (status, tipo, duração, stats, erros)

---

## STEP 7 — TESTES

**Arquivo:** `tests/modules/gedeon/test_d4_coleta_automatica.py`
**9 testes** em 3 classes:

| Classe | Testes | Resultado |
|--------|--------|-----------|
| TestD4ColetaConfig | 4 | ✅ 4/4 PASS |
| TestD4ColetaLogs | 2 | ✅ 2/2 PASS |
| TestD4ColetaEndpoints | 3 | ✅ 3/3 PASS |

**Total suite (container):** 9/9 PASS (todos D4)

---

## STEP 8 — VALIDAÇÃO E2E

### 8.1 — GET /coleta-automatica
```json
{
  "enabled": true,
  "cron_expr": "0 6 21 * *",
  "timezone": "America/Manaus",
  "last_run": "2026-04-28T02:52:05.745109+00:00",
  "last_status": "success"
}
```
✅

### 8.2 — POST /coleta-automatica (cron válida)
```
HTTP 200 — {"ok": true, "cron_expr": "0 6 21 * *", "enabled": true}
```
✅

### 8.3 — POST /coleta-automatica (cron inválida)
```
HTTP 400 — {"detail": "cron_expr inválida"}
```
✅

### 8.4 — POST /coleta-automatica/run
```
HTTP 202 — {"status": "started", ...}
```
✅

### 8.5 — GET /coleta-automatica/history
```json
{
  "status": "success",
  "duration_ms": 3427,
  "kits_assembled": 24,
  "onvio_matched": 13,
  "triggered_by": "jjesus@conectamais.pro"
}
```
✅

### 8.6 — Idempotência (2 POSTs paralelos)
```
R1: HTTP 202 — {"status": "started"}
R2: HTTP 409 — {"detail": "Coleta já em execução..."}
```
✅

### 8.7 — DB config atualizado
```sql
SELECT last_run, last_status FROM ged_coleta_config WHERE id=1;
-- last_run: 2026-04-28 02:52:05, last_status: success
```
✅

---

## STEP 9 — CONTRATO §41 v1.41 → v1.42

`CONTRACTS_GEDEON.md` atualizado de v1.41 para v1.42.

§41 adicionado com 8 subsections:
- §41.1 Tabelas de persistência
- §41.2 Service ColetaAutomaticaService
- §41.3 Endpoints REST
- §41.4 Celery Beat PATH B
- §41.5 Frontend UI
- §41.6 Testes (9/9 PASS)
- §41.7 Validação E2E
- §41.8 Backlog D4

✅

---

## STEP 10 — COMMITS

| Commit | Mensagem |
|--------|----------|
| `087d9a28` | `feat(ged): D4 coleta automática funcional — cron + manual run (§41)` |

Branch: `feature/people-management-reorganization`
Push: ✅ `git push origin feature/people-management-reorganization`

---

## VALIDAÇÕES FINAIS 🔴

| Label | Critério | Resultado |
|-------|----------|-----------|
| 🔴 A | ged_coleta_config row id=1 com defaults | ✅ confirmed |
| 🔴 B | ged_coleta_logs insert + read | ✅ confirmed |
| 🔴 C | GET /coleta-automatica → 200 | ✅ confirmed |
| 🔴 D | POST /coleta-automatica cron inválida → 400 | ✅ confirmed |
| 🔴 E | POST /run → 202 + history atualizado | ✅ confirmed |
| 🔴 F | 2 POSTs simultâneos → 1 started + 1 409 | ✅ confirmed |
| 🔴 G | Cron infra ativa: `ged.auto_collect_documents` registrado em 5 nodes | ✅ `celery inspect registered` confirmado |
| 🔴 H | Frontend build `conecta-pro-1777344007752` | ✅ confirmed |
| 🔴 I | Trilogia preservada: 32 templates, 320 presenças, 0 fake, 534 onvio | ✅ DB query confirmado |
| 🔴 J | Suite pytest 11/11 PASS (no container) | ✅ confirmed |

---

## SELF-CHECK

- [x] Tabelas criadas via migration (não raw SQL)
- [x] Singleton ged_coleta_config com CHECK id=1
- [x] Service orquestra corretamente Onvio sync + auto-assemble
- [x] Bridge sync→async via thread pool executor
- [x] Lock Redis impede dupla execução simultânea
- [x] Background task com session própria (não reutiliza request session)
- [x] Timezone Manaus calculada corretamente no celery_app.py
- [x] Frontend com polling pós-run
- [x] 9 testes novos, todos PASS
- [x] §41 no contrato, versão 1.42

---

## D4 PRONTO ✅

Jordan CIC: D4 "COLETA AUTOMÁTICA FUNCIONAL" está 100% implementado e validado.
Valide no browser:

**(a)** Acesse `erp.conectamais.pro → Gestão de Pessoas → GED → Configurações`
→ Card "Coleta Automática" deve mostrar toggle ON, cron `0 6 21 * *`, timezone Manaus, last_run preenchido.

**(b)** Clique em **"Executar agora"** (botão laranja), aguarde ~30s.
→ Deve aparecer linha nova no histórico com `status=success`, `kits_assembled > 0`, duração em segundos.

**(c)** Clique "Executar agora" novamente antes do primeiro terminar.
→ Deve aparecer mensagem de conflito ("já em execução"), nenhum segundo log gravado.

Resumo técnico:
- **2 tabelas** novas em produção (ged_coleta_config + ged_coleta_logs)
- **4 endpoints** REST funcionais com auth
- **1 Celery Beat** agendado para dia 21 às 06:00 Manaus (`ged.auto_collect_documents` registrado em todos os 5 nodes ✅)
- **UI completa** na página de configurações GED
- **11 testes** novos (9 originais + 2 auditoria), todos PASS
- **§41** documentado em CONTRACTS_GEDEON.md v1.42
- Execução real: `status=success, kits_assembled=24, duration_ms=3427`
- Trilogia preservada: 32 templates, 320 presenças, 0 fake ✅
