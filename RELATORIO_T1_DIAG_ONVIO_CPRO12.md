# T1 CPRO12 — Diagnóstico Profundo Onvio (READ-ONLY)
**Sessão:** CPRO12 T1-DIAG-ONVIO
**Data:** 2026-05-05
**Responsável:** Jordan Jesus (jjesus@conectamais.pro)
**Branch:** feature/people-management-reorganization
**Tipo:** Diagnóstico READ-ONLY — zero alterações

---

## Objetivo

Mapear a estrutura real dos documentos Onvio: campos disponíveis, preenchimento,
categorias e possibilidades de matching com DP/condomínios para o GEDEON.

---

## 1. Schema real de `onvio_documents`

```
         Column          |           Type
-------------------------+--------------------------
 id                      | uuid (PK)
 onvio_id                | varchar(100) UNIQUE NOT NULL
 onvio_folder_id         | varchar(100)
 nome_arquivo            | varchar(500) NOT NULL
 categoria               | varchar(100)
 mes_ref                 | varchar(10)         ← "MM.YYYY" ou "YYYY"
 caminho_local           | varchar(1000)
 data_onvio              | timestamptz
 processado              | boolean (default false)
 tamanho_bytes           | integer
 data_importado          | timestamptz
 metadata_json           | text                ← sempre NULL (não usado)
 confianca_extracao      | float8
 metodo_extracao         | varchar(50)
 revisao_manual          | boolean
 detalhes_json           | jsonb               ← extração PDF (121 docs)
 extraido_em             | timestamptz
 doc_scope               | varchar(50)         ← 'condominio'|'empresa_matriz'|'funcionario'
 condominio_id           | uuid (FK condominios)
 referente_a_employee_id | uuid (FK employees)
```

**Índices:** categoria, mes_ref, condominio_id, doc_scope

### Colunas que o prompt assumia mas NÃO EXISTEM:
| Coluna assumida | Realidade |
|----------------|-----------|
| `colaborador_nome` | não existe — nome está embutido em `nome_arquivo` |
| `cpf_colaborador` | não existe |
| `cnpj` | não existe — CNPJ está embutido em `nome_arquivo` |
| `titulo` | não existe — há `nome_arquivo` e `categoria` |
| `documento_tipo` | não existe — é `categoria` |
| `competencia` | não existe como coluna — está em `detalhes_json->>'competencia'` (apenas 121 docs extraídos) |
| `file_path` | não existe — é `caminho_local` |

---

## 2. Preenchimento dos campos (605 documentos)

| Campo | Preenchidos | % |
|-------|-------------|---|
| `categoria` | 605 | 100% |
| `caminho_local` | 605 | 100% |
| `mes_ref` | 440 | 73% |
| `doc_scope` | 436 | 72% |
| `detalhes_json` | 121 | 20% |
| `condominio_id` | 116 | 19% |
| `referente_a_employee_id` | 39 | 6% |
| `metadata_json` | 0 | 0% ← nunca usado |

---

## 3. Distribuição por categoria e doc_scope

| Categoria | Scope | Total |
|-----------|-------|-------|
| outros | NULL | 140 |
| folha_pagamento | condominio | 69 |
| recibo_folha | condominio | 68 |
| das_simples_nacional | empresa_matriz | 21 |
| parcelamento_simples | empresa_matriz | 20 |
| guia_issqn | empresa_matriz | 20 |
| documento_digitalizado | empresa_matriz | 16 |
| fgts_guia | condominio | 12 |
| fgts_relatorio | condominio | 12 |
| dctfweb_declaracao | condominio | 12 |
| contrato_trabalho | funcionario | 12 |
| outros | funcionario | 12 |
| dctfweb_resumo_debitos | condominio | 11 |
| dctfweb_resumo_creditos | condominio | 11 |
| dctfweb_recibo | condominio | 11 |
| dctfweb_extrato | condominio | 10 |
| dctfweb_creditos | condominio | 9 |
| ficha_registro | funcionario | 9 |
| fgts_consignado_relatorio | funcionario | 9 |
| fgts_consignado | funcionario | 9 |
| ... | | |

