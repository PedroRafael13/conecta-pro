# RELATÓRIO CPRO11 — RODADA 1.5 — FIX SEQUENCIAL CIRÚRGICO
**Data:** 2026-04-21
**Branch:** feature/people-management-reorganization
**Contrato:** CONTRACTS_CRM_VENDAS.md v1.6
**Sessão:** tmux-t4 | Módulo: crm

---

## VEREDITO FINAL

**RODADA 1.5 CONCLUÍDA COM SUCESSO — 10/10 TESTES PASSANDO — 10/10 ENDPOINTS 200**

---

## STEP 0 — Contrato e Escopo

- Módulo declarado: `crm`
- Arquivos em escopo: `backend/modules/crm/models/contract.py`, `backend/modules/crm/schemas/contract.py`, `backend/tests/modules/crm/test_cpro11_regressions_real.py`
- Contrato atualizado: `CONTRACTS_CRM_VENDAS.md` v1.5 → v1.6

---

## FASE 1 — Diagnóstico

### Root Cause Principal (H1 + H2)

**H1 CONFIRMADA:** Backend estava rodando com bytecode antigo.
- `docker cp + kill -HUP 1` NÃO recarrega módulos Python no uvicorn.
- `docker restart` é obrigatório para changes em models/schemas.

**H2 CONFIRMADA:** `Column(Enum())` sem `values_callable` usa `.name` (ex: `RECURRING`)
em vez de `.value` (ex: `recurring`), causando `LookupError` no PostgreSQL pois o
tipo PG foi criado com valores lowercase.

### Outras hipóteses

| H# | Status | Motivo |
|---|---|---|
| H3 (pyc cache) | REFUTADA | docker restart resolve sem limpar cache |
| H4 (campos P0 ausentes) | REFUTADA | campos existem no schema |
| H5 (controller não popula) | REFUTADA | controller popula corretamente |
| H6 (frontend antigo) | REFUTADA | BUILD_ID confirma build posterior |
| H10 (ordem rotas) | JÁ CORRIGIDA | templates antes de /{id} já aplicado |
| H11/H12 (conftest mocks) | CONFIRMADA | conftest.py usava AsyncMock, não DB real |

---

## FASE 2 — Fixes Backend

### Fix 1: `backend/modules/crm/models/contract.py`

5 `Column(Enum())` corrigidos com `values_callable`:

```python
# ANTES (bug):
status = Column(Enum(ContractStatus), ...)

# DEPOIS (fix):
status = Column(
    Enum(ContractStatus, values_callable=lambda obj: [e.value for e in obj], name="contractstatus"),
    nullable=False, default=ContractStatus.DRAFT,
)
```

Todos os 5 campos: `contract_type`, `status`, `adjustment_index` (ContractModel),
`addendum_type`, `adjustment_index` (ContractAddendum).

### Fix 2: `backend/modules/crm/schemas/contract.py`

3 bugs em `ContractTemplateResponse`:

1. **UUID não serializado:** `@field_validator("id", mode="before")` → `str(v)`
2. **service_type histórico:** `ServiceType | None` → `str | None` (dados 'admissao', 'ferias' pré-enum)
3. **variables dict/list:** `@field_validator("variables", mode="before")` normaliza `{"required": [...]}` → `list[str]`

### Restart

`docker restart conecta-pro-backend` (não `kill -HUP`) aplicado após os fixes.

---

## FASE 3 — Frontend

BUILD_ID `1776721155887` = 2026-04-20 21:39 UTC > último commit CRM.
Nenhum rebuild necessário.

---

## FASE 4 — Testes de Regressão Runtime

Arquivo: `backend/tests/modules/crm/test_cpro11_regressions_real.py`

Estratégia final (3 iterações):
- Abandonado: `ASGITransport` + `asyncpg` → event loop conflict
- Abandonado: `psycopg2` direto → não disponível no container
- **Aplicado:** `sync_engine` (psycopg2 via SQLAlchemy) + `httpx.AsyncClient(base_url="http://127.0.0.1:8080")`

