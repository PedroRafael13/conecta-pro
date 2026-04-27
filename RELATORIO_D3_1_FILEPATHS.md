# RELATÓRIO D3.1 — CORREÇÃO DOS file_paths PARA PDFs REAIS
**Data:** 2026-04-27
**Sessão:** Claude Code — D3.1
**Branch:** feature/people-management-reorganization
**Status Final:** ✅ CONCLUÍDO (Cenário B — file_paths zerados + PDFs falsos removidos)

---

## 1. STEP 0 — Backup + 7 Docs Originais

**Backup criado:** `/tmp/backup_before_d3_1_20260427_202513.sql` (512KB)
**Versão contrato:** v1.39 ✅

| ID | Tipo | file_path ANTES |
|----|------|-----------------|
| `00fabbe6-9e40-4ab4-b524-5709af7884c7` | folha_pagamento | `/app/uploads/onvio/inss_guia/2026-04/Folha 03.2026_Mirante das Flores (2).pdf` |
| `a92b06b9-ed1d-41c9-8313-c32adae147f9` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Ideal Flores.pdf` |
| `a049d426-98ae-4f4f-b482-f9b4ee2002f1` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Laranjeiras Village.pdf` |
| `57484c54-8c4b-4314-bb1c-2792e4e4cba2` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Michelangelo.pdf` |
| `8dbf8e11-de9d-4357-b9ee-ad4d4d2a46cb` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Prime Arena (1).pdf` |
| `9485afe0-4eb9-4411-a2ff-aca1927a9f1b` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Villa Dei Fior.pdf` |
| `c64bb7dd-88d2-4c7b-a968-f7bc3a6c4d08` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Villa dos Passaros.pdf` |

---

## 2. STEP 1 — Inventário Disco + Matching

**Inventário total:** 106 PDFs em `/uploads/onvio/`

| Diretório | PDFs | Tipo |
|-----------|------|------|
| `/outros/2025/` | 96 | Comprovante de Rendimentos (reais, D1) |
| `/outros/2026-04/` | 7 | **TEST COPIES D3** (conteúdo 2025) |
| `/inss_guia/2026-04/` | 1 | **TEST COPY D3** |
| `/outros/sem-ref/` | 1 | Ficha de Empregado |
| `/dctfweb_debitos/2025/` | 1 | DCTFWeb |

**Busca por nome exato de cada doc:**

| Nome esperado | Resultado |
|---------------|-----------|
| `Folha 03.2026_Michelangelo.pdf` | ⚠️ APENAS test copy em `/2026-04/` |
| `Folha 03.2026_Ideal Flores.pdf` | ⚠️ APENAS test copy em `/2026-04/` |
| `Folha 03.2026_Laranjeiras Village.pdf` | ⚠️ APENAS test copy em `/2026-04/` |
| `Folha 03.2026_Prime Arena (1).pdf` | ⚠️ APENAS test copy em `/2026-04/` |
| `Folha 03.2026_Villa Dei Fior.pdf` | ⚠️ APENAS test copy em `/2026-04/` |
| `Folha 03.2026_Villa dos Passaros.pdf` | ⚠️ APENAS test copy em `/2026-04/` |
| `Folha 03.2026_Mirante das Flores (2).pdf` | ⚠️ APENAS test copy em `/inss_guia/2026-04/` |

**STEP 1.3 — onvio_documents.caminho_local: existência em disco (script per-path):**

```
❌ /app/uploads/onvio/outros/2026-04/Folha03.2026_IdealFlores(2).pdf (NÃO EXISTE)
❌ /app/uploads/onvio/outros/2026-04/Folha03.2026_PrimeArena(1).pdf (NÃO EXISTE)
❌ /app/uploads/onvio/outros/2026-04/Folha03.2026_VillaDeiFior.pdf (NÃO EXISTE)
❌ /app/uploads/onvio/outros/2026-04/Folha03.2026_VilladosPassaros.pdf (NÃO EXISTE)
❌ /app/uploads/onvio/outros/2026-04/Folha03.2026_Michelangelo.pdf (NÃO EXISTE)
❌ /app/uploads/onvio/outros/2026-04/Folha03.2026_ConectaMais-Geral(4).pdf (NÃO EXISTE)
❌ /app/uploads/onvio/inss_guia/2026-04/Folha03.2026_MirantedasFlores(2).pdf (NÃO EXISTE)
❌ /app/uploads/onvio/outros/2026-04/Folha03.2026_LaranjeirasVillage.pdf (NÃO EXISTE)
❌ /app/uploads/onvio/outros/2026-04/Folha03.2026_IdealFlores.pdf (NÃO EXISTE)
```
9/9 caminho_local NÃO EXISTEM em disco — confirmação definitiva de Cenário B.

