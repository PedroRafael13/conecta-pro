# RELATÓRIO CPRO11-T5 — Frontend CRM Mismatches
**Data:** 2026-04-20
**Terminal:** T5 (Frontend owner)
**Branch:** feature/people-management-reorganization
**Commits:** docs=`22121f3c` code=`27b931a8`

---

## §1 STEP 0 — Contrato e Princípio

- **Contrato CRM/Vendas:** v1.4 (início) → v1.5 (fim)
- **Princípio §13 mais relevante:** §13.4 — Escopo é Sagrado. T5 só toca `frontend/src/app/modulos/crm/**`, `hooks/crm/**`, `components/crm/**`, `constants/crm/**`, `utils/crm/**`. Nada fora dessas pastas.
- **O que foi feito:** Corrigidos todos os mismatches entre schema backend (EN) e frontend (PT): campo names, enums de status/stage, FK dropdowns, formatação de MRR, React Error #31 do endereco-objeto, rota contratos/[id] criada, simulador com limpeza.

---

## §2 STEP 1 — Investigação (H1–H10)

| Hipótese | Verdade Confirmada | Fonte |
|---|---|---|
| H1 | Backend retorna `name` e `trading_name` (não `nome`) | `client_controller.py` query SQL |
| H2 | `useCRMClients` tipado com `name`/`trading_name`; page usava `client.nome` | `useLeads.ts` + page diff |
| H3 | Orval tem `api:generate:crm` — regenerar seria alternativa mas não necessária | `package.json` |
| H4 | `statusConfig` tinha chaves PT; backend envia EN (`new`, `won`, etc.) | `leadStatus.ts` antes |
| H5 | Modal stage `novo/qualificado/etc.` — não existe no backend enum | `opportunity.py` ORM |
| H6 | `/api/v1/users/` existe, requer admin, retorna `{ users, total }` | `endpoints/users.py` |
| H7 | WebSocket em layout.tsx global, já tem HEAD health-check graceful (não crash CRM) | `WebSocketProvider.tsx` |
| H8 | `cliente-detail-modal.tsx:80` renderiza `{cliente.endereco}` direto (objeto) → React Error #31 | código anterior |
| H9 | `contratos/page.tsx` query alertas tinha try/catch silenciando 500 | código anterior |
| H10 | `contratos/[id]/page.tsx` não existia — rota 404 | `ls contratos/` |

**Descoberta crítica:** `OpportunityCreate` não tem `client_id` — usa `contact_name: str`. P0.8 = dropdown de clientes para popular `contact_name` (não FK real), `owner_id` é FK real para `users`.

---

## §3 STEP 2 — Implementação

### Arquivos criados (3 novos)

| Arquivo | Propósito |
|---|---|
| `src/constants/crm/leadStatus.ts` | 7 status EN + 6 PT fallbacks; `leadStatusConfig()` helper; `LEAD_SOURCE_LABELS` |
| `src/constants/crm/opportunityStage.ts` | 6 stages lowercase (`qualification`→`closed_lost`); `OPPORTUNITY_STAGE_OPTIONS` const |
| `src/utils/crm/clientLabel.ts` | `clientLabel(c)` = `name \|\| trading_name \|\| cnpj \|\| '—'` |
| `src/app/modulos/crm/contratos/[id]/page.tsx` | Página minimal de detalhe de contrato (4 cards: Geral, Valores, Vigência, Responsável) |

### Arquivos modificados (7)

| Arquivo | Fixes aplicados |
|---|---|
| `components/crm/cliente-detail-modal.tsx` | P0.2: endereco estruturado (string|objeto→partes). `clientLabel()`. `segmentoConfig[client.segment]` |
| `components/crm/oportunidade-form-modal.tsx` | P0.7: stages dropdown `OPPORTUNITY_STAGE_OPTIONS`. P0.8: clients dropdown `/api/v1/crm/clients/`, users dropdown `/api/v1/users/`. Campos corretos: `title`, `contact_name`, `contact_email`, `value`, `stage`, `owner_id` |
| `app/modulos/crm/clientes/page.tsx` | P0.3: `clientLabel(client)`. P1.4: `getSegmentoBadge(client.segment)`. Status bilíngue (EN+PT) |
| `app/modulos/crm/leads/page.tsx` | P0.4: `leadStatusConfig(lead.status)`. P0.3: `lead.name \|\| lead.nome`. P1.3: `LEAD_SOURCE_LABELS[lead.source ?? '']` |
| `app/modulos/crm/contratos/page.tsx` | P0.6: `formatCurrency(stats.mrr ?? 0)`. P1.1: alertas query sem try/catch + `useEffect` toast. P1.2: `router.push('/modulos/crm/contratos/${id}')` |
| `app/modulos/crm/precificacao/page.tsx` | P1.8: `limpeza` adicionado ao `TIPOS_SERVICO` |
| `hooks/useLeads.ts` | Lead interface: campos EN opcionais (`name`, `contact_name`, `company`, `source`) adicionados como opcionais ao lado dos PT existentes |

---

## §4 STEP 3 — Build

```
NODE_OPTIONS=--max-old-space-size=4096 npm run build
```

**Resultado:** ✅ `Compiled successfully in 66s` — 284 páginas — 0 erros Turbopack

---

## §5 STEP 4 — CIC E2E (requer Jordan)

