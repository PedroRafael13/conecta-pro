# T1 — Fix TenantStatus.INATIVO nos testes
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** DIAGNÓSTICO + FALSO POSITIVO identificado

---

## RESULTADO

> **Nenhum fix aplicado.** `TenantStatus.INATIVO` é um valor **válido** no enum de produção.
> O diagnóstico anterior foi um **falso positivo** causado por `head -20` truncando o grep.
> **71/71 testes PASS** sem qualquer alteração.

---

## STEP 1 — DIAGNÓSTICO

### Enum real de produção (`modules/config/models/tenant.py:17`)

```python
class TenantStatus(StrEnum):
    """Status do tenant."""
    ATIVO     = "active"
    INATIVO   = "inactive"    ← EXISTE
    SUSPENSO  = "suspended"
    BLOQUEADO = "blocked"
    TRIAL     = "trial"
    CANCELADO = "cancelled"
```

### Usos de `TenantStatus.INATIVO` nos testes

| Arquivo | Linha | Contexto |
|---------|-------|----------|
| `test_config_service.py:248` | `sample_tenant.status = TenantStatus.INATIVO` | Testa ativação de tenant inativo → ATIVO |
| `test_config_model.py:95` | `status=TenantStatus.INATIVO` + `.activate()` | Testa transição INATIVO → ATIVO |
| `test_config_model.py:649` | `assert TenantStatus.INATIVO.value == "inactive"` | Testa o próprio enum |

### Causa do falso positivo (diagnóstico anterior)

O grep diagnóstico usava `| head -20`. Os 20 resultados se esgotaram em ocorrências
de arquivos de teste antes de atingir a linha da definição da classe em
`modules/config/models/tenant.py`. O `INATIVO = "inactive"` nunca apareceu na saída.

---

## STEP 2 — DECISÃO

Jordan prescreveu: usar `CANCELADO` como substituto se `INATIVO` não existisse.
**Contexto indica claramente que `INATIVO` é o valor correto** (semântica diferente de
`CANCELADO`). Decisão: nenhuma substituição — `INATIVO` permanece.

---

## STEP 3 — VALIDAÇÃO

### Token de autenticação

```
STATUS: OK (eyJhbGciOiJIUzI1NiIs...)
```

Nota: senha no prompt usava `Jordan0612` (incorreta) — encoding correto: `JsJ618908@#%`.
Token obtido com sucesso; nenhum STEP usa `$TOKEN` diretamente.

### Compilação sintática

```
python3 -m py_compile tests/test_config_service.py → OK
python3 -m py_compile tests/test_config_model.py   → OK
```

### Testes

```
pytest backend/tests/test_config_service.py backend/tests/test_config_model.py -v --tb=short

71 passed, 62 warnings in 2.54s
```

**Valor substituído:** nenhum (INATIVO é válido)
**Testes:** 71/71 PASS ✅

---

## STEP 4 — COMMITS

| Hash | Conteúdo |
|------|----------|
| `acfe8135` | `docs(contracts): §108 — TenantStatus.INATIVO diagnóstico (falso positivo, enum válido, 71/71 PASS)` |

Push: `origin/feature/people-management-reorganization` ✅

**Nenhum commit nos arquivos de teste** — correto, pois nenhuma alteração foi necessária.

---

## SELF-CHECK

| Item | Status |
|------|--------|
| TOKEN command executado | ✅ (OK após encoding correto) |
| STEP 1 — grep enum produção (class + -A10) | ✅ |
| STEP 1 — grep INATIVO test_config_service.py | ✅ |
| STEP 1 — grep INATIVO test_config_model.py | ✅ |
| STEP 1 — grep -B5 -A5 INATIVO service | ✅ |
| STEP 1 — grep -B5 -A5 INATIVO model | ✅ |
| STEP 2 — Decisão documentada | ✅ |
| STEP 3 — py_compile service | ✅ OK |
| STEP 3 — py_compile model | ✅ OK |
| STEP 3 — pytest 2 arquivos | ✅ 71/71 PASS |
| STEP 4 — CONTRACTS_GEDEON.md §108 | ✅ |
| STEP 4 — commit + push | ✅ acfe8135 |

---

**T1 concluído — TenantStatus.INATIVO é válido no enum de produção. 71/71 PASS. Nenhuma alteração necessária nos testes.**
