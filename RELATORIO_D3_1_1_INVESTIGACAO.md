# RELATÓRIO D3.1.1 — INVESTIGAÇÃO file_paths FAKE (documents/%)
**Data:** 2026-04-27
**Sessão:** Claude Code — D3.1.1
**Branch:** feature/people-management-reorganization
**Status:** ✅ DIAGNÓSTICO CONCLUÍDO — D3.2 pendente (autorização Jordan)

---

## 1. Gatilho

Dashboard mostrava docs de 03/2026 com `file_path` preenchido que não resultavam em
download funcional. Investigação para identificar origem e padrão dos paths.

---

## 2. Queries executadas

### Query 1 — Agregação por document_type e fonte

```sql
SELECT
  kd.document_type,
  COUNT(*) AS qtd,
  array_agg(DISTINCT
    CASE
      WHEN kd.file_path IS NULL THEN 'NULL'
      WHEN kd.file_path LIKE '/app/uploads/onvio/%' THEN 'onvio_real'
      WHEN kd.file_path LIKE 'documents/%' THEN 'seed_fake_relativo'
      WHEN kd.file_path LIKE '/app/uploads/%' THEN 'uploads_outros'
      ELSE 'OUTRO: ' || substring(kd.file_path, 1, 40)
    END
  ) AS fontes
FROM ged_kit_documents kd
JOIN ged_document_kits dk ON dk.id=kd.kit_id
WHERE dk.reference_month='2026-03-01'
  AND kd.file_path IS NOT NULL
GROUP BY kd.document_type
ORDER BY 2 DESC;
```

**Resultado:**

| document_type | qtd | fonte |
|---------------|-----|-------|
| folha_ponto | 51 | seed_fake_relativo |
| comprovante_va | 51 | seed_fake_relativo |
| comprovante_vr | 51 | seed_fake_relativo |
| comprovante_vt | 51 | seed_fake_relativo |
| contracheque | 51 | seed_fake_relativo |
| escala_mes | 51 | seed_fake_relativo |
| cnd_federal | 8 | seed_fake_relativo |
| cnd_municipal | 8 | seed_fake_relativo |
| cndt_trabalhista | 8 | seed_fake_relativo |
| crf_fgts | 8 | seed_fake_relativo |
| cnd_estadual | 8 | seed_fake_relativo |

**→ 100% seed_fake_relativo. Zero paths reais.**

---

### Query 2 — Paths únicos e repetição

**Padrão DP/Operacional** (UUID único por funcionário):
```
documents/dp/contracheques/2026-03/176f110f-237c-44c6-bad3-e5ba7e495b3a.pdf
documents/dp/folhas_ponto/2026-03/176f110f-237c-44c6-bad3-e5ba7e495b3a.pdf
documents/dp/beneficios/2026-03/vt/176f110f-237c-44c6-bad3-e5ba7e495b3a.pdf
documents/dp/beneficios/2026-03/va/176f110f-237c-44c6-bad3-e5ba7e495b3a.pdf
documents/dp/beneficios/2026-03/vr/176f110f-237c-44c6-bad3-e5ba7e495b3a.pdf
documents/operacoes/escalas/2026-03/176f110f-237c-44c6-bad3-e5ba7e495b3a.pdf
```

**Padrão Certidões** (mesmo path repetido para todos os 8 clientes):
```
documents/fiscal/certidoes/cnd_federal.pdf      ← 8× (1 por cliente)
documents/fiscal/certidoes/cnd_estadual.pdf     ← 8×
documents/fiscal/certidoes/cnd_municipal.pdf    ← 8×
documents/fiscal/certidoes/cndt_trabalhista.pdf ← 8×
documents/fiscal/certidoes/crf_fgts.pdf         ← 8×
```

---

### Query 3 — Inventário global (todos os meses)

```sql
SELECT
  COUNT(*) FILTER (WHERE file_path IS NULL)                          AS null_placeholder,
  COUNT(*) FILTER (WHERE file_path LIKE '/app/uploads/%')            AS uploads_reais,
  COUNT(*) FILTER (WHERE file_path LIKE 'documents/%')               AS documents_fake,
  COUNT(*) FILTER (WHERE file_path NOT LIKE 'documents/%'
                     AND file_path NOT LIKE '/app/uploads/%'
                     AND file_path IS NOT NULL)                       AS outros
FROM ged_kit_documents;
```

**Resultado:**

| null_placeholder | uploads_reais | documents_fake | outros |
|-----------------|---------------|----------------|--------|
| 559 | **0** | 346 | 0 |

**Total: 905 kit_documents. Zero PDFs reais em disco.**

---

## 3. Causa Raiz

