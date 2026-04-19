# RELATÓRIO FASE 3.5 BLOCO 2 / T3 — Kit Documental Templates
**Data:** 2026-04-19
**Agente:** Engenheiro Backend Sênior — T3
**Terminal:** T3 (paralelo com T2 — escopos distintos)
**Branch:** feature/people-management-reorganization

---

## STEP 0 — Pré-voo

- [x] Versão contrato: **1.14** (antes) → **1.15** (após este commit)
- [x] Princípios: §13.1 Chesterton + §13.3 Documentar antes de código + §13.4 Escopo sagrado
- [x] O que foi feito: Criado seeder `seed_kit_templates_fase_3_5.py` com 38 rows da planilha GEDEON oficial (32 kit_mensal + 2×3 serviços simples + 0 administrativo), documentado §24, 2 commits separados, push.

---

## STEP 1 — Hipóteses Validadas (H1–H3)

### H1 — Tabela kit_documental_templates existe e está VAZIA
```
 count
-------
     0
```
✅ CONFIRMADO

### H2 — UNIQUE constraint uq_kit_template existe
```
"uq_kit_template" UNIQUE CONSTRAINT, btree (tipo_servico, tipo_documento, escopo)
```
✅ CONFIRMADO

### H3 — Tipos de serviço no banco
```
   tipo_servico    | count
-------------------+-------
 administrativo    |     1
 kit_mensal        |     7
 manutencao_cftv   |     1
 portaria_autonoma |     1
 portaria_remota   |     1
```
✅ CONFIRMADO — 5 tipos conforme esperado

---

## STEP 2 — Seeder criado e executado

**Arquivo:** `backend/scripts/seed_kit_templates_fase_3_5.py`

### 38 rows inseridas (listagem completa)

#### kit_mensal (32 docs — M1..M8)
| # | tipo_documento | escopo | obrigatorio | periodicidade |
|---|---|---|---|---|
| 1 | nfse | condominio | true | mensal |
| 2 | boleto | condominio | true | mensal |
| 3 | folha_pagamento | condominio | true | mensal |
| 4 | contracheque | funcionario | true | mensal |
| 5 | folhas_ponto | funcionario | true | mensal |
| 6 | gfd_fgts_mensal | condominio | true | mensal |
| 7 | relatorio_gfd_fgts | condominio | true | mensal |
| 8 | comp_pag_fgts | condominio | true | mensal |
| 9 | gfd_fgts_rescisao | funcionario | false | eventual |
| 10 | relatorio_gfd_rescisao | funcionario | false | eventual |
| 11 | comp_fgts_rescisao | funcionario | false | eventual |
| 12 | dctfweb_declaracao | condominio | true | mensal |
| 13 | dctfweb_recibo | condominio | true | mensal |
| 14 | dctfweb_extrato | condominio | true | mensal |
| 15 | cnd_rfb | empresa_matriz | true | mensal |
| 16 | cnd_caixa | empresa_matriz | true | mensal |
| 17 | cnd_prefeitura | empresa_matriz | true | mensal |
| 18 | cnd_sefaz | empresa_matriz | true | mensal |
| 19 | cnd_trabalhista | empresa_matriz | true | mensal |
| 20 | comp_vt_individual | funcionario | true | mensal |
| 21 | comp_va_solides | funcionario | true | mensal |
| 22 | comp_vt_va_combinado | funcionario | false | mensal |
| 23 | recibo_vt_va | condominio | true | mensal |
| 24 | relatorio_pedido_va | condominio | true | mensal |
| 25 | aso | funcionario | false | eventual |
| 26 | contrato_trabalho | funcionario | false | eventual |
| 27 | ficha_empregado | funcionario | false | eventual |
| 28 | aviso_previo_ferias | funcionario | false | eventual |
| 29 | recibo_ferias | funcionario | false | eventual |
| 30 | rescisao_contrato | funcionario | false | eventual |
| 31 | comp_rescisao | funcionario | false | eventual |
| 32 | comp_salario_individual | funcionario | true | mensal |

#### portaria_remota (2)
| tipo_documento | escopo | obrigatorio | periodicidade |
|---|---|---|---|
| nfse | condominio | true | mensal |
| boleto | condominio | true | mensal |