**Docs sem scope (NULL):** 169 — não passaram pelo scope classifier ainda.
Categorias mais comuns: `outros` (140), `documento_digitalizado` (10), `ficha_registro` (4).

---

## 4. Status do matching por scope

| Scope | Total | Com FK preenchida | Sem FK | Taxa de match |
|-------|-------|------------------|--------|---------------|
| condominio | 236 | 116 (condominio_id) | 120 | 49% |
| funcionario | 93 | 39 (employee_id) | 54 | 42% |
| empresa_matriz | 107 | N/A | N/A | 100% (não precisa FK) |
| NULL | 169 | 0 | 169 | 0% (não processado) |

---

## 5. Causa raiz dos 120 docs scope=condominio sem condominio_id

Amostra dos arquivos sem match:
```
DCTFWEB ResumoCreditos_35710481000103_012026_40_.pdf    ← CNPJ da empresa matriz
Folha 01.2026_Conecta Mais - Geral (1).pdf              ← nome "Conecta Mais"
RELATORIO GFD FGTS 12.2025_Conecta Mais.pdf             ← nome "Conecta Mais"
Recibo Folha 03.2026_Conecta Mais - Geral (4).pdf       ← nome "Conecta Mais"
```

**Diagnóstico:** Esses documentos pertencem à **empresa matriz** (CNPJ 35.710.481/0001-03),
não a condomínios específicos. Foram classificados como `scope='condominio'` porque a categoria
(`folha_pagamento`, `dctfweb_*`) mapeia para scope=condominio no `CATEGORIA_TO_SCOPE`.

**Bug no OnvioDocScopeClassifier (Grupo A):** Para scope=condominio, o classifier
chama apenas `match_condominio(nome_arquivo, cond_lookup)` sem checar `is_matriz()` primeiro.
O `is_matriz()` detecta CNPJ `35.710.481` e nome "Conecta Mais" — mas nunca é chamado para Grupo A.
Resultado: 120 docs da empresa matriz ficam em scope=condominio com condominio_id=NULL.

---

## 6. Como o parser Onvio funciona

### O que a API Onvio entrega por documento (STEP 5 — raw da API):
```json
{
  "id": "onvio_id",
  "name": "Folha 03.2026_Prime Arena (1).pdf",
  "containerId": "folder_id",
  "createdDate": "2026-03-15T..."
}
```
**O Onvio NÃO envia:** condominio_id, CPF, nome de funcionário em campo separado,
CNPJ em campo separado, categoria, competência.

Campos confirmados via grep (`onvio_client.py`):
- `item.get("id")` → onvio_id
- `item.get("name")` → nome_arquivo (ÚNICO campo com conteúdo identificável)
- `item.get("containerId")` ou `item.get("parentId")` → onvio_folder_id
- `item.get("createdDate")` → data_onvio (IGNORADA para mes_ref — bug histórico corrigido no v2)
- Sessão via Redis (`onvio:session`) com cookies + `Authorization: UDSLongToken <token>`

### O que o parser extrai do `name` (STEP 5 — grep campos no parser):
O parser `onvio_parser.py` trabalha EXCLUSIVAMENTE com o `nome_arquivo`:
1. **`categoria`** — via 26 regras regex no `classificar_documento()` (ex: "DCTFWEB" in nome)
2. **`mes_ref`** — via `extract_mes_ref()`: regex MM.YYYY / _MMYYYY_ / YYYY no nome
3. Remove CNPJs (14 dígitos) antes de extrair mes_ref para evitar falso-positivos

**NÃO extrai:** colaborador_nome, cpf_colaborador, cnpj separado, condominio.

### O que o sync salva na tabela:
```python
OnvioDocument(
    onvio_id=item["id"],
    onvio_folder_id=item["containerId"],
    nome_arquivo=item["name"],          ← ÚNICO campo identificável da API
    categoria=cl.categoria,
    mes_ref=cl.mes_ref,
    caminho_local=caminho,
    tamanho_bytes=...,
    data_onvio=item["createdDate"],
    processado=False,
)
```

