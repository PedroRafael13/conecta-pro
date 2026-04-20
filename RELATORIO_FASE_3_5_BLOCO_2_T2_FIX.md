# RELATORIO FASE 3.5 BLOCO 2 — T2_FIX
**Versão:** 1.0
**Data:** 2026-04-20
**Agente:** Engenheiro Backend Sênior
**Commit docs:** `4955bb83` | **Commit código:** `8c8340dc`

---

## 1. OBJETIVO

Corrigir bug crítico no `OnvioDocScopeClassifier` identificado pela auditoria Opus CPRO 10:
162/436 docs (37%) de Grupos A e B eram incorretamente reclassificados para `doc_scope='empresa_matriz'`
quando nenhum `condominio_id` ou `employee_id` era encontrado via regex.

**§13.1 Chesterton:** entender por que o bug existia antes de corrigir.
**§25 (Lição 9):** invariante de saída ≠ regra de fallback.

---

## 2. DIAGNÓSTICO (§13.1)

### 2.1 — Root cause

O código original interpretou INV-9/10 como regra de fallback:

> "Se INV-9 diz que `condominio_id` não pode ser NULL → usar `empresa_matriz` como fallback"

Mas INV-9/10 são invariantes de **estado final** (pós-commit), não regras de comportamento em runtime.
A leitura correta é:

> "Se o doc pertence ao Grupo A, seu `doc_scope` DEVE ser `'condominio'` — mas pode ter `condominio_id=NULL` desde que `revisao_manual=True`"

### 2.2 — Código com bug (antes)

```python
# GRUPO A — ERRADO
if scope == "condominio":
    cond_id = match_condominio(nome_arquivo, cond_lookup)
    if cond_id:
        return ClassificationResult(doc_scope="condominio", ...)
    if is_matriz(nome_arquivo):
        return ClassificationResult(doc_scope="empresa_matriz", ...)  # BUG
    return ClassificationResult(doc_scope="empresa_matriz", revisao_manual=True, ...)  # BUG

# GRUPO B — ERRADO
if scope == "funcionario":
    emp_id = match_employee(nome_arquivo, emp_lookup)
    if emp_id:
        return ClassificationResult(doc_scope="funcionario", ...)
    if is_matriz(nome_arquivo):
        return ClassificationResult(doc_scope="empresa_matriz", ...)  # BUG
    return ClassificationResult(doc_scope="empresa_matriz", revisao_manual=True, ...)  # BUG
```

### 2.3 — Evidência do impacto

Antes do fix (distribuição real no banco):
- `empresa_matriz`: **281** (muito acima do esperado 119)
- `condominio`: **116** (abaixo do esperado 236)
- `funcionario`: **39** (abaixo do esperado 81)

Exemplo concreto de doc mal classificado:
```
13º SALARIO 2025_Laranjeiras Village (1).pdf
  categoria: decimo_terceiro → scope esperado: funcionario
  doc_scope ANTES do fix: empresa_matriz ← BUG
  doc_scope APÓS o fix:   funcionario ✅
```

---

## 3. STEP 0 — PRÉ-FLIGHT

| Verificação | Resultado |
|-------------|-----------|
| CONTRACTS_GEDEON.md versão | 1.17 ✅ |
| Branch ativa | feature/people-management-reorganization ✅ |
| Distribuição pré-fix | empresa_matriz=281, condominio=116, funcionario=39 ✅ confirmado |
| Último commit | backfill T2 original (commit `121973fd`) ✅ |

---

## 4. STEP 1 — CONFIRMAÇÃO DO BUG

Query de diagnóstico executada:
```sql
SELECT categoria, doc_scope, COUNT(*) AS total
FROM onvio_documents
WHERE doc_scope = 'empresa_matriz'
  AND categoria NOT IN (
    'das_simples_nacional', 'guia_issqn', 'parcelamento_simples',
    'dar_sefaz', 'inss_guia', 'alvara', 'empresa_docs', 'outros', 'documento_digitalizado'
  )
GROUP BY categoria, doc_scope ORDER BY total DESC;
```

