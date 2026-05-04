# RELATORIO T5 — Mapa Tipos Onvio + Categorias Órfãs
**Data:** 2026-05-04
**Tipo:** READ-ONLY / Diagnóstico
**Branch:** feature/people-management-reorganization

---

## Objetivo

Mapear estado real do `MAPA_TIPOS_ONVIO` e identificar categorias órfãs em `onvio_documents`
que bloqueiam 448/592 docs de serem casados com kits GED.

---

## STEP 1 — MAPA_TIPOS_ONVIO atual

Arquivo: `backend/modules/people_management/ged/services/kit_builder_service.py:25`
Tamanho: 28953 bytes (modificado 2026-04-28)

```python
# Mapa de conversão: categoria onvio_documents → document_type ged_kit_documents
# Restrito a documentos de EMPRESA (employee_id IS NULL) — D2 auditoria 2026-04-27
MAPA_TIPOS_ONVIO: dict[str, str] = {
    "folha_pagamento":           "folha_pagamento",
    "dctfweb_recibo":            "dctfweb_recibo",
    "dctfweb_extrato":           "dctfweb_extrato",
    "dctfweb_declaracao":        "dctfweb_declaracao",
    "fgts_guia":                 "gfd_fgts_mensal",
    "fgts_relatorio":            "relatorio_gfd_fgts",
    "fgts_consignado":           "comp_pag_fgts",
    "fgts_consignado_relatorio": "relatorio_gfd_fgts",
}
```

**Nomes de exibição** (`_NOMES_DOCS_ONVIO`):
```python
"folha_pagamento": "Folha de Pagamento"
"dctfweb_recibo":  "DCTFWeb Recibo"
"dctfweb_extrato": "DCTFWeb Extrato"
"dctfweb_declaracao": "DCTFWeb Declaração"
"gfd_fgts_mensal": "Guia FGTS Mensal"
"relatorio_gfd_fgts": "Relatório GFD FGTS"
"comp_pag_fgts": "Comprovante Pagamento FGTS"
```

**Usado em:** `kit_builder_service.py:600` — `_match_onvio_docs()` itera o mapa,
busca `onvio_documents` por categoria + condomínio (fuzzy match palavras significativas),
preenche `file_path` no `ged_kit_documents`.

---

## STEP 2 — Distribuição real (38 categorias, 592 docs total)

| Categoria | Qtd | Com scope | Sem scope | No mapa |
|-----------|-----|-----------|-----------|---------|
| outros | 160 | 20 | 140 | ❌ |
| folha_pagamento | 69 | 69 | 0 | ✅ |
| recibo_folha | 68 | 68 | 0 | ❌ per-employee |
| documento_digitalizado | 26 | 16 | 10 | ❌ |
| das_simples_nacional | 21 | 21 | 0 | ❌ |
| guia_issqn | 20 | 20 | 0 | ❌ |
| parcelamento_simples | 20 | 20 | 0 | ❌ |
| contrato_trabalho | 16 | 12 | 4 | ❌ per-employee |
| ficha_registro | 13 | 9 | 4 | ❌ per-employee |
| fgts_relatorio | 12 | 12 | 0 | ✅ |
| dctfweb_declaracao | 12 | 12 | 0 | ✅ |
| declaracao_vt | 12 | 8 | 4 | ❌ per-employee |
| fgts_guia | 12 | 12 | 0 | ✅ |
| dctfweb_resumo_creditos | 11 | 11 | 0 | ❌ |
| dctfweb_recibo | 11 | 11 | 0 | ✅ |
| dctfweb_resumo_debitos | 11 | 11 | 0 | ❌ |
| dctfweb_extrato | 10 | 10 | 0 | ✅ |
| autodeclaracao | 9 | 5 | 4 | ❌ per-employee |
| fgts_consignado | 9 | 9 | 0 | ✅ |
| dctfweb_creditos | 9 | 9 | 0 | ❌ |
| dctfweb_debitos | 9 | 8 | 1 | ❌ |
| fgts_consignado_relatorio | 9 | 9 | 0 | ✅ |
| decimo_terceiro | 8 | 8 | 0 | ❌ |
| empresa_docs | 8 | 8 | 0 | ❌ |
| recibo_decimo_terceiro | 8 | 8 | 0 | ❌ per-employee |
| dar_sefaz | 6 | 6 | 0 | ❌ |
| rescisao | 5 | 5 | 0 | ❌ per-employee |
| inss_guia | 5 | 5 | 0 | ❌ |
| alvara | 3 | 3 | 0 | ❌ |
| certidao | 2 | 0 | 2 | ❌ |
| afastamento | 2 | 2 | 0 | ❌ |
| dctfweb_situacao | 2 | 2 | 0 | ❌ |
| atestado | 2 | 2 | 0 | ❌ |
| portal_empregador | 1 | 1 | 0 | ❌ |
| ferias | 1 | 1 | 0 | ❌ per-employee |
| folha_ponto | 1 | 1 | 0 | ❌ |
| aso | 1 | 1 | 0 | ❌ |
| aviso_previo | 1 | 1 | 0 | ❌ per-employee |

