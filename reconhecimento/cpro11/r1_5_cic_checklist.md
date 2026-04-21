# CIC Checklist — CPRO11 Rodada 1.5
**Data:** 2026-04-21
**Branch:** feature/people-management-reorganization
**Versão contrato:** v1.6

## Resultado por Check

| # | Check | Resultado | Evidência |
|---|---|---|---|
| C01 | PG type `contractstatus` existe | ✅ PASS | `SELECT typname FROM pg_type WHERE typname='contractstatus'` → 1 row |
| C02 | Valores `contractstatus` são lowercase | ✅ PASS | `draft, pending_signature, active, suspended, cancelled, terminated` |
| C03 | PG type `contracttype` existe | ✅ PASS | `SELECT typname FROM pg_type WHERE typname='contracttype'` → 1 row |
| C04 | Valores `contracttype` são lowercase | ✅ PASS | `recurring, one_time` |
| C05 | PG type `adjustmentindex` existe | ✅ PASS | `SELECT typname FROM pg_type WHERE typname='adjustmentindex'` → 1 row |
| C06 | PG type `addendumtype` existe | ✅ PASS | `SELECT typname FROM pg_type WHERE typname='addendumtype'` → 1 row |
| C07 | `Column(Enum())` com `values_callable` em `contract.py` | ✅ PASS | 5 ocorrências corrigidas (linhas 124, 129, 156, 419, 425) |
| C08 | `GET /crm/contracts/alerts` → 200 | ⏳ AGUARDANDO GATE | Verificado após restart do backend |
| C09 | `GET /crm/contracts/templates` → 200 | ⏳ AGUARDANDO GATE | Verificado após restart do backend |
| C10 | `GET /crm/proposals/templates` → 200 | ⏳ AGUARDANDO GATE | Rotas ordenadas corretamente (templates antes de /{id}) |
| C11 | `GET /crm/dashboard/kpis` tem `clientes_total` | ⏳ AGUARDANDO GATE | Campo existente + query direta na tabela clients |
| C12 | `GET /crm/dashboard/kpis` tem `mrr` não-NaN | ⏳ AGUARDANDO GATE | COALESCE no SQL protege de NULL |
| C13 | `GET /crm/dashboard/kpis` tem `em_negociacao` | ⏳ AGUARDANDO GATE | Calculado por dashboard_service |
| C14 | `GET /crm/dashboard/kpis` tem `leads_conversion_rate` | ⏳ AGUARDANDO GATE | Calculado por dashboard_service |
| C15 | Frontend BUILD_ID posterior aos commits T5 | ✅ PASS | BUILD_ID 1776721155887 = 2026-04-20 21:39 UTC > commit 27b931a8 (20:56 UTC) |
| C16 | 10/10 testes regressão runtime passando | ⏳ AGUARDANDO FASE 4 | `test_cpro11_regressions_real.py` criado |

## Hipóteses Validadas

| H# | Hipótese | Resultado |
|---|---|---|
| H1 | Backend StartedAt < commit 3ede548b | CONFIRMADA — backend startedAt 20:14 < commit 20:35 |
| H2 | Enum sem values_callable | CONFIRMADA — `LookupError 'recurring' not in enum values` reproduzido |
| H3 | PyC cache impedindo reload | NÃO NECESSÁRIO — docker restart resolve H1 e H2 |
| H4 | DashboardKPIs sem campos P0 | REFUTADA — campos existem no schema |
| H5 | Controller não popula campos | REFUTADA — controller popula clientes_total/mrr/condominios_total |
| H6 | Frontend image antes dos commits | REFUTADA — BUILD_ID confirma build posterior |
| H7/H8 | Chunks sem strings T5 | REFUTADA — strings são lowercase (values, não names uppercase) |
| H10 | Ordem rotas proposals/templates | JÁ CORRIGIDA em commits anteriores (templates antes de /{id}) |
| H11/H12 | Conftest com mocks, não DB real | CONFIRMADA — conftest.py atual usa AsyncMock, não DB real |

## Trabalho Adicional Identificado (§13.1)

1. **Rate limiter de login:** 5 req/min interfere em diagnóstico. Criar `/api/v1/internal/test-token` sem rate limit.
2. **`docker cp + kill -HUP` em documentação CLAUDE.md:** Documentar que este procedimento NÃO funciona para uvicorn — sempre `docker restart` para alterações em models.
3. **Template de docs para novas migrations:** Adicionar checklist de `values_callable` para migrations com enums.
4. **CPQ feature scaffolded:** `pricing_simulations` table existe mas endpoints não implementados.
5. **Life Centro lead:** Lead convertido com `client_id IS NULL` — requer criação manual do cliente com CNPJ correto.