**162 docs** de Grupos A e B no bucket errado (`empresa_matriz`).

---

## 5. STEP 2 — BACKUP PRÉ-FIX

Backup criado antes de qualquer modificação:
```
/tmp/backup_fase_3_5_t2_fix_20260420_1713/onvio_documents_pre_fix.sql
Tamanho: 384KB
empresa_matriz confirmado: 281 docs
```

---

## 6. STEP 3 — DOCUMENTAÇÃO (§13.3: docs antes do código)

Adicionado a CONTRACTS_GEDEON.md v1.18:
- **§25** — Lição 9: Invariantes de Saída vs Regras de Fallback (§25.1–§25.5)
- **§23.11** — Correção do T2 original: escopo, diff lógico, distribuição antes/depois, backup
- Changelog v1.18

**Commit 1:** `4955bb83`

---

## 7. STEP 4 — FIX CIRÚRGICO (§13.4)

Apenas 2 ramos de `OnvioDocScopeClassifier.classify()` alterados:

### Ramo Grupo A — DEPOIS (correto):
```python
# §23.11: preservar scope='condominio' mesmo sem match — levantar revisao_manual
if scope == "condominio":
    cond_id = match_condominio(nome_arquivo, cond_lookup)
    return ClassificationResult(
        doc_scope="condominio",
        condominio_id=cond_id,
        referente_a_employee_id=None,
        revisao_manual=(cond_id is None),
        motivo=("OK" if cond_id else f"Grupo A sem match condomínio: {nome_arquivo[:60]}"),
    )
```

### Ramo Grupo B — DEPOIS (correto):
```python
# §23.11: preservar scope='funcionario' mesmo sem match — levantar revisao_manual
if scope == "funcionario":
    emp_id = match_employee(nome_arquivo, emp_lookup)
    return ClassificationResult(
        doc_scope="funcionario",
        condominio_id=None,
        referente_a_employee_id=emp_id,
        revisao_manual=(emp_id is None),
        motivo=("OK" if emp_id else f"Grupo B sem match funcionário: {nome_arquivo[:60]}"),
    )
```

**Grupos C e D: INALTERADOS.**

Deploy via: `docker cp /opt/conecta-pro/backend/modules/ conecta-pro-backend:/app/modules/`
Import validado: `✅ import OK, CATEGORIA_TO_SCOPE tem 37 entradas`

---

## 8. STEP 5 — DRY-RUN PRÉ-BACKFILL

```
empresa_matriz : 107
condominio     : 236
funcionario    : 93
revisao_manual : 198
```

Todos dentro das faixas H3–H5. Funcionario=93 (4 acima do estimado 89) explicado por
12 docs de Grupo D (`outros`/`documento_digitalizado`) que encontraram match de funcionário.

---

## 9. STEP 6 — RE-BACKFILL REAL

```
Lote 1/9 commitado (50 docs)
Lote 2/9 commitado (100 docs)
...
Lote 9/9 commitado (436 docs)
✅ INV-8 OK — zero doc_scope NULL
```

---

## 10. STEP 7 — VALIDAÇÃO PÓS-FIX

### 7.1 — Distribuição final

| doc_scope      | total | com_revisao | com_cond_id | com_emp_id |
|----------------|-------|-------------|-------------|------------|
| condominio     |   236 |         120 |         116 |          0 |
| empresa_matriz |   107 |          24 |           0 |          0 |
| funcionario    |    93 |          54 |           0 |         39 |

### 7.2 — Distribuição por condomínio

| condominio       | total | revisao |
|------------------|-------|---------|
| (sem match)      |   120 |     120 |
| ideal_flores     |    22 |       0 |
| prime_arena      |    18 |       0 |
| michelangelo     |    18 |       0 |
| mirante          |    18 |       0 |
| villa_passaros   |    16 |       0 |
| villa_dei_fiori  |    16 |       0 |
| laranjeiras      |     8 |       0 |

### 7.3 — Casos específicos verificados

