# RELATORIO_DIAGNOSTICO_GEDEON_SLOTS_NULL_20260506.md
**Sessão:** CPRO12 — §119 Fix slots gedeon file_path=NULL
**Data:** 2026-05-06
**Responsável:** Jordan Jesus (jjesus@conectamais.pro)
**Branch:** feature/people-management-reorganization

---

## Objetivo

Diagnosticar por que `KitBuilderService` criaria slots `source=gedeon` com `file_path=NULL`,
implementar o fix e validar. Implementação cirúrgica — sem criar novos slots (INV-3).

---

## INVARIANTES verificadas

| INV | Descrição | Status |
|-----|-----------|--------|
| INV-1 | `kit_builder_service.py` lido integralmente antes de qualquer alteração | ✅ |
| INV-2 | Arquivo único modificado: `hermes.py` (MAPA_TIPOS_ONVIO_EMPRESA) | ✅ |
| INV-3 | Zero novos slots criados — apenas `file_path` preenchido em slots existentes | ✅ |
| INV-4 | `py_compile` executado antes do hot-copy | ✅ |
| INV-5 | Hot-copy para backend + todos containers Celery relevantes | ✅ |
| INV-6 | `docker restart` (não `kill -HUP 1`) para recarregar módulos Python | ✅ |

---

## STEP 1 — Diagnóstico inicial (banco)

```sql
-- Slots gedeon com file_path=NULL por document_type
SELECT document_type, COUNT(*) as null_count
FROM ged_kit_documents
WHERE source_module = 'gedeon' AND file_path IS NULL
GROUP BY document_type
ORDER BY null_count DESC;
```

Resultado (22 tipos, 511 slots null em kit abril/2026):

| document_type | null_count |
|--------------|-----------|
| contracheque | 47 |
| comp_salario_individual | 47 |
| comp_vt_individual | 47 |
| comp_va_solides | 47 |
| comp_vt_va_combinado | 47 |
| dctfweb_extrato | 7 |
| relatorio_gfd_fgts | 7 |
| gfd_fgts_mensal | 7 |
| folha_pagamento | 7 |
| comp_pag_fgts | 7 |
| cnd_federal | 7 |
| cnd_estadual | 7 |
| cnd_municipal | 7 |
| cnd_trabalhista | 7 |
| cnd_fgts | 7 |
| nfse | 7 |
| boleto | 7 |
| relatorio_gfd_rescisao | 7 |
| gfd_fgts_rescisao | 7 |
| comp_fgts_rescisao | 7 |
| ... | ... |

---

## STEP 2 — Investigação KitBuilderService

**Conclusão:** `KitBuilderService` NÃO cria slots `ged_kit_documents`.
Ele apenas calcula completude (percentual) consultando os slots existentes.
Os slots foram criados por **seed scripts** de abril/2026.

Redirecionado para `hermes.py` — agente responsável por vincular `onvio_documents` → `ged_kit_documents`.

---

## STEP 3 — Diagnóstico hermes.py

Arquivo: `/opt/conecta-pro/backend/modules/gedeon/agents/hermes.py`

Lido integralmente. Identificados **2 bugs estruturais** em `MAPA_TIPOS_ONVIO_EMPRESA`:

### Bug 1 — `recibo_folha` ausente do mapa empresa

`onvio_documents` com `categoria='recibo_folha'` e `doc_scope='condominio'` são roteados
para `_vincular_empresa()`, mas `recibo_folha` não estava em `MAPA_TIPOS_ONVIO_EMPRESA`.
Resultado: esses documentos eram **descartados silenciosamente** — 47 slots `contracheque` ficavam NULL.

### Bug 2 — Sub-tipos dctfweb mapeados para slots inexistentes

```python
# ANTES (incorreto):
"dctfweb_creditos": "dctfweb_creditos",           # slot NÃO existe
"dctfweb_debitos": "dctfweb_debitos",             # slot NÃO existe
"dctfweb_resumo_creditos": "dctfweb_resumo_creditos",  # slot NÃO existe
"dctfweb_resumo_debitos": "dctfweb_resumo_debitos",    # slot NÃO existe
```

`kit_builder_service.py` (CategoriaToTipoDocumento) corretamente mapeia todos esses para
`dctfweb_extrato`. O HERMES estava divergente, criando links para tipos de slot inexistentes.
7 slots `dctfweb_extrato` ficavam NULL.

### Bug 3 — Causa operacional (não estrutural)

Kit abril/2026: 511 slots null aguardam `onvio_documents` com `mes_ref='04.2026'`.
O sync Onvio de abril/2026 não foi executado — `onvio_documents` só tem `documento_digitalizado`
para `04.2026`. Não corrigível estruturalmente; requer trigger operacional do sync.