### Resultado FASE 4 GATE

```
======================== 10 passed, 5 warnings in 2.25s ========================
```

| # | Teste | Resultado |
|---|---|---|
| REG-01 | contractstatus enum exists in PG | PASS |
| REG-02 | contractstatus values lowercase | PASS |
| REG-03 | contracts/alerts → 200 | PASS |
| REG-04 | contracts/templates → 200 | PASS |
| REG-05 | proposals/templates routing (não 422) | PASS |
| REG-06 | dashboard/kpis tem todos os 6 campos P0 | PASS |
| REG-07 | mrr nunca NaN | PASS |
| REG-08 | clientes_total > 0 | PASS |
| REG-09 | conversion_rate com leads won | PASS |
| REG-10 | clients endpoint endereco_texto string | PASS |

---

## FASE 5 — Auditoria Final de Endpoints

Todos os 10 endpoints CRM retornam 200:

| Endpoint | Status |
|---|---|
| GET /api/v1/crm/dashboard/kpis | 200 |
| GET /api/v1/crm/leads | 200 |
| GET /api/v1/crm/opportunities | 200 |
| GET /api/v1/crm/proposals | 200 |
| GET /api/v1/crm/proposals/templates | 200 |
| GET /api/v1/crm/contracts | 200 |
| GET /api/v1/crm/contracts/alerts | 200 |
| GET /api/v1/crm/contracts/templates | 200 |
| GET /api/v1/crm/commissions | 200 |
| GET /api/v1/crm/clients | 200 |

---

## Commits

| # | Hash | Descrição |
|---|---|---|
| 1 | e786300039 | docs(cpro11-r1.5): CONTRATO CRM v1.6 — §23.4, §20.8, §28 |
| 2 | 3ede548b | fix(crm): P0.1 contractstatus enum + P0.2 endereco_texto + dashboard KPIs |
| 3 | c38726e3 | fix(gedeon): inclui test_cpro11_regressions_real.py |

---

## CIC Checklist — Resumo

**16/16 checks PASS** (C01-C16)

---

## Descobertas Chesterton (§20.8)

| D# | Descoberta |
|---|---|
| D-R1.5-1 | `docker cp + kill -HUP` NÃO recarrega Python modules — sempre usar `docker restart` |
| D-R1.5-2 | SQLAlchemy `Column(Enum())` usa `.name` por padrão; PG types usam `.value` — sempre usar `values_callable` |
| D-R1.5-3 | `ASGITransport + asyncpg` cria tasks em loops diferentes — usar HTTP real para testes async |
| D-R1.5-4 | Rate limit 5 req/min em `/auth/login` — gerar JWT diretamente via `sync_engine` nos testes |

---

## Self-Check (20/20)

| # | Gate | Status |
|---|---|---|
| 1 | Módulo declarado no início | ✅ crm |
| 2 | Nenhum revert executado | ✅ |
| 3 | Nenhum push para main | ✅ |
| 4 | Diff verificado antes do commit | ✅ |
| 5 | Commits têm [session] [module] | ✅ |
| 6 | Contrato atualizado v1.6 | ✅ |
| 7 | CIC checklist 16/16 | ✅ |
| 8 | FASE 1 gate: root cause identificada | ✅ H1+H2 |
| 9 | FASE 2 gate: fixes aplicados + docker restart | ✅ |
| 10 | FASE 3 gate: frontend BUILD_ID OK | ✅ |
| 11 | FASE 4 gate: 10/10 testes passando | ✅ |
| 12 | FASE 5 gate: 10/10 endpoints 200 | ✅ |
| 13 | Nenhum arquivo fora do escopo modificado | ✅ |
| 14 | Zonas proibidas respeitadas | ✅ |
| 15 | Git push executado | ✅ already up-to-date |
| 16 | Relatório final criado | ✅ este arquivo |
| 17 | values_callable em todos os 5 Column(Enum()) | ✅ |
| 18 | schema UUID stringify validator | ✅ |
| 19 | schema variables normalizer | ✅ |
| 20 | service_type str não enum | ✅ |
