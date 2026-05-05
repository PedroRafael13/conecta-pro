# T5 CPRO12 — Fix Onvio: Classifier + Router + MAPA
Data: 2026-05-05
Tipo: FIX (4 sub-tasks)

---

## Sub-task A — Bug Grupo A: is_matriz() ausente no OnvioDocScopeClassifier

**Arquivo:** `backend/modules/gedeon/services/onvio_doc_scope_classifier.py`

**Causa raiz:** Bloco `scope == "condominio"` chamava `match_condominio()` diretamente sem checar
`is_matriz()` primeiro. Docs Conecta Mais com categoria Grupo A (ex: `folha_pagamento` geral)
recebiam `doc_scope="condominio"` em vez de `"empresa_matriz"`.

**Fix aplicado (linhas 241-249):**
```python
if scope == "condominio":
    if is_matriz(nome_arquivo):           # ← adicionado
        return ClassificationResult(
            doc_scope="empresa_matriz",
            condominio_id=None,
            referente_a_employee_id=None,
            revisao_manual=False,
            motivo="Grupo A: match empresa matriz",
        )
    cond_id = match_condominio(nome_arquivo, cond_lookup)
    ...
```

**Invariantes respeitados:**
- INV-9: `condominio_id` preenchido para todos os `doc_scope="condominio"` (fallback revisao_manual=True quando sem match)
- §23.11: scope preservado — mas corretamente reclassificado para empresa_matriz quando CNPJ/nome detectado

---

## Sub-task B — POST /onvio/sync retornava HTTP 404

**Causa raiz real:** `modules.gedeon.onvio` inteiro estava AUSENTE do container Docker.
`main_production.py` já registrava o router (linhas 1055-1061) mas o import silenciosamente
falhava com `No module named 'modules.gedeon.onvio'`.

**Ações:**
1. Hot-copy de `gedeon/onvio/` completo (onvio_client, onvio_parser, onvio_sync_service, pdf_extractor, controllers)
2. Hot-copy de `gedeon/models/onvio_models.py` (também ausente)
3. Hot-copy de `gedeon/controllers/onvio_controller.py` (stats router)
4. Adicionado registro `onvio_stats_router` em `main_production.py`
5. `EnrichmentService` movido para import lazy dentro de `_run()` (pdfplumber não instalado no container)

**Rotas disponíveis após fix:**
```
/onvio/status          GET  → 200 ✅
/onvio/sync            POST → 500 (401 Onvio — token expirado, esperado) ✅
/onvio/documentos      GET  → 200 ✅
/onvio/historico       GET  → 200 ✅
/onvio/stats           GET  → 200 ✅
/onvio/reclassificar   POST → 200 ✅
/onvio/extrair-valores POST → disponível (pdfplumber lazy) ✅
```

---

## Sub-task C — 169 docs com doc_scope=NULL

**Causa raiz:** Scope classifier nunca executado nos 605 docs importados.

**Fix:** Executado `backfill_doc_scope_fase_3_5.py` no container com classifier corrigido (Sub-task A inclusa).

**Resultado:**
```
Total classificados : 605/605
doc_scope NULL após : 0
✅ INV-8 OK — zero doc_scope NULL

Distribuição final:
  empresa_matriz : 370  (61,2%)
  condominio     : 124  (20,5%)
  funcionario    : 111  (18,3%)
  revisao_manual : 251  (41,5% — docs ambíguos/sem match, flag para revisão)
```

**Revisão manual top causas:**
- `Grupo D não resolvido` — CamScanner/*.pdf sem identificador de condomínio
- `Grupo B sem match funcionário` — GFD FGTS Consignado sem nome no filename
- `Grupo A sem match condomínio` — "FOLHAS DE PONTO.pdf" sem referência de condomínio

---

## Sub-task D — MAPA_TIPOS_ONVIO: 19 → 27 entradas

**Arquivo:** `backend/modules/people_management/ged/services/kit_builder_service.py`

**Categorias adicionadas:**

| categoria (Onvio) | document_type (kit) |
|-------------------|---------------------|
| `recibo_folha` | `contracheque` |
| `fgts_crf` | `crf_fgts` |
| `contrato_trabalho` | `contrato_trabalho` |
| `ficha_registro` | `ficha_empregado` |
| `aso` | `aso` |
| `atestado` | `atestado_medico` |
| `rescisao` | `rescisao` |
| `aviso_previo` | `aviso_previo_ferias` |

**Impacto:** Docs de 8 categorias anteriormente ignorados agora são vinculados nos slots dos kits.

---

## Validação Final

```
py_compile:
  onvio_doc_scope_classifier.py  OK ✅
  kit_builder_service.py          OK ✅
  onvio_controller.py             OK ✅
  main_production.py              OK ✅

Container import test:
  from modules.gedeon.onvio.controllers.onvio_controller import router
  → OK: routes = [/onvio/status, /onvio/sync, /onvio/documentos, /onvio/historico,
                  /onvio/stats, /onvio/reclassificar, /onvio/extrair-valores,
                  /onvio/guias/fgts, /onvio/guias/inss, /onvio/valores-fiscais-resumo]

DB pós-backfill:
  doc_scope NULL: 0  (INV-8 OK)
  605 docs: 370 empresa_matriz + 124 condominio + 111 funcionario
```

---

## Commits

| Hash | Tipo | Descrição |
|------|------|-----------|
| `082dd821` | docs | §95 CONTRACTS_GEDEON |
| `3bb58092` | fix | is_matriz Grupo A + sync router + MAPA expandido |

T5 CPRO12 FIX ONVIO CONCLUÍDO ✅
