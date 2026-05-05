# T5 CPRO12 — Expansão MAPA_TIPOS_ONVIO 8→19
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization

---

## Estado antes

- MAPA: 8 categorias
- Docs casáveis: 144/605 (24%)

## Estado depois

- MAPA: 19 categorias
- Docs casáveis: 272/605 (45%)
- **+128 docs desbloqueados**

---

## Hipóteses

| H# | Descrição | Resultado |
|----|-----------|-----------|
| H1 | MAPA_TIPOS_ONVIO na linha ~25 com 8 entradas | ✅ linha 25, 8 entradas |
| H2 | DocumentType em kit_document.py | ✅ confirmado |
| H3 | OUTRO e GPS_INSS já existiam | ✅ OUTRO linha 64, GPS_INSS linha 51 |
| H4 | Enum Python puro (não SQLAlchemy) | ✅ `String(30)` no banco — sem migration |
| H5 | 9 document_types novos não existiam | ✅ DAS_SIMPLES_NACIONAL, PARCELAMENTO_SIMPLES, GUIA_ISSQN, DCTFWEB_RESUMO_CREDITOS, DCTFWEB_RESUMO_DEBITOS, DCTFWEB_CREDITOS, DCTFWEB_DEBITOS, DECIMO_TERCEIRO, DAR_SEFAZ adicionados |
| H6 | Docs desbloqueados por categoria | ✅ ver tabela abaixo |
| H7 | _NOMES_DOCS_ONVIO no mesmo arquivo | ✅ linha 37 de kit_builder_service.py |
| H8 | py_compile ambos | ✅ OK |

### H6 — Docs por categoria

| Categoria | Total | Com scope |
|-----------|-------|-----------|
| das_simples_nacional | 21 | 21 |
| guia_issqn | 20 | 20 |
| parcelamento_simples | 20 | 20 |
| dctfweb_resumo_debitos | 11 | 11 |
| dctfweb_resumo_creditos | 11 | 11 |
| dctfweb_debitos | 9 | 8 |
| dctfweb_creditos | 9 | 9 |
| decimo_terceiro | 8 | 8 |
| empresa_docs | 8 | 8 |
| dar_sefaz | 6 | 6 |
| inss_guia | 5 | 5 |
| **Total** | **128** | **127** |

---

## Arquivos modificados

### `kit_document.py` — enum DocumentType (+9 valores)
```python
# Documentos fiscais — Simples Nacional / ISSQN / SEFAZ
DAS_SIMPLES_NACIONAL = "das_simples_nacional"
PARCELAMENTO_SIMPLES = "parcelamento_simples"
GUIA_ISSQN = "guia_issqn"
DAR_SEFAZ = "dar_sefaz"

# DCTFWeb — variantes
DCTFWEB_RESUMO_CREDITOS = "dctfweb_resumo_creditos"
DCTFWEB_RESUMO_DEBITOS = "dctfweb_resumo_debitos"
DCTFWEB_CREDITOS = "dctfweb_creditos"
DCTFWEB_DEBITOS = "dctfweb_debitos"

# Folha — eventos especiais
DECIMO_TERCEIRO = "decimo_terceiro"
```

### `kit_builder_service.py` — MAPA (+11 pares) e NOMES (+11 entradas)
```python
# MAPA expandido
"das_simples_nacional":    "das_simples_nacional",
"parcelamento_simples":    "parcelamento_simples",
"guia_issqn":              "guia_issqn",
"dctfweb_resumo_creditos": "dctfweb_resumo_creditos",
"dctfweb_resumo_debitos":  "dctfweb_resumo_debitos",
"dctfweb_creditos":        "dctfweb_creditos",
"dctfweb_debitos":         "dctfweb_debitos",
"decimo_terceiro":         "decimo_terceiro",
"empresa_docs":            "outro",       # OUTRO já existia
"inss_guia":               "gps_inss",    # GPS_INSS já existia
"dar_sefaz":               "dar_sefaz",
```

---

## Smoke test endpoint kits
**HTTP 200** ✅ — 18 kits retornados

---

## Commits
- docs: `8afec291` — §62 CONTRACTS_GEDEON.md
- feat: `a96cc28b` — kit_builder_service.py + kit_document.py

## Cenário: A — Tudo OK

Ganho real: **+128 docs desbloqueados** = 45% de cobertura (antes: 24%)

Próxima execução do `auto_build` casará os 128 novos docs nos kits mensais.

---

## Self-check

- [x] STEP 0 — contrato lido, §54 última seção, §13.1 citado
- [x] STEP 1.1 — MAPA_TIPOS_ONVIO atual lido (8 entradas confirmadas)
- [x] STEP 1.3 — DocumentType enum lido inteiro (Chesterton)
- [x] STEP 1.5 — enum Python puro (String(30) no banco — sem migration)
- [x] STEP 1.6 — SQL confirmou 128 docs a desbloquear
- [x] STEP 2 — backups criados e removidos após sucesso
- [x] STEP 3 — 9 novos valores adicionados ao enum DocumentType
- [x] STEP 4 — _NOMES_DOCS_ONVIO expandido com 11 entradas
- [x] STEP 5 — MAPA_TIPOS_ONVIO expandido com 11 entradas
- [x] STEP 6 — py_compile OK em ambos os arquivos
- [x] STEP 7 — contagem final: 144→272 docs casáveis
- [x] STEP 8 — §62 no CONTRACTS_GEDEON ANTES do commit de código
- [x] STEP 9 — hot-reload + smoke test HTTP 200
- [x] STEP 10 — 2 commits separados + push + backups removidos
- [x] INV-5 — 7 categorias per-employee NÃO adicionadas
- [x] §13.3 — _match_onvio_docs() e get_employees_for_client() intocadas
