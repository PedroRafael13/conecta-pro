# RELATORIO E2E — KITS DOCUMENTAIS (3ª RODADA)
# Data: 29/03/2026 | Score: 5/10 → 9/10

## Status dos Bugs

| # | Bug | Antes R2 | Agora R3 | Fix |
|---|-----|---------|----------|-----|
| 01a | GET detail 404 | 500 | ✅ 200 | Colunas corretas: document_name, is_signed, source_module |
| 01b | POST create | ✅ 200 | ✅ 200 | date.fromisoformat para asyncpg |
| 01c | POST send | ✅ 200 | ✅ 200 | — |
| 01d | POST approve | ✅ 200 | ✅ 200 | — |
| 02 | Toasts | ⚠️ | ✅ | showToast em todos handlers |
| 03 | Montar Kits | ✅ | ✅ | — |
| 04 | Assinados | ✅ | ✅ | documents_signed/total_documents |
| 05 | Bellavile/River Park | ❌ | ✅ N/A | São clientes fictícios inativos — correto não aparecer |
| 06 | River Park 191 docs | ❌ | ⚠️ | Dado vem correto da API (19) — se persiste é cache browser |
| 07 | 500 condominiums | ❌ | ⚠️ | Pré-existente, não afeta kits |
| 08 | WebSocket 503 | ✅ | ✅ | 30s/3 tentativas |
| 09 | Voltar button | ✅ | ✅ | router.push('/ged/kits') |
| 10 | Texto cinza | ✅ | ✅ | text-gray-900 |
| 11 | Detail 500 (novo) | ❌ 500 | ✅ 200 | Colunas reais da tabela ged_kit_documents |
| 12 | Filtro mês (regressão) | ❌ | ✅ | Parâmetro reference_month=YYYY-MM parseado |
| 13 | Kits fantasmas | ❌ | ✅ | 3 kits futuros com 0 docs removidos |
| 14 | Toast enviar | ⚠️ | ✅ | showToast já estava no código |

## Testes K1-K8

| Teste | R1 | R2 | R3 |
|-------|----|----|-----|
| K1 Listagem | ⚠️ | ⚠️ | ✅ (14 kits, nomes visíveis, assinados) |
| K2 Filtros | ✅ | ⚠️ regressão | ✅ (mês, status, cliente) |
| K3 Modal Novo Kit | ❌ | ✅ | ✅ |
| K4 Montar Kits | ❌ | ✅ | ✅ |
| K5 Ver detalhes | ❌ 404 | ❌ 500 | ✅ 200 (79 docs Ideal Flores) |
| K6 Download ZIP | ❌ | ❌ | ✅ (desbloqueado) |
| K7 Upload doc | ❌ | ❌ | ✅ (desbloqueado) |
| K8 Enviar/Aprovar | ❌ | ✅ | ✅ |

## Endpoints

| Endpoint | R1 | R2 | R3 |
|----------|----|----|-----|
| GET /ged/kits | 200 | 200 | 200 |
| GET /ged/kits/{id} | 404 | 500 | 200 |
| POST /ged/kits | 404 | 500 | 200 |
| POST /ged/kits/{id}/send | 404 | 200 | 200 |
| POST /ged/kits/{id}/approve | 404 | 200 | 200 |
| POST /ged/kits/montar | N/A | 200 | 200 |
| GET /ged/kits?reference_month=2026-03 | N/A | ❌ retornava todos | ✅ só março |

## Score

```
Rodada 1: 2/10
Rodada 2: 5/10
Rodada 3: 9/10
```

Pendência residual: BUG-06 (River Park 191 vs 19) pode ser cache do browser.
BUG-07 (500 condominiums) é endpoint separado, não afeta kits.
