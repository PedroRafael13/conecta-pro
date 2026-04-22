# RELATÓRIO — GEDEON BLOCO B: 1º KIT REAL LARANJEIRAS 04/2026
**Data:** 2026-04-22
**Branch:** feature/people-management-reorganization
**Sessão:** tmux-t1 [module: ged]

---

## 1. STEP 0 — Pré-voo (BLOCO A confirmado)

| Check | Resultado |
|-------|-----------|
| Versão contrato | v1.34 → v1.35 após §36 |
| templates | 32 ✅ |
| presencas | 320 ✅ |
| kits_antes | 0 ✅ |
| docs_antes | 0 ✅ |

---

## 2. STEP 1 — 7 Investigações

| INV | Resultado |
|-----|-----------|
| H1 LARANJEIRAS condominio_id | `7c2323fd-e226-4121-806d-d9b2598feeed`, tipo_servico=kit_mensal |
| H2 N funcionários ativos 04/2026 | **6** ✅ (ADAILSON, ANDREA, ANILSON, BIANCA, EIDY, ELEN) |
| H3 /uploads/onvio/ estrutura | Diretório LARANJEIRAS inexistente; 0 PDFs para 04/2026 |
| H4 PDFs LARANJEIRAS 04/2026 | 0 arquivos (competência ainda aberta em 22/04) |
| H5 CNDs válidas em ged_certidoes | 5/5 válidas até 04/2026 mas file_path=NULL (aguardam upload) |
| H6 onvio_documents LARANJEIRAS 04/2026 | 0 rows — 04.2026 não sincronizado; 03.2026 tem 2 (folha+recibo) |
| H7 ged_document_kits schema | client_id (FK→ged_clients), reference_month (date). Sem motivo_faltante → usar `notes`. Sem template_id → usar document_type |
| H8 Endpoint POST | `POST /api/v1/ged/kits` existe em auto_assemble_controller.py. Seed via SQL/Python direto |

**Adaptações schema identificadas:**
- `ged_document_kits.client_id` → `ged_clients.id` (não condominios.id!)
- `ged_clients` LARANJEIRAS id = `e55f6f4c-a641-4b08-9584-eef61dcb5575`
- `reference_month` = date `2026-04-01` (não string MM.YYYY)
- `ged_document_kits` tem UNIQUE CONSTRAINT em (client_id, reference_month) → idempotência via ON CONFLICT

**Decisão Cenário C:** 0/83 PDFs localizados (<30%) → kit parcial aceito. Todos os 83 docs obrigatórios inseridos como placeholder. Eventuais NÃO inseridos.

**Pausas trigadas e resolvidas:**
- `<30% PDFs localizados`: apresentei 3 opções; Jordan autorizou execução completa ("execute agora")

---

## 3. STEP 2 — §36 no Contrato

- CONTRACTS_GEDEON.md v1.34 → v1.35
- §36.1–§36.7 adicionados (escopo, inventário, matching, registros, completude, faltantes, fora de escopo)
- **Commit 1:** `6efdfaa7` — `docs(gedeon): CONTRATO v1.35 — §36 BLOCO B primeiro kit real LARANJEIRAS`

---

## 4. STEP 3 — Seed executado

### 3.1 Backup SQL
```
/tmp/backup_before_bloco_b_20260422_150328.sql
```

### 3.2 Script criado
`backend/scripts/seed_bloco_b_laranjeiras_042026.py`

**Output do seed:**
```
GEDEON BLOCO B — Seed LARANJEIRAS 04.2026
Funcionários ativos: 6
Templates aplicáveis: 30
Kit criado: 0107be85-0109-464e-a80b-3665c666dd01
total_esperado: 83
docs inseridos: 83
com PDF: 0
placeholder (NULL): 83
completude: 0.0%
```

**Bug corrigido:** eventuais (rescisao_contrato, comp_rescisao) foram inseridos sem PDF na 1ª tentativa (12 rows extras) → limpeza manual + correção do script com guard `if eh_eventual and fp is None: continue`.

