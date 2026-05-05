# T1-MODAL-PONTO CPRO12 — Fix KitDetalheModal + Diagnóstico Ponto Sólides→GEDEON
**Data:** 2026-05-05
**Branch:** feature/people-management-reorganization
**Tipo:** FRONTEND FIX (CSS) + DIAGNÓSTICO READ-ONLY (pipeline ponto)
**Commits:** `6f69b10c` (frontend fix) · `8eaee024` + `906fbefb` (§100 CONTRACTS_GEDEON)

---

## RESULTADO — SUCESSO

> **Item A:** KitDetalheModal fundo opaco — `bg-white dark:bg-gray-900` adicionado ao `DialogContent`.
> **Item B:** Cenário B confirmado — batidas existem (`gp_clock_punches`: 1830 registros) mas pipeline PDF (D3.1.1) não implementado; `collect_time_sheets()` cria `KitDocument` com `file_path=None`.

---

## ITEM A — Fix KitDetalheModal fundo transparente

### Cenário identificado: A (DialogContent sem bg-white)

**Arquivo:** `frontend/src/components/gedeon/KitDetalheModal.tsx` · linha 86

**ANTES:**
```tsx
<DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
```

**DEPOIS:**
```tsx
<DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto bg-white dark:bg-gray-900">
```

### Build e deploy

| Etapa | Resultado |
|-------|-----------|
| `npm run build` | ✅ `Compiled successfully in 45s` · 286 páginas |
| BUILD_ID gerado | `conecta-pro-1778011721693` |
| `docker cp standalone/` para container | ✅ |
| `docker cp .next/static/` para container | ✅ |
| `docker restart conecta-pro-frontend` | ✅ HTTP 200 |
| BUILD_ID no container | ✅ `conecta-pro-1778011721693` (confirmado) |
| `bg-white` no chunk compilado | ✅ presente em `7a0a16547a9ef0e5.js` |

---

## ITEM B — Diagnóstico Sólides→Ponto→GEDEON

### STEP B1 — Tabelas de ponto encontradas

```
gp_clock_punches     — 1830 registros (última batida: 2026-03-30)
solides_employees    — 44 registros
solides_sync_log     — 0 registros (nenhuma sync completa registrada)
solides_sync_state   — tabela existe, sem dados preenchidos
solides_entity_mapping — 44 registros
```

### STEP B2 — punch_controller.py (391 linhas)

Endpoints relevantes identificados:

| Endpoint | Rota |
|----------|------|
| Registrar batida | `POST /people-management/ponto/batida` |
| Espelho mensal | `GET /people-management/ponto/espelho/{employee_id}` |
| Sync Sólides (absências) | `POST /people-management/ponto/sincronizar-solides` |
| Sync escalas | `POST /people-management/ponto/sync-escalas` |
| Dashboard ponto | `GET /people-management/ponto/dashboard` |

### STEP B3 — PDF de ponto: pipeline NÃO implementado

**`kit_builder_service.py` → `collect_time_sheets()`:**
```python
# Placeholder honesto: NULL até pipeline DP gerar o arquivo real (D3.1.1).
file_path = None
doc = KitDocument(
    document_type=DocumentType.FOLHA_PONTO,
    file_path=file_path,  # sempre NULL
    ...
)
```

**`document_collector_service.py`:** registra `documents/dp/folhas_ponto/{ref_str}/{employee_id}.pdf`
como caminho esperado — arquivo físico nunca gerado.

**Conclusão:** `KitDocument.FOLHA_PONTO` existe no banco mas `file_path=NULL` para todos os funcionários.

### STEP B4 — Cenário e testes de endpoint

**Cenário: B — Batidas existem mas PDF não é gerado (D3.1.1 pendente)**

| Teste | Resultado |
|-------|-----------|
| `GET /people-management/ponto/dashboard` | HTTP 200 — `45 colaboradores`, `6 inconsistências`, `ultima_sync_solides: 2026-01-18` |
| `POST /people-management/ponto/sincronizar-solides` (04/2026) | HTTP 201 — Tangerino `/absence/find-all` → **HTTP 404** (API path desatualizada ou token sem escopo) |
| `GET /api/v1/integrations/solides/status` | HTTP 200 — `connected=true`, `webhook_enabled=false`, `last_full_sync_at=null` |
| `gp_clock_punches` count | 1830 batidas · `synced_at=NULL` em todos |

### Gap encontrado: Tangerino API 404

`dashboard_service.sync_solides_ponto()` chama `https://employer.tangerino.com.br/absence/find-all` → 404.
O endpoint da API Tangerino pode ter mudado de rota ou o token `SOLIDES_API_TOKEN` está sem escopo para absências.

---

## §100 CONTRACTS_GEDEON

Adicionado em `906fbefb`:
- Fix modal + cenário B documentados
- Próximo passo ponto: `POST /ponto/folha-pdf/{employee_id}` — gerador de PDF a partir de `gp_clock_punches`

---

## SELF-CHECK (8 itens)

| Item | Status |
|------|--------|
| STEP A2 — grep `DialogContent\|bg-` diagnóstico | ✅ Cenário A confirmado (linha 86) |
| STEP A3 — fix `bg-white dark:bg-gray-900` aplicado | ✅ commit `6f69b10c` |
| STEP A4 — build 286 páginas sem erro | ✅ |
| STEP A4 — hot-copy standalone + static + restart | ✅ HTTP 200, BUILD_ID confirmado |
| STEP B1 — tabelas ponto + solides consultadas | ✅ |
| STEP B2 — punch_controller.py lido (391 linhas) | ✅ |
| STEP B3 — PDF pipeline: `file_path=None` (D3.1.1) | ✅ Cenário B |
| STEP C — §100 CONTRACTS_GEDEON + commits + push | ✅ branch up-to-date com origin |

---

**T1-MODAL-PONTO CPRO12 OK — modal opaco em produção + pipeline ponto diagnosticado (D3.1.1 pendente).**
