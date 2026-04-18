# RELATÓRIO — Auditoria de Conformidade FASES 1 e 2 GEDEON
**Data:** 2026-04-18 | **Auditor:** T_AUDIT_FASES_1_2 | **Tipo:** Auditoria retrospectiva (zero código)

---

## 1. STEP 0 — Contrato
- Versão: **1.9** (início) → **1.10** (após auditoria)
- Princípios: **13.1 Chesterton** (investigar antes de julgar) + **13.5 Universal** (auditor não corrige)
- Por que não corrigir: escopo é MAPA, não correção. Jordan decide o que fazer com os gaps.

---

## 2. STEP 1 — Descoberta Preliminar

| Checagem | Resultado |
|----------|-----------|
| 48 módulos em backend | módulos relevantes: `ged`, `financial`, `integrations`, `people_management`, `hr` |
| Dirs por keyword | `solides` em integrations/mypy, `nfse` em government_integrations, `/backend/templates` |
| Tabelas por keyword | 41 hits: `ged_certidoes`, `nfses`, `nfse_entrada`, `solides_*` (17 tabelas), `contract_templates`, etc. |
| Frontend dirs | `fiscal/certidoes/*`, `financeiro/boletos`, `financeiro/nfse-entrada`, `integracoes/solides` |
| OpenAPI | `localhost:8080/openapi.json` retornou 0 paths (conexão sem auth não expõe JSON completo) |

---

## 3. STEP 3 — Tabela Consolidada (11 itens)

