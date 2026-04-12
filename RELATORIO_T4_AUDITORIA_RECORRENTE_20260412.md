# Auditoria T4 — PIX Recorrente: Prompt 100% Executado
**Data:** 2026-04-12
**Auditor:** Claude Code — auditoria pós-entrega linha por linha
**Veredicto:** ✅ 100% DO PROMPT IMPLEMENTADO — todos os itens verificados

---

## Checklist Linha por Linha

| # | Item do Prompt | Status | Evidência |
|---|---------------|--------|-----------|
| PASSO 1 | Schema discovery: clients, receivable_accounts | ✅ | Colunas reais mapeadas e adaptadas |
| PASSO 2 | `create_pix_cobv` adicionado a InterAdapter | ✅ | async, PUT /pix/v2/cobv/{txid} |
| PASSO 2 | `list_cobv` adicionado a InterAdapter | ✅ | async, GET /pix/v2/cobv |
| PASSO 3 | `INTER_PIX_KEY` adicionado ao .env | ✅ | 35710481000103 (CNPJ sem pontuação) |
| PASSO 3 | `self._pix_key = os.getenv("INTER_PIX_KEY")` no `__init__` | ✅ | Corrigido na auditoria |
| PASSO 4 | `recurring_billing_service.py` criado | ✅ | syntax OK, MD5 disco=container |
| PASSO 4 | `gerar_cobrancas_mensais(mes, ano, apenas_preview)` | ✅ | Testado: preview + execução real |
| PASSO 4 | Idempotência por `metadata->>'client_id'` | ✅ | 2a chamada: 10/10 ja_cobrados |
| PASSO 5 | `recurring_billing_controller.py` criado | ✅ | 2 endpoints |
| PASSO 5 | `GET /billing/cobrar-recorrente/{mes}/{ano}/preview` | ✅ | Sob prefix /financial |
| PASSO 5 | `POST /billing/cobrar-recorrente/{mes}/{ano}` | ✅ | Sob prefix /financial |
| PASSO 5 | URL completa `/api/v1/financial/billing/...` | ✅ | Corrigido na auditoria |
| PASSO 5 | Registrado em `main_production.py` | ✅ | prefix="/financial" adicionado |
| PASSO 6 | `docker cp` + `docker restart` | ✅ | MD5 disco = MD5 container ✅ |
| PASSO 6 | Health check healthy | ✅ | healthy em ~72s |
| PASSO 6 | Token via `jjesus@conectamais.pro` | ✅ | Jordan Jesus, role: admin |
| PASSO 6 | `GET /financial/billing/.../preview` testado | ✅ | HTTP 200, 10 clientes, R$ 270.586,96 |
| PASSO 7 | `git add` arquivos billing + inter.py | ✅ | staged + committed |
| PASSO 7 | `git add -u` tracked modificados | ✅ | agents/cto/* incluídos |
| PASSO 7 | `git commit` feat(billing) + fix(billing) | ✅ | `ae572531` + `85f3aa5c` |
| PASSO 7 | `git push origin` | ✅ | pushed — 2 commits |

---

## Problemas Encontrados na Auditoria e Corrigidos

### Problema 1 — FK constraint: `receivable_accounts.customer_id` → `customers`
**Causa:** O campo `customer_id` FK aponta para `customers`, não `clients`. UUIDs são diferentes.
**Correção:** `customer_id = NULL` (nullable) + `client_id` em `metadata JSONB`.
**Idempotência:** `WHERE metadata->>'client_id' = %s` em vez de `customer_id`.

### Problema 2 — URL prefix errado: `/billing/` em vez de `/financial/billing/`
**Causa:** Router registrado sem `prefix="/financial"` em `main_production.py`.
**Evidência:** `GET /api/v1/financial/billing/.../preview` retornava HTTP 404.
**Correção:** `api_router.include_router(..., prefix="/financial", ...)`.
**Verificação:** HTTP 200 na URL exata do prompt ✅

### Problema 3 — `self._pix_key` ausente no `__init__` do adapter
**Causa:** Prompt pedia `self._pix_key = os.getenv("INTER_PIX_KEY", "35710481000103")` no `__init__`, mas os métodos async usavam `_os.getenv()` local.
**Correção:** Adicionado `import os` no topo + `self._pix_key` no `__init__`.

### Problema 4 — MD5 mismatch pós-ruff (2x)
**Causa:** ruff reformatou arquivos durante pre-commit hook após cada commit.
**Correção:** Re-executado `docker cp` pós-ruff + `docker restart`.

---

## Testes Finais — URL Exata do Prompt

**Usuário:** `jjesus@conectamais.pro` (Jordan Jesus / admin)

```
GET  http://127.0.0.1:8080/api/v1/financial/billing/cobrar-recorrente/4/2026/preview
→ HTTP 200 ✅
→ modo="preview", total_clientes=10, total_mrr=270586.96, sem_pix_key=[]
```

---

## Banco de Dados — Estado Final

```
receivable_accounts (is_recurring=TRUE, origem=cobranca_automatica, 04/2026):
  COUNT: 10 registros ✅
  TOTAL: R$ 270.586,96 ✅

Clientes cobrados (10 de 10):
  CONDOMINIO DO EDIFICIO MICHELANGELO       R$   8.346,70
  CONDOMINIO IDEAL FLORES DA CIDADE         R$  65.842,42
  CONDOMINIO MIRANTE DAS FLORES             R$  42.255,80
  CONDOMINIO PARQUE RESIDENCIAL GELAIN      R$   6.000,00
  CONDOMINIO PRIME ARENA                    R$  40.466,50
  CONDOMINIO RESIDENCIAL GREEN HILLS        R$     500,00
  CONDOMINIO RESIDENCIAL PARISE VILLAGE     R$   1.700,00
  CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS R$  37.338,33
  CONDOMINIO VILLA DEI FIORI                R$  25.592,71
  RESIDENCIAL LARANJEIRAS VILLAGE           R$  42.544,50
```

---

## Commits Gerados (todos pushed)

```
ae572531  feat(billing): cobrança PIX recorrente mensal — MRR clientes Conecta Mais
85f3aa5c  fix(billing): corrige prefixo URL /financial/billing + _pix_key no adapter
```

Branch: `feature/people-management-reorganization` — pushed ✅

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T4_AUDITORIA_RECORRENTE_20260412.md ~/Downloads/
```
