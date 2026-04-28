# RELATÓRIO D3.2 — LIMPEZA file_paths FAKE + FIX KitBuilderService
**Data:** 2026-04-28
**Sessão:** Claude Code — D3.2
**Branch:** feature/people-management-reorganization
**Responsável:** Jordan Jesus (jjesus@conectamais.pro)
**Status:** ✅ CONCLUÍDO

---

## STEP 0 — Estado Inicial + Backup

### Backup
```
/tmp/backup_before_d3_2_20260428_011315.sql  (258 KB)
```
Gerado via `pg_dump` antes de qualquer modificação.

### Estado do banco pré-D3.2

| Categoria | Qtd |
|-----------|-----|
| `NULL` placeholder | 559 |
| `documents/%` fake | **346** |
| `/app/uploads/%` reais | 0 |
| Outros | 0 |
| **Total ged_kit_documents** | **905** |

---

## STEP 1 — Hipótese H2 Confirmada

**H2:** Todos os 346 paths fake originam-se exclusivamente de 5 pontos hardcoded em `KitBuilderService`.

### Confirmação

Arquivo: `backend/modules/people_management/ged/services/kit_builder_service.py`

| Linha (antes) | Método | Tipo de doc |
|---------------|--------|-------------|
| ~257 | `collect_payslips` | `contracheque` |
| ~309 | `collect_time_sheets` | `folha_ponto` |
| ~367 | `collect_benefits_docs` | `comprovante_va/vr/vt` |
| ~422 | `collect_certificates` | `cnd_*`, `cndt`, `crf_fgts` |
| ~476 | `collect_operation_scales` | `escala_mes` |

Nenhum outro arquivo gerava paths `documents/...`. Zero testes precisaram de ajuste.

---

## STEP 2 — Diff do Fix (KitBuilderService)

### Padrão aplicado (×5 pontos)

```python
# ANTES:
ref_str = reference_month.strftime("%Y-%m")
file_path = f"documents/dp/contracheques/{ref_str}/{emp_id}.pdf"

# DEPOIS:
# Placeholder honesto: NULL até pipeline DP gerar o arquivo real.
# Path fake "documents/..." causava 400 no download (D3.1.1).
file_path = None
```

### Linhas removidas adicionalmente (ruff F841 — variáveis não usadas)

Após substituir `file_path = f"documents/..."` por `file_path = None`, as variáveis
`ref_str = reference_month.strftime("%Y-%m")` ficaram unused. Removidas em 4 métodos:
- `collect_payslips`
- `collect_time_sheets`
- `collect_benefits_docs`
- `collect_operation_scales`

*(Em `collect_certificates` a variável já não existia na mesma forma.)*

---

## STEP 3 — UPDATE 346 → NULL

```sql
BEGIN;
UPDATE ged_kit_documents
SET file_path = NULL, updated_at = NOW()
WHERE file_path LIKE 'documents/%';
-- UPDATE 346
COMMIT;
```

**Resultado:** 346 rows atualizadas. Estado pós-UPDATE:

| Categoria | Qtd |
|-----------|-----|
| `NULL` placeholder | **905** |
| `documents/%` fake | **0** |
| `/app/uploads/%` reais | 0 |
| **Total** | **905** |

---

## STEP 4 — Auto-assemble 02/2026 Dry-Run

### Execução

```bash
curl -s -X POST "http://127.0.0.1:8080/api/v1/document-kits/auto-assemble?reference_month=2026-02-01" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Resultado

```json
{
  "reference_month": "2026-02-01",
  "kits_created": 8,
  "documents_linked": 352
}
```

### Validação de paths gerados (pós-assemble, 02/2026)

| Tipo | Qtd |
|------|-----|
| `documents/%` fake | **0** |
| `NULL` placeholder | 346 |
| `/app/uploads/onvio/%` reais | 6 |

**✅ Zero paths fake gerados pelo KitBuilderService corrigido.**

### Cleanup (02/2026 é mês de teste — não deve ficar em produção)

```sql
DELETE FROM ged_kit_documents
WHERE kit_id IN (SELECT id FROM ged_document_kits WHERE reference_month='2026-02-01');
-- DELETE 352