### O que é descartado (não extraído pelo sync):
- Nome do funcionário (está no `nome_arquivo` mas não salvo em coluna própria)
- CNPJ da empresa/condomínio (está no `nome_arquivo` mas não em coluna própria)
- Condomínio identificado (resolvido em etapa posterior pelo scope classifier)
- `readByClientUser`, `loadPermission` e `customFields` da API (filtros de listagem, não dados do doc)

---

## 7. MAPA_TIPOS_ONVIO — categoria Onvio → tipo kit GED (STEP 6)

**Localização:** `backend/modules/people_management/ged/services/kit_builder_service.py`
**Total:** 21 categorias mapeadas (o prompt dizia 19 — código tem 21 após expansão CPRO12 T5)

```python
MAPA_TIPOS_ONVIO: dict[str, str] = {
    # Originais (7)
    "folha_pagamento":            "folha_pagamento",
    "dctfweb_recibo":             "dctfweb_recibo",
    "dctfweb_extrato":            "dctfweb_extrato",
    "dctfweb_declaracao":         "dctfweb_declaracao",
    "fgts_guia":                  "gfd_fgts_mensal",
    "fgts_relatorio":             "relatorio_gfd_fgts",
    "fgts_consignado":            "comp_pag_fgts",
    "fgts_consignado_relatorio":  "relatorio_gfd_fgts",  ← mesmo tipo que fgts_relatorio
    # Expansão CPRO12 T5 — 13 categorias empresa-level
    "das_simples_nacional":       "das_simples_nacional",
    "parcelamento_simples":       "parcelamento_simples",
    "guia_issqn":                 "guia_issqn",
    "dctfweb_resumo_creditos":    "dctfweb_resumo_creditos",
    "dctfweb_resumo_debitos":     "dctfweb_resumo_debitos",
    "dctfweb_creditos":           "dctfweb_creditos",
    "dctfweb_debitos":            "dctfweb_debitos",
    "decimo_terceiro":            "decimo_terceiro",
    "empresa_docs":               "outro",
    "inss_guia":                  "gps_inss",
    "dar_sefaz":                  "dar_sefaz",
}
```

**Categorias do parser NÃO mapeadas no MAPA_TIPOS_ONVIO** (sem vinculação ao kit):
`recibo_folha`, `contracheque`, `fgts_crf`, `divida_ativa_simples`, `rescisao`, `admissao`,
`ferias`, `aviso_previo`, `contrato_trabalho`, `ficha_registro`, `declaracao_vt`,
`autodeclaracao`, `aso`, `atestado`, `certidao`, `alvara`, `documento_digitalizado`,
`portal_empregador`, `dctfweb_situacao`, `outros`

**Impacto:** docs com essas categorias não são vinculados a `ged_kit_documents` pelo kit_builder.

---

## 8. OnvioDocScopeClassifier — lógica atual

### CATEGORIA_TO_SCOPE (mapeamento aprovado por Jordan em 2026-04-19):
| Grupo | Scope | Categorias |
|-------|-------|-----------|
| A | condominio | folha_pagamento, recibo_folha, fgts_guia, fgts_relatorio, dctfweb_* (7 tipos) |
| B | funcionario | contrato_trabalho, ficha_registro, declaracao_vt, rescisao, decimo_terceiro, recibo_decimo_terceiro, afastamento, atestado, aso, aviso_previo, ferias, autodeclaracao, fgts_consignado, fgts_consignado_relatorio |
| C | empresa_matriz | das_simples_nacional, guia_issqn, parcelamento_simples, dar_sefaz, inss_guia, alvara, empresa_docs |
| D | None (ambíguo) | outros, documento_digitalizado |

### Matching de condomínio (regex no nome_arquivo):
11 condomínios mapeados: ideal_flores, mirante, laranjeiras, prime_arena,
villa_dei_fiori, villa_passaros, michelangelo, p_gelain, green_hills, parise, escritorio

