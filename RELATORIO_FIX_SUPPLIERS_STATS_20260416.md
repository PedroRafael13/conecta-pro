# Fix — Fornecedores Stats: total=0 → total=13
**Data:** 2026-04-16
**Branch:** feature/people-management-reorganization
**Commit:** f7a5dfcc (push ✅)

---

## Problema confirmado

| Endpoint | Antes | Depois |
|----------|-------|--------|
| `GET /api/v1/financial/suppliers` | 13 registros | 13 registros |
| `GET /api/v1/financial/suppliers/stats` | `total=0 ativos=0` | `total=13 ativos=13` |

---

## Root cause

**Arquivo:** `backend/modules/financial/repositories/supplier_repository.py`
**Método:** `get_stats(self, condominio_id: UUID)`

A query sempre aplicava `WHERE condominio_id == condominio_id`. Quando o frontend
chama sem passar `condominio_id`, o valor chega como `None`. Em SQLAlchemy,
`Supplier.condominio_id == None` vira `IS NULL` no SQL — retornando 0 registros,
pois todos os 13 fornecedores têm `condominio_id` preenchido.

O método `list` (que retorna os 13 corretamente) já fazia o skip condicional:
```python
if condominio_id is not None:
    base_conditions.append(Supplier.condominio_id == condominio_id)
```

`get_stats` não tinha essa proteção.

---

## Correção aplicada

### `supplier_repository.py` — get_stats

```python
# ANTES
async def get_stats(self, condominio_id: UUID) -> SupplierStats:
    status_query = select(...).where(
        and_(
            Supplier.condominio_id == condominio_id,  # ← sempre aplicado, None→IS NULL
            Supplier.ativo.is_(True),
        )
    )

# DEPOIS
async def get_stats(self, condominio_id: UUID | None) -> SupplierStats:
    base = [Supplier.ativo.is_(True)]
    if condominio_id is not None:           # ← skip quando None
        base.append(Supplier.condominio_id == condominio_id)
    status_query = select(...).where(and_(*base))
```

### `supplier_service.py` — assinatura

```python
# ANTES
async def get_stats(self, condominio_id: UUID) -> SupplierStats:

# DEPOIS
async def get_stats(self, condominio_id: UUID | None) -> SupplierStats:
```

---

## Validação final

| Check | Resultado |
|-------|-----------|
| `GET /financial/suppliers` | ✅ 200 — 13 registros |
| `GET /financial/suppliers/stats` | ✅ 200 — `total=13 ativos=13 por_tipo={pessoa_juridica:13}` |
| DB `SELECT count(*) FROM suppliers WHERE ativo=true` | ✅ 13 |
| MD5 container == MD5 disco | ✅ `d1b94f78909a8b46b670af0c9effae55` |
| `docker exec kill -HUP 1` | ✅ módulos recarregados |

---

## Deploy

| Etapa | Status |
|-------|--------|
| `docker cp repository.py → container` | ✅ |
| `docker cp service.py → container` | ✅ |
| `kill -HUP 1` (reload sem downtime) | ✅ |
| `git commit f7a5dfcc` | ✅ |
| `git push` | ✅ |

```
╔══════════════════════════════════════════════════════════════════╗
║  Fix Fornecedores Stats ✅                                      ║
║  /suppliers/stats: total=13 (era 0)                            ║
║  Causa: condominio_id=None → IS NULL → 0 rows                  ║
╚══════════════════════════════════════════════════════════════════╝
```
