# T1 — Diagnóstico GED / Completude dos Kits
**Data:** 2026-05-06
**Branch:** feature/people-management-reorganization
**Tipo:** DIAGNÓSTICO — estado atual da completude dos kits documentais

---

## RESUMO EXECUTIVO

| Métrica | Valor |
|---------|-------|
| Clientes com kits (2026) | 10 |
| Melhor completude | 35.2% (Gelain) |
| Pior completude | 0% (Parise Village, Green Hills) |
| Tipos de documento com 0% | 22 de 38 tipos |
| Onvio: docs não processados | 436+ (100% não processados) |
| Auto-assemble | ✅ funcional — criou 382 slots em 8 kits |

---

## STEP 1 — COMPLETUDE POR CONDOMÍNIO (hoje)

| Condomínio | Total Slots | Com Arquivo | Sem Arquivo | % Completo |
|------------|-------------|-------------|-------------|------------|
| Parque Residencial Gelain | 71 | 25 | 46 | **35.2%** |
| Edifício Michelangelo | 88 | 28 | 60 | 31.8% |
| Villa Dei Fiori | 223 | 62 | 161 | 27.8% |
| Mirante das Flores | 343 | 91 | 252 | 26.5% |
| Villa dos Pássaros | 133 | 33 | 100 | 24.8% |
| Laranjeiras Village | 207 | 48 | 159 | 23.2% |
| **Ideal Flores da Cidade** | **304** | **69** | **235** | **22.7%** |
| Prime Arena | 217 | 47 | 170 | 21.7% |
| Parise Village | 2 | 0 | 2 | 0.0% |
| Green Hills | 2 | 0 | 2 | 0.0% |
| **TOTAL** | **1.590** | **403** | **1.187** | **~25.3%** |

**Nenhum cliente está acima de 36%.** A completude global é ~25%.

---

## STEP 2 — TOP TIPOS DE DOCUMENTO COM MAIS SLOTS VAZIOS

| Tipo | Total | Preenchidos | Vazios | % |
|------|-------|-------------|--------|---|
| contracheque | 193 | 58 | **135** | 30% |
| escala_mes | 153 | 51 | **102** | 33% |
| comprovante_vr | 153 | 51 | **102** | 33% |
| comprovante_va | 153 | 51 | **102** | 33% |
| comprovante_vt | 153 | 51 | **102** | 33% |
| comp_salario_individual | 47 | 0 | **47** | 0% |
| folhas_ponto | 47 | 0 | **47** | 0% |
| comp_vt_individual | 46 | 0 | **46** | 0% |
| comp_va_solides | 46 | 0 | **46** | 0% |
| ficha_empregado | 40 | 0 | **40** | 0% |
| contrato_trabalho | 40 | 0 | **40** | 0% |
| comp_vt_va_combinado | 40 | 0 | **40** | 0% |

**Atenção:** `folha_ponto` está em 61.4% (94/153) — o melhor desempenho.
Tipos com 0% são todos de source `gedeon` — indicam que o parser/kit builder Gedeon
cria os slots mas não popula os arquivos.

---

## STEP 3 — IDEAL FLORES DETALHADO

### Mês 2026-03 (março)
| Tipo | Slots | Com Arquivo | Fonte | Status |
|------|-------|-------------|-------|--------|
| folha_ponto | 9 | 8 | dp | ✅ quase completo |
| folha_pagamento | 1 | 1 | gedeon | ✅ OK |
| contracheque (gedeon) | 1 | 1 | gedeon | ✅ OK |
| contracheque (dp) | 9 | 0 | dp | ❌ vazio |
| comprovante_vr/vt/va | 9×3 | 0 | dp | ❌ vazio |
| escala_mes | 9 | 0 | operacoes | ❌ vazio |
| cnd_* (5 certidões) | 5 | 0 | fiscal | ❌ vazio |

### Mês 2026-04 (abril) — Pior mês
**45 tipos de slot, 1 com arquivo (0%)**
- Todos os slots de source `gedeon` → 0% preenchidos
- Todos os slots de source `dp` → 0% preenchidos
- Todos os slots de source `fiscal` → 0% preenchidos
- Todos os slots de source `operacoes` → 0% preenchidos

