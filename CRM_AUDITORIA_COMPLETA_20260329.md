# CRM Conecta PRO — Auditoria Arqueológica Completa
**Data:** 29/03/2026
**Branch:** feature/people-management-reorganization

---

## 1. Inventário de Dados Reais

| Tabela | Registros | Status |
|--------|-----------|--------|
| clients | 13 (11 ativos reais + 2 internos) | Fonte oficial |
| leads | 11 (todos `converted`, `score=100`) | Vinculados a clients |
| opportunities | 5 (upsell real) | Vinculadas a leads |
| client_contracts | 11 | Contratos ativos |
| proposals | 0 | Vazia |
| commissions | 0 | Vazia |
| commission_rules | 0 | Vazia |
| proposal_items | 0 | Vazia |
| lead_scores | 0 | Vazia |

**Conclusão:** CRM contém apenas dados reais. Zero simulados.

---

## 2. Backend — Estrutura Completa

### 2.1 Controllers (7 arquivos, ~95 endpoints)

| Controller | Prefix | Endpoints | Status |
|-----------|--------|-----------|--------|
| **client_controller.py** | `/crm/clients` | 3 (GET /, GET /resumo, GET /{id}) | Novo — criado 29/03 |
| **lead_controller.py** | `/crm/leads` | 9 (CRUD + stats + score + action) | Completo |
| **opportunity_controller.py** | `/crm/opportunities` | 9 (CRUD + pipeline/stats + stage + close) | Completo |
| **proposal_controller.py** | `/crm/proposals` | 18 (CRUD + items + templates + approval flow) | Completo |
| **contract_controller.py** | `/crm/contracts` | 25 (CRUD + items + addendums + templates + SLA) | Completo |
| **commission_controller.py** | `/crm/commissions` | 17 (rules + calc + payments + summaries) | Completo |
| **dashboard_controller.py** | `/crm/dashboard` | 12 (KPIs + funnel + trends + charts) | Completo |

### 2.2 Models (5 arquivos, 15+ tabelas)

| Model | Tabela | Colunas | Enums |
|-------|--------|---------|-------|
| Lead | leads | 21 | LeadStatus(7), LeadSource(8) |
| Opportunity | opportunities | 23 | OpportunityStage(6), Priority(4), LossReason(8) |
| Proposal | proposals | 38 | ProposalStatus(10), ProposalType(5), DiscountType(2) |
| Contract | contracts | 42 | ContractStatus(6), ContractType(2), AdjustmentIndex(5), ServiceType(8) |
| Commission | commissions | 26 | CommissionStatus(5), CommissionType(5), CommissionTrigger(5) |

Tabelas auxiliares: proposal_items, proposal_templates, proposal_approvals, contract_items, contract_addendums, contract_templates, contract_sla_reports, commission_rules, seller_commission_rules, commission_payments, commission_summaries

### 2.3 Repositories (5 arquivos, ~120 métodos)

| Repository | Métodos | Destaque |
|-----------|---------|---------|
| LeadRepository | 10 | Filtros por status/source/score/company, cálculo de score |
| OpportunityRepository | 10 | Pipeline stats, conversão lead→oportunidade, stages |
| ProposalRepository | 20+ | Versionamento, templates, fluxo aprovação, itens |
| ContractRepository | 25+ | Aditivos, templates, SLA reports, renovação/reajuste |
| CommissionRepository | 20+ | Regras, cálculo, pagamentos, resumos mensais |

### 2.4 Services (9 arquivos)

| Service | Propósito |
|---------|-----------|
| lead_service.py | Lógica de leads |
| pipeline_service.py | Pipeline e conversão |
| proposal_service.py | Propostas e itens |
| contract_service.py | Contratos e aditivos |
| commission_service.py | Comissões e pagamentos |
| dashboard_service.py | KPIs e métricas |
| crm_360_service.py | Visão 360° do cliente |
| pricing_engine.py | Motor de precificação |
| signature_integration.py | Integração assinatura digital |

### 2.5 Foreign Keys

```
leads.assigned_to_id → users.id
leads.client_id → clients.id (bidirecional)
clients.lead_id → leads.id (bidirecional)
opportunities.lead_id → leads.id
opportunities.owner_id → users.id
proposals.opportunity_id → opportunities.id
proposals.parent_id → proposals.id (versionamento)
proposals.template_id → proposal_templates.id
proposals.created_by_id → users.id
commissions.seller_id → users.id
commissions.proposal_id → proposals.id
commissions.rule_id → commission_rules.id
```

---

## 3. Frontend — Páginas e Componentes

### 3.1 Páginas (6)

