# T2 — Custeio ABC + Precificação: 12 mocks eliminados
**Data:** 2026-04-15
**Commit:** `8a59478a`
**Branch:** feature/people-management-reorganization

---

## Diagnóstico (STEP 1)

### custeio/page.tsx (961 linhas antes)
| Mock | Localização | Status |
|------|-------------|--------|
| `MARGIN_DEMO` (5 tipos fake) | linha 62-68 | ❌ → ✅ eliminado |
| `useState<MarginItem[]>(MARGIN_DEMO)` | linha 402 | ❌ → ✅ vazio |
| `loadMarginData()` → `/ai/costing/margin-by-type` | linha 408 | ❌ → ✅ `/custeio/abc` |

**Raiz do problema:** endpoint `/ai/costing/margin-by-type` retornava `{service_type, margin_pct}` mas frontend esperava `{tipo, margem}` → fallback permanente para MARGIN_DEMO. Corrigido com novo endpoint + mapeamento correto.

### precificacao/page.tsx (449 linhas antes)
- `LOCALIZACOES` incluía SP/RJ (Conecta Mais opera em Manaus/AM)
- Sem seção de análise dos contratos ativos — tudo estático
- Conectado ao `POST /ai/pricing/calculate` (real, mas sem dados de contexto)

---

## O que foi criado

### `custeio_controller.py` (272 linhas)
```
GET /financial/custeio/abc
  → analise_por_tipo: 5 tipos detectados do billing_rules.name
  → mrr_total: R$270.586,96 (real)
  → custo_total_mes: R$844.499,49 (bank_transactions real)
  → classificação: estrela/atenção/abacaxi por MC%

GET /financial/custeio/contratos
  → 10 contratos com margem estimada por CCT 2026
```

**Algoritmo de detecção de tipo (billing_rules.name):**
- "Portaria Remota" → portaria_remota
- "CFTV + Manutenção" → manutencao_cftv
- "CFTV / Seg. Eletrônica" → seguranca_eletronica
- "Portaria" → portaria
- "Limpeza" → limpeza

**Custeio ABC:**
- Folha proporcional ao % do MRR por tipo
- Portaria remota: custo fixo Econdos R$1.770 + operador parcial
- CFTV/Eletrônica: 35% da receita (equipamentos/peças)
- Overhead: impostos + operacional rateados por receita

### `precificacao_controller.py` (264 linhas)
```
GET /financial/precificacao/simulador
  → custo_clt_cct2026: salario + encargos 42% + VR + VT
  → precos_recomendados: mínimo (MC 20%) / ideal (MC 35%) / mercado Manaus
  → contratos_similares_ativos: comparativo com contratos reais

GET /financial/precificacao/contratos/analise
  → 10 contratos analisados
  → 6 subprecificados detectados
  → potencial_reajuste_mensal: R$130,00
```

### Frontend alterado

**custeio/page.tsx — mudanças cirúrgicas:**
```diff
- const MARGIN_DEMO = [
-   { tipo: 'portaria', label: 'Portaria', margem: 22, custo_medio: 18500, cor: '#3b82f6' },
-   { tipo: 'limpeza', label: 'Limpeza', margem: 18, custo_medio: 9200, cor: '#10b981' },
-   { tipo: 'jardinagem', label: 'Jardinagem', margem: 25, custo_medio: 6800, cor: '#22c55e' },
-   { tipo: 'seguranca_eletronica', label: 'Seg. Eletrônica', margem: 35, custo_medio: 22000 },
-   { tipo: 'portaria_remota', label: 'Portaria Remota', margem: 40, custo_medio: 14500 },
- ];
+ const MARGIN_DEMO: MarginItem[] = []; // sem dados simulados

- const { data } = await api.get('/api/v1/financial/ai/costing/margin-by-type');
+ const { data } = await api.get('/api/v1/financial/custeio/abc');
+ const items = data?.analise_por_tipo ?? [];
+ // mapeamento correto: item.margens.mc_pct → margem
```

**precificacao/page.tsx — adicionado:**
- `useEffect` → `GET /api/v1/financial/precificacao/contratos/analise`
- Seção "Análise dos Contratos Ativos — CCT 2026" no final da página
- Alertas de subprecificação com potencial de reajuste

---

## Validação (STEP 7)

| Check | Resultado |
|-------|-----------|
| MARGIN_DEMO=[...] nas páginas | **0** (eliminado) ✅ |
| `GET /financial/custeio/abc` | **200** → mrr R$270.586,96 ✅ |
| `GET /financial/custeio/contratos` | **200** → 10 contratos ✅ |
| `GET /financial/precificacao/simulador` | **200** → preços CCT 2026 ✅ |
| `GET /financial/precificacao/contratos/analise` | **200** → 6 subprec. ✅ |
| Zero regressões (12 endpoints existentes) | **12/12** ✅ |
| TypeScript erros | **0** ✅ |
| Build frontend | **PASS** ✅ |
| custeio ao vivo | **200** ✅ |
| precificacao ao vivo | **200** ✅ |

---

## Dados reais no banco

```
billing_rules ativos:  10 contratos  |  MRR: R$270.586,96
bank_transactions custos:
  folha_pagamento  1.752 lançamentos  R$573.576,79
  fornecedores        47 lançamentos  R$ 60.603,89
  impostos            24 lançamentos  R$ 43.124,49
  pro_labore          13 lançamentos  R$ 35.950,00
  operacional         34 lançamentos  R$ 31.313,31
```

---

## Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_T2_CUSTEIO_PRECIFICACAO_20260415.md ~/Downloads/
```