### Mês 2026-05 (maio) — Melhor mês
**Todos os slots de source `dp` e `fiscal` → 100% preenchidos**
- `contracheque`, `comprovante_va/vr/vt`, `folha_ponto`, `escala_mes` → todos com arquivo
- `cnd_estadual/municipal/federal`, `cndt_trabalhista`, `crf_fgts` → todos com arquivo

**Conclusão Ideal Flores:** Março e maio têm boa alimentação do módulo `dp` e `fiscal`.
Abril está zerado — possível falha no job de coleta ou ausência de upload naquele mês.
Slots de source `gedeon` nunca preenchidos em nenhum mês.

---

## STEP 4 — FONTES DE DADOS DISPONÍVEIS

### 4a — Onvio Documents

**Total de documentos no Onvio: 500+ (estimativa)**

| Categoria | Disponíveis | Processados | Não Processados |
|-----------|-------------|-------------|-----------------|
| outros | 157 | 0 | **157** |
| folha_pagamento | 69 | 0 | **69** |
| recibo_folha | 68 | 0 | **68** |
| documento_digitalizado | 26 | 0 | **26** |
| das_simples_nacional | 21 | 0 | **21** |
| guia_issqn | 20 | 0 | **20** |
| parcelamento_simples | 20 | 0 | **20** |
| contrato_trabalho | 16 | 0 | **16** |
| ficha_registro | 14 | 0 | **14** |
| dctfweb_declaracao | 12 | 0 | **12** |
| fgts_relatorio | 12 | 0 | **12** |
| fgts_guia | 12 | 0 | **12** |

**⚠️ CRÍTICO: 100% dos documentos Onvio estão `processado = false`.**
Nenhum documento Onvio foi vinculado ao kit. O auto-assemble reportou `onvio_matched: 0`.
Os docs estão no banco mas o pipeline de matching Onvio → kit_document está quebrado ou desabilitado.

### 4b — Inter Transactions (HERMES)

| Categoria | Total |
|-----------|-------|
| vt_va_combinado | 433 |
| vale_transporte | 91 |
| salario | 82 |
| vale_alimentacao | 9 |

**Nota:** `kit_document_id` não existe em `inter_transactions` — não há FK de vinculação
Inter → kit_document na estrutura atual do banco. Comprovantes disponíveis mas sem
mecanismo de vinculação ao kit.

### 4c — Folha Ponto

| Total Slots | Com PDF | Sem PDF |
|-------------|---------|---------|
| 153 | 94 (61.4%) | 59 (38.6%) |

Melhor tipo preenchido — fonte `dp` funciona para `folha_ponto`.

---

## STEP 5 — AUTO-ASSEMBLE

### Endpoint

- `POST /api/v1/ged/auto-assemble` → **HTTP 201 ✅**
- `GET /api/v1/ged/auto-assemble` → **405 Method Not Allowed** (GET não existe, só POST)

### Resultado do POST (execução ao vivo)

```json
{
  "reference_month": "2026-05-01",
  "total_clients": 11,
  "kits_created": 8,
  "kits_updated": 0,
  "total_documents": 382,
  "onvio_matched": 0,
  "errors": []
}
```

**O auto-assemble funciona** — cria kits e slots corretamente.
**Bloqueio identificado:** `onvio_matched: 0` — matching Onvio → slot zerado.

### Métodos do controller (`auto_assemble_controller.py`)

| Endpoint | Método |
|----------|--------|
| `POST /auto-assemble` | `auto_assemble_kits` |
| `GET /kits` | `list_kits` |
| `GET /kits/summary` | `kits_summary` |
| `GET /kits/{kit_id}` | `get_kit_detail` |
| `POST /kits` | `create_kit` |
| `POST /kits/{kit_id}/send` | `send_kit` |
| `POST /kits/{kit_id}/enviar` | `enviar_kit` |
| `POST /kits/{kit_id}/approve` | `approve_kit` |
| `POST /kits/montar` | `montar_kits` |
| `GET /dashboard` | `ged_dashboard` |

---

## DIAGNÓSTICO CONSOLIDADO — O QUE ESTÁ BLOQUEANDO

| Bloqueio | Impacto | Evidência |
|---------|---------|-----------|
| **Onvio matching zerado** | ~500 docs disponíveis, 0 vinculados | `onvio_matched: 0` + `processado=false` em todos |
| **Source `gedeon` não popula arquivos** | 22 tipos de doc em 0% | Slots criados com `source=gedeon` mas `file_path=NULL` |
| **Inter → kit sem FK** | Comprovantes de salário/VT/VA não chegam ao kit | `kit_document_id` ausente em `inter_transactions` |
| **Abril Ideal Flores: 0%** | Mês inteiro zerado | Nenhum slot preenchido em nenhuma fonte |
| **Certidões fiscais (cnd_*)** | 0% em março/abril | Fonte `fiscal` não alimentou esses meses |