### Matching de funcionário:
Regex primeiro_nome + sobrenome no `nome_arquivo` (normalizado sem acentos).

---

## 8. `detalhes_json` — campos extraídos por PDF extractor

Para 121 docs (DCTFWEB + FGTS + INSS) o PDF foi lido e campos extraídos:
```json
{
  "tipo": "dctfweb_recibo",
  "competencia": "01/2026",          ← mais preciso que mes_ref
  "valor": "14604.94",
  "vencimento": "2026-02-20",
  "codigo_barras": "858600...",
  "numero_recibo": "50000443648449",
  "confianca": 1.0,
  "metodo_extracao": "regex_v1"
}
```
`detalhes_json->>'competencia'` é mais preciso que `mes_ref` (vem do conteúdo do PDF).
Disponível apenas para docs com extrator implementado (DCTFWEB, FGTS, INSS).

---

## 9. Campos disponíveis para matching com DP/condomínio

| Campo | O que contém | Pode identificar condomínio? | Pode identificar funcionário? |
|-------|-------------|------------------------------|-------------------------------|
| `condominio_id` | FK direta para condominios | ✅ SIM — 116 docs já resolvidos | ❌ |
| `referente_a_employee_id` | FK direta para employees | ❌ | ✅ SIM — 39 docs já resolvidos |
| `nome_arquivo` | nome original do PDF | ✅ via regex (scope classifier) | ✅ via regex (nome funcionário) |
| `mes_ref` | "MM.YYYY" ou "YYYY" | ❌ (período, não identificador) | ❌ (período, não identificador) |
| `doc_scope` | 'condominio'/'funcionario'/'empresa_matriz' | ✅ (classificação do tipo) | ✅ (classificação do tipo) |
| `detalhes_json->>'competencia'` | competência extraída do PDF | ❌ | ❌ |
| `categoria` | tipo do documento | ✅ indiretamente (via CATEGORIA_TO_SCOPE) | ✅ indiretamente |

**Campos que NÃO existem e seriam úteis:**
- `colaborador_nome` — precisaria ser extraído do `nome_arquivo`
- `cnpj` — presente no `nome_arquivo` mas não em coluna separada
- `cpf_colaborador` — não disponível em nenhum campo

---

## 10. Recomendação para o GEDEON — matching

### Estratégia atual (já implementada):
1. `nome_arquivo` → parser classifica `categoria` + `mes_ref`
2. `categoria` → scope classifier atribui `doc_scope`
3. `nome_arquivo` → regex identifica condomínio → preenche `condominio_id`
4. `nome_arquivo` → regex identifica funcionário → preenche `referente_a_employee_id`

### Para vincular doc Onvio a kit GED:
```
onvio_documents.condominio_id → condominios.id → ged_document_kits.client_id (via condomínio)
onvio_documents.mes_ref       → ged_document_kits.reference_month
onvio_documents.categoria     → mapeamento para tipo de doc no kit
```

### Bug a corrigir (escopo futuro — não READ-ONLY):
**OnvioDocScopeClassifier Grupo A:** adicionar `is_matriz()` antes de `match_condominio()`
para reclassificar os 120 docs "Conecta Mais - Geral" como empresa_matriz em vez de
condominio+revisao_manual.

### 169 docs sem scope:
Executar scope classifier nos docs com `doc_scope IS NULL` para classificar os
140 "outros" e 29 restantes. Muitos são documentos pessoais de funcionários
(RG, CPF, certidão de nascimento de "Sebastião") que não têm categoria específica.

---

## Commits

| Hash | Descrição |
|------|-----------|
| `fe5660d5` | `docs(contracts): §87 — Diagnóstico Onvio matching GEDEON (CPRO12 T1)` |
| `[hash-auditoria]` | `docs(gedeon): auditoria T1-DIAG-ONVIO — MAPA_TIPOS_ONVIO + STEP 5/6 completos` |

---

**T1 DIAG-ONVIO CPRO12 — Diagnóstico READ-ONLY concluído. §87 documentado em CONTRACTS_GEDEON.**