#### portaria_autonoma (2)
(idem portaria_remota)

#### manutencao_cftv (2)
(idem portaria_remota)

#### administrativo (0)
⏭️ Sem template de kit — escritório não tem kit (INV-6, Jordan aprovou)

---

## STEP 3 — Validações

### 3.1 — Total por tipo_servico
```
   tipo_servico    | count | obrigatorios | mensais | eventuais
-------------------+-------+--------------+---------+-----------
 kit_mensal        |    32 |           21 |      22 |        10
 manutencao_cftv   |     2 |            2 |       2 |         0
 portaria_autonoma |     2 |            2 |       2 |         0
 portaria_remota   |     2 |            2 |       2 |         0
```
✅ Dentro do range esperado pelo prompt

### 3.2 — Distribuição por escopo
```
     escopo     | count
----------------+-------
 condominio     |    17
 funcionario    |    16
 empresa_matriz |     5
```
✅ empresa_matriz=5 (exatamente as 5 CNDs)

### 3.3 — CNDs: escopo matriz em kit_mensal (regra crítica Jordan)
```
tipo_documento  |     escopo     | tipo_servico
-----------------+----------------+--------------
 cnd_caixa       | empresa_matriz | kit_mensal
 cnd_prefeitura  | empresa_matriz | kit_mensal
 cnd_rfb         | empresa_matriz | kit_mensal
 cnd_sefaz       | empresa_matriz | kit_mensal
 cnd_trabalhista | empresa_matriz | kit_mensal
```
✅ 5 rows, todas escopo='empresa_matriz' e tipo_servico='kit_mensal'

---

## STEP 4 — Testes de Falsificação 🔴

| Teste | Resultado |
|---|---|
| 🔴 A — Total = 38 | ✅ `count=38` |
| 🔴 B — UNIQUE constraint rejeita duplicata | ✅ `ERROR: duplicate key value violates unique constraint "uq_kit_template"` |
| 🔴 C — Idempotência (2ª execução do seeder) | ✅ `0 criados, 38 já existentes` |
| 🔴 C — SELECT COUNT(*) separado após 2ª execução | ✅ `count=38` (DB confirmado independentemente) |
| 🔴 D — administrativo sem kit | ✅ `count=0` |
| 🔴 E — Regressão condominios intactos | ✅ `count=11` (sem mudança BLOCO 1) |

---

## STEP 5 — Contrato §24

Adicionado ao `CONTRACTS_GEDEON.md`:
- §24.1: Fonte (planilha oficial)
- §24.2: Estrutura final 38 rows
- §24.3: Regra CNDs (empresa_matriz em kit_mensal)
- §24.4: Obrigatoriedade (21 true / 11 false)
- §24.5: Distribuição por escopo
- §24.6: Próximo passo (BLOCO 3 KitBuilderService)
- §24.7: Seeder (caminho + idempotência)
- Versão incrementada: 1.14 → 1.15

---

## STEP 6 — Commits

| Commit | Hash | Conteúdo |
|---|---|---|
| docs | `9c928c24` | CONTRACTS_GEDEON.md §24 + versão 1.15 |
| feat | `787cfa8e` | seeder + relatório |

---

## SELF-CHECK (11 itens)

- [x] STEP 0 — contrato lido, kit_documental_templates vazio (count=0)
- [x] STEP 1 — H1 (vazia) + H2 (uq_kit_template) + H3 (5 tipos serviço) validados
- [x] STEP 2 — seeder criado com 32 (kit_mensal) + 2×3 (simples) rows
- [x] STEP 3 — 3 validações: tipo_servico + escopo + CNDs ✅
- [x] STEP 4 — 5 testes 🔴 passam (A,B,C,D,E)
- [x] STEP 5 — CONTRATO §24 adicionado antes dos commits
- [x] STEP 6 — 2 commits separados + push
- [x] Total rows = 38 (H4 confirmada)
- [x] Tempo ≤ 1h
- [x] Zero toques em zonas proibidas
- [x] administrativo com 0 templates (INV-6)

**CENÁRIO A — 11/11 → BLOCO 2 T3 OK — AGUARDANDO T2 + T7 PARA AUDITORIA FASE 3.5**