**Resumo:** 8 categorias mapeadas cobrem 143 docs. 430 docs (72%) são órfãos.

---

## STEP 3 — Uso do MAPA_TIPOS_ONVIO

```
kit_builder_service.py:25   → definição do dict
kit_builder_service.py:561  → docstring de _match_onvio_docs
kit_builder_service.py:600  → for onvio_cat, kit_doc_type in MAPA_TIPOS_ONVIO.items()
```

Usado apenas em um lugar. Expansão do mapa tem impacto direto e imediato.

---

## STEP 4 — Função _match_onvio_docs (resumo)

- Itera `MAPA_TIPOS_ONVIO`
- Para cada par `(categoria_onvio, document_type_ged)`:
  - Busca `onvio_documents` por categoria + fuzzy match do nome do condomínio
  - Se acha placeholder com `file_path IS NULL` → atualiza com caminho real
  - Se não existe placeholder → cria novo `kit_document`
- Só processa docs de empresa (`employee_id IS NULL` na lógica de scope)
- Nunca sobrescreve `file_path` que começa com `/app/` ou `http`

---

## STEP 5 — document_types em ged_kit_documents (top)

| document_type | Qtd | Com file_path |
|---------------|-----|---------------|
| contracheque | 135 | 0 |
| comprovante_vt/vr/va | 102 cada | 0 |
| folha_ponto / escala_mes | 102 cada | 0 |
| comp_salario_individual | 47 | 0 |
| folhas_ponto | 47 | 0 |
| contrato_trabalho | 40 | 0 |
| ficha_empregado | 40 | 0 |
| gfd_fgts_rescisao | 34 | 0 |
| cnd_federal/estadual/municipal | 16 cada | 0 |
| **folha_pagamento** | 14 | **7** |
| dctfweb_extrato/recibo/declaracao | 7 cada | 0 |
| gfd_fgts_mensal / comp_pag_fgts | 7 cada | 0 |
| relatorio_gfd_fgts | 7 | 0 |
| aso | 3 | 0 |

**Único document_type com file_path preenchido:** `folha_pagamento` (7/14).
Todos os demais estão vazios — estrutura criada mas arquivo nunca vinculado.

---

## STEP 6 — Sample categoria='outros' (15 mais recentes)

```
ANTECEDENTES ESTADUAL_SEBASTIAO.pdf   | mes_ref: null | scope: null
PIS_SEBASTIÃO.pdf                     | mes_ref: null | scope: null
CARTEIRA DE TRABALHO_SEBASTIÃO.pdf    | mes_ref: null | scope: null
COMPROVANTE DE RESIDENCIA_SEBASTIÃO   | mes_ref: null | scope: null
TITULO DE ELEITOR_SEBASTIÃO.pdf       | mes_ref: null | scope: null
CPF_SEBASTIÃO.pdf                     | mes_ref: null | scope: null
RG_SEBASTIÃO.pdf                      | mes_ref: null | scope: null
CERTIFICADOS_SEBASTIAO.pdf            | mes_ref: null | scope: null
CARTEIRA DE RESERVISTA_SEBASTIÃO.pdf  | mes_ref: null | scope: null
ANTECEDENTES FEDERAL_SEBASTIAO.pdf    | mes_ref: null | scope: null
CTPSContratosDigitais_*.pdf           | mes_ref: 02.2026 | scope: null
0uy5zr (1) (1).pdf                    | mes_ref: null | scope: null
Documento_1771435880049.pdf           | mes_ref: null | scope: null
do Livro NE. A14...pdf                | mes_ref: null | scope: null
```

**Conclusão:** 140 dos 160 "outros" são documentos pessoais de admissão de funcionários
(RG, CPF, CTPS, título eleitor, reservista, antecedentes). Sem mes_ref e sem scope.
Não mapeáveis. Os 20 com scope requerem amostra adicional.

---

## STEP 7 — Top 20 categorias órfãs (fora do mapa)

