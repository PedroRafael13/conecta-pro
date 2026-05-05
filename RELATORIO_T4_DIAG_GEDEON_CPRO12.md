# T4 CPRO12 — Diagnóstico Profundo GEDEON
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Tipo:** READ-ONLY (INV-2: zero alterações de código)
**Executor:** Claude Sonnet 4.6 [session: t4] [module: gedeon]

---

## 1 — Arquitetura dos Agentes GEDEON

O módulo GEDEON possui 4 agentes em `backend/modules/gedeon/agents/`:

| Agente | Arquivo | Responsabilidade | É matching? |
|--------|---------|------------------|-------------|
| KRONOS | `kronos.py` (401 linhas) | Alertas de vencimento de certidões + ASOs (janelas 60d/30d/15d/7d/CRÍTICO) | ❌ |
| THEMIS | `themis.py` (192 linhas) | Monitoramento de assinaturas pendentes (limites 48h=alto / 72h=crítico) | ❌ |
| ATLAS  | `atlas.py` (312 linhas) | Aprendizado de histórico de kits (`gedeon_kit_history`, `gedeon_client_patterns`) | ❌ |
| SOPHIA | `sophia.py` | Assistente IA (NLP, busca semântica de documentos) | ❌ |

**Conclusão:** nenhum dos 4 agentes GEDEON faz matching de documentos Onvio para kits.

---

## 2 — Quem faz o matching hoje

O matching é feito por **dois serviços separados**, não por agentes:

### 2a — `OnvioDocScopeClassifier` (`gedeon/services/onvio_doc_scope_classifier.py`, 272 linhas)
- Classifica cada `onvio_document` em 3 escopos: `condominio` / `funcionario` / `empresa_matriz`
- Matching por regex no `nome_arquivo`:
  - `match_condominio()`: 10 padrões fixos por condomínio (ideal_flores, mirante, laranjeiras, prime_arena, villa_dei_fiori, villa_passaros, michelangelo, gelain, green_hills, parise)
  - `match_employee()`: primeiro+segundo nome do funcionário no filename
  - `is_matriz()`: CNPJ `35\.710\.481` ou "conecta mais"
- **NÃO usa CPF** — matching exclusivamente por nome no filename
- `CATEGORIA_TO_SCOPE`: 34 mapeamentos categoria → escopo

### 2b — `KitBuilderService` — módulo `people_management/ged` (`kit_builder_service.py`)
- `MAPA_TIPOS_ONVIO` (19 categorias): converte `onvio_documents.categoria` → `document_type` em `ged_kit_documents`
- `auto_build_all_kits(reference_month)`: orquestra criação de kits para todos os clientes ativos
- `build_kit_for_client(client_id, reference_month)`: coleta payslips, time_sheets, benefit_receipts, certidões, escalas via DP+Fiscal
- `get_employees_for_client(client_id)`: JOIN `employee_alocacoes` → retorna funcionários alocados ao cliente

### 2c — `KitBuilderService` — módulo `gedeon` (`gedeon/services/kit_builder_service.py`)
- `CategoriaToTipoDocumento` (23 mapeamentos): diferente do mapa anterior — para completude/scoring
- `build_completude(condominio_id, mes_ref)`: calcula % de completude do kit por condomínio + mês
- Usa `employee_alocacoes` para listar funcionários do condomínio

---

## 3 — Como deveria ser implementado (lacunas)

| # | Lacuna | Impacto | Recomendação |
|---|--------|---------|--------------|
| L1 | `referente_a_employee_id` ausente em 566/605 docs (93,6%) | Docs `funcionario`-scope não vinculam a funcionário específico | Preencher via `match_employee()` + JOIN `employees` na re-classificação |
| L2 | Apr/2026: 10 docs, 10 com `doc_scope=NULL` | Nenhum doc de abr/2026 pode ser casado com kit | Executar scope classifier (endpoint `/onvio/reclassify`) nos 169 docs sem scope |
| L3 | Sem função retroativo/backfill | Fev/2026 tem 0 kits construídos apesar de 29 docs disponíveis | Criar endpoint `POST /gedeon/auto-build?mes_ref=02.2026&force=true` |
| L4 | `MAPA_TIPOS_ONVIO` cobre 19/38 categorias (50%) | ~316 docs em categorias não mapeadas ficam como `outro` ou ignorados | Expandir MAPA com as 19 categorias restantes (pós T5 expansão) |
| L5 | Matching por regex no nome_arquivo (frágil) | Novos condomínios requerem edição manual de `match_condominio()` | Médio prazo: lookup por CNPJ no filename (regex `\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}`) |

---

## 4 — Estado do DB (STEP 5)

### Kits por mês de referência
| reference_month | Kits | Statuses |
|-----------------|------|----------|
| 2026-03-01 | 8 | 7 em_montagem + 1 enviado |
| 2026-04-01 | 10 | 10 em_montagem |
| 2026-05-01 | 11 | 11 em_montagem |
| **2026-02-01** | **0** | **Sem kits construídos** |

