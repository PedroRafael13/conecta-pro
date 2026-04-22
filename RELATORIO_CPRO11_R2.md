# RELATÓRIO CPRO11-R2 — BrasilAPI Integration
**Data:** 2026-04-22
**Branch:** feature/people-management-reorganization
**Executor:** Claude Sonnet 4.6 [session: tmux-t1] [module: crm]

---

## Resumo Executivo

Implementação completa da integração BrasilAPI para o módulo CRM do Conecta PRO ERP.
Entrega: proxy backend FastAPI + Redis cache + circuit breaker + 3 endpoints REST +
React Query hooks + 3 componentes UI integrados em 3 locais.

**Score Rodada 2: 20/20 ✅**

---

## Arquivos Criados

### Backend (8 arquivos)
| Arquivo | Descrição |
|---------|-----------|
| `backend/modules/integrations/brasilapi/__init__.py` | Package init |
| `backend/modules/integrations/brasilapi/exceptions.py` | `BrasilAPIError`, `NotFound`, `Unavailable`, `InvalidFormat` |
| `backend/modules/integrations/brasilapi/circuit_breaker.py` | 5 falhas/60s → open 120s |
| `backend/modules/integrations/brasilapi/cache.py` | Redis asyncio, JSON, TTL por tipo |
| `backend/modules/integrations/brasilapi/client.py` | httpx async, retry 2x, ViaCEP fallback |
| `backend/modules/integrations/brasilapi/schemas.py` | Pydantic v2, `situacao_cadastral: Any`, validator coords |
| `backend/modules/crm/schemas/enrichment.py` | Response shapes para frontend |
| `backend/modules/crm/controllers/enrichment_controller.py` | 3 endpoints, X-Cache header |

### Frontend (5 arquivos)
| Arquivo | Descrição |
|---------|-----------|
| `frontend/src/types/crm/enrichment.ts` | TypeScript interfaces |
| `frontend/src/hooks/crm/useEnrichment.ts` | React Query hooks (mutation + query) |
| `frontend/src/components/crm/CnpjSearchButton.tsx` | Botão com spinner, PT-BR errors |
| `frontend/src/components/crm/CepAutoFill.tsx` | Input onBlur, inline "buscando…" |
| `frontend/src/components/crm/TaxasWidget.tsx` | Selic/CDI/IPCA, skeleton, cache badge |

### Testes (1 arquivo)
| Arquivo | Descrição |
|---------|-----------|
| `backend/tests/modules/crm/test_enrichment_real.py` | 8 testes reais (sem mock) |

---

## Arquivos Modificados

| Arquivo | Modificação |
|---------|-------------|
| `backend/main_production.py` | Router enrichment registrado em `/api/v1/crm` |
| `frontend/src/components/crm/cliente-form-modal.tsx` | CnpjSearchButton + CepAutoFill + campo CEP |
| `frontend/src/app/modulos/crm/leads/page.tsx` | Campo CNPJ + CnpjSearchButton no form inline |
| `frontend/src/app/modulos/crm/page.tsx` | TaxasWidget inserido |
| `CONTRACTS_CRM_VENDAS.md` | v1.8 → v1.9: §23.7 + §20.11 + §27 linha |

---

## Bugs Encontrados e Corrigidos

### BUG-R2-01: `situacao_cadastral` int vs str
- **Causa:** BrasilAPI retorna `situacao_cadastral: 2` (int, código ATIVA)
- **Efeito:** ValidationError 500 em toda chamada CNPJ
- **Fix:** `situacao_cadastral: Optional[Any] = None`

### BUG-R2-02: `coordinates` dict vazio não é None
- **Causa:** BrasilAPI retorna `"coordinates": {}` (não null) quando sem geo
- **Efeito:** ValidationError no schema CEP
- **Fix:** `field_validator("coordinates")` converte `{}` → `None`

### BUG-R2-03: `CurrentActiveUser` Annotated duplo Depends
- **Causa:** `= Depends()` após tipo Annotated já contém Depends
- **Efeito:** TypeError no FastAPI ao registrar router
- **Fix:** `current_user: CurrentActiveUser` sem `= Depends()`

### BUG-R2-04: `docker cp` não copia novos subdiretórios
- **Causa:** `docker cp modules/` não cria diretórios novos no container
- **Efeito:** Endpoints 404 após hot copy
- **Fix:** `docker exec --user root mkdir -p` + `docker cp` individual + `docker restart`

### BUG-R2-05: Cache Redis com schema inválido
- **Causa:** Dado inválido cacheado antes do fix do schema
- **Efeito:** Retorna 500 mesmo após fix
- **Fix:** `r.delete('brasilapi:cnpj:35710481000103')` manual

---

## Gates

| Gate | Status |
|------|--------|
| FASE 1: módulos importáveis sem erro | ✅ |
| FASE 2: endpoints 200/422/200 + X-Cache HIT | ✅ |
| FASE 3: 8/8 testes reais PASS | ✅ |
| FASE 4: 0 erros TypeScript | ✅ |
| FASE 5: BUILD_ID externo = local | ✅ |
| FASE 6: CIC 16/16 | ✅ |

---

## Self-Check 20/20

| # | Critério | Status |
|---|----------|--------|
| 1 | BrasilAPIClient com get_cnpj/get_cep/get_taxas | ✅ |
| 2 | Redis cache com TTLs diferenciados | ✅ |
| 3 | Circuit breaker 5 falhas → open 120s | ✅ |
| 4 | ViaCEP fallback para CEP | ✅ |
| 5 | `situacao_cadastral: Optional[Any]` | ✅ |
| 6 | `coordinates {}` → None validator | ✅ |
| 7 | X-Cache HIT/MISS header nos endpoints | ✅ |
| 8 | Router registrado em main_production.py | ✅ |
| 9 | TypeScript interfaces para 3 tipos | ✅ |
| 10 | useEnrichCNPJ mutation com erros PT-BR | ✅ |
| 11 | useEnrichCEP mutation com errors PT-BR | ✅ |
| 12 | useTaxasVigentes staleTime 6h | ✅ |
| 13 | CnpjSearchButton integrado em cliente-form-modal | ✅ |
| 14 | CnpjSearchButton integrado em leads/page.tsx | ✅ |
| 15 | CepAutoFill com campo CEP novo em cliente-form-modal | ✅ |
| 16 | TaxasWidget no CRM Dashboard | ✅ |
| 17 | 8/8 testes reais PASS | ✅ |
| 18 | Build Next.js PASS 284 páginas | ✅ |
| 19 | BUILD_ID container = local (conecta-pro-1776872076415) | ✅ |
| 20 | CONTRACTS_CRM_VENDAS.md v1.9 com §23.7 + §20.11 | ✅ |

---

**RODADA 2 COMPLETA: 20/20 ✅**

[session: tmux-t1] [module: crm]