---

## SELF-CHECK

| Item | Status |
|------|--------|
| TOKEN obtido | ✅ |
| DB container identificado (`conecta-pro-postgres`) | ✅ |
| STEP 1 — completude por condomínio | ✅ |
| STEP 2 — breakdown por tipo de documento | ✅ |
| STEP 3 — Ideal Flores detalhado | ✅ |
| STEP 4a — Onvio docs disponíveis | ✅ |
| STEP 4b — Inter transactions categorias | ✅ |
| STEP 4c — folha_ponto slots | ✅ |
| STEP 5 — auto-assemble endpoint | ✅ funcional |
| STEP 5 — arquivos auto_assemble localizados | ✅ |
| STEP 5 — métodos do controller lidos | ✅ |

---

**Diagnóstico completo. Completude global ~25%. Principal bloqueio: matching Onvio → kit com `onvio_matched: 0` (100% dos docs Onvio não processados). Auto-assemble funcional mas não vincula docs.**

---

## AUDITORIA — ACHADOS ADICIONAIS (2ª passagem)

### STEP 4b — Query original falhou (coluna ausente)

A query prescrita no prompt usa `it.kit_document_id` que **não existe** em `inter_transactions`:

```sql
-- ERRO: column it.kit_document_id does not exist
COUNT(*) FILTER (WHERE it.kit_document_id IS NOT NULL) as vinculados,
```

Não há FK de vinculação `inter_transactions → ged_kit_documents` na estrutura atual.
Comprovantes Inter disponíveis (433 vt_va_combinado, 91 VT, 82 salário, 9 VA) mas
**sem mecanismo de linkagem ao kit** — feature não implementada.

### STEP 5 — Leitura do service (head -1 pegou arquivo errado)

O comando `find ... | head -1` retornou `main_production.py` (não o controller).
Arquivo correto: `modules/ged/controllers/auto_assemble_controller.py`.
Análise correta: `auto_assemble_kits` chama `KitBuilderService.auto_build_all_kits`
→ `_match_onvio_docs`.

### Root cause real do `onvio_matched: 0`

**Não é bug de matching — é ausência de dados para o mês corrente.**

O `_match_onvio_docs` busca:
```sql
WHERE condominio_id = ANY(matching_cond_ids)
  AND mes_ref = '05.2026'          ← mês atual
  AND caminho_local IS NOT NULL
```

| mes_ref | Docs disponíveis |
|---------|-----------------|
| 01.2026 | 27 |
| 02.2026 | 29 |
| 03.2026 | 43 |
| 04.2026 | 10 |
| **05.2026** | **0** ← nenhum doc sincronizado ainda |

O matching funciona corretamente. O job de sync Onvio simplesmente ainda
não importou documentos de maio/2026. Quando chegarem, o auto-assemble
os vinculará automaticamente.

### Confirmações adicionais

- `onvio_documents.caminho_local`: 605/605 preenchidos (0 NULL) — sync OK
- `onvio_documents.condominio_id`: 116 docs vinculados a condomínios
- `condominios` ativos: 11
- Matching por palavras significativas (subset): funciona corretamente
  (ex: "MICHELANGELO" ∈ "CONDOMINIO DO EDIFICIO MICHELANGELO")

### Diagnóstico consolidado REVISADO

| Bloqueio | Impacto | Evidência | Gravidade |
|---------|---------|-----------|-----------|
| Onvio maio/2026 não sincronizado | onvio_matched=0 para mês atual | 0 docs com mes_ref='05.2026' | ⚠️ Temporal |
| Source `gedeon` não popula slots individuais | 22 tipos em 0% | file_path=NULL nos slots criados pelo kit builder Gedeon | 🔴 Funcional |
| Inter → kit sem FK | Comprovantes não chegam ao kit | kit_document_id ausente em inter_transactions | 🔴 Feature ausente |
| Abril Ideal Flores: 0% | Mês inteiro zerado | Nenhuma fonte alimentou em abril | 🟡 Investigar |
