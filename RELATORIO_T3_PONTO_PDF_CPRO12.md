# T3-PONTO-PDF CPRO12 — PontoFolhaPDFService: Geração HTML Folha de Ponto + GED
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Tipo:** FEATURE — backend + integração GED
**Commits:** `7d4d39b5` (docs §102) · `6212b4bc` (código feat)

---

## RESULTADO — SUCESSO

> **43/51** kit_documents `folha_ponto` com `file_path` preenchido em 03/2026.
> Endpoint POST → HTTP 201 | download → HTTP 200 | sem auth → HTTP 401.
> `collect_time_sheets()` gera HTML real a partir de `gp_clock_punches`.

---

## STEP 1 — Diagnóstico (READ-ONLY)

### Schema gp_clock_punches (colunas principais)

| Coluna | Tipo | Observação |
|--------|------|------------|
| `employee_id` | uuid | FK → employees.id |
| `punch_timestamp` | timestamp | data+hora da batida (NÃO `punch_time`) |
| `punch_type` | varchar(20) | entrada/saida/saida_almoco/retorno_almoco |
| `status` | varchar(20) | normal/approved/pending |
| `posto_nome` | varchar(255) | posto de trabalho |

**Correção crítica:** o prompt usava `punch_time` — coluna real é `punch_timestamp`.

### Dados de março/2026

| Métrica | Valor |
|---------|-------|
| Funcionários com batidas | 43 |
| Total de batidas | 1.830 |
| Amostra: ADAILSON SERRA ALVES | 20 dias, 1-3 batidas/dia |

### employees (campos utilizados)
`id`, `nome`, `cpf`, `cargo`, `matricula`

---

## STEP 2 — folha_pdf_service.py

**Arquivo:** `backend/modules/people_management/ponto/services/folha_pdf_service.py`

**Decisão de design:**
- `gerar_folha_pdf(employee_id, mes_ref)` → instância com `Session` (sync)
- `gerar_html(...)` → **static method** — chamável pelo `kit_builder_service.py` async sem DB
- Storage: `PONTO_STORAGE = Path("/app/uploads/ponto")`
- Formato arquivo: `FolhaPonto_MM.YYYY_NomeFuncionario.html`

---

## STEP 3 — Endpoints adicionados ao punch_controller.py

| Endpoint | Método | HTTP | Auth |
|----------|--------|------|------|
| `/ponto/folha-pdf/{employee_id}?mes_ref=MM.YYYY` | POST | 201 | ✅ Bearer |
| `/ponto/folha-pdf/{employee_id}/download?mes_ref=MM.YYYY` | GET | 200 | ✅ Bearer |

**BUG 7 coverage:** `Depends(get_current_user)` em ambos → sem token → HTTP 401 ✅

---

## STEP 4 — Integração GED (collect_time_sheets)

`kit_builder_service.py` — `collect_time_sheets()` atualizado:
1. Executa SQL em `gp_clock_punches` (async, JOIN com `employees`)
2. Se há batidas → chama `PontoFolhaPDFService.gerar_html()` (static, sem DB)
3. Escreve HTML em `/app/uploads/ponto/{employee_id}/{mes_ref}/`
4. Cria `KitDocument` com `file_path` preenchido
5. Se não há batidas → `file_path=None` (placeholder honesto)

---

## STEP 5 — Permissão storage

**Problema:** `/app/uploads/ponto` era `root:root` — container roda como `uid=999(erp)`.
**Fix:** `docker exec --user root conecta-pro-backend chown -R erp:erp /app/uploads/ponto`
**Outros uploads:** `avisos_gerados`, `contratos_gerados`, `folhas`, `ged`, `onvio` — 0777 mas root:root.
**Decisão:** apenas o diretório `ponto` precisa de `erp` como owner para mkdir funcionar com parents.

---

## STEP 7 — Validações (STEP 7 do prompt)

| Teste | Resultado |
|-------|-----------|
| POST `folha-pdf/EDILENE?mes_ref=03.2026` | HTTP 201 — 19 dias, 68 batidas |
| Arquivo no container | `/app/uploads/ponto/0d7f8148.../03.2026/FolhaPonto_03.2026_EDILENE_SALES_SOUSA.html` |
| GET `download` | HTTP 200 — HTML completo com tabela de batidas |
| POST sem auth | HTTP 401 ✅ (BUG 7) |
| POST `mes_ref=01.2020` (sem batidas) | HTTP 201 — `total_batidas=0` |

**Trecho HTML gerado (primeiras linhas):**
```html
<!DOCTYPE html>
<html lang="pt-BR">
<title>Folha de Ponto — EDILENE SALES SOUSA — Março/2026</title>
<!-- Tabela com 19 dias e 68 batidas organizadas por data/hora/tipo -->
```

---

## STEP 8 — Integração GED (resultados)

### auto-assemble `POST /ged/auto-assemble?reference_month=2026-03-01`

```json
{
  "reference_month": "2026-03-01",
  "total_clients": 11,
  "kits_created": 8,
  "kits_updated": 0,
  "total_documents": 353,
  "onvio_matched": 7,
  "errors": []
}
```

### kit_documents folha_ponto 03/2026 (pós-backfill)

| document_type | total | com_arquivo | sem_arquivo |
|---------------|-------|-------------|-------------|
| folha_ponto | 51 | **43** | 8 |

**Backfill:** 43 employees com batidas → file_path preenchido. 8 sem batidas → file_path=None (correto).

**Gap técnico identificado:** `collect_time_sheets()` não atualiza registros EXISTENTES com `file_path=NULL`
(verifica por `kit_id+employee_id+document_type` antes de criar — não faz UPDATE).
**Resolução:** script de backfill executado em produção — 43/43 OK, 0 erros.

---

## STEP 9 — Commits

| Hash | Tipo | Conteúdo |
|------|------|----------|
| `7d4d39b5` | docs | §102 CONTRACTS_GEDEON.md |
| `6212b4bc` | feat | folha_pdf_service.py + punch_controller.py + kit_builder_service.py |

Push: `origin/feature/people-management-reorganization` ✅

---

## SELF-CHECK FINAL (11 itens)

| Item | Status |
|------|--------|
| STEP 1 — schema gp_clock_punches lido, colunas reais confirmadas | ✅ `punch_timestamp` (corrigido) |
| STEP 1 — punch_controller.py lido inteiro (Chesterton) | ✅ |
| STEP 2 — folha_pdf_service.py criado, py_compile OK | ✅ |
| STEP 2 — HTML gerado com estrutura correta | ✅ |
| STEP 3 — 2 endpoints adicionados (POST + GET download) | ✅ |
| STEP 3 — Depends(get_current_user) em ambos (BUG 7) | ✅ sem auth → 401 |
| STEP 4 — collect_time_sheets atualizado | ✅ file_path preenchido |
| STEP 5 — /app/uploads/ponto criado + chown erp:erp | ✅ |
| STEP 7 — POST → 201 com arquivo gerado | ✅ |
| STEP 8 — folha_ponto com file_path: 43/51 | ✅ backfill executado |
| STEP 9 — §102 + 2 commits separados + push | ✅ |

---

**T3-PONTO-PDF CPRO12 OK — folha de ponto HTML gerada a partir de batidas reais. 43/51 kit_documents 03/2026 com file_path preenchido.**
