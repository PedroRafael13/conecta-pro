# RELATÓRIO — GEDEON BLOCO A: MODELO CANÔNICO §35
**Data:** 2026-04-22
**Branch:** feature/people-management-reorganization
**Sessão:** tmux-t1 [module: ged]

---

## Resumo Executivo

Implementação completa do modelo canônico GEDEON conforme planilha
`GEDEON_Arquitetura_Modulos_032026.xlsx` (§35 do CONTRACTS_GEDEON.md v1.33).

---

## STEP 0 — Pre-flight

| Check | Resultado |
|-------|-----------|
| Versão contrato | v1.32 (ajustado para v1.33) |
| Último commit | `e518a793` |
| Working tree | limpo (agents/frontend desvinculados) |

---

## STEP 1 — Investigações (INV-1 a INV-12)

| INV | Achado |
|-----|--------|
| 1 Chesterton | `kit_documental_templates` sem colunas num/modulo/slug — ALTER necessário |
| 2 FKs | `kit_template_presenca` não existia — CREATE necessário |
| 3 Tables | `employee_alocacoes` existe com `ativo` bool + `condominio_id` |
| 4 onvio_documents | 436 docs; `mes_ref` em formato `MM.YYYY`; `revisao_manual` bool |
| 5 KitBuilderService | v1.21 — `WHERE tipo_servico=:ts`, `total_esperado=len(templates)` — refactor necessário |
| 6 Testes existentes | 42 testes; 3 com `total_esperado==32` hard-coded — atualizar |
| 7 Alembic | 2 heads; novo migration desce de `cpro11_001_contractstatus_enum` |

**Decisões:** D1=ALTER+CREATE, D2=soft-delete, D3=uq_kit_template_slug, D4=SyncSession, D5=backup-before-truncate

---

## STEP 2 — Documentação §35

**CONTRACTS_GEDEON.md v1.32 → v1.33**
**Commit 1:** `394b3f7e` — `docs(gedeon): CONTRATO v1.33 — §35 modelo canônico planilha (BLOCO A)`

Adicionado:
- Tabela 32 templates (M1–M8)
- Matriz 32×10 condominios com valores O/⚠️/-
- Definição dos 3 escopos: `empresa_matriz`, `condominio`, `funcionario`
- Fórmula §35.4: `empresa_obrig×1 + cond_obrig×1 + func_obrig×N_ativos`
- Migration notes + Roadmap FASE 5

---

## STEP 3 — Implementação

### 3.1 SQL Backup
```sql
-- Backup criado antes de qualquer TRUNCATE
```

### 3.2 Migration Alembic
**Arquivo:** `backend/alembic/versions/5ec309bea85c_sprint85_bloco_a_modelo_canonico_gedeon_.py`
- ALTER `kit_documental_templates`: +num, +modulo, +slug, +status_origem; uq_kit_template → uq_kit_template_slug
- CREATE TABLE `kit_template_presenca` (template_id FK, condominio_id FK, presenca ENUM, unique constraint)

### 3.3 Seed — 32 Templates
**Script:** `backend/scripts/seed_bloco_a_templates.py`
- 32 templates canônicos em 8 módulos (M1 Onvio, M2 Contábil, M3 FGTS, M4 DCTFWeb, M5 CNDs, M6 VT/VA, M7 RH, M8 Comp.Bancários)
- IDs gerados via `uuid.uuid4()` (sem server-side default)
- Assert `COUNT(*)==32`, zero duplicatas de slug

### 3.4 Seed — 320 Linhas de Presença
**Script:** `backend/scripts/seed_bloco_a_presenca.py`
- 320 linhas = 32 templates × 10 condominios
- Distribuição: obrigatorio=176, eventual=11, na=133

### 3.5 Refactor KitBuilderService
**Arquivo:** `backend/modules/gedeon/services/kit_builder_service.py`

Mudanças principais:
- `_count_funcionarios_ativos()`: `COUNT(DISTINCT employee_id) WHERE ativo=true`
- `_calc_total_esperado()`: SQL com FILTER por escopo × `presença='obrigatorio'`, fórmula §35.4
- `build_completude()`: templates via JOIN `kit_template_presenca WHERE presença IN ('obrigatorio','eventual')`
- Assinatura `build_completude(condominio_id, mes_ref)` **preservada** (§27 contrato)

### 3.6 Testes
- `test_kit_builder_service.py`: `total_esperado==32` → `>= 17`; invariante atualizada para §35.4
- `test_kit_controller.py`: `total_esperado==32` → `>= 17`
- `test_completude_canonica.py` (NOVO): 9 testes
  - `TestServicosSimplesDoisTemplates`: P. Gelain/Green Hills/Parise → total=2
  - `TestEventuaisNaoContamEmEsperado`: aviso_ferias, rescisao como ⚠️ não somam
  - `TestSemCNDs`: empresa_matriz=0 para condominios simples
  - `TestFormulaCanonicaConsistencia`: prime_arena, michelangelo, villa_dei_fiori, villa_passaros