### 3.4 Testes criados
`backend/tests/modules/gedeon/test_seed_bloco_b.py` — 17 testes em 4 classes:
- `TestBlocoB` (9): kit existe, N=6, total_docs=83, docs_count=83, placeholder, eventuais ausentes, func×6, empresa×1, notes correto
- `TestBlocoBIdempotencia` (2): 1 kit, total kits=1
- `TestBlocoBZonasProibidas` (4): templates=32, presencas=320, onvio≥436, certidoes≥7
- `TestBlocoBKitBuilderService` (2): total_esperado=83, pct=0%

### 3.5 Smoke test endpoint
- `/api/v1/gedeon/kits/lote?mes_ref=04.2026` retorna LARANJEIRAS com `total_esperado=83, total_confirmado=0` ✅

---

## 5. STEP 4 — Validações 🔴

| ID | Check | Resultado |
|----|-------|-----------|
| 🔴A | pytest 72/72 gedeon (55 BLOCO A + 17 BLOCO B) | ✅ PASS |
| 🔴B | GET /kits/lote sem auth → 401 | ✅ 401 |
| 🔴C | kits=1, docs=83, com_pdf=0, faltantes=83 | ✅ EXACT |
| 🔴D | Endpoint 04.2026 → LARANJEIRAS total_esperado=83, presente=0 | ✅ |
| 🔴E | E2E CIC visual | ⏳ Aguarda Jordan |
| 🔴F | Zero diff em zonas proibidas | ✅ 0 bytes |

---

## 6. STEP 5 — Commits

| Commit | Hash | Descrição |
|--------|------|-----------|
| 1 (docs) | `6efdfaa7` | docs(gedeon): CONTRATO v1.35 — §36 BLOCO B |
| 2 (code) | `405f8111` | feat(gedeon): BLOCO B — seed 1º kit real LARANJEIRAS |

**Push:** `feature/people-management-reorganization` → origin ✅

---

## 7. Self-check 12/12

| # | Check | Status |
|---|-------|--------|
| 1 | STEP 0 — BLOCO A confirmado (32/320/0/0) | ✅ |
| 2 | STEP 1 — 7 investigações + decisões | ✅ |
| 3 | STEP 1 — N funcionários = 6 | ✅ |
| 4 | STEP 2 — §36 em v1.35 + commit 1 `6efdfaa7` | ✅ |
| 5 | STEP 3 — Backup SQL criado antes de INSERT | ✅ |
| 6 | STEP 3 — Script seed executado: 1 kit + 83 docs | ✅ |
| 7 | STEP 3 — Idempotência testada (rodar 2× não duplica) | ✅ |
| 8 | STEP 3 — Novos testes pytest criados e PASS (17/17) | ✅ |
| 9 | STEP 4 — 5 validações automatizadas PASS; E2E CIC pendente Jordan | ✅ |
| 10 | STEP 4 — total_esperado=83 confirmado pós-seed | ✅ |
| 11 | STEP 5 — Commit 2 `405f8111` + push | ✅ |
| 12 | Relatório final gerado | ✅ |

---

## 8. Cenário identificado

**CENÁRIO C** (parcial): `<30% PDFs localizados`. Kit LARANJEIRAS 04/2026 criado com 83 placeholders.
Sem bloqueios técnicos. Jordan autorizou execução completa ("execute agora").

---

## 9. Tabela 83 docs × fonte

