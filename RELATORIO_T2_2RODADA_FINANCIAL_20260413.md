# T2 2ª RODADA — Auto-sync Cashflow + Fix product_categories 500
**Data:** 2026-04-13
**Commit:** `53ae3ff6`
**Branch:** feature/people-management-reorganization

---

## MISSÃO 1 — Auto-sync bank_transactions → cashflow_entries

### Problema
Novas transações chegadas via webhook do Banco Inter (PIX recebidos)
eram salvas em `bank_transactions` mas não sincronizadas para
`cashflow_entries`. O sync anterior era retroativo (script único).

### Solução

#### 1a — `auto_sync_service.py`
```
backend/modules/financial/services/auto_sync_service.py
```

Funções criadas:
| Função | Descrição |
|--------|-----------|
| `_map_category(desc, entry_type)` | Deriva categoria por keywords (mesma lógica do retroativo) |
| `_map_row(row)` | Converte linha DB → dict para INSERT |
| `run_full_sync(limit=500)` | Sincroniza todas as pendentes (idempotente) |
| `sync_single_transaction(tx_id)` | Sync de 1 transação (chamado no webhook) |

#### 1b — Celery Task (cron a cada hora:15)
```
backend/modules/financial/tasks.py
```
```python
@app.task(name="financial.sync_cashflow_entries")
def sync_cashflow_entries_task(self): ...
```

`celery_app.py` atualizado:
- `include`: `"modules.financial.tasks"` adicionado
- `beat_schedule`: `"financial-sync-cashflow-hourly"` → `crontab(minute=15)`

#### 1c — Hook no Webhook (best-effort)
`webhook_controller.py` — após INSERT em `bank_transactions`:
```python
if tx_id:
    try:
        from modules.financial.services.auto_sync_service import sync_single_transaction
        sync_single_transaction(tx_id)
    except Exception:
        pass  # best-effort, não bloqueia webhook
```

#### 1d — Endpoint manual POST /financial/cashflow/sync
```
cashflow_controller.py: POST /sync → run_full_sync()
```

### Validação

```
POST /financial/cashflow/sync
HTTP: 200 ✅
{
  "ok": true,
  "pending": 0,
  "synced": 0,
  "errors": 0
}
```

(0 pendentes porque sync retroativo já estava completo)

---

## MISSÃO 2 — Fix product_categories HTTP 500

### Problema
```
asyncpg.exceptions.UndefinedColumnError:
  column product_categories.requires_approval does not exist
→ HTTP 500 em GET /financial/purchases/categories
```

**Root cause:** Model SQLAlchemy tinha 6 colunas que não existiam no banco.

### Colunas adicionadas
```sql
ALTER TABLE product_categories
  ADD COLUMN IF NOT EXISTS requires_approval BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS approval_limit VARCHAR(20),
  ADD COLUMN IF NOT EXISTS default_account_code VARCHAR(20),
  ADD COLUMN IF NOT EXISTS default_cost_center VARCHAR(50),
  ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS product_count INTEGER DEFAULT 0;
```

### 6 Categorias Conecta Mais inseridas

| Code | Nome | Tipo | Aprovação |
|------|------|------|-----------|
| EPI-001 | EPIs e Uniformes | material | Não |
| EQP-001 | Equipamentos de Segurança | equipamento | Sim |
| ESC-001 | Materiais de Escritório | material | Não |
| TI-001 | Serviços de TI | servico | Sim |
| MAN-001 | Manutenção Predial | servico | Não |
| LOG-001 | Combustível e Transporte | material | Não |

### Validação

```
GET /financial/purchases/categories?condominio_id=...
HTTP antes: 500 ❌
HTTP depois: 200 ✅

Retorno:
LOG-001 Combustível e Transporte
EPI-001 EPIs e Uniformes
EQP-001 Equipamentos de Segurança
MAN-001 Manutenção Predial
ESC-001 Materiais de Escritório
TI-001 Serviços de TI
```

---

## Arquivos Modificados / Criados

| Arquivo | Ação |
|---------|------|
| `backend/modules/financial/services/auto_sync_service.py` | CRIADO |
| `backend/modules/financial/tasks.py` | CRIADO |
| `backend/modules/financial/controllers/cashflow_controller.py` | POST /sync adicionado |
| `backend/modules/integrations/banking/controllers/webhook_controller.py` | Hook auto-sync |
| `backend/celery_app.py` | include + beat_schedule adicionados |
| `product_categories` (DB) | 6 colunas + 6 categorias |

---

## Commit

| Hash | Descrição |
|------|-----------|
| `53ae3ff6` | feat(financial): auto-sync cashflow + fix product_categories 500 |

```
git push origin feature/people-management-reorganization ✅
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T2_2RODADA_FINANCIAL_20260413.md ~/Downloads/RELATORIO_T2_2RODADA_FINANCIAL_20260413.md
```
