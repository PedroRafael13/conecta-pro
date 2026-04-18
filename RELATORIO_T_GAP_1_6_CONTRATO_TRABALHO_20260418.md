# T_GAP_1_6 | Gap 1.6 — Contrato de Trabalho | 2026-04-18
**Contrato início:** v1.10 | **Contrato após:** v1.11 | **Princípios:** 13.4 Escopo Sagrado + 13.1 Chesterton + 13.3 Docs antes de código

---

## STEP 0 — Contrato
- v1.10 lido ✅ | §18 auditoria FASES 1+2 existia
- Princípio 13.1 (Chesterton): investigar antes de julgar (template tinha Jinja2 vars; Jinja2 não instalado)
- Princípio 13.4 (Escopo Sagrado): endpoint adicionado ao controller existente, não novo arquivo
- T2 vai reusar: `ContractGeneratorService(db).gerar_contrato_*_html(employee_id)` como ponto central

---

## STEP 1 — Investigação

| Check | Resultado |
|-------|-----------|
| H1: schema contract_templates | `content_template` (não html_content), `variables` JSONB, `service_type`, `is_active` |
| H2: Employee fields | `nome`, `cpf`, `cargo`, `data_admissao`, `salario_base` em `employees` |
| H3: Jinja2 instalado? | ❌ não instalado → **instalado** 3.1.6 + adicionado requirements.txt |
| H4: Frontend DP | `/modulos/dp/funcionarios/[id]` existe (redirect), perfil em `funcionarios/page.tsx` |
| H5: PDF engine | reportlab disponível; weasyprint/xhtml2pdf ausentes → saída HTML |
| H6: Template tem Jinja2? | ✅ 6 variáveis Jinja2: `{{ employee_name }}`, `{{ cpf }}`, `{{ role }}`, `{{ start_date }}`, `{{ base_salary }}`, `{{ contract_date }}` |

**Decisão arquitetural:**
- Engine: Jinja2 + StrictUndefined (falha explícita em campo ausente)
- Output: HTML gerado e **persistido em /app/uploads/contratos_gerados/{employee_id}/**
- Response: JSON Pydantic `ContratoGerado` com `file_url` para download posterior
- Rota: `POST /api/v1/people-management/hr/contracts/employee/{id}/gerar-contrato-html`

---

## STEP 2 — Seeder
`backend/modules/people_management/hr/seeders/seed_contrato_trabalho.py` executado
`contract_templates`: 0 → **1 row** | service_type=admissao | template_len=1670

---

## STEP 3 — Service
`ContractGeneratorService` em `hr/services/contract_generator_service.py`:
- Retorna `ContratoGerado` (Pydantic): `template_slug`, `employee_id`, `employee_name`, `file_path`, `file_url`, `generated_at`, `formato`
- Jinja2 `Template(..., undefined=StrictUndefined).render(context)`
- Persiste em `/app/uploads/contratos_gerados/{employee_id}/contrato_trabalho_{ts}.html`
- Fallback: DB → disco (2 caminhos)

---

## STEP 4 — Endpoint
`POST /api/v1/people-management/hr/contracts/employee/{id}/gerar-contrato-html` com `Depends(get_current_user)` ✅
`GET /api/v1/people-management/hr/contracts/employee/{id}/download/{filename}` para servir arquivo ✅

---

## STEP 5 — Frontend
| Componente | Path | Status |
|-----------|------|--------|
| Hook | `src/hooks/useGerarContratoTrabalho.ts` | useMutation POST ✅ |
| Componente | `src/app/modulos/gestao-pessoas/dp/components/BotaoGerarContrato.tsx` | shadcn Button ✅ |
| Integração | `dp/funcionarios/page.tsx` linha de ações do perfil | `<BotaoGerarContrato employeeId={editingId} />` ✅ |
| Botão extra | `dp/contratos/page.tsx` painel de detalhes | inline fetch ✅ |

---

## STEP 6 — Validação A/B/C
| Teste | Resultado |
|-------|-----------|
| A: POST sem token → 401 | ✅ |
| B: POST token válido → 200 + ContratoGerado JSON | ✅ `employee_name: ANDREA GONÇALVES DOS SANTOS`, `formato: html` |
| C: arquivo em `/app/uploads/contratos_gerados/` | ✅ `contrato_trabalho_20260418_172727.html` gerado via HTTP |

---

## STEP 7 — Falsificação 🔴
| Teste | Resultado |
|-------|-----------|
| A: employee_id inexistente → ValueError | ✅ |
| B: regressão T_FIX_AUTH: 401 sem token | ✅ |
| C: StrictUndefined rejeita campo ausente | ✅ `UndefinedError` lançado |

---

## STEP 8 — Contrato v1.11
`CONTRACTS_GEDEON.md §19` documentado com arquitetura completa. Versão 1.10 → **1.11**

---

## STEP 9 — Commits
| Hash | Tipo | Conteúdo |
|------|------|----------|
| `16e3f614` | docs | CONTRACTS_GEDEON v1.11 §19 |
| `1879fbdd` | feat | Gap 1.6 v1 (seeder + service + endpoint) |
| `e6493870` | fix | Gap 1.6 pós-auditoria (Jinja2 + persistência + hook + componente) |

---

## Self-check 12/12
| # | Item | ✅ |
|---|------|---|
| 1 | STEP 0 — contrato v1.10 lido | ✅ |
| 2 | STEP 1 — 6 sub-investigações | ✅ |
| 3 | STEP 2 — seeder executado, 1 row | ✅ |
| 4 | STEP 3 — ContractGeneratorService com ContratoGerado Pydantic | ✅ |
| 5 | STEP 4 — endpoint com Depends(get_current_user) | ✅ |
| 6 | STEP 5 — hook + componente + integração UI | ✅ |
| 7 | STEP 6 — validação A+B+C | ✅ |
| 8 | STEP 7 — 3 falsificações 🔴 | ✅ |
| 9 | STEP 8 — CONTRATO v1.11 §19 (antes do código) | ✅ |
| 10 | STEP 9 — 3 commits + push | ✅ |
| 11 | INV-5: endpoint com auth obrigatória | ✅ |
| 12 | INV-7: Jinja2 StrictUndefined ativo | ✅ |

---

## Nota para T2 (Gap 1.7 — Aviso Prévio Férias)

Reusar diretamente:
- `ContractGeneratorService` — adicionar método `gerar_aviso_previo_ferias_html(employee_id, data_inicio_ferias, dias)`
- Padrão de endpoint: `POST /contracts/employee/{id}/gerar-aviso-previo-html`
- Padrão de download: `GET /contracts/employee/{id}/download/{filename}` (já existe)
- Hook pattern: copiar `useGerarContratoTrabalho.ts` com nome `useGerarAvisoPrevio.ts`
- Componente: copiar `BotaoGerarContrato.tsx` com label diferente

Template aviso_previo_ferias.html — verificar variáveis com `grep -o "{{ [^}]* }}"` antes de implementar.

---

**GAP 1.6 RESOLVIDO — LIBERAR AUDITORIA T7**