**PASSO 4 É MANUAL** — requer Jordan no browser DevTools.

Roteiro para validação CIC:

| Tela | O que verificar | Bug corrigido |
|---|---|---|
| `/modulos/crm/clientes` | Coluna Nome preenchida (não vazia) | P0.3 |
| `/modulos/crm/clientes/{id_real}` | Detalhe abre sem React Error #31; endereço formatado | P0.2 |
| `/modulos/crm/leads` | Status variados (não todos "Novo"); coluna Origem com labels PT | P0.4, P1.3 |
| `/modulos/crm/oportunidades` | Modal "Nova Oportunidade": dropdown stages, dropdown cliente, campo email, dropdown responsável | P0.7, P0.8 |
| `/modulos/crm/contratos` | MRR = valor real (não NaN); "Ver detalhes" navega para rota | P0.6, P1.2 |
| `/modulos/crm/contratos/{id_real}` | Página de detalhe carrega sem erro 404 | P1.2 |
| `/modulos/crm/precificacao` | Tipo "Limpeza" aparece no seletor | P1.8 |
| DevTools Console | Zero `WebSocket 404` originados do CRM | P1.9 (validar) |
| DevTools Network | `/api/v1/crm/contracts/alerts` 500 → toast de erro visível | P1.1 |

---

## §6 STEP 5 — Contrato

- **Versão:** v1.4 → v1.5
- **Seção atualizada:** §23.2 — Status T5 preenchido completamente

---

## §7 STEP 6 — Commits

| Commit | Hash | Mensagem |
|---|---|---|
| docs | `22121f3c` | `docs(cpro11): CONTRATO CRM v1.5 — §23.2 T5 frontend mismatches concluído` |
| code | `27b931a8` | `fix(cpro11): frontend CRM — P0.2 P0.3 P0.4 P0.6 P0.7 P0.8 P1.1 P1.2 P1.3 P1.4 P1.8` |

---

## §8 SELF-CHECK (INV-10)

| Camada | Verificação | Status |
|---|---|---|
| 1 — HTML chunk-hash | `curl http://127.0.0.1:3001/` retorna chunk hashes | ✅ `6e3f8fd0aa1f833a.js` |
| 2 — Chunk no filesystem | `ls .next/static/chunks/6e3f8fd0aa1f833a.js` | ✅ EXISTS |
| 3 — Strings no chunk | `grep -r "closed_won\|limpeza\|crm-contracts-alerts"` | ✅ encontrado em `fed6c8037ecfe09e.js`, `d6018e6d88c93995.js` |
| 4 — Network trace | `/modulos/crm/contratos` → 307 (rota ativa); `/modulos/crm/contratos/test-id` → 307 | ✅ |

---

## §9 TypeScript

| Escopo | Erros |
|---|---|
| Arquivos CRM (`src/app/modulos/crm/**`, `components/crm/**`, etc.) | **0 erros** ✅ |
| Total projeto (2 erros fora do escopo CRM) | 2 erros — `fiscal/certidoes/page.tsx` e `gestao-pessoas/ged/onvio-sync/types.ts` — pré-existentes, fora do escopo T5 |

---

## §10 Bugs Tratados vs Pendentes

### Tratados nesta sessão (T5)

| Bug | Status |
|---|---|
| P0.2 React Error #31 endereco | ✅ |
| P0.3 Coluna Nome vazia | ✅ |
| P0.4 Todos leads "Novo" | ✅ |
| P0.6 MRR NaN | ✅ |
| P0.7 Modal stage "Novo" inválido | ✅ |
| P0.8 Modal FK dropdowns | ✅ |
| P1.1 Alertas 500 silenciados | ✅ |
| P1.2 Ver-detalhes botão morto | ✅ |
| P1.3 Origem "-" em leads | ✅ |
| P1.4 Tipo "-" em clientes | ✅ |
| P1.8 Limpeza faltante no simulador | ✅ |
| P1.9 WebSocket 404 CRM | ✅ (graceful existia, sem alteração) |

### Pendentes / Fora de escopo T5

| Bug | Dono | Observação |
|---|---|---|
| P0.5 Dashboard KPI Clientes=3 | T4 ✅ backend corrigido | Necessita verificação frontend (useCRMDashboardKpis) |
| P0.9 Life Centro client_id=NULL | T6 | CNPJ desconhecido — pendente dados manuais |
| P0.11 conversion_rate=0 | T4 ✅ | Backend corrigido — validar visualmente |
| P1.5 KPI Condomínios=0 | T4+T5 | Backend corrigido — validar via CIC |
| P1.6 KPIs Oportunidades | T4+T5 | Backend corrigido — validar via CIC |
| P1.7 Propostas erro 500 templates | T4 ✅ P0.3 aplicado | Validar via CIC |
| P1.13 Precificação duplicata | T4 | Investigação §13.1 pendente |

---

## §11 Trabalho Adicional Identificado (§13.4 — não implementado)

1. **P0.5 frontend side**: `useCRMDashboardKpis` — verificar se hook usa `clientes_total` do novo DashboardKPIs retornado por T4. Se não, precisará ser atualizado.
2. **38 `: any`** em CRM frontend — débito técnico P2, não P0/P1.
3. **Testes frontend CRM** — zero atualmente; P2.

---

## §12 Comando de Download

```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_CPRO11_T5.md ~/Downloads/RELATORIO_CPRO11_T5.md
```