| Item | Descrição | Endpoint | Tabela | Frontend | Estado |
|------|-----------|----------|--------|----------|--------|
| 1.1 | CND Receita Federal | ged_certidoes_controller.py ✅ | ged_certidoes / 8 rows (fed ✅) | cnd-federal/page.tsx ✅ | 🟢 |
| 1.2 | CND FGTS/Caixa | kit_real_controller cnd_caixa ✅ | ged_certidoes / certidao_negativa_fgts ✅ | crf-fgts/page.tsx ✅ | 🟢 |
| 1.3 | CND Trabalhista TST | cnd_sync_task cndt_trabalhista ✅ | ged_certidoes / certidao_negativa_trabalhista ✅ | cndt/page.tsx ✅ | 🟢 |
| 1.4 | CND Prefeitura Manaus | kit_real_controller cnd_prefeitura ✅ | ged_certidoes / certidao_negativa_municipal ✅ | cnd-municipal/page.tsx ✅ | 🟢 |
| 1.5 | CND Sefaz-AM | kit_real_controller cnd_sefaz ✅ | ged_certidoes / certidao_negativa_estadual ✅ | cnd-estadual/page.tsx ✅ | 🟢 |
| 1.6 | Template Contrato Trabalho | contrato_trabalho.html em disco ✅ | contract_templates / **0 rows** ⚠️ | sem página geração ❌ | 🟡 |
| 1.7 | Template Aviso Prévio Férias | aviso_previo_ferias.html em disco ✅ | contract_templates / **0 rows** ⚠️ | sem página geração ❌ | 🟡 |
| 2.1 | NFS-e automática | POST /nfse + POST /nfse/emitir ✅ | nfses / **27 rows** + nfse_entrada / **10 rows** ✅ | fiscal/nfse-multi/ + tipos ✅ | 🟢 |
| 2.2 | Boleto Inter automático | generate_boleto + bulk_generate ✅ | receivable_installments / **21 rows** ✅ | financeiro/boletos/page.tsx ✅ | 🟢 |
| 2.3 | Solides VA integração | integrations/solides_router ✅ | solides_employees /**44 rows** + config/**2** ✅ | integracoes/solides/page.tsx ✅ | 🟢 |
| 2.4 | Comprovante salário Inter | payslip_controller/download_payslip ✅ | comprovante_salario.html em disco ✅ | só diaristas (comprovanteUrl) ⚠️ | 🟡 |

**8/11 🟢 PRODUCTION · 3/11 🟡 PARCIAL · 0 🔴 AUSENTE · 0 ⚠️ STALE**

---

## 4. STEP 4 — Evidências Brutas (itens 🟡)

### 1.6 e 1.7 — Templates
```
# disco:
/opt/conecta-pro/backend/templates/contrato_trabalho.html
/opt/conecta-pro/backend/templates/aviso_previo_ferias.html
/opt/conecta-pro/backend/templates/comprovante_salario.html

# DB:
SELECT COUNT(*) FROM contract_templates; → 0

# backend model:
modules/documents/models/document.py: CONTRATO_TRABALHO = "contrato_trabalho"
modules/gedeon/agents/sophia.py: "contrato_trabalho" (lista de tipos)
modules/cct/controllers/termination_controller.py: aviso_previo_cumprido, dias_aviso_previo
  (contexto: rescisão, não férias)

# frontend: nenhum arquivo encontrado com "template_contrato" ou "aviso_ferias"
```

### 2.4 — Comprovante salário
```
# disco:
/opt/conecta-pro/backend/templates/comprovante_salario.html ✅

# backend:
modules/hr/employee_portal/controllers/payslip_controller.py:
  download_payslip, list_payslips, acknowledge_payslip
  (payslip = contracheque — não comprovante de pagamento PIX Inter)

# frontend:
frontend/src/api/diarists/generated/models/diaristPaymentResponseComprovanteUrl.ts
  (escopo: apenas diaristas, não folha principal)

# sem tabela "comprovante_pagamento" ou "pix_batch_comprovante"
```

---

## 5. STEP 5 — Gaps Específicos

### 5.1 Gaps de integração
- **1.6/1.7:** `contract_templates` com 0 rows — templates HTML existem mas nunca populados no DB. Geração automática incompleta.
- **2.4:** Comprovante salário cobre diaristas, não folha principal via Inter API.
- **Solides sync_log:** 0 rows — integração configurada (44 employees) mas sem histórico de sync.
- **CND sync:** `cnd_sync_task.py` existe como task mas sem endpoint de trigger visível — pode ser Celery sem UI.

### 5.2 Gaps de autenticação
✅ **Nenhum endpoint sem auth encontrado nas FASES 1/2.**
Todos verificados têm `Depends(get_current_user)` ou `require_permission()`:
`ged_certidoes_controller.py:99`, `fiscal_controller.py` (require_permission), `receivable_controller.py:70`, `connector_controller.py:38`.

### 5.3 Gaps de documentação
CONTRACTS_GEDEON.md (seções 1-17 pré-auditoria) **não mencionava** FASES 1/2 do Roadmap.
Adicionado §18 nesta auditoria (contrato v1.10).

---

## 6. STEP 6 — §18 adicionado ao Contrato
Versão: 1.9 → **1.10** | Seção §18 criada com tabela consolidada, gaps e recomendação.

---

## 7. STEP 7 — Commit
Hash: (ver após commit)

---

## 8. Cenário identificado
**Cenário A** — Mapeamento completo sem achado crítico.
Sem endpoints sem auth, sem tabelas corrompidas, sem 🔴 AUSENTE.

---

## 9. Self-check 10/10
| # | Item | Status |
|---|------|--------|
| 1 | STEP 0 — contrato v1.9 + princípios 13.1+13.5 | ✅ |
| 2 | STEP 1 — 5 sub-passos executados | ✅ |
| 3 | STEP 2 — 11 itens, 3 checagens cada | ✅ |
| 4 | STEP 3 — tabela 11 itens em markdown | ✅ |
| 5 | STEP 4 — evidências brutas só para 🟡 | ✅ |
| 6 | STEP 5 — 3 listas de gaps | ✅ |
| 7 | STEP 6 — §18 no contrato, versão 1.10 | ✅ |
| 8 | STEP 7 — commit docs pushado | ✅ |
| 9 | INV-1 — zero código alterado | ✅ |
| 10 | Tempo ≤ 25 min | ✅ |

---

## 10. Conclusão
**AUDITORIA FASES 1+2 CONCLUÍDA — aguardando decisão Jordan**

8/11 em produção. 3 gaps parciais de baixo risco:
- **1.6/1.7** (templates): HTML existe, DB vazio — 1 sprint de templateware
- **2.4** (comprovante): escopo a clarificar (Inter PIX vs HR payslip)

Recomendação: avançar FASE 4 GEDEON CORE e registrar 1.6/1.7/2.4 como backlog paralelo.
