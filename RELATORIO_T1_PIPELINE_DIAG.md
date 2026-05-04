# T1 — Diagnóstico Pipeline onvio_documents → ged_kit_documents
**Data:** 2026-05-04
**Branch:** feature/people-management-reorganization
**Tipo:** Read-only — zero deploy

---

## CAUSA RAIZ — RESUMO EXECUTIVO

> **O pipeline onvio → ged_kit_documents funciona, mas só roda no dia 21 de cada mês via Celery Beat.**
> Os 592 docs Onvio têm `caminho_local` preenchido. A função `_match_onvio_docs()` lê esse campo
> e preenche `ged_kit_documents.file_path`. Ela só é chamada via `auto_build_all_kits()`,
> agendada para **dia 21 às 07:00** (`ged-auto-collect-monthly`).
> Os 58 docs do sync T2 (2026-05-04) ainda não foram casados porque o próximo auto_build
> é 2026-05-21. O campo `processado` em `onvio_documents` é **vestigial** — nenhum código
> GEDEON o marca como `true`.

---

## STEP 1 — Schema e Contadores

### onvio_documents (592 linhas)

| Campo | Preenchimento |
|-------|---------------|
| `caminho_local` | **592/592 — 100%** — todos preenchidos |
| `doc_scope` | 436/592 (74%) — 156 NULL |
| `processado` | **0/592 = false** — 100% false (campo vestigial) |
| `condominio_id` | parcialmente preenchido (docs scope=condominio) |

### ged_kit_documents (1.237 linhas)

| Campo | Preenchimento |
|-------|---------------|
| `file_path` | **7/1.237 (0,6%)** — 1.230 NULL |
| `source_module` | gedeon (559), dp (496), operacoes (102), fiscal (80) |
| `auto_generated` | maioria=true (placeholders criados por DP) |

### 7 docs com file_path (únicos presentes reais)

| document_type | source_module | file_path | created_at |
|---------------|---------------|-----------|------------|
| folha_pagamento | gedeon | /app/uploads/onvio/outros/2026-04/Folha 03.2026_Prime Arena.pdf | 2026-04-27 02:54 |
| folha_pagamento | gedeon | /app/uploads/onvio/outros/2026-04/Folha 03.2026_Ideal Flores.pdf | 2026-04-27 02:54 |
| folha_pagamento | gedeon | /app/uploads/onvio/outros/2026-04/Folha 03.2026_Villa dos Passaros.pdf | 2026-04-27 02:54 |
| folha_pagamento | gedeon | /app/uploads/onvio/outros/2026-04/Folha 03.2026_Laranjeiras Village.pdf | 2026-04-27 02:54 |
| folha_pagamento | gedeon | /app/uploads/onvio/outros/2026-04/Folha 03.2026_Michelangelo.pdf | 2026-04-27 02:54 |
| folha_pagamento | gedeon | /app/uploads/onvio/inss_guia/2026-04/Folha 03.2026_Mirante das Flores.pdf | 2026-04-27 02:57 |
| folha_pagamento | gedeon | /app/uploads/onvio/outros/2026-04/Folha 03.2026_Villa Dei Fior.pdf | 2026-04-27 02:57 |

**Conclusão STEP 1:** Os 7 docs reais são todos `folha_pagamento 03/2026`, criados em 2026-04-27 por `_match_onvio_docs()`. O módulo `dp` cria 496 placeholders (`auto_generated=true`, `file_path=NULL`) que nunca têm arquivo real associado via onvio.

---

## STEP 2 — Relacionamento entre tabelas

| Item | Status |
|------|--------|
| FK de `ged_kit_documents` → `onvio_documents` | ❌ **Não existe** |
| Coluna `onvio_document_id` em `ged_kit_documents` | ❌ Não existe |
| Coluna `source_record_id` em `ged_kit_documents` | ✅ Existe — mas `NULL` para os 7 docs Onvio |
| Linkagem feita por | **Nome de arquivo fuzzy + categoria** via `_match_onvio_docs()` |

**source_module breakdown (ged_kit_documents):**

| source_module | total | com file_path |
|---------------|-------|---------------|
| gedeon | 559 | **7** |
| dp | 496 | 0 |
| operacoes | 102 | 0 |
| fiscal | 80 | 0 |

---

## STEP 3 — Campo `processado` em onvio_documents

```sql
SELECT COUNT(*) FROM onvio_documents WHERE processado = true;  → 0
SELECT COUNT(*) FROM onvio_documents WHERE processado = false; → 592
```

**Campo vestigial — NUNCA setado pelo pipeline GEDEON.**

Análise do código `onvio_sync_service.py` (linha 148–151):
```python
caminho_local=caminho,
...
processado=False,   # ← inserido sempre como False
```