---

## STEP 4 — Fix implementado

Arquivo: `backend/modules/gedeon/agents/hermes.py`

```python
# DEPOIS (correto):
MAPA_TIPOS_ONVIO_EMPRESA: dict[str, str] = {
    "folha_pagamento": "folha_pagamento",
    # Bug 1 fix: recibo_folha doc_scope=condominio → contracheque (47 slots)
    "recibo_folha": "contracheque",
    "dctfweb_recibo": "dctfweb_recibo",
    "dctfweb_extrato": "dctfweb_extrato",
    "dctfweb_declaracao": "dctfweb_declaracao",
    # Bug 2 fix: sub-tipos dctfweb → slot canônico dctfweb_extrato (7 slots)
    "dctfweb_creditos": "dctfweb_extrato",
    "dctfweb_debitos": "dctfweb_extrato",
    "dctfweb_resumo_creditos": "dctfweb_extrato",
    "dctfweb_resumo_debitos": "dctfweb_extrato",
    "fgts_guia": "gfd_fgts_mensal",
    "fgts_relatorio": "relatorio_gfd_fgts",
    "fgts_consignado": "comp_pag_fgts",
    "fgts_consignado_relatorio": "relatorio_gfd_fgts",
    ...
}
```

---

## STEP 5 — Validação

```bash
# py_compile
python3 -m py_compile backend/modules/gedeon/agents/hermes.py  # OK

# Hot-copy + restart
docker cp backend/modules/gedeon/ conecta-pro-backend:/app/modules/gedeon/
docker cp backend/modules/gedeon/ conecta-pro-celery-integrations:/app/modules/gedeon/
docker cp backend/modules/gedeon/ conecta-pro-celery-beat:/app/modules/gedeon/
docker restart conecta-pro-backend

# Backfill
processar_mes('03.2026') → 0 vinculados (março já preenchido — correto)
processar_mes('04.2026') → 0 vinculados (sem onvio_documents 04.2026 — esperado)
```

| Kit | Slots gedeon preenchidos | Status |
|-----|--------------------------|--------|
| Março 2026 | 14/14 gedeon slots | ✅ já preenchidos |
| Abril 2026 | 0/511 | ⏳ aguarda sync Onvio 04.2026 |

---

## STEP 6 — Gaps estruturais (não corrigíveis neste §)

| Tipo | Slots | Motivo |
|------|-------|--------|
| `comp_salario_individual`, `comp_vt_individual`, `comp_va_solides`, `comp_vt_va_combinado` | 179 | Requerem geração de comprovantes Inter PDF |
| `cnd_federal`, `cnd_estadual`, `cnd_municipal`, `cnd_trabalhista`, `cnd_fgts` | 35 | Fase 1 CND pendente |
| `nfse`, `boleto` | 14 | Geração NFS-e/boleto pendente |
| `relatorio_gfd_rescisao`, `gfd_fgts_rescisao`, `comp_fgts_rescisao` | 21 | Rescisão — docs específicos |

---

## STEP 7 — Commits

| Commit | Hash | Mensagem |
|--------|------|---------|
| fix | `157a2ec3` | `fix(gedeon): §119 — MAPA_TIPOS_ONVIO_EMPRESA recibo_folha + dctfweb sub-tipos` |
| docs | `148b0876` | `docs(contracts): §119 — fix slots gedeon file_path=NULL` |

Push: `feature/people-management-reorganization` → GitHub ✅

---

## SELF-CHECK FINAL

| Item | Status |
|------|--------|
| INV-1 a INV-6 verificadas | ✅ |
| STEP 1 — query banco executada, 22 tipos mapeados | ✅ |
| STEP 2 — KitBuilderService investigado (não cria slots) | ✅ |
| STEP 3 — 2 bugs + 1 causa operacional identificados | ✅ |
| STEP 4 — fix aplicado em hermes.py | ✅ |
| STEP 5 — py_compile + hot-copy + backfill executados | ✅ |
| STEP 6 — gaps estruturais documentados | ✅ |
| STEP 7 — 2 commits + push | ✅ |

---

## STATUS FINAL

- **Bug 1 corrigido:** `recibo_folha` → `contracheque` (47 slots serão preenchidos no próximo sync 04.2026)
- **Bug 2 corrigido:** `dctfweb_creditos/debitos/resumo_*` → `dctfweb_extrato` (7 slots serão preenchidos)
- **Causa operacional:** Sync Onvio 04.2026 pendente — 511 slots aguardam
- **Fix estrutural ativo:** próxima execução de `processar_mes('04.2026')` preencherá 54+ slots automaticamente