**STEP 1.4 — Decisão:**
- Quantos dos 7 file_paths esperados existem em disco com nome exato? **0 (apenas test copies)**
- caminho_local em onvio_documents é path real existente? **NÃO (9/9 ❌)**
- Hipótese vencedora: **H5 — PDFs reais nunca foram baixados**
- Path real esperado (template): **N/A — Cenário B → file_path=NULL**

**Hipótese vencedora: Cenário B / H5**
PDFs reais NUNCA foram baixados. D1 baixou 98 PDFs (todos Comprovante de Rendimentos
de 2025). As 7 folhas de pagamento 03/2026 existem no servidor Onvio mas não foram
puxadas. Os únicos arquivos em `/2026-04/` são as cópias de teste criadas em D3 STEP 2C.

**Decisão (INV-5):** `file_path = NULL` para todos os 7 docs.

---

## 3. STEP 2 — UPDATEs Aplicados

**STEP 2.3 — DRY-RUN Python (container):**
```
Cenário B: updates=[] (todos NULL — sem path pra validar em disco)
TODOS OK — SEGURO COMITAR
```

**STEP 2.5 — Verificação pós-UPDATE (folha_pagamento 03/2026 com file_path NOT NULL):**
```sql
SELECT kd.id, kd.document_type, kd.file_path,
       EXISTS(SELECT 1 FROM pg_ls_dir('/app/uploads') WHERE 1=0) AS dummy
FROM ged_kit_documents kd
JOIN ged_document_kits dk ON dk.id=kd.kit_id
WHERE dk.reference_month='2026-03-01'
  AND kd.document_type='folha_pagamento'
  AND kd.file_path IS NOT NULL
```
```
folha_pagamento 03/2026 com file_path NOT NULL: 0 rows
```
→ ✅ Cenário B confirmado — todos os 7 file_paths foram zerados corretamente.

**STEP 2 — Tabela de UPDATEs:**

| ID | Tipo | file_path ANTES | file_path DEPOIS |
|----|------|-----------------|------------------|
| `00fabbe6-...` | folha_pagamento | `/app/uploads/onvio/inss_guia/2026-04/Folha 03.2026_Mirante das Flores (2).pdf` | `NULL` |
| `a92b06b9-...` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Ideal Flores.pdf` | `NULL` |
| `a049d426-...` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Laranjeiras Village.pdf` | `NULL` |
| `57484c54-...` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Michelangelo.pdf` | `NULL` |
| `8dbf8e11-...` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Prime Arena (1).pdf` | `NULL` |
| `9485afe0-...` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Villa Dei Fior.pdf` | `NULL` |
| `c64bb7dd-...` | folha_pagamento | `/app/uploads/onvio/outros/2026-04/Folha 03.2026_Villa dos Passaros.pdf` | `NULL` |

**SQL:** `/tmp/d3_1_updates.sql`

```sql
BEGIN;
UPDATE ged_kit_documents SET file_path=NULL, updated_at=NOW()
  WHERE id = '00fabbe6-9e40-4ab4-b524-5709af7884c7';  -- Mirante
UPDATE ged_kit_documents SET file_path=NULL, updated_at=NOW()
  WHERE id = 'a92b06b9-ed1d-41c9-8313-c32adae147f9';  -- Ideal Flores
UPDATE ged_kit_documents SET file_path=NULL, updated_at=NOW()
  WHERE id = 'a049d426-98ae-4f4f-b482-f9b4ee2002f1';  -- Laranjeiras
UPDATE ged_kit_documents SET file_path=NULL, updated_at=NOW()
  WHERE id = '57484c54-8c4b-4314-bb1c-2792e4e4cba2';  -- Michelangelo
UPDATE ged_kit_documents SET file_path=NULL, updated_at=NOW()
  WHERE id = '8dbf8e11-de9d-4357-b9ee-ad4d4d2a46cb';  -- Prime Arena
UPDATE ged_kit_documents SET file_path=NULL, updated_at=NOW()
  WHERE id = '9485afe0-4eb9-4411-a2ff-aca1927a9f1b';  -- Villa Dei Fior
UPDATE ged_kit_documents SET file_path=NULL, updated_at=NOW()
  WHERE id = 'c64bb7dd-88d2-4c7b-a968-f7bc3a6c4d08';  -- Villa Passaros
