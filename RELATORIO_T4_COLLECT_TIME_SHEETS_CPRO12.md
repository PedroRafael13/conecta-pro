# T4-COLLECT-TIME-SHEETS CPRO12 — Fix collect_time_sheets UPDATE + asyncpg date
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Tipo:** BUGFIX — backend GED
**Commits:** `f86b2911` (docs §103) · `4c7172f8` (fix)

---

## RESULTADO — SUCESSO

> **43/51** kit_documents `folha_ponto` com `file_path` preenchido em 03/2026.
> Auto-assemble: 0 erros (era 6 DataError asyncpg) · 11 clientes · 8 kits.
> UPDATE de slots existentes com `file_path=NULL` funcionando.

---

## STEP 1 — Diagnóstico

### Bug 1 — continue incondicional (slot existente sempre pulado)

**ANTES:**
```python
existing = await self.db.execute(select(KitDocument).where(...))
if existing.scalar_one_or_none():
    continue  # pulava mesmo com file_path=NULL
```

**DEPOIS:**
```python
existing_doc = existing_result.scalar_one_or_none()
if existing_doc is not None and existing_doc.file_path is not None:
    continue  # só pula se já tem arquivo
```

### Bug 2 — asyncpg rejeita strings como parâmetros de data

**Erro:**
```
asyncpg.exceptions.DataError: invalid input for query argument $2:
'2026-03-01' (expected a datetime.date or datetime.datetime instance, got 'str')
```

**ANTES:**
```python
data_inicio = f"{ano_s}-{mes_s}-01"
data_fim = f"{ano_s}-{mes_s}-{ultimo_dia:02d}"
{"emp_id": str(emp_id), "inicio": data_inicio, "fim": f"{data_fim} 23:59:59"}
```

**DEPOIS:**
```python
from datetime import date as _date, datetime as _datetime
dt_inicio = _date(ano_i, mes_i, 1)
dt_fim = _datetime(ano_i, mes_i, ultimo_dia, 23, 59, 59)
{"emp_id": str(emp_id), "inicio": dt_inicio, "fim": dt_fim}
```

---

## STEP 2 — Lógica final collect_time_sheets

```
Para cada employee_id:
  1. Busca existing_doc (KitDocument folha_ponto do kit/employee)
  2. Se existing_doc.file_path is not None → skip (já OK)
  3. Gera HTML a partir de gp_clock_punches (asyncpg date objects)
  4. Se existing_doc is not None e file_path gerado → UPDATE
  5. Se existing_doc is None → INSERT novo KitDocument
  6. Se sem batidas → file_path=None (honesto)
```

---

## STEP 3 — Hot-copy

| Container | Resultado |
|-----------|-----------|
| conecta-pro-backend | ✅ MD5 `99edb8ae` (pré-ruff: `51ce9e5c`) |

**Nota:** ruff formatou o arquivo no pre-commit hook → second hot-copy executado com versão pós-ruff.
MD5 disk == container: `99edb8ae` ✅

---

## STEP 4 — Validação

| Etapa | Resultado |
|-------|-----------|
| Reset employee `2e814e1c` para `file_path=NULL` | ✅ 42 com_arquivo antes |
| POST `/api/v1/ged/auto-assemble?reference_month=2026-03-01` | HTTP 200 |
| `total_clients: 11, kits_created: 8, errors: []` | ✅ era 6 erros DataError |
| `com_arquivo` após auto-assemble | **43/51** ✅ |

---

## STEP 5 — Commits

| Hash | Tipo | Conteúdo |
|------|------|----------|
| `f86b2911` | docs | §103 CONTRACTS_GEDEON.md |
| `4c7172f8` | fix | kit_builder_service.py — dois bugs corrigidos |

Push: `origin/feature/people-management-reorganization` ✅

---

## SELF-CHECK FINAL (9 itens)

| Item | Status |
|------|--------|
| STEP 1 — Bug 1 diagnosticado (continue incondicional) | ✅ |
| STEP 1 — Bug 2 diagnosticado (asyncpg DataError string→date) | ✅ descoberto em STEP 4 |
| STEP 2 — Fix lógica UPDATE/INSERT aplicado | ✅ |
| STEP 2 — Fix asyncpg date objects aplicado | ✅ |
| STEP 2 — py_compile OK | ✅ |
| STEP 3 — hot-copy + ruff hot-copy + MD5 `99edb8ae` disk==container | ✅ |
| STEP 4 — auto-assemble 0 erros (era 6 DataError) | ✅ |
| STEP 4 — 43/51 com_arquivo (>=43 exigido) | ✅ |
| STEP 5 — §103 + 2 commits separados + push | ✅ |

---

**T4-COLLECT-TIME-SHEETS CPRO12 OK — dois bugs corrigidos: UPDATE slots NULL + asyncpg date objects. 43/51 kit_documents folha_ponto com arquivo em 03/2026.**