| Rota | Componente | Dados | UI |
|------|-----------|-------|-----|
| `/modulos/crm` | CRMDashboardPage | KPIs via `/crm/dashboard/kpis` | 4 cards KPI + 3 métricas + navegação |
| `/modulos/crm/leads` | LeadsPage | `/crm/leads` + `/crm/leads/stats` | Tabela 5 cols + filtros + 3 métricas |
| `/modulos/crm/oportunidades` | OportunidadesPage | `/crm/opportunities` + pipeline/stats | Tabela 6 cols + modais + 4 stats |
| `/modulos/crm/propostas` | PropostasPage | `/crm/proposals` + stats | Tabela 6 cols + form inline + 4 stats |
| `/modulos/crm/clientes` | ClientesPage | `/api/v1/clients/clients` | Tabela 6 cols + modais + 4 stats |
| `/modulos/crm/contatos` | ContatosPage | Estado local (sem API) | Tabela 6 cols + form inline |

### 3.2 Hooks

| Hook | API Base | Tipo |
|------|----------|------|
| useLeads | `/api/v1/crm/leads` | Custom (api-client) |
| useOpportunities | `/api/v1/crm/opportunities` | Orval generated |
| useProposals | `/api/v1/crm/proposals` | Orval generated |
| useContracts | `/api/v1/crm/contracts` | Orval generated |
| useCommissions | `/api/v1/crm/commissions` | Orval generated |
| useCRMDashboardKpis | `/api/v1/crm/dashboard/kpis` | Orval generated |
| useClients | `/api/v1/clients/clients` | Orval generated |

### 3.3 Componentes

| Componente | Arquivo | Propósito |
|-----------|---------|-----------|
| oportunidade-form-modal.tsx | 5.0K | Modal criar/editar oportunidade |
| oportunidade-detail-modal.tsx | 3.0K | Modal detalhe oportunidade |
| cliente-form-modal.tsx | 4.3K | Modal criar/editar cliente |
| cliente-detail-modal.tsx | 3.0K | Modal detalhe cliente |

### 3.4 Menu/Sidebar (modules.ts)

Módulo "Comercial" com 6 sub-itens:
- Leads → `/modulos/crm/leads`
- Oportunidades → `/modulos/crm/oportunidades`
- Clientes → `/modulos/crm/clientes`
- Contatos → `/modulos/crm/contatos`
- Propostas → `/modulos/crm/propostas`
- Contratos → `/modulos/servicos/contratos` (fora do CRM!)

---

## 4. Capacidades Atuais vs Necessárias

### Backend

| Capacidade | Status | Observação |
|-----------|--------|-----------|
| CRUD clientes | ✅ Parcial | GET só (via client_controller novo). CRUD completo em `/clients/clients` |
| CRUD leads | ✅ Completo | 9 endpoints, filtros, score, actions |
| Pipeline oportunidades | ✅ Completo | 9 endpoints, stages, stats |
| Propostas + aprovação | ✅ Completo | 18 endpoints, templates, versionamento |
| Contratos + SLA | ✅ Completo | 25 endpoints, aditivos, reajuste |
| Comissões | ✅ Completo | 17 endpoints, regras, pagamentos |
| Dashboard KPIs | ✅ Completo | 12 endpoints, funil, tendências |
| Atividades/histórico | ❌ Falta | Sem tabela de atividades |
| Contatos múltiplos | ❌ Falta | Sem tabela de contatos CRM |
| Tarefas e follow-up | ❌ Falta | Sem tabela de tarefas CRM |
| Notas por cliente | ❌ Falta | Apenas campo `notes` em cada entidade |
| Integração financeiro | ✅ | Via client_id e referências cruzadas |
| Integração operacional | ❌ Parcial | Contratos referem serviços mas sem vínculo postos |
| Busca e filtros | ✅ | Implementado em todos os controllers |
| Paginação | ✅ | skip/limit em todos os list endpoints |
| Exportação | ❌ Falta | Sem endpoint de export CSV/Excel |
| Webhook/eventos | ❌ Falta | Sem event bus para CRM |

### Frontend

| Capacidade | Status | Observação |
|-----------|--------|-----------|
| Listagem clientes com filtros | ✅ | Tabela + busca + filtro tipo/status |
| Detalhe cliente 360° | ❌ Parcial | Modal simples, não página completa |
| Kanban pipeline | ❌ Falta | Oportunidades em tabela, não kanban |
| Timeline atividades | ❌ Falta | Sem backend |
| Formulário novo lead | ✅ | Via modal na página leads |
| Dashboard CRM | ✅ | KPIs + navegação |
| Relatórios conversão | ❌ Parcial | Funil via API, sem página dedicada |
| Busca global | ❌ Falta | Busca por página, não global |
| Mobile responsivo | ✅ | Tailwind CSS responsive |