COMMIT;
```

**Resultado:** 7 UPDATE 1, COMMIT ✅

**Confirmação pós-update:**
```
SELECT COUNT(*) FROM ged_kit_documents WHERE file_path LIKE '%/2026-04/%'
→ 0
```

---

## 4. STEP 3 — PDFs de Teste Movidos

```
/tmp/d3_1_pdfs_teste_descartados/
  Folha 03.2026_Ideal Flores (2).pdf    (121197 bytes)
  Folha 03.2026_Ideal Flores.pdf        (121844 bytes)
  Folha 03.2026_Laranjeiras Village.pdf (121330 bytes)
  Folha 03.2026_Michelangelo.pdf        (121330 bytes)
  Folha 03.2026_Mirante das Flores (2).pdf (121330 bytes)
  Folha 03.2026_Prime Arena (1).pdf     (121330 bytes)
  Folha 03.2026_Villa Dei Fior.pdf      (121330 bytes)
  Folha 03.2026_Villa dos Passaros.pdf  (121330 bytes)
```

**Diretórios removidos:**
- `/uploads/onvio/outros/2026-04/` ✅
- `/uploads/onvio/inss_guia/2026-04/` ✅

```
find /uploads/onvio -name "*2026-04*" → (vazio) ✅
```

---

## 5. STEP 4 — Validação E2E

### 4.1 — Download dos 7 docs (curl %{http_code}|%{size_download}|%{content_type})

```bash
for DOC in ${DOCS[@]}; do
  curl -s -o /dev/null -w "%{http_code}|%{size_download}|%{content_type}" \
    -H "Authorization: Bearer $TOKEN" \
    "http://127.0.0.1:8080/api/v1/people-management/ged/documents/${DOC}/download"
done
```

| Doc ID | http_code | size_download | content_type |
|--------|-----------|---------------|--------------|
| `00fabbe6-...` | 404 | 51 | application/json |
| `a92b06b9-...` | 404 | 51 | application/json |
| `a049d426-...` | 404 | 51 | application/json |
| `57484c54-...` | 404 | 51 | application/json |
| `8dbf8e11-...` | 404 | 51 | application/json |
| `9485afe0-...` | 404 | 51 | application/json |
| `c64bb7dd-...` | 404 | 51 | application/json |

✅ Todos 7 retornam 404 + JSON (51 bytes = `{"detail":"Documento nao possui arquivo vinculado"}`)

### 4.2 — Loop de tamanho (folha_pagamento 03/2026 com path Onvio)

```sql
SELECT kd.id, kd.document_type, kd.file_path
FROM ged_kit_documents kd
JOIN ged_document_kits dk ON dk.id=kd.kit_id
WHERE dk.reference_month='2026-03-01'
  AND kd.document_type='folha_pagamento'
  AND kd.file_path LIKE '/app/uploads/onvio/%'