| nome_arquivo | categoria | doc_scope | tem_cond_id | revisao |
|---|---|---|---|---|
| 13º SALARIO 2025_Laranjeiras Village (1).pdf | decimo_terceiro | funcionario | false | true |
| Recibo 13º SALARIO 2025_Ideal Flores (1).pdf | recibo_decimo_terceiro | funcionario | false | true |
| Folha 02.2026_Villa Dei Fiori (1).pdf | folha_pagamento | condominio | true | false |

`13º SALARIO_Laranjeiras` era `empresa_matriz` antes → agora `funcionario` ✅

### 7.4 — Regression BLOCO 1 + T3

| tabela | esperado | encontrado |
|--------|----------|------------|
| condominios | 11 | 11 ✅ |
| employee_alocacoes | 47 | 47 ✅ |
| kit_documental_templates | 38 | 38 ✅ |

---

## 11. STEP 8 — 5 TESTES DE FALSIFICAÇÃO

| Teste | Descrição | Resultado |
|-------|-----------|-----------|
| 🔴 A | Distribuição dentro de H3/H4/H5 | **PASS** |
| 🔴 B | Zero `doc_scope NULL` (INV-8) | **PASS** |
| 🔴 C | Idempotência (re-run diff=0) | **PASS** |
| 🔴 D | Unit test (5 asserts Grupos A/B/C/D) | **PASS** (5/5) |
| 🔴 E | Regression BLOCO 1+T3 (11, 47, 38) | **PASS** |

**FALSIFICAÇÃO: 5/5 PASS ✅**

### Detalhes Unit Test (Assert D):
- Assert 1: Grupo A sem match → `condominio` + `revisao_manual=True` ✅
- Assert 2: Grupo A com match → `condominio` + `revisao_manual=False` ✅
- Assert 3: Grupo B sem match → `funcionario` + `revisao_manual=True` ✅
- Assert 4: Grupo C → `empresa_matriz` + `revisao_manual=False` ✅
- Assert 5: Grupo D `is_matriz` → `empresa_matriz` ✅

---

## 12. STEP 9 — COMMITS

| # | Hash | Conteúdo |
|---|------|----------|
| 1 | `4955bb83` | docs: CONTRACTS_GEDEON.md §25+§23.11 v1.18 |
| 2 | `8c8340dc` | fix: onvio_doc_scope_classifier.py Grupos A/B |
| 3 | este commit | docs: RELATORIO_FASE_3_5_BLOCO_2_T2_FIX.md |

---

## 13. SELF-CHECK 14/14

| # | Invariante | Status |
|---|------------|--------|
| INV-1 | CATEGORIA_TO_SCOPE não alterado | ✅ |
| INV-2 | BATCH_SIZE=50 intacto | ✅ |
| INV-3 | SyncSessionLocal usado | ✅ |
| INV-4 | Idempotência (8-C PASS) | ✅ |
| INV-5 | Commits incrementais a cada 50 | ✅ |
| INV-6 | CAST(:param AS uuid) syntax | ✅ |
| INV-7 | Backup pré-fix criado | ✅ |
| INV-8 | Zero doc_scope NULL (8-B PASS) | ✅ |
| INV-9 | condominio_id NULL → revisao_manual, nunca empresa_matriz | ✅ |
| INV-10 | employee_id NULL → revisao_manual, nunca empresa_matriz | ✅ |
| INV-11 | revisao_manual=True em todos casos incertos | ✅ |
| INV-12 | Distribuição H3/H4/H5 dentro das faixas | ✅ |
| INV-13 | Regression BLOCO 1+T3 (8-E PASS) | ✅ |
| INV-14 | §13.3: docs commitados antes do código | ✅ |

**SELF-CHECK: 14/14 ✅**

---

## CONCLUSÃO

**T2_FIX OK — LIBERAR T7 PARA AUDITORIA FINAL FASE 3.5**

Bug de 162 docs (37%) corrigido. Distribuição normalizada:
- `empresa_matriz`: 107 (era 281 — ↓62%)
- `condominio`: 236 (era 116 — ↑103%)
- `funcionario`: 93 (era 39 — ↑138%)

Lição 9 (§25) documentada como princípio permanente de engenharia:
**Invariante de saída ≠ regra de fallback.**