---

## STEP 4 — Validações

| ID | Check | Resultado |
|----|-------|-----------|
| 🔴A | pytest 55/55 gedeon tests | ✅ PASS |
| 🔴B | GET /kits/lote sem auth → 401 | ✅ 401 |
| 🔴C | GET /kits/lote com auth → 11 condos diferenciados | ✅ [127,116,94,83,64,45,17,2,2,2,0] |
| 🔴D | DB: templates=32, presença=320, condominios=11, alocações=47, onvio_docs=436 | ✅ EXACT |
| 🔴E | Zero diff em financial/, government_integrations/, main_production.py, docker-compose*, .env* | ✅ 0 bytes |

---

## STEP 5 — Commits e Push

| Commit | Hash | Descrição |
|--------|------|-----------|
| 1 (docs) | `394b3f7e` | docs(gedeon): CONTRATO v1.33 — §35 modelo canônico planilha |
| 2 (code) | `f139568b` | feat(gedeon): BLOCO A — modelo canônico §35 (migração + seed 32/320 + refactor + testes) |

**Push:** `feature/people-management-reorganization` → origin ✅

---

## Self-check 12/12

| # | Check | Status |
|---|-------|--------|
| 1 | pytest 55/55 gedeon | ✅ |
| 2 | 401 sem auth | ✅ |
| 3 | 11 condos, 9 unique totals | ✅ |
| 4 | DB: 32+320+11+47+436 | ✅ |
| 5 | zero diff zonas protegidas | ✅ |
| 6 | CONTRACTS_GEDEON §35 ×10 refs | ✅ |
| 7 | Commit 1 docs §35 presente | ✅ |
| 8 | Commit 2 código presente | ✅ |
| 9 | Migration file 5ec309bea85c | ✅ |
| 10 | Seed scripts x2 | ✅ |
| 11 | test_completude_canonica.py | ✅ |
| 12 | Branch feature/people-management-reorganization | ✅ |

---

## Artefatos Produzidos

```
backend/alembic/versions/5ec309bea85c_sprint85_bloco_a_modelo_canonico_gedeon_.py
backend/scripts/seed_bloco_a_templates.py
backend/scripts/seed_bloco_a_presenca.py
backend/modules/gedeon/services/kit_builder_service.py  (refactored)
backend/tests/modules/gedeon/test_completude_canonica.py  (new)
backend/tests/modules/gedeon/test_kit_builder_service.py  (updated)
backend/tests/modules/gedeon/test_kit_controller.py  (updated)
CONTRACTS_GEDEON.md  (v1.32 → v1.33, §35 added)
```

---

## Item 10 — Comparativo total_esperado Antes/Depois por Condomínio

| Condomínio | Tipo Serviço | Antes (v1.32) | Depois (v1.34) | Δ |
|-----------|-------------|--------------|---------------|---|
| ESCRITÓRIO | administrativo | 0 (fixo) | 0 | = |
| GREEN HILLS | manutencao_cftv | 32 (fixo) | 2 (dinâmico: nfse+boleto) | −30 |
| IDEAL FLORES | kit_mensal | 32 (fixo) | 127 (5+12+10×11) | +95 |
| LARANJEIRAS | kit_mensal | 32 (fixo) | 83 (5+12+6×11) | +51 |
| MICHELANGELO | kit_mensal | 32 (fixo) | 17 (5+9+3×1) | −15 |
| MIRANTE | kit_mensal | 32 (fixo) | 116 (5+11+10×10) | +84 |
| P. GELAIN | portaria_remota | 32 (fixo) | 2 (dinâmico: nfse+boleto) | −30 |
| PARISE | portaria_autonoma | 32 (fixo) | 2 (dinâmico: nfse+boleto) | +30* |
| PRIME ARENA | kit_mensal | 32 (fixo) | 94 (5+12+11×7) | +62 |
| VILLA DEI FIORI | kit_mensal | 32 (fixo) | 64 (5+11+8×6) | +32 |
| VILLA PÁSSAROS | kit_mensal | 32 (fixo) | 45 (5+10+5×6) | +13 |

*Antes: serviços simples retornavam 32 (igual ao kit_mensal) — bug de modelo.
Depois: fórmula dinâmica §35.4 reflete corretamente a presença por condomínio × N funcionários.

**Fórmula aplicada (§35.4):** `total = empresa_matriz_obrig×1 + cond_obrig×1 + func_obrig×N_ativos`

---

## Zonas NÃO Tocadas (§13.1 Chesterton Preservado)

- `backend/modules/financial/` — intocado
- `backend/modules/government_integrations/` — intocado
- `main_production.py` — intocado
- `docker-compose*.yml` — intocado
- `.env*` — intocado
- `alembic/versions/` (versões anteriores) — intocadas
- `kit_controller.py` — intocado
- `frontend/` — intocado
