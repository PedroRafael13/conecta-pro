# RELATÓRIO — T5 Backend: Salvar Boleto/PIX no receivable_accounts
**Data:** 2026-04-12
**Commit:** `62ea4ecb` (backend banking_controller.py)

---

## SUMÁRIO EXECUTIVO

| Item | Status |
|------|--------|
| Helper `_salvar_cobranca_no_receivable` | ✅ |
| `receivable_id` em `BoletoGenerateRequest` | ✅ |
| `receivable_id` em `PixChargeRequest` | ✅ |
| `generate_boleto` chama helper via `asyncio.create_task` | ✅ |
| `generate_pix_charge` chama helper via `asyncio.create_task` | ✅ |
| DB: ADD COLUMN `boleto_id`, `customer_name`, `customer_document` | ✅ |
| Syntax check Python | ✅ SYNTAX_OK |
| Docker deploy + restart (healthy) | ✅ |
| Commit + Push | ✅ `62ea4ecb` |

---

## 1 — DIAGNÓSTICO INICIAL

```
grep generate_boleto banking_controller.py → linha 383, 427
→ sem UPDATE receivable / sem _salvar_cobranca: confirmado
```

---

## 2 — MUDANÇAS IMPLEMENTADAS

### 2.1 — Helper `_salvar_cobranca_no_receivable` (linhas 38–94)

```python
async def _salvar_cobranca_no_receivable(
    receivable_id: str,
    tipo: str,       # "boleto" | "pix"
    dados: dict,
) -> None:
    # UPDATE receivable_accounts SET boleto_generated=TRUE, boleto_id, barcode, digitable_line
    # OU pix_generated=TRUE, pix_txid, pix_copy_paste
    # via psycopg2 direto (DATABASE_URL do env)
```

### 2.2 — `BoletoGenerateRequest` — campo adicionado (linha 150)

```python
receivable_id: str | None = None  # ID do receivable_account para salvar boleto gerado
```

### 2.3 — `PixChargeRequest` — campo adicionado (linha 201)

```python
receivable_id: str | None = None  # ID do receivable_account para salvar PIX gerado
```

### 2.4 — `generate_boleto` — chamada do helper (linhas 503–505)

```python
if req.receivable_id and result.get("boleto_id"):
    asyncio.create_task(
        _salvar_cobranca_no_receivable(req.receivable_id, "boleto", result)
    )
```

### 2.5 — `generate_pix_charge` — chamada do helper (linhas 609–611)

```python
if req.receivable_id and (result.get("charge_id") or result.get("pix_copy_paste")):
    asyncio.create_task(
        _salvar_cobranca_no_receivable(req.receivable_id, "pix", result)
    )
```

---

## 3 — BANCO DE DADOS

```sql
ALTER TABLE receivable_accounts
  ADD COLUMN IF NOT EXISTS boleto_generated BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS boleto_id VARCHAR(100),        -- NOVA
  ADD COLUMN IF NOT EXISTS boleto_barcode TEXT,
  ADD COLUMN IF NOT EXISTS boleto_digitable_line TEXT,
  ADD COLUMN IF NOT EXISTS pix_generated BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS pix_copy_paste TEXT,
  ADD COLUMN IF NOT EXISTS pix_txid VARCHAR(100),
  ADD COLUMN IF NOT EXISTS customer_name VARCHAR(200),    -- NOVA
  ADD COLUMN IF NOT EXISTS customer_document VARCHAR(20); -- NOVA
```

**Resultado:** ALTER TABLE OK — 3 colunas novas adicionadas, 6 já existiam (skipped)

---

## 4 — CICLO COMPLETO IMPLEMENTADO

```
Frontend: modal seleciona conta a receber
    ↓ POST /api/v1/integrations/banking/boleto/generate
         body: { receivable_id: "uuid", bank_code: "077", ... }
    ↓ InterAdapter.generate_boleto() → boleto_id, barcode, digitable_line
    ↓ asyncio.create_task(_salvar_cobranca_no_receivable())
         UPDATE receivable_accounts SET boleto_generated=TRUE, boleto_id=..., ...
    ↓ Frontend reabre modal → exibe boleto existente ✅
```

---

## 5 — DEPLOY

```
python3 -m py_compile banking_controller.py → SYNTAX_OK
docker cp modules/ conecta-pro-backend:/app/modules/
docker restart conecta-pro-backend → Up (healthy)
```

---

## 6 — PENDÊNCIA FRONTEND

Para fechar o ciclo 100%, o frontend precisa passar `receivable_id` no body das chamadas de geração. Atualmente o modal **não envia** `receivable_id`. Próxima sessão: adicionar `receivable_id: receivable.id` ao body do `handleGerarCobranca`.

---

**Relatório gerado:** 2026-04-12