Nenhum arquivo em `backend/modules/gedeon/` seta `processado=True`. O campo `processado=True`
aparece apenas em `government_integrations/extractors/` (FGTS, eCac, DCTFWeb etc.) — modelo diferente.

**O `processado=false` em 100% dos docs Onvio não é sintoma de falha — é comportamento normal.**

---

## STEP 4 — Código KitBuilderService (GEDEON)

**Arquivo:** `backend/modules/gedeon/services/kit_builder_service.py`

`build_completude()` (linha 200) — usada para o dashboard de completude:
```python
# Lê diretamente de onvio_documents (NÃO de ged_kit_documents)
onvio_rows = self.db.execute(
    "FROM onvio_documents od WHERE ..."
)
```

⚠️ O `KitBuilderService` em `gedeon/services/` lê `onvio_documents` diretamente para calcular
completude — NÃO usa `ged_kit_documents.file_path` como filtro.

O `KitBuilderService` em `people_management/ged/services/` (diferente!) é quem faz o matching:

---

## STEP 5 — Quem insere em ged_kit_documents

| Origem | Arquivo | Método | file_path |
|--------|---------|--------|-----------|
| **Onvio matching** | `people_management/ged/services/kit_builder_service.py` | `_match_onvio_docs()` | `caminho_local` de onvio_documents |
| Auto-assemble DP | `people_management/ged/services/kit_builder_service.py` | `_build_dp_docs()` etc. | `None` (placeholder) |
| Upload manual | `ged/controllers/document_controller.py` | POST upload | path do arquivo enviado |
| Kit PDF gerado | `ged/controllers/kit_pdf_controller.py` | UPDATE | path do PDF gerado |
| Kit Real (boleto etc.) | `ged/controllers/kit_real_controller.py` | INSERT | path do doc |

---

## STEP 6 — onvio_sync_service.py

```python
# O que faz:
caminho_local = f"/app/uploads/onvio/{categoria}/{mes_folder}/{nome_arquivo}"
onvio_doc = OnvioDocument(
    caminho_local=caminho,
    processado=False,   # ← sempre False, nunca atualizado
    ...
)
# O que NÃO faz:
# - NÃO escreve em ged_kit_documents
# - NÃO seta processado=True após download
# - NÃO chama _match_onvio_docs()
```

**onvio_sync_service → apenas baixa PDFs e salva em onvio_documents. Matching é trabalho separado.**

---

## STEP 7 — 7 docs completos: padrão

Todos criados em **2026-04-27 02:54–02:57** pelo `_match_onvio_docs()` chamado por
algum trigger de `auto_build_all_kits()` nesse dia.

`source_record_id` = NULL nos 7 docs → linkagem feita por fuzzy match de nome de cliente,
não por ID de onvio_document. Sem trilha de auditoria direta.

**Categorias mapeadas por MAPA_TIPOS_ONVIO:**

| categoria (onvio) | document_type (ged_kit) | qtd onvio_docs |
|-------------------|------------------------|----------------|
| folha_pagamento | folha_pagamento | **69** |
| dctfweb_recibo | dctfweb_recibo | 11 |
| dctfweb_extrato | dctfweb_extrato | 10 |
| dctfweb_declaracao | dctfweb_declaracao | 12 |
| fgts_guia | gfd_fgts_mensal | 12 |
| fgts_relatorio | relatorio_gfd_fgts | 12 |
| fgts_consignado | comp_pag_fgts | 9 |
| fgts_consignado_relatorio | relatorio_gfd_fgts | 9 |
| **SUBTOTAL mapeável** | | **144** |

**Categorias SEM mapeamento (não casáveis pelo pipeline atual):**

| categoria | qtd | motivo |
|-----------|-----|--------|
| outros | 160 | categoria genérica, sem mapeamento |
| recibo_folha | 68 | per-employee (sem employee_id em onvio_docs) |
| documento_digitalizado | 26 | sem mapeamento |
| das_simples_nacional | 21 | sem mapeamento |
| guia_issqn | 20 | sem mapeamento |
| parcelamento_simples | 20 | sem mapeamento |
| contrato_trabalho | 16 | per-employee |
| ficha_registro | 13 | per-employee |
| + 21 outras categorias | 104 | sem mapeamento ou per-employee |
| **SUBTOTAL não-mapeável** | **448** | — |

---

## STEP 8 — 58 docs T2 em ged_kit_documents?

```sql
-- ged_kit_documents criados após T2 sync (2026-05-04 17:30):
→ 0 registros

-- onvio_documents criados pelo T2 sync:
→ 58 docs, todos processado=false, categoria='outros', doc_scope=NULL
```

