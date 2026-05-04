# Relatório — Fix saldo_inter R$0 → R$32.298,58 D7
**Data:** 2026-05-04
**Commit:** 82bdf3f4
**Branch:** feature/people-management-reorganization
**CONTRACTS_GEDEON:** §54

---

## 1. Sintoma

Card "Saldo Inter" em `/modulos/financeiro/inter/pagamentos` exibia R$0,00.
D6 (`/financeiro/inter`) exibia R$32.298,58 para a mesma conta 370990072-2.

---

## 2. Diagnóstico

### 2.1 — Comparação endpoints

```
GET /api/v1/financeiro/inter/saldo (D6)
→ {"disponivel": 32298.58, "bloqueado": 0.0, "total": 32298.58, ...}  HTTP 200 ✅

GET /api/v1/financeiro/inter/payments/saldo-limite (D7)
→ {"saldo_inter": 0.0, "limite_diario": 5000.0, ...}  HTTP 200 ❌
```

### 2.2 — Causa raiz

`_get_saldo_inter()` em `payment_service.py` (linha 104):
```python
return Decimal(str(balance.available_balance))  # ← campo NÃO existe
```

`AccountBalance` dataclass (`base.py`):
```python
@dataclass
class AccountBalance:
    available: Decimal   # ← campo correto
    blocked: Decimal
    total: Decimal
    currency: str = "BRL"
    updated_at: datetime = ...
    # SEM available_balance
```

`AttributeError` capturado por `except Exception` → retorna `Decimal("0")` silenciosamente.

### 2.3 — D6 usa campo correto

`inter_controller.py` (D6): `balance.available` → R$32.298,58 via Redis cache.

---

## 3. Fix

**Arquivo:** `backend/modules/integrations/inter/services/payment_service.py`

**REGRA DE OURO aplicada:** reusar Redis cache D6 (`inter:saldo:cache`) primeiro.

```python
async def _get_saldo_inter(self) -> Decimal:
    """Consulta saldo Inter — Redis cache D6 primeiro, depois adapter direto."""
    # 1. Redis cache D6 (inter:saldo:cache, TTL 300s)
    try:
        import json as _json
        from core.cache.redis import get_redis
        redis = await get_redis()
        cached = await redis.get("inter:saldo:cache")
        if cached:
            data = _json.loads(cached)
            return Decimal(str(data.get("disponivel", 0)))
    except Exception:
        pass
    # 2. Fallback: adapter direto com campo correto
    try:
        ...
        balance = await adapter.get_balance()
        return Decimal(str(balance.available))  # ← CORRETO (era available_balance)
    except Exception as exc:
        logger.warning("D7 _get_saldo_inter falhou: %s", exc)
        return Decimal("0")
```

---

## 4. Deploy

```bash
docker cp backend/modules/integrations/inter/services/payment_service.py \
  conecta-pro-backend:/app/modules/integrations/inter/services/payment_service.py
docker restart conecta-pro-backend
```

---

## 5. Validação

```
GET /api/v1/financeiro/inter/payments/saldo-limite (Jordan)
→ {"saldo_inter": 32298.58, "limite_diario": 5000.0, "consumido_hoje": 0.0,
    "disponivel_hoje": 5000.0, "limite_restante": 5000.0}  HTTP 200 ✅
```

| Item | Antes | Depois |
|------|-------|--------|
| `saldo_inter` | 0.0 | 32298.58 ✅ |
| Redis cache D6 reutilizado | ❌ | ✅ |
| Chamada Inter API duplicada | ❌ (falha silenciosa) | Evitada via cache ✅ |

---

## 6. Regra derivada

> Ao acessar campos de dataclass/Pydantic, nunca assumir — verificar em `base.py`.
> `AccountBalance.available` (não `available_balance`).
> Sempre consultar Redis cache D6 antes de criar novo adapter Inter.