### Documentos por tipo em `ged_kit_documents` (top 20)
| document_type | Total | Com arquivo | Sem arquivo |
|---------------|-------|-------------|-------------|
| contracheque | 186 | 51 | 135 |
| comprovante_vt | 153 | 51 | 102 |
| comprovante_vr | 153 | 51 | 102 |
| comprovante_va | 153 | 51 | 102 |
| folha_ponto | 153 | 51 | 102 |
| escala_mes | 153 | 51 | 102 |
| comp_salario_individual | 47 | 0 | 47 |
| folhas_ponto | 47 | 0 | 47 |
| comp_va_solides | 46 | 0 | 46 |
| comp_vt_individual | 46 | 0 | 46 |
| contrato_trabalho | 40 | 0 | 40 |
| cnd_municipal | 24 | 8 | 16 |
| cnd_federal | 24 | 8 | 16 |
| cnd_estadual | 24 | 8 | 16 |
| crf_fgts | 24 | 8 | 16 |
| cndt_trabalhista | 24 | 8 | 16 |
| folha_pagamento | 14 | 7 | 7 |

**Padrão:** tipos coletados via DP (contracheque, ponto, escala) têm arquivo em 51/153 (33%). Tipos via Onvio (comp_salario_individual, folhas_ponto, etc.) têm 0 arquivos vinculados.

---

## 5 — 3 meses retroativos (STEP 7)

### `onvio_documents` por mes_ref
| mes_ref | Total | condominio | funcionario | empresa_matriz | sem_scope |
|---------|-------|------------|-------------|----------------|-----------|
| 02.2026 | 29 | 22 | 2 | 4 | 1 |
| 03.2026 | 43 | 26 | 3 | 14 | 0 |
| 04.2026 | 10 | 0 | 0 | 0 | 10 |

### Análise retroativo

**Fevereiro/2026:**
- 29 docs disponíveis no Onvio; 22 com scope `condominio`, 2 `funcionario`
- **0 kits construídos** — nunca foi executado `auto_build_all_kits(date(2026,2,1))`
- Ação: `POST /people-management/ged/auto-assemble?reference_month=2026-02-01` (HTTP 201 esperado)

**Março/2026:**
- 43 docs disponíveis; 26 condominio, 3 funcionario, 14 empresa_matriz
- 8 kits já criados (7 em_montagem, 1 enviado); completude parcial (total_pct=107)
- Ação: re-executar `auto_build_all_kits(date(2026,3,1))` para complementar slots vazios

**Abril/2026:**
- 10 docs — mas **todos com `doc_scope=NULL`** (10 sem scope)
- 10 kits criados, todos em_montagem, completude=5,7% média
- **Bloqueio:** sem scope classification esses docs não podem ser casados via `build_completude()`
- Ação 1: executar scope classifier nos 10 docs de abr/2026 (`POST /api/v1/onvio/reclassify?mes_ref=04.2026`)
- Ação 2: re-executar `auto_build_all_kits(date(2026,4,1))`

---

## 6 — Resumo executivo

**O matching GEDEON hoje:**
- Feito por dois serviços (`OnvioDocScopeClassifier` + `KitBuilderService`) — não por agentes
- KRONOS/THEMIS/ATLAS/SOPHIA são agentes de monitoramento/alertas/aprendizado — sem papel no matching
- Pipeline: Onvio sync → scope classifier (regex filename) → auto_build_all_kits → kits em `ged_document_kits`

**Capacidades confirmadas:**
- Scope classification por regex filename ✅
- Mapeamento categoria→doc_type via `MAPA_TIPOS_ONVIO` (19 cats) ✅
- `auto_build_all_kits()` para um mes_ref específico ✅
- JOIN `employee_alocacoes` para funcionários por condomínio ✅
- Alertas KRONOS (certidão) + THEMIS (assinatura) ✅

**Lacunas críticas para retroativos:**
- L1: 93,6% dos docs sem `referente_a_employee_id` → docs funcionario não vinculam ao funcionário ❌
- L2: 10 docs abr/2026 com `doc_scope=NULL` → bloqueio total para abr ❌
- L3: Fev/2026 tem 0 kits → nunca foi executado auto_build para esse mês ❌

**Plano de execução retroativos (sem code change):**
1. `POST /api/v1/onvio/reclassify` para os 169 docs com scope=NULL (incluindo abr/2026)
2. `POST /people-management/ged/auto-assemble?reference_month=2026-02-01`
3. `POST /people-management/ged/auto-assemble?reference_month=2026-03-01`
4. `POST /people-management/ged/auto-assemble?reference_month=2026-04-01` (após passo 1)

---

Commit: (a adicionar)

T4 CPRO12 DIAGNÓSTICO OK — GEDEON matching e retroativos mapeados.