| # | Categoria | Qtd |
|---|-----------|-----|
| 1 | outros | 160 |
| 2 | recibo_folha | 68 |
| 3 | documento_digitalizado | 26 |
| 4 | das_simples_nacional | 21 |
| 5 | parcelamento_simples | 20 |
| 6 | guia_issqn | 20 |
| 7 | contrato_trabalho | 16 |
| 8 | ficha_registro | 13 |
| 9 | declaracao_vt | 12 |
| 10 | dctfweb_resumo_creditos | 11 |
| 11 | dctfweb_resumo_debitos | 11 |
| 12 | dctfweb_debitos | 9 |
| 13 | autodeclaracao | 9 |
| 14 | dctfweb_creditos | 9 |
| 15 | empresa_docs | 8 |
| 16 | recibo_decimo_terceiro | 8 |
| 17 | decimo_terceiro | 8 |
| 18 | dar_sefaz | 6 |
| 19 | inss_guia | 5 |
| 20 | rescisao | 5 |

---

## Tipos do GED não mapeáveis via Onvio

Os seguintes `document_type` em `ged_kit_documents` são gerados por outros módulos,
não pelo Onvio — não devem entrar no `MAPA_TIPOS_ONVIO`:

- `contracheque` — DP (per-employee)
- `comprovante_vt/vr/va` — DP (per-employee)
- `folha_ponto / folhas_ponto` — DP / Operacional
- `escala_mes` — Operacional
- `comp_salario_individual / comp_vt_individual / comp_va_solides / comp_vt_va_combinado` — DP
- `contrato_trabalho / ficha_empregado` — RH
- `gfd_fgts_rescisao / relatorio_gfd_rescisao / comp_fgts_rescisao` — DP rescisão
- `cnd_federal/estadual/municipal/sefaz/caixa/rfb/prefeitura/trabalhista` — Fiscal (certidões)
- `nfse / boleto` — Fiscal

---

## Proposta de Expansão (sem aplicar — aguardar T1)

### Candidatos seguros (empresa-level, 100% com scope):

```python
# Adicionar a MAPA_TIPOS_ONVIO — requer também adicionar ao enum DocumentType
"das_simples_nacional":    "das_simples_nacional",     # 21 docs
"parcelamento_simples":    "parcelamento_simples",      # 20 docs
"guia_issqn":              "guia_issqn",                # 20 docs
"dctfweb_resumo_creditos": "dctfweb_resumo_creditos",  # 11 docs
"dctfweb_resumo_debitos":  "dctfweb_resumo_debitos",   # 11 docs
"dctfweb_creditos":        "dctfweb_creditos",          # 9 docs
"dctfweb_debitos":         "dctfweb_debitos",           # 9 docs
"decimo_terceiro":         "decimo_terceiro",            # 8 docs
"empresa_docs":            "outro",                     # 8 docs (enum já tem OUTRO)
"inss_guia":               "gps_inss",                  # 5 docs (enum já tem GPS_INSS)
"dar_sefaz":               "dar_sefaz",                 # 6 docs
```

**Impacto estimado:** +120 docs mapeáveis (de 143 para ~263, de 24% para ~44%)

### Obs. crítica — enum não sincronizado com banco
Os novos `document_type` (`das_simples_nacional`, `parcelamento_simples` etc.)
**não existem no enum `DocumentType`** em `kit_document.py`.
A task de expansão precisará:
1. Adicionar ao enum `DocumentType`
2. Adicionar a `_NOMES_DOCS_ONVIO`
3. Adicionar a `MAPA_TIPOS_ONVIO`

### NÃO adicionar (per-employee sem employee_id linkável):
`recibo_folha`, `contrato_trabalho`, `ficha_registro`, `declaracao_vt`,
`autodeclaracao`, `recibo_decimo_terceiro`, `rescisao`

---

## Checklist do Prompt

- [x] STEP 1: MAPA_TIPOS_ONVIO atual (ls -la + grep dict)
- [x] STEP 2: Distribuição categorias onvio_documents (38 categorias)
- [x] STEP 3: Onde MAPA_TIPOS_ONVIO é usado
- [x] STEP 4: Função _match_onvio_docs completa
- [x] STEP 5: document_types em ged_kit_documents
- [x] STEP 6: Sample categoria='outros'
- [x] STEP 7: Categorias órfãs TOP 20
- [x] REPORTAR: 5 itens reportados no chat
- [x] READ-ONLY: nenhuma modificação aplicada
- [x] ATENÇÃO: aguardar T1 antes de qualquer fix

---

*T5 READ-ONLY concluído. Nenhuma modificação no sistema.*
