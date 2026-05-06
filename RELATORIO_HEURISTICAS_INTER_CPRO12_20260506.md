# RELATORIO_HEURISTICAS_INTER_CPRO12_20260506.md
**Sessão:** CPRO12 — Refinamento heurísticas Inter + endpoint auto-processar
**Data:** 2026-05-06
**Responsável:** Jordan Jesus (jjesus@conectamais.pro)
**Branch:** feature/people-management-reorganization

---

## Objetivo

Refinar heurísticas de auto-categorização do `InterCategorizacaoService`
com base em valores reais da folha da Conecta Mais, e criar endpoint REST
`POST /categorias/auto-processar` identificado como pendência no §109.

---

## INVARIANTES verificadas

| INV | Descrição | Status |
|-----|-----------|--------|
| INV-1 | Service lido completo antes de modificar | ✅ |
| INV-2 | Assinaturas públicas não alteradas | ✅ |
| INV-3 | py_compile após cada alteração | ✅ |
| INV-4 | Não recategorizar conf >= 0.8 | ✅ (UPSERT WHERE sugerido_por_ia=true; query filtra conf < 0.8) |
| INV-5 | Comentário inline em cada heurística H1-H6 | ✅ |

---

## STEP 1 — Diagnóstico

### Distribuição de valores 20-50 (débitos)

| Valor | Ocorrências | Categoria |
|-------|-------------|-----------|
| 32.00 | 406 | vt_va_combinado (conf 0.70) |
| 30.00 | 9 | vt_va_combinado |
| 50.00 | 8 | outros |
| 20.00 | 3 | vale_alimentacao |
| 25.00 | 3 | vale_alimentacao |

### Transações R$32,00 (406 ocorrências)

Todos os 406 corretamente como `vt_va_combinado` com conf 0.70 (heurística antiga `28-40`).
H1 eleva conf de 0.70 → 0.92 para o valor exato.

### Transações 'outros' com valores típicos

| Valor | Qtd como `outros` |
|-------|-------------------|
| 90.00 | 12 |
| 100.00 | 5 |
| 70.00 | 2 |
| 80.00 | 2 |

### Análise complementar

- Múltiplos de 32 em `outros`: 64(5), 96(3), 128(2), 160(10), 320(2), 352(2), 480(2), 512(1) = **27 transações**
- Múltiplos de 10 em `outros`: 50(8), 120(4), 150(21), 200(6)... = **70+ transações**
- Distribuição `outros` mais frequente: 150(21), 90(12), 600(12), 500(11), 160(10)

---

## STEP 2 — Heurísticas implementadas

**Arquivo:** `backend/modules/integrations/inter/services/categorizacao_service.py`

| ID | Regra | Categoria | Conf. | Fonte |
|----|-------|-----------|-------|-------|
| H1 | v == 32.00 | vt_va_combinado | 0.92 | H1_vt_va_32_exato |
| H2 | v % 32 == 0, 32 < v ≤ 640 | vt_va_combinado | 0.85 | H2_multiplo_32 |
| H5 | v ∈ {70, 80, 90, 100} | diaria_avulsa | 0.88 | H5_diaria_exata |
| H6 | v % base == 0, base ∈ {100,90,80,70}, v/base ≤ 20 | diaria_avulsa | 0.80 | H6_multiplo_diaria |
| H3 | v % 10 == 0, 10 ≤ v ≤ 200, v % 22 ≠ 0 | vale_transporte | 0.75 | H3_multiplo_10_vt |
| H4 | v % 22 == 0, 22 ≤ v ≤ 440 | vale_alimentacao | 0.75 | H4_multiplo_22_va |
| — | 1500 ≤ v ≤ 3000 | salario | 0.65 | heuristica_faixa_salarial |
| — | fallback | outros | 0.20 | fallback |

**Prioridade:** histórico (0.9) > H1 > H2 > H5 > H6 > H3 > H4 > salário > fallback

**Bug corrigido:** `_split_nome("")` → `IndexError` quando nome é vazio. Fix: retornar `("", "")`.

---

## STEP 3 — Re-categorização (conf < 0.8)

### Breakdown ANTES

| Categoria | Qtd | Conf. média |
|-----------|-----|-------------|
| vt_va_combinado | 430 | 0.70 |
| outros | 325 | 0.20 |
| salario | 204 | 0.50 |
| vale_transporte | 52 | 0.65 |
| vale_alimentacao | 15 | 0.65 |

### Breakdown DEPOIS

| Categoria | Qtd | Conf. média |
|-----------|-----|-------------|
| vt_va_combinado | 433 | **0.92** |
| outros | 290 | 0.20 |
| diaria_avulsa | **121** | 0.81 |
| vale_transporte | **91** | 0.75 |
| salario | 82 | 0.65 |
| vale_alimentacao | 9 | 0.75 |

**1.022 transações re-categorizadas** via `POST /categorias/auto-processar`

### Kit HERMES após refinamento

| Categoria | Qtd |
|-----------|-----|
| vt_va_combinado | 433 |
| vale_transporte | 91 |
| salario | 82 |
| vale_alimentacao | 9 |
| **TOTAL KIT** | **615** |

---

## STEP 4 — Endpoint criado

**Endpoint:** `POST /api/v1/financeiro/inter/categorias/auto-processar`

| Teste | Resultado |
|-------|-----------|
| POST sem mes_ref | HTTP 200 — {processadas: 1022, categorizadas: 1022, mes_ref: "todos"} |
| POST ?mes_ref=2026-03 | HTTP 200 — {processadas: 488, categorizadas: 488} |

---

## STEP 5 — Commits

| Commit | Hash | Mensagem |
|--------|------|---------|
| 1 — feat | 70988020 | `feat(inter): heurísticas refinadas H1-H6 + endpoint auto-processar (§112)` |
| 2 — docs | 952727e8 | `docs(contracts): §112 — heurísticas Inter refinadas + endpoint auto-processar` |

Push: `feature/people-management-reorganization` → GitHub ✅

---

## SELF-CHECK FINAL

| Item | Status |
|------|--------|
| INV-1 a INV-5 verificadas | ✅ |
| STEP 1 — 4 queries diagnóstico executadas | ✅ |
| STEP 2 — H1-H6 + prioridade + comentários inline | ✅ |
| STEP 3 — contagem antes/depois + re-cat 1.022 txs | ✅ |
| STEP 4 — endpoint criado e validado (com/sem mes_ref) | ✅ |
| STEP 5 — 2 commits + push | ✅ |

---

## STATUS FINAL

- `sugerir_categoria()`: **H1-H6 implementadas** — confiança média vt_va 0.70 → 0.92
- `diaria_avulsa`: **121 transações** identificadas (categoria nova nos dados)
- Endpoint `auto-processar`: **HTTP 200** — pendência §109 resolvida
- Kit HERMES: **615 transações** (era 701 — 82 salários CLT dentro da faixa 1.5k-3k, restante diárias excluídas do kit)