| Escopo | Template (slug) | N instâncias | Fonte | file_path |
|--------|-----------------|-------------|-------|-----------|
| empresa_matriz | cnd_rfb | 1 | ausente | NULL |
| empresa_matriz | cnd_caixa | 1 | ausente | NULL |
| empresa_matriz | cnd_prefeitura | 1 | ausente | NULL |
| empresa_matriz | cnd_sefaz | 1 | ausente | NULL |
| empresa_matriz | cnd_trabalhista | 1 | ausente | NULL |
| condominio | nfse | 1 | ausente | NULL |
| condominio | boleto | 1 | ausente | NULL |
| condominio | folha_pagamento | 1 | ausente | NULL |
| condominio | gfd_fgts_mensal | 1 | ausente | NULL |
| condominio | relatorio_gfd_fgts | 1 | ausente | NULL |
| condominio | comp_pag_fgts | 1 | ausente | NULL |
| condominio | dctfweb_declaracao | 1 | ausente | NULL |
| condominio | dctfweb_recibo | 1 | ausente | NULL |
| condominio | dctfweb_extrato | 1 | ausente | NULL |
| condominio | recibo_vt_va | 1 | ausente | NULL |
| condominio | relatorio_pedido_va | 1 | ausente | NULL |
| condominio | aso | 1 | ausente | NULL |
| funcionario | contracheque | 6 | ausente | NULL |
| funcionario | folhas_ponto | 6 | ausente | NULL |
| funcionario | gfd_fgts_rescisao | 6 | ausente | NULL |
| funcionario | relatorio_gfd_rescisao | 6 | ausente | NULL |
| funcionario | comp_fgts_rescisao | 6 | ausente | NULL |
| funcionario | comp_vt_individual | 6 | ausente | NULL |
| funcionario | comp_va_solides | 6 | ausente | NULL |
| funcionario | comp_vt_va_combinado | 6 | ausente | NULL |
| funcionario | contrato_trabalho | 6 | ausente | NULL |
| funcionario | ficha_empregado | 6 | ausente | NULL |
| funcionario | comp_salario_individual | 6 | ausente | NULL |
| **TOTAL** | **28 templates obrigatorios** | **83** | **0 com PDF** | **83 NULL** |

*Eventuais (rescisao_contrato + comp_rescisao): NÃO inseridos (sem PDF encontrado)*

---

## 10. Status Final

**BLOCO B PRONTO. Aguardando Jordan validar CIC visual (🔴E):**
- Dashboard `/ged/kits?mes_ref=04.2026` → LARANJEIRAS com `0/83`
- Modal KitDetalheModal abre e lista 83 docs faltantes

**Após CIC: autorização para BLOCO C** (extensão aos outros 9 condomínios).

- Kit criado: `0107be85-0109-464e-a80b-3665c666dd01` ✅
- 83 placeholders prontos para preenchimento via Onvio sync (quando 04/2026 fechar) ✅
- Regressão BLOCO A: 55/55 PASS ✅
- Novos testes BLOCO B: 17/17 PASS ✅
- Total: 72/72 PASS ✅
- Commits: `6efdfaa7` (docs §36) + `405f8111` (código) ✅

---

## Artefatos Produzidos

```
backend/scripts/seed_bloco_b_laranjeiras_042026.py  (novo)
backend/tests/modules/gedeon/test_seed_bloco_b.py   (novo)
CONTRACTS_GEDEON.md  (v1.34 → v1.35, §36 adicionado)
RELATORIO_BLOCO_B_LARANJEIRAS.md  (este arquivo)
```

## Zonas NÃO Tocadas (§13.4 Chesterton Preservado)

- `backend/modules/gedeon/services/kit_builder_service.py` — intocado
- `backend/modules/gedeon/controllers/kit_controller.py` — intocado
- `backend/modules/gedeon/schemas/` — intocado
- `backend/alembic/versions/` — intocado
- `backend/modules/financial/` — intocado
- `backend/modules/government_integrations/` — intocado
- `main_production.py` — intocado
- `docker-compose*.yml` — intocado
- `.env*` — intocado
- `frontend/` — intocado
- `kit_documental_templates` (32 rows) — intacto
- `kit_template_presenca` (320 rows) — intacto
- `onvio_documents` (436 rows) — intacto
- `ged_certidoes` (7+ rows) — intacto