**Os 58 docs T2 estão em onvio_documents mas NÃO em ged_kit_documents.**

Motivo: categoria = `outros` → não está em `MAPA_TIPOS_ONVIO` → `_match_onvio_docs()` ignora.
Mesmo se o auto_build rodar em 21/05, esses 58 docs **não serão casados**.

---

## STEP 9 — Tasks Celery que tocam ged_kit_documents

| Task | Schedule | Arquivo |
|------|----------|---------|
| `ged.auto_collect_documents` | **dia 21 de cada mês, 07:00** | `auto_collect_task.py` |

**Fluxo completo:**
```
ged-auto-collect-monthly (Celery Beat, dia 21 07:00)
  → ged_auto_collect_documents()
  → ColetaAutomaticaService.executar()
    → Fase 1: onvio_sync (opcional, se trigger)
    → Fase 2: auto_build_all_kits(mes)  ← AQUI ocorre o matching
      → _build_kit()
        → _match_onvio_docs()  ← seta file_path em ged_kit_documents
    → Fase 3: certidoes
```

**Próxima execução automática:** 2026-05-21 07:00

---

## DECISÃO STEP 9 — Checkboxes

| # | Item | Status |
|---|------|--------|
| ✅ | `processado` nunca é setado `True` — campo vestigial no pipeline Onvio | Confirmado |
| ✅ | `_match_onvio_docs()` é a única função que popula `file_path` via Onvio | Confirmado |
| ✅ | `_match_onvio_docs()` só roda via `auto_build_all_kits()` → Celery dia 21 ou manual | Confirmado |
| ✅ | 58 docs T2 não serão casados: categoria `outros` não está em `MAPA_TIPOS_ONVIO` | Confirmado |
| ✅ | 144 docs mapeáveis (8 categorias), 448 não-mapeáveis por design ou ausência de employee_id | Confirmado |
| ✅ | Próximo auto_build automático: 2026-05-21 07:00 | Confirmado |
| ✅ | `ged_kit_documents` não tem FK para `onvio_documents` — linkagem por fuzzy de nome | Confirmado |
| ⚠️ | `source_record_id` NULL nos 7 docs casados — sem trilha de auditoria do match | Atenção |

---

## SINAIS DE ATENÇÃO

| # | Sinal | Impacto |
|---|-------|---------|
| 🔴 | 448 de 592 docs Onvio (75%) nunca serão casados em `ged_kit_documents` | KitBuilderService sub-reporta completude permanentemente |
| 🟡 | 58 docs T2 (categoria `outros`) sem mapeamento → `MAPA_TIPOS_ONVIO` não cobre `outros` | Sync T2 não contribui para kits |
| 🟡 | `processado` vestigial — confunde leitura do pipeline se consultado | Baixo risco técnico, alto risco de diagnóstico errado |
| 🟡 | `source_record_id` NULL nos docs Onvio matchados — sem rastreabilidade reversa | Dificulta auditoria futura |
| 🟢 | `caminho_local` 100% preenchido (592/592) — base de dados sólida para matching futuro | Pronto para expansão do MAPA_TIPOS_ONVIO |
| 🟢 | Pipeline funcional para 8 categorias mapeadas — 7 docs reais provam que roda | Infra OK |
| 🟢 | Próxima execução automática: 2026-05-21 07:00 | Sem intervenção necessária para meses futuros |

---

## PRÓXIMOS PASSOS (Jordan decide)

1. **Expandir MAPA_TIPOS_ONVIO** — adicionar `outros`, `das_simples_nacional`, `guia_issqn` etc.
   Arquivo: `backend/modules/people_management/ged/services/kit_builder_service.py` linhas 25–37
2. **Disparar auto_build manual** para meses 03–04.2026:
   `POST /api/v1/ged/auto-assemble?mes_ref=2026-04-01`
3. **Reclassificar 156 docs sem doc_scope** (NULL) em `onvio_documents` — separado do pipeline ged_kit
4. **Preencher source_record_id** ao fazer match para rastreabilidade reversa

---

## RESUMO FINAL

| Pergunta | Resposta |
|----------|----------|
| Por que `file_path` NULL em 99% dos docs? | `auto_build_all_kits()` ainda não rodou para a maioria dos meses/condomínios |
| Por que `processado=false` em 592 docs? | Campo vestigial — nenhum código Onvio o atualiza |
| Os 58 docs T2 serão matchados automaticamente? | **Não** — categoria `outros` fora do MAPA_TIPOS_ONVIO |
| O pipeline está quebrado? | **Não** — funcionou em 2026-04-27. Próxima execução: 2026-05-21 |
| Quantos docs são mapeáveis? | 144/592 (24%) — 8 categorias no mapa atual |