---

## 5. Gaps Críticos

### 5.1 Clientes usa endpoint errado no frontend

A página `clientes/page.tsx` chama `/api/v1/clients/clients` (módulo Financeiro) em vez de `/api/v1/crm/clients/` (novo endpoint CRM com MRR e lead_source). Precisa migrar para o endpoint CRM.

### 5.2 Contatos sem backend

A página `contatos/page.tsx` usa apenas estado local React (`useState`). Dados são perdidos ao recarregar. Precisa de tabela + CRUD no backend.

### 5.3 Sem visão 360° do cliente

Não existe página de detalhe completo do cliente com:
- Contratos ativos e histórico
- NFS-e emitidas
- Funcionários alocados (postos)
- Oportunidades de upsell
- Timeline de interações
- Score de saúde

O service `crm_360_service.py` existe no backend mas não tem endpoint exposto.

### 5.4 Pipeline não visual

Oportunidades são listadas em tabela. Precisa de Kanban drag-and-drop.

### 5.5 Contratos fora do CRM no menu

O item "Contratos" no sidebar aponta para `/modulos/servicos/contratos` (módulo Serviços), não para `/crm/contracts` que tem o CRUD completo com SLA e aditivos.

---

## 6. Dados no Banco

### Registros reais

| Entidade | Registros | Exemplo |
|---------|-----------|---------|
| Clientes | 13 | Ideal Flores, Michelangelo, Gelain... |
| Leads | 11 | Todos converted, vinculados a clients |
| Oportunidades | 5 | Upsell: Life Centro, Mirante, Parise, Green Hills, Gelain |
| Contratos (client_contracts) | 11 | Todos active, com MRR real |
| Propostas | 0 | Vazia |
| Comissões | 0 | Vazia |

### MRR por cliente

| Cliente | MRR |
|--------|-----|
| Ideal Flores da Cidade | R$ 65.842,42 |
| Laranjeiras Village | R$ 42.544,50 |
| Mirante das Flores | R$ 42.255,80 |
| Prime Arena | R$ 40.466,50 |
| Villa dos Pássaros | R$ 37.338,33 |
| Villa Dei Fiori | R$ 25.592,71 |
| Michelangelo | R$ 8.346,70 |
| Gelain | R$ 6.000,00 |
| Parise Village | R$ 1.700,00 |
| Life Centro | R$ 1.500,00 |
| Green Hills | R$ 500,00 |
| **Total MRR** | **R$ 272.086,96** |

---

## 7. Arquitetura Técnica

```
Backend:
  /api/v1/crm/clients/     → client_controller (novo, lê de `clients`)
  /api/v1/crm/leads/       → lead_controller (CRUD completo)
  /api/v1/crm/opportunities/ → opportunity_controller (pipeline)
  /api/v1/crm/proposals/   → proposal_controller (aprovação)
  /api/v1/crm/contracts/   → contract_controller (SLA, aditivos)
  /api/v1/crm/commissions/ → commission_controller (pagamentos)
  /api/v1/crm/dashboard/   → dashboard_controller (KPIs)

Frontend:
  /modulos/crm/            → Dashboard
  /modulos/crm/leads       → Leads (tabela)
  /modulos/crm/oportunidades → Oportunidades (tabela)
  /modulos/crm/clientes    → Clientes (tabela — endpoint errado!)
  /modulos/crm/contatos    → Contatos (sem backend!)
  /modulos/crm/propostas   → Propostas (tabela)

Banco:
  clients (69 cols) ← leads (21 cols) ← opportunities (23 cols)
  ← proposals (38 cols) ← commissions (26 cols)
  ← client_contracts (31 cols)
```

---

## 8. Recomendações para Transformação

### Prioridade 1 — Corrigir frontend
1. Migrar `clientes/page.tsx` para usar `/api/v1/crm/clients/` (com MRR e lead)
2. Criar backend para `contatos` (tabela + CRUD)
3. Mover "Contratos" no sidebar de Serviços para CRM

### Prioridade 2 — Melhorar UX
4. Kanban de oportunidades (drag-and-drop stages)
5. Página detalhe 360° do cliente (expor crm_360_service)
6. Timeline de atividades por cliente

### Prioridade 3 — Funcionalidades novas
7. Tabela de atividades/interações (chamadas, emails, visitas)
8. Tabela de tarefas CRM com follow-up automático
9. Export CSV/Excel
10. Webhook de eventos CRM → notificações

---

*Relatório gerado em 29/03/2026 — Conecta PRO v2.0.0*