### 3.1 — GED_STORAGE_BASE inexistente

```python
# document_collector_service.py
GED_STORAGE_BASE = /opt/conecta-pro/storage/ged
```

Diretório **não existe** no host nem no container.
Path resolvido: `/opt/conecta-pro/storage/ged/documents/dp/contracheques/2026-03/...`

### 3.2 — INV-3 bloqueia todos os paths `documents/`

```python
# document_controller.py — download_document()
_base = Path("/app/uploads").resolve()   # /app/uploads
_target = Path(full_path).resolve()      # /opt/conecta-pro/storage/ged/documents/...
if not _target.is_relative_to(_base):
    raise HTTPException(status_code=400, detail="Path de arquivo invalido")
```

`/opt/conecta-pro/storage/ged/...` não é relativo a `/app/uploads` → **400 para todos os 346**.

### 3.3 — Origem dos paths fake

O `KitBuilderService` (BLOCO A — geração de kits 03/2026) populou `file_path` com
paths de placeholder no formato `documents/...`, esperando que um pipeline posterior
(geração de contracheques, upload de certidões) preenchesse os arquivos físicos.
Esse pipeline nunca rodou — os paths ficaram como dívida técnica.

---

## 4. Mapa completo — ged_kit_documents

| Categoria | Qtd | Mês | Retorno download |
|-----------|-----|-----|-----------------|
| `NULL` placeholder | 559 | 03/2026 (7) + 04/2026 (552) | 404 |
| `documents/dp/...` fake | 255 | 03/2026 | 400 |
| `documents/operacoes/...` fake | 51 | 03/2026 | 400 |
| `documents/fiscal/...` fake | 40 | 03/2026 | 400 |
| `/app/uploads/...` reais | **0** | — | — |
| **Total** | **905** | | |

---

## 5. Breakdown dos 346 fake (03/2026)

| Subtipo | Qtd | Padrão path | Problema |
|---------|-----|-------------|----------|
| Certidões compartilhadas | 40 | `documents/fiscal/certidoes/X.pdf` (1 arquivo × 8 clientes) | Path fake + arquivo único compartilhado (inválido por cliente) |
| DP individual | 255 | `documents/dp/{tipo}/2026-03/{uuid}.pdf` | Path fake com UUID por funcionário — diretório nunca criado |
| Escalas | 51 | `documents/operacoes/escalas/2026-03/{uuid}.pdf` | Idem DP |

---

## 6. Cenário identificado

**Cenário X1 — 100% seed_fake_relativo**

Nenhum dos dois outros cenários se confirmou:
- ❌ Cenário X2 (paths reais de outro pipeline) — `uploads_reais = 0`
- ❌ Cenário X3 (misto) — todos `documents/%`, zero `/app/uploads/%`

---

## 7. Ação necessária — D3.2 (pendente autorização Jordan)

```sql
-- Preview: 346 docs afetados
SELECT COUNT(*) FROM ged_kit_documents WHERE file_path LIKE 'documents/%';
-- → 346

-- UPDATE (executar com BEGIN/COMMIT após autorização)
BEGIN;
UPDATE ged_kit_documents
SET file_path = NULL, updated_at = NOW()
WHERE file_path LIKE 'documents/%';
-- Expected: UPDATE 346
COMMIT;
```

**Pós-D3.2:** 905 kit_documents, todos NULL (placeholder honesto).
Download retorna 404 limpo em vez de 400 (path traversal block).

**Origem correta dos arquivos:**
- `contracheque`, `folha_ponto`, `comprovante_*`: gerados pelo pipeline DP (a implementar)
- `escala_mes`: exportado pelo módulo Operacional (a implementar)
- `cnd_*`, `cndt_trabalhista`, `crf_fgts`: baixados do GovBR/Receita (a implementar)

---

## 8. Self-Check

| Item | Status |
|------|--------|
| Query 1 executada — agregação por tipo e fonte | ✅ |
| Query 2 executada — paths raw amostra 30 linhas | ✅ |
| Query 3 executada — inventário global todos os meses | ✅ |
| GED_STORAGE_BASE identificado (`/opt/conecta-pro/storage/ged`) | ✅ |
| Diretório inexistente confirmado (host + container) | ✅ |
| Download teste confirmado (400 para `documents/%`) | ✅ |
| INV-3 identificado como bloqueador correto | ✅ |
| Cenário X1 confirmado (100% seed_fake_relativo) | ✅ |
| D3.2 escopo definido (346 UPDATEs → NULL) | ✅ |
| D3.2 aguardando autorização Jordan | ⏳ |

---

*Gerado por Claude Code — [session: D3.1.1] [module: gedeon/ged]*