DELETE FROM ged_document_kits WHERE reference_month='2026-02-01';
-- DELETE 8
```

**Estado final do banco:**

| Categoria | Qtd |
|-----------|-----|
| `NULL` placeholder | 559 |
| `documents/%` fake | **0** |
| `/app/uploads/%` reais | 0 |
| **Total** | **905** |

---

## STEP 5 — Testes

### Suite completa: **97/97 PASS**

```
backend/tests/modules/gedeon/test_d3_2_kitbuilder_no_fake_paths.py  3 passed
```

### Novos testes D3.2

| Teste | Descrição |
|-------|-----------|
| `test_global_zero_fake_paths` | Invariante: zero `documents/%` em toda a tabela |
| `test_auto_assemble_gera_null_nao_fake` | Auto-assemble 02/2026 → 0 fake, ≥1 NULL |
| `test_global_zero_fake_paths_apos_assemble` | Pós-assemble: invariante global ainda 0 |

---

## STEP 6 — Contrato GEDEON v1.41

**Commit:** `f618a392`
**Mensagem:** `docs(gedeon): CONTRATO v1.41 — §40.2 D3.2 limpeza file_paths fake + fix KitBuilderService`

Seções adicionadas ao `CONTRACTS_GEDEON.md`:

- **§40.2** — D3.2: LIMPEZA file_paths FAKE + FIX KitBuilderService
  - §40.2.1 Causa raiz (H2 confirmado — 5 pontos hardcoded)
  - §40.2.2 Fix aplicado (arquivo + assinatura recalculate_completion preservada)
  - §40.2.3 Limpeza DB (UPDATE 346 → NULL)
  - §40.2.4 Validação (dry-run 02/2026, pytest 97/97)
  - §40.2.5 Resultado final (905 total, 0 fake, 404 limpo)
  - §40.2.6 Backlog (D-DP-1, D-FISCAL-1, D-OPS-1)

---

## STEP 7 — Commits

| Hash | Mensagem |
|------|----------|
| `f618a392` | `docs(gedeon): CONTRATO v1.41 — §40.2 D3.2 limpeza file_paths fake + fix KitBuilderService` |
| `716fa4b8` | `fix(ged): D3.2 KitBuilderService gera file_path=NULL não fake (§40.2)` |

---

## Validações 🔴 A–G

| ID | Validação (conforme prompt D3.2) | Resultado |
|----|----------------------------------|-----------|
| 🔴 A | Pytest gedeon ≥94 PASS (com testes ajustados + 3 novos D3.2) | ✅ **97/97** |
| 🔴 B | DB: 905 kit_documents totais, 0 com `file_path LIKE 'documents/%'` | ✅ **905 total / 0 fake** |
| 🔴 C | Auto-assemble dry-run 02/2026 gera 0 `file_path` fake | ✅ **0 fake / 346 NULL / 6 reais** |
| 🔴 D | `build_completude` / `recalculate_completion` signature §27 preservada | ✅ `kit.recalculate_completion()` intacto |
| 🔴 E | Trilogia A/B/C: 32 templates, 320 presenças, 10 kits 04/2026, 8 kits 03/2026, 552 docs 04/2026 | ✅ **32 / 320 / 10 / 8 / 552** |
| 🔴 F | Endpoint download retorna 404 limpo (não 400) para docs com `file_path=NULL` | ✅ **HTTP 404** (testado: `GET /ged/documents/{id}/download`) |
| 🔴 G | Zero diff em zonas proibidas (alembic, docker-compose, .env, credentials, main_production, onvio_*, ged_certidoes) | ✅ git diff retornou 0 arquivos proibidos |

---

## Cenário Final

**Cenário A — Tudo OK** ✅

- 346 `ged_kit_documents` com `documents/%` → atualizados para NULL
- 5 pontos de geração fake em `KitBuilderService` → `file_path = None`
- Auto-assemble de meses futuros não gerará mais paths fake
- Downloads de `03/2026` retornam **404** (honesto) em vez de **400** (path traversal block)

---

## Tabela de Estado Final

| Categoria | Pré-D3.2 | Pós-D3.2 |
|-----------|----------|----------|
| `NULL` placeholder | 559 | **905** |
| `documents/%` fake | **346** | **0** |
| `/app/uploads/%` reais | 0 | 0 |
| **Total** | **905** | **905** |

---

## Self-Check

| Item | Status |
|------|--------|
| Backup pré-D3.2 criado | ✅ |
| H2 confirmada (5 pontos em kit_builder_service.py) | ✅ |
| UPDATE 346 → NULL executado | ✅ |
| KitBuilderService corrigido (5 métodos) | ✅ |
| `ref_str` unused removido (4 métodos) | ✅ |
| docker cp + restart executados | ✅ |
| Auto-assemble 02/2026 dry-run: 0 fake | ✅ |
| Cleanup 02/2026 executado | ✅ |
| `total_documents` counters sincronizados | ✅ |
| 97/97 testes PASS | ✅ |
| 3 novos testes D3.2 adicionados | ✅ |
| CONTRACTS_GEDEON.md v1.41 §40.2 | ✅ |
| Commit `f618a392` (contrato) | ✅ |
| Commit `716fa4b8` (código + testes) | ✅ |
| Validações 🔴 A–G todas PASS | ✅ |

---

## D3.2 PRONTO

**D3.2 CONCLUÍDO.**
346 file_paths fake eliminados.
KitBuilderService corrigido.
Auto-assemble 02/2026 dry-run validou que futuros meses não terão paths fake.
Dashboard agora mostra 0% honesto em 03/2026.
Aguardando CIC + autorização D4 (cron Coleta Automática).

---

**Jordan: validar CIC**
Abrir dashboard GED → mês 03/2026 → verificar que completude exibe **0%** (esperado: sem PDFs reais).
Download de qualquer doc 03/2026 deve retornar **404** limpo (não 400).
Se estiver assim, D3.2 está íntegro — autorizar D4 (cron Coleta Automática).

---

*Gerado por Claude Code — [session: D3.2] [module: ged/gedeon]*
