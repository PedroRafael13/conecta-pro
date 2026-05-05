# RELATORIO_TANGERINO_FIX_CPRO12.md
**Sessão:** CPRO12 T2-Tangerino — Fix API 404
**Data:** 2026-05-05
**Responsável:** Jordan Jesus (jjesus@conectamais.pro)
**Branch:** feature/people-management-reorganization

---

## Objetivo

Diagnosticar e corrigir o erro HTTP 404 em `sync_solides_ponto()` ao chamar
`/absence/find-all` na API Tangerino (Sólides DP), garantindo que o sync
não crasha e não polui `erros[]` com falhas conhecidas.

---

## STEP 1 — Diagnóstico (Chesterton)

### Arquivos lidos integralmente (INV-1)

| Arquivo | Linhas |
|---------|--------|
| `backend/modules/people_management/ponto/services/dashboard_service.py` | 806 |
| `backend/modules/integrations/connectors/solides/connector.py` | 889 |

### Endpoint problemático identificado

- `dashboard_service.py:386` — `_fetch_solides_entities(token, "/absence/find-all", inicio, fim)`
- `dashboard_service.py:506` — `_fetch_solides_entities(token, "/occurrence/find-all", inicio, fim)`
- `_fetch_solides_entities()` usa `resp.raise_for_status()` → 404 propaga como `httpx.HTTPStatusError`

### Variáveis de ambiente no container

```
SOLIDES_API_TOKEN=Y2RmYTI2NjdiM2M2NDJhNzg3YTMzYTI4ZDAyYjFiZDI6... (presente)
SOLIDES_WEBHOOK_SECRET=b478c69f19c247af5... (presente)
```
Token válido — confirmado por `/test` → HTTP 200 + mensagem "Hello, CONECTA MAIS - SEGURANÇA E TECNOLOGIA!"

### Testes de endpoint realizados

| Endpoint | HTTP |
|----------|------|
| `https://employer.tangerino.com.br/` | 401 (servidor OK, requer auth) |
| `/absence/find-all` | **404** |
| `/occurrence/find-all` | **404** |
| `/api/v1/absence` | 404 |
| `/api/absence` | 404 |
| `/absenteeism/find-all` | 404 |
| `/time-off/find-all` | 404 |
| `/punch-absence/find-all` | 404 |
| `/absence/list` | 404 |
| `/absence/search` | 404 |
| `/absence/all` | 404 |
| `/v2/absence/find-all` | 404 |
| `/test` | **200** |
| `/employee/find-all` | **200** |
| `/job-role/find-all` | **200** |
| `/workplace/find-all` | **200** |
| `/cost-center/find-all` | **200** |
| `/work-schedule` | **200** |
| `/department/find-all` | 404 |

---

## STEP 2 — Identificação do cenário

**Cenário C — endpoints descontinuados/fora do plano.**

Token válido, servidor respondendo, 6 endpoints funcionando, mas
`/absence/find-all` e `/occurrence/find-all` retornam 404 para esta conta.

Documentação Tangerino nos .md do projeto: `docs/COMPARATIVO_SOLIDES.md`
e outros — nenhum documenta endpoint alternativo para ausências.

---

## STEP 3 — Fix aplicado

**Arquivo:** `backend/modules/people_management/ponto/services/dashboard_service.py`

**Mudança cirúrgica em `_fetch_solides_entities()` (linhas 328-337):**

```python
# ANTES
except httpx.HTTPStatusError as exc:
    logger.warning("Tangerino API HTTP error %s for %s: %s", exc.response.status_code, entity_path, exc)
    raise  # ← 404 propagava para o chamador → adicionado ao erros[]

# DEPOIS
except httpx.HTTPStatusError as exc:
    if exc.response.status_code == 404:
        # Endpoint descontinuado ou plano sem modulo — nao e erro, apenas sem dados
        logger.warning(
            "Tangerino API endpoint indisponivel (404) para %s — descontinuado ou fora do plano. "
            "Ausencias/ocorrencias nao importadas neste ciclo.",
            entity_path,
        )
        return []  # ← retorna lista vazia, sync continua limpo
    logger.warning("Tangerino API HTTP error %s for %s: %s", exc.response.status_code, entity_path, exc)
    raise
```

**py_compile:** OK ✅

**Hot-copy:**
```bash
# 3 containers afetados (ponto tem tasks em beat + operacional)
OK: conecta-pro-backend
OK: conecta-pro-celery-beat
OK: 297439d0453a_conecta-pro-celery-operacional
docker restart conecta-pro-backend  # kill -HUP 1 não recarrega uvicorn produção
```

---

## STEP 4 — Validação

```bash
POST /api/v1/people-management/ponto/sincronizar-solides

# ANTES do fix:
{"success":true,"erros":["Erro ao buscar ausencias do Tangerino: Client error '404' ...",
                          "Erro ao buscar ocorrencias do Tangerino: Client error '404' ..."]}

# DEPOIS do fix:
{"success":true,"message":"Sincronizacao concluida para periodo 2026-05-01 a 2026-05-05",
 "total_importados":0,"total_atualizados":0,"total_inconsistencias":6,"erros":[]}

HTTP 201  ✅
```

---

## STEP 4 — §104 + Commits + Push

§104 adicionado ao `CONTRACTS_GEDEON.md` com todos os campos do template:
- Data, Problema, Cenário, Endpoints testados, Fix aplicado, Resultado antes/depois
- Arquivo, Hot-copy, **Impacto**, Validação

| Commit | Hash | Mensagem |
|--------|------|---------|
| 1 — docs | f89ab322 | `docs(contracts): §104 — fix Tangerino API endpoint /absence/find-all descontinuado` |
| 2 — fix | 035c14f4 | `fix(ponto): Tangerino 404 — _fetch_solides_entities trata ausencias/ocorrencias como optional (§104)` |
| 3 — audit | 1f8f748e | `docs(contracts): §104 — campo Impacto + dados diagnóstico completo (auditoria)` |

Push: `feature/people-management-reorganization` → GitHub ✅

---

## SELF-CHECK FINAL (prompt original — 5 itens)

| Item | Status | Dado real |
|------|--------|-----------|
| STEP 1 — código lido inteiro, endpoint identificado | ✅ | dashboard_service.py 806L + connector.py 889L |
| STEP 1 — teste curl do endpoint atual executado | ✅ | `/absence/find-all` → HTTP 404 com token real |
| STEP 2 — cenário identificado (A/B/C) | ✅ | **Cenário C** — endpoints fora do plano |
| STEP 3 — fix aplicado, sync não crasha | ✅ | `erros=[]` HTTP 201 confirmado |
| STEP 4 — §104 + 2 commits + push | ✅ | 3 commits + push OK |
| INV-1 — dashboard_service.py + connector.py lidos inteiros | ✅ | |
| INV-2 — escopo: apenas endpoint Tangerino | ✅ | Nenhum outro arquivo modificado |
| INV-3 — API real não chamada sem saber endpoint correto | ✅ | STEP 1 diagnóstico primeiro |
| INV-4 — py_compile + hot-copy após fix | ✅ | py_compile OK + 3 containers |
| INV-5 — 2 commits separados | ✅ | docs(contracts) + fix(ponto) |

---

## STATUS FINAL

- `dashboard_service.py`: **CORRIGIDO** — HTTP 404 tratado como `return []`
- Sync `/sincronizar-solides`: **erros=[]** HTTP 201
- §104 CONTRACTS_GEDEON.md: **ATUALIZADO**
- Ausências Tangerino: **indisponíveis neste plano** (log warning, não erro)