```
```
folha_pagamento 03/2026 com path Onvio: 0 rows
```
→ ✅ N/A — nenhum doc com path Onvio em disco (Cenário B)

### 4.3 — onvio_documents intacto

```
SELECT COUNT(*) FROM onvio_documents → 534 ✅
```

### 4.4 — pytest gedeon

```
94/94 PASS ✅
```

Testes atualizados para refletir estado pós-D3.1:
- `test_d3_download.py::test_folha_pagamento_03_2026_placeholder` — verifica 7 NULL
- `test_d3_download.py::real_doc_id` fixture — usa PDF histórico GED (não Onvio)
- `test_d2_onvio_matching.py::test_match_onvio_casa_docs_existentes` — verifica 7 NULL

---

## 6. STEP 5 + STEP 6 — §40.1 v1.40 Commitado

| Commit | Hash | Tipo |
|--------|------|------|
| fix(gedeon): D3.1 — file_paths Onvio zerados + testes atualizados (§40.1) | `b17d795a` | Fix |
| docs(gedeon): CONTRATO v1.40 — §40.1 D3.1 correção file_paths | `4e42d4da` | Docs |
| docs(gedeon): D3.1 relatório correção file_paths (§40.1) | `e4ceef48` | Docs |

---

## 7. Validações 🔴 A-G

| # | Validação | Resultado |
|---|-----------|-----------|
| 🔴 A | pytest 94/94 PASS (zero código mudou) | ✅ |
| 🔴 B | 7 ged_kit_documents.file_path → NULL (Cenário B INV-5) | ✅ |
| 🔴 C | file_path != NULL: arquivo existe em disco | ✅ N/A (todos NULL) |
| 🔴 D | curl 7 docs → 404 "Documento nao possui arquivo vinculado" | ✅ |
| 🔴 E | Dirs `/uploads/onvio/.../2026-04/` removidos | ✅ |
| 🔴 F | `find /uploads/onvio -name "*2026-04*"` = vazio | ✅ |
| 🔴 G | onvio_documents (534), 10 kits 04/2026, 552 docs 04/2026, 32 templates, 320 presenças, 8 certidões — todos intactos | ✅ |

---

## 8. Self-Check

| Item | Status |
|------|--------|
| STEP 0 — backup SQL criado (512KB) | ✅ |
| STEP 1 — disco inventariado (106 PDFs) | ✅ |
| STEP 1 — 7/7 nomes só existem como test copies em /2026-04/ | ✅ |
| STEP 1 — hipótese vencedora: Cenário B / H5 | ✅ |
| STEP 2 — DRY-RUN antes de UPDATE | ✅ |
| STEP 2 — 7 UPDATEs aplicados (file_path=NULL) | ✅ |
| STEP 3 — 8 PDFs movidos para /tmp (não rm) | ✅ |
| STEP 3 — dirs /2026-04/ removidos | ✅ |
| STEP 4 — 7 downloads retornam 404 (placeholder honesto) | ✅ |
| STEP 4 — onvio_documents intacto (534) | ✅ |
| STEP 4 — pytest 94/94 PASS | ✅ |
| 🔴 G — trilogia A/B/C: 32 templates, 320 presenças, 10 kits, 552 docs 04/2026, 8 certidões | ✅ |
| STEP 2.5 — query explícita: 0 folha_pagamento 03/2026 com file_path NOT NULL | ✅ |
| STEP 4.1 — curl loop com %{http_code}\|%{size_download}\|%{content_type} | ✅ |
| STEP 4.2 — loop size: 0 docs com path Onvio em disco (Cenário B N/A) | ✅ |
| STEP 5 — fix commitado (`b17d795a`) + contrato (`4e42d4da`) + relatório (`e4ceef48`) | ✅ |
| 🔴 A-G todas PASS | ✅ |
| Zero código alterado (controllers, services, models, frontend) | ✅ |

---

## 9. Cenário Identificado

**Cenário B** — PDFs reais nunca foram baixados.

D1 criou 534 registros em `onvio_documents` com `caminho_local` como path esperado,
mas o download físico dos arquivos ocorreu apenas para 98 PDFs (Comprovante de
Rendimentos de 2025). Os 7 "Folha 03.2026" da competência 03/2026 existem no
servidor Onvio mas não foram puxados.

D3 STEP 2C criou cópias de teste (conteúdo de Comprovante de Rendimentos renomeado)
para permitir validação do endpoint. Esses arquivos são falsos — não contêm folha
de pagamento.

D3.1 corrige o estado para honesto: `file_path=NULL` (placeholder), sem inventar paths.
Quando o próximo sync Onvio rodar com download forçado, os 7 PDFs serão baixados e
os `file_paths` serão preenchidos com paths reais.

---

## 10. D3.1 PRONTO

Os 7 `ged_kit_documents` de 03/2026 agora estão em estado honesto — placeholders
aguardando o próximo sync Onvio:

| Kit | Condomínio | Doc ID |
|-----|------------|--------|
| `011e6182-...` | Michelangelo | `57484c54-8c4b-4314-bb1c-2792e4e4cba2` |
| (03/2026) | Ideal Flores | `a92b06b9-ed1d-41c9-8313-c32adae147f9` |
| (03/2026) | Laranjeiras Village | `a049d426-98ae-4f4f-b482-f9b4ee2002f1` |
| (03/2026) | Prime Arena (1) | `8dbf8e11-de9d-4357-b9ee-ad4d4d2a46cb` |
| (03/2026) | Villa Dei Fior | `9485afe0-4eb9-4411-a2ff-aca1927a9f1b` |
| (03/2026) | Villa dos Passaros | `c64bb7dd-88d2-4c7b-a968-f7bc3a6c4d08` |
| (03/2026) | Mirante das Flores (2) | `00fabbe6-9e40-4ab4-b524-5709af7884c7` |

Botão ⬇️ retorna 404 limpo para esses docs até o próximo sync Onvio.
PDFs de teste descartados em `/tmp/d3_1_pdfs_teste_descartados/`.

*Gerado por Claude Code — [session: D3.1] [module: gedeon/ged]*
