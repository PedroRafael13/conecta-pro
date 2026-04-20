# CPRO11 — Reconhecimento Frontend Menu Negócios
**Data:** 2026-04-20
**Sessão:** tmux t5
**Branch:** feature/people-management-reorganization
**Path:** /opt/conecta-pro/frontend/src/

> **NOTA CRÍTICA:** O prompt menciona 4 módulos (CRM, Vendas, Marketing, Licitações).
> **"Vendas" NÃO existe como módulo separado.** Não há `/modulos/vendas/`.
> As funcionalidades de vendas (propostas, contratos, comissões, oportunidades) estão
> integradas ao módulo CRM. A seção 2 documenta o CRM completo com suas sub-áreas de vendas.

---

## 1. CRM

### 1.1 Rotas e Páginas

| URL | Arquivo | S/C | Linhas | Status |
|-----|---------|-----|--------|--------|
| `/modulos/crm` | `crm/page.tsx` | Client | ~246 | ✅ Funcional — Dashboard KPIs |
| `/modulos/crm/leads` | `crm/leads/page.tsx` | Client | ~409 | ✅ Funcional — CRUD completo |
| `/modulos/crm/oportunidades` | `crm/oportunidades/page.tsx` | Client | ~474 | ✅ Funcional — Kanban drag-drop |
| `/modulos/crm/clientes` | `crm/clientes/page.tsx` | Client | ~300 | ✅ Funcional — Lista + filtros |
| `/modulos/crm/clientes/[id]` | `crm/clientes/[id]/page.tsx` | Client | ~160 | ✅ Funcional — Detalhe com abas |
| `/modulos/crm/propostas` | `crm/propostas/page.tsx` | Client | ~598 | ✅ Funcional — CRUD + ações |
| `/modulos/crm/contratos` | `crm/contratos/page.tsx` | Client | ~350 | ✅ Funcional — CRUD completo |
| `/modulos/crm/contatos` | `crm/contatos/page.tsx` | Client | ~280 | ✅ Funcional — CRUD com tabela |
| `/modulos/crm/comissoes` | `crm/comissoes/page.tsx` | Client | ~320 | ✅ Funcional — Tabelas + filtros |
| `/modulos/crm/precificacao` | `crm/precificacao/page.tsx` | Client | ~200 | ✅ Funcional — Simulador CLT |

**Metadata:** Nenhuma `export const metadata` encontrada nas páginas CRM — todas Client Components (incompatível com Server-side metadata).

### 1.2 Componentes

| Componente | Arquivo | Tipo | Linhas | Deps Externas |
|-----------|---------|------|--------|---------------|
| ClienteDetailModal | `components/crm/cliente-detail-modal.tsx` | Modal | ~180 | shadcn/ui Dialog |
| ClienteFormModal | `components/crm/cliente-form-modal.tsx` | Modal | ~220 | shadcn/ui Dialog, react-hook-form |
| OportunidadeFormModal | `components/crm/oportunidade-form-modal.tsx` | Modal | ~260 | shadcn/ui Dialog |
| OportunidadeDetailModal | `components/crm/oportunidade-detail-modal.tsx` | Modal | ~200 | shadcn/ui Dialog |

Tabelas, cards e filtros são inline nas páginas (sem extração para componentes reutilizáveis).

### 1.3 Hooks e Estado

**Arquivo consolidado:** `hooks/crm/useCRM.ts` (~150 linhas de re-exports)
**Arquivo legacy:** `hooks/useLeads.ts` (~150 linhas, padrão TanStack Query manual)

| Grupo | Hooks | Padrão |
|-------|-------|--------|
| Leads | useLeads, useLead, useLeadsStats, useCreateLead, useUpdateLead, useDeleteLead, useUpdateLeadStatus, useRecalculateLeadScore | useQuery + useMutation ✅ |
| Oportunidades | useOpportunities, useOpportunity, usePipelineStats, useCreateOpportunity, useUpdateOpportunity, useUpdateOpportunityStage, useCloseOpportunity, useCreateOpportunityFromLead | useQuery + useMutation ✅ |
| Propostas | useProposals, useProposal, useProposalStats, useCreateProposal, useSubmitProposal, useApproveProposal, useSendProposal, useAcceptProposal, useRejectProposal, useNewProposalVersion, useProposalTemplates | useQuery + useMutation ✅ |
| Contratos | useContracts, useContract, useContractStats, useCreateContract, useActivateContract, useSuspendContract, useTerminateContract, useRenewContract, useContractAdjustment, useContractAlerts, useCreateAddendum | useQuery + useMutation ✅ |
| Comissões | useCommissions, useCommission, useCommissionStats, useCommissionRules, useSellerCommissionStats | useQuery + useMutation ✅ |
| Dashboard | useCRMDashboardKpis, useSalesFunnel, useLeadsTrends, useSalesTrends, useConversionRates, useSellerPerformance | useQuery ✅ |

**staleTime padrão:** 30.000ms nas queries estáticas.
**Anti-padrão `useState([])`:** Não encontrado nas queries — padrão correto.
**Stores Zustand/Jotai:** Não encontrado — estado local via useState para forms/modais.

**Endpoints consumidos:**
```
GET/POST/PUT/DELETE  /api/v1/crm/leads
GET/POST/PUT/PATCH   /api/v1/crm/opportunities
GET/POST/PUT         /api/v1/crm/proposals + /approve /send /submit
GET/POST/PUT         /api/v1/crm/contracts  + /renew /suspend /terminate
GET/POST/PUT/DELETE  /api/v1/crm/commissions
GET                  /api/v1/crm/dashboard/kpis
GET                  /api/v1/crm/activities/recent
GET                  /api/v1/financial/precificacao/simulador  (CRM Precificação)
```

### 1.4 UI/UX Qualitativo (tela por tela)

| Tela | Lista | Criar | Editar | Deletar | Detalhe | Dashboard | Loading | Empty | Error |
|------|-------|-------|--------|---------|---------|-----------|---------|-------|-------|
| Dashboard | — | — | — | — | — | ✅ KPIs + funil | ✅ Skeleton | ✅ | ✅ Alert |
| Leads | ✅ Tabela | ✅ Modal | ✅ Modal | ✅ Confirm | ✅ Drawer | — | ✅ Spinner | ✅ | ✅ |
| Oportunidades | ✅ Kanban | ✅ Modal | ✅ Modal | ✅ | ✅ Modal | — | ✅ | ✅ | ✅ |
| Clientes | ✅ Tabela | ✅ Modal | ✅ Modal | ✅ | ✅ Abas | — | ✅ | ✅ | ✅ |
| Propostas | ✅ Tabela | ✅ Inline | ✅ Inline | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| Contratos | ✅ Tabela | ✅ Modal | ✅ Modal | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| Contatos | ✅ Tabela | ✅ Modal | ✅ Modal | ✅ | — | — | ✅ | ✅ | ✅ |
| Comissões | ✅ Tabela | ✅ Modal | ✅ Modal | ✅ | — | — | ✅ | ✅ | ✅ |
| Precificação | ✅ Simulador | — | — | — | — | — | ✅ | ✅ | ✅ |

### 1.5 Aderência à Marca

- **Cores:** Módulo usa `cyan-500/50/100` como cor de acento (não o azul canônico `#0A2540/#1E3A5F`). O laranja `#FF6B35` / Tailwind `orange-500` não aparece nos acentos do CRM.
- **Tipografia:** Padrão Tailwind (sans-serif) — sem fonte customizada visível.
- **Responsividade:** `hidden md:table-cell`, `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` — ✅ mobile-first presente.
- **Acessibilidade:** `<Button>` shadcn com `aria-*` implícito; sem `aria-label` explícito nos ícones de ação; `<label>` não verificado em todos os forms.
- **Score aderência à marca:** 6/10 — Funcional, mas cor de acento diverge do azul canônico. Laranja ausente. Estilo próximo ao padrão mas não idêntico ao Financeiro.

### 1.6 TypeScript Health

**`npx tsc --noEmit`:** 0 erros no módulo CRM. (2 erros totais no projeto — ambos em módulos externos: `fiscal/certidoes/page.tsx` e `gestao-pessoas/ged/onvio-sync/types.ts`)

- **`: any` explícito:** 38 instâncias em `src/app/modulos/crm/`
  - `oportunidades/page.tsx`: 13 (Kanban + handlers sem tipagem)
  - `clientes/page.tsx`: 7
  - `clientes/[id]/page.tsx`: 5
  - `propostas/page.tsx`: 5
  - `contratos/page.tsx`: 3
  - `contatos/page.tsx`: 2
  - `comissoes/page.tsx`: 2
  - `page.tsx` (dashboard): 1
- **`@ts-ignore`:** 0
- **`@ts-expect-error`:** 0
- **Todos Client Components:** 100% ('use client' presente)

### 1.7 TODOs

**Resultado:** Zero TODOs, FIXMEs, @ts-ignore ou @ts-expect-error nos arquivos do módulo CRM.

---

## 2. Vendas

> **⚠️ MÓDULO NÃO EXISTE COMO ENTIDADE SEPARADA**
>
> Não há diretório `/modulos/vendas/` nem `/modulos/sales/` no App Router.
> As funcionalidades de vendas estão distribuídas dentro do CRM:
>
> | Funcionalidade | Localização |
> |----------------|-------------|
> | Pipeline de vendas | `/modulos/crm/oportunidades` (Kanban) |
> | Propostas comerciais | `/modulos/crm/propostas` |
> | Contratos | `/modulos/crm/contratos` |
> | Comissões de vendedores | `/modulos/crm/comissoes` |
> | Precificação / Simulador | `/modulos/crm/precificacao` |
> | Dashboard de vendas | `/modulos/crm` (KPIs + funil) |
>
> No `config/modules.ts` e no menu lateral, "Vendas" não aparece como item separado.
> Toda a estrutura de Negócios é: **Negócios → CRM / Marketing / Licitações**.

### 2.1 Rotas e Páginas

N/A — módulo não existe. Ver seção 1.1 (CRM) para rotas de propostas, oportunidades, contratos e comissões.

### 2.2 Componentes

N/A — módulo não existe. Componentes de vendas estão em `components/crm/` (ver seção 1.2).

### 2.3 Hooks e Estado

N/A — módulo não existe. Hooks de vendas estão em `hooks/crm/useCRM.ts` (ver seção 1.3).

### 2.4 UI/UX Qualitativo

N/A — módulo não existe. UX das funcionalidades de vendas documentado em seção 1.4.

### 2.5 Aderência à Marca

N/A — módulo não existe. Aderência do CRM documentada em seção 1.5.

### 2.6 TypeScript Health

N/A — módulo não existe. TypeScript health do CRM documentado em seção 1.6.

### 2.7 TODOs

N/A — módulo não existe.

**Recomendação:** Se houver intenção de separar "Vendas" em módulo próprio no futuro, as rotas `/modulos/crm/propostas`, `/modulos/crm/contratos` e `/modulos/crm/oportunidades` são candidatas naturais. Por ora, documentar como sub-área do CRM é o correto.

---

## 3. Marketing

### 3.1 Rotas e Páginas

| URL | Arquivo | S/C | Linhas | Status |
|-----|---------|-----|--------|--------|
| `/modulos/marketing/funil` | `marketing/funil/page.tsx` | Client | ~64 | ✅ Funcional — Stats do funil |
| `/modulos/marketing/campanhas` | `marketing/campanhas/page.tsx` | Client | ~110 | ✅ Funcional — CRUD campanhas |
| `/modulos/marketing/lead-magnet` | `marketing/lead-magnet/page.tsx` | Client | ~100 | ✅ Funcional — Lista + upload |
| `/modulos/marketing/brand-voice` | `marketing/brand-voice/page.tsx` | Client | ~80 | ⚠️ Estático — Conteúdo hardcoded |

**Nota Brand Voice:** Página existe e renderiza conteúdo (Personalidade, Tom, Vocabulário, Exemplos), mas é 100% estático/hardcoded. Sem backend, sem edição, sem CRUD.

### 3.2 Componentes

Não há pasta `components/marketing/`. Os componentes são inline nas páginas.

### 3.3 Hooks e Estado

Sem hooks customizados em `hooks/marketing/`. As páginas usam `customInstance` + `useQuery`/`useMutation` diretamente.

| Página | Hooks | Endpoints |
|--------|-------|-----------|
| Funil | useQuery (stats) | GET `/api/v1/marketing/leads/stats` + GET `/api/v1/crm/clients/resumo` |
| Campanhas | useQuery + useMutation | GET/POST/PUT `/api/v1/marketing/campaigns/` |
| Lead Magnet | useQuery + useMutation | GET `/api/v1/marketing/lead-magnet` |
| Brand Voice | nenhum | — (estático) |

**staleTime:** Não definido explicitamente nas páginas Marketing — usa o default (0).
**Anti-padrão:** `useState([])` usado em campanhas para lista local antes do fetch — menor issue.

### 3.4 UI/UX Qualitativo

| Tela | Lista | Criar | Editar | Deletar | Loading | Empty | Error |
|------|-------|-------|--------|---------|---------|-------|-------|
| Funil | ✅ Métricas cards | — | — | — | ✅ | ✅ | ✅ |
| Campanhas | ✅ Tabela | ✅ Modal | ✅ Modal | ✅ | ✅ | ✅ | ✅ |
| Lead Magnet | ✅ Cards | ✅ Upload | — | ✅ | ✅ | ✅ | ✅ |
| Brand Voice | ✅ Estático | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

### 3.5 Aderência à Marca

- **Cores:** `purple-500`, `blue-500` como acentos. Sem uso do azul canônico.
- **Responsividade:** Breakpoints `md:/lg:` presentes.
- **Score:** 5/10 — Brand Voice é estático, Marketing tem apenas 3 funcionalidades reais, sem dashboard dedicado.

### 3.6 TypeScript Health

**`npx tsc --noEmit`:** 0 erros no módulo Marketing.

- **`: any` explícito:** 11 instâncias em `src/app/modulos/marketing/`
- **`@ts-ignore`:** 0
- **`@ts-expect-error`:** 0

### 3.7 TODOs

**Resultado:** Zero TODOs, FIXMEs nos arquivos de Marketing.

---

## 4. Licitações

### 4.1 Rotas e Páginas

| URL | Arquivo | S/C | Linhas | Status |
|-----|---------|-----|--------|--------|
| `/modulos/licitacoes` | `licitacoes/page.tsx` | Client | ~200 | ✅ Dashboard KPIs |
| `/modulos/licitacoes/editais` | `licitacoes/editais/page.tsx` | Client | ~250 | ✅ Lista + filtros + sync PNCP |
| `/modulos/licitacoes/editais/[id]` | `licitacoes/editais/[id]/page.tsx` | Client | ~500 | ✅ Detalhe completo |
| `/modulos/licitacoes/propostas` | `licitacoes/propostas/page.tsx` | Client | ~300 | ✅ Lista + ações |
| `/modulos/licitacoes/propostas/[id]` | `licitacoes/propostas/[id]/page.tsx` | Client | ~350 | ✅ Detalhe + itens |
| `/modulos/licitacoes/documentos` | `licitacoes/documentos/page.tsx` | Client | ~350 | ✅ Upload + aprovação |
| `/modulos/licitacoes/certidoes` | `licitacoes/certidoes/page.tsx` | Client | ~300 | ✅ Upload + validação |
| `/modulos/licitacoes/disputas` | `licitacoes/disputas/page.tsx` | Client | ~300 | ✅ WebSocket real-time |
| `/modulos/licitacoes/contratos` | `licitacoes/contratos/page.tsx` | Client | ~400 | ✅ Lista + medições |
| `/modulos/licitacoes/contratos/[id]` | `licitacoes/contratos/[id]/page.tsx` | Client | ~550 | ✅ Detalhe + aditivos |
| `/modulos/licitacoes/contratos/[id]/editar` | `licitacoes/contratos/[id]/editar/page.tsx` | Client | ~300 | ✅ Edição inline |
| `/modulos/licitacoes/ia` | `licitacoes/ia/page.tsx` | Client | ~400 | ✅ IA Hub (análise + precificação) |
| `/modulos/licitacoes/oportunidades` | `licitacoes/oportunidades/page.tsx` | Client | ~350 | ✅ Discovery |
| `/modulos/licitacoes/resultados` | `licitacoes/resultados/page.tsx` | Client | ~300 | ✅ Resultados |

**Total:** 14 páginas, todas funcionais. 0 stubs.

### 4.2 Componentes

17 componentes em `components/licitacoes/`:

| Componente | Tipo | Responsabilidade |
|-----------|------|-----------------|
| TenderStatusBadge | Badge | Status visual de editais |
| ModalityBadge | Badge | Modalidade (Pregão, Tomada, etc.) |
| ProposalStatusBadge | Badge | Status de propostas |
| TenderFilters | FilterPanel | Filtros avançados de editais |
| ProposalFilters | FilterPanel | Filtros de propostas |
| TenderFormModal | Modal | CRUD de edital |
| ProposalFormModal | Modal | CRUD de proposta |
| ContractFormModal | Modal | CRUD de contrato |
| ProposalItemsManager | Editor | Gestor de itens de proposta |
| SubmitProposalDialog | Dialog | Confirmação de submissão |
| ContractAddendumModal | Modal | Aditivo contratual |
| CertificateUploadModal | Modal | Upload de certidão |
| DocumentUploadModal | Modal | Upload de documento |
| CertificateStatusBadge | Badge | Status de certidão |
| CertificateTypeIcon | Icon | Tipo de certidão |
| DocumentStatusBadge | Badge | Status de documento |
| DisputeRoomComponent | Real-time | Sala de disputa WebSocket |

### 4.3 Hooks e Estado

7 arquivos de hooks em `hooks/bidding/` (1.459 linhas totais + barrel index.ts de 1.003 linhas):

| Arquivo | Hooks principais | Linhas |
|---------|-----------------|--------|
| `useTenders.ts` | useListarEditais, useGetEdital, useCreateEdital, useUpdateEdital, useRemoverEdital, useMarcarParticipacao, useAlterarStatusEdital, useSincronizarPNCP | 224 |
| `useProposals.ts` | useListarPropostas, useGetProposta, useCreateProposta, useUpdateProposta, useEnviarProposta, useApproveProposta, useRejectProposta | 198 |
| `useContracts.ts` | useListarContratos, useGetContrato, useCreateContrato, useUpdateContrato, useMedicaoContrato, useAditivo, useCalculoRenovacao | 209 |
| `useDocuments.ts` | useListarDocumentos, useUploadDocumento, useApprovarDocumento, useRejectarDocumento, useDownloadDocumento | 157 |
| `useCertificates.ts` | useListarCertidoes, useUploadCertificado, useValidarCertificado, useRenovarCertificado | 180 |
| `useAgents.ts` | useAnalizeEdital, usePricingProposal, usePipelineAnalysis, useDocumentGeneration | 150 |

**Endpoints consumidos:**
```
GET/POST/PUT/DELETE  /api/v1/bidding/tenders + /status /participation /pncp/sync
GET/POST/PUT/DELETE  /api/v1/bidding/proposals + /submit /approve /reject
GET/POST/PUT/DELETE  /api/v1/bidding/contracts + /measurement /addendum /renewal
GET/POST/DELETE      /api/v1/bidding/documents + /approve /reject /download
GET/POST/DELETE      /api/v1/bidding/certificates + /validate /renew
POST                 /api/v1/bidding/agents/analyze + /pricing /pipeline /document-generation
WS                   /ws/bidding/disputes/{id}  (WebSocket para disputas)
```

**React Query keys:** Prefixo `['bidding', '<entidade>', ...]` em todos os hooks.

### 4.4 UI/UX Qualitativo

| Tela | Lista | Criar | Editar | Deletar | Detalhe | Loading | Empty | Error |
|------|-------|-------|--------|---------|---------|---------|-------|-------|
| Dashboard | — | — | — | — | — | ✅ | ✅ | ✅ |
| Editais | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Propostas | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Documentos | ✅ | ✅ Upload | — | ✅ | — | ✅ | ✅ | ✅ |
| Certidões | ✅ | ✅ Upload | — | ✅ | — | ✅ | ✅ | ✅ |
| Disputas | ✅ Real-time | — | — | — | ✅ | ✅ | ✅ | ✅ |
| Contratos | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| IA Hub | ✅ Análise | — | — | — | ✅ Resultado | ✅ | ✅ | ✅ |
| Oportunidades | ✅ | — | — | — | — | ✅ | ✅ | ✅ |
| Resultados | ✅ | — | — | — | — | ✅ | ✅ | ✅ |

### 4.5 Aderência à Marca

- **Cores:** `orange-500`, `amber-500` — acento laranja alinhado com `#FF6B35`. ✅
- **Responsividade:** `md:/lg:/xl:` aplicados sistematicamente em tabelas e grids.
- **Acessibilidade:** `aria-label` em botões de upload; `<label htmlFor>` nos formulários.
- **Testes:** 6 arquivos de teste em `licitacoes/__tests__/` — único módulo com cobertura.
- **WebSocket:** Implementado em disputas — diferencial técnico.
- **Score:** 8/10 — Módulo mais completo e bem estruturado. Leve penalidade pela ausência de Server Components.

### 4.6 TypeScript Health

**`npx tsc --noEmit`:** 0 erros no módulo Licitações.

- **`: any` explícito:** 31 instâncias em `src/app/modulos/licitacoes/`
  - `contratos/[id]/page.tsx`: 7
  - `contratos/page.tsx`: 5
  - `documentos/page.tsx`: 5
  - `disputas/page.tsx`: 4
  - `propostas/[id]/page.tsx`: 2
  - `editais/[id]/page.tsx`: 2
  - `certidoes/page.tsx`: 2
  - `page.tsx` (dashboard): 1
  - `oportunidades/page.tsx`: 1
  - `ia/page.tsx`: 1 (salario_base_vigilante no payload)
  - `editais/page.tsx`: 1
- **`@ts-ignore`:** 0
- **`@ts-expect-error`:** 0
- **Testes:** 6 arquivos de teste Jest/RTL cobrindo fluxos principais

### 4.7 TODOs

**Resultado:** Zero TODOs, FIXMEs nos arquivos de Licitações.

---

## 5. Navegação Global

### 5.1 Arquivo de configuração

**Arquivo canônico:** `/opt/conecta-pro/frontend/src/config/modules.ts`
**Arquivo legado (descontinuado):** `/opt/conecta-pro/frontend/src/config/modules.ts.bak`

### 5.2 Estrutura do grupo "Negócios" no sidebar

```typescript
// config/modules.ts — linha 521
{
  id: 'negocios',
  title: 'Negócios',
  modules: modules.filter(m => ['crm', 'marketing', 'licitacoes'].includes(m.id)),
}
```

**Grupo "Negócios" contém 3 módulos:**

```
Negócios
├── CRM  (cor: cyan, icon: Handshake)
│   ├── Dashboard       /modulos/crm
│   ├── Clientes        /modulos/crm/clientes
│   ├── Leads           /modulos/crm/leads
│   ├── Oportunidades   /modulos/crm/oportunidades
│   ├── Propostas       /modulos/crm/propostas
│   ├── Contratos       /modulos/crm/contratos
│   ├── Contatos        /modulos/crm/contatos
│   ├── Comissões       /modulos/crm/comissoes
│   └── Precificação    /modulos/crm/precificacao
│
├── Marketing  (cor: purple, icon: Megaphone)
│   ├── Funil           /modulos/marketing/funil
│   ├── Campanhas       /modulos/marketing/campanhas
│   ├── Lead Magnet     /modulos/marketing/lead-magnet
│   └── Brand Voice     /modulos/marketing/brand-voice
│
└── Licitações  (cor: orange, icon: Scale)
    ├── Dashboard       /modulos/licitacoes
    ├── Editais         /modulos/licitacoes/editais
    ├── Propostas       /modulos/licitacoes/propostas
    ├── Documentos      /modulos/licitacoes/documentos
    ├── Resultados      /modulos/licitacoes/resultados
    ├── Disputas        /modulos/licitacoes/disputas
    └── IA Hub          /modulos/licitacoes/ia
```

### 5.3 Sidebar / Layout

- **Arquivo layout:** `src/app/modulos/layout.tsx` — renderiza sidebar com os grupos de módulos
- **Autenticação:** `useAuth()` protege o layout — redireciona para `/login` se não autenticado
- **Breadcrumbs:** Não encontrado — sem componente de breadcrumb nos módulos de Negócios
- **Tabs internas:** Presentes em: `crm/clientes/[id]` (abas de detalhe) e `licitacoes/contratos/[id]` (abas com medições, aditivos)
- **Active state:** Link ativo destacado via `pathname` no sidebar

---

## 6. Ocorrências "vigilante" — Lista Completa

**Total encontrado: 37 ocorrências em 18 arquivos**

> **Avaliação:** Todas as ocorrências são **semanticamente corretas** — referem-se ao cargo
> "Vigilante Patrimonial/Armado", segmento core da Conecta Mais. NÃO são bugs nem
> conteúdo a remover. Documentado aqui conforme pedido para Jordan decidir.

| Arquivo | Linha | Contexto |
|---------|-------|----------|
| `src/types/operacional.ts` | 7 | `\| 'vigilante'` — tipo PostType |
| `src/types/operacional.ts` | 405 | `vigilante: 'Agente de Portaria'` — label display |
| `src/types/generated/operacional/...schemas.ts` | 3817 | `vigilante: 'vigilante'` — enum gerado Orval |
| `src/types/generated/document-kits/index.ts` | 19 | `\| 'VIGILANTE'` — enum de kits documentais |
| `src/hooks/operacional/__tests__/usePosts.test.tsx` | 63 | `post_type: 'VIGILANTE'` — fixture de teste |
| `src/hooks/operacional/__tests__/usePosts.test.tsx` | 110 | `validTypes = ['VIGILANTE', 'PORTEIRO', ...]` — fixture |
| `src/hooks/operacional/__tests__/usePosts.test.tsx` | 140 | `post_type: 'VIGILANTE'` — fixture |
| `src/hooks/operacional/__tests__/usePosts.test.tsx` | 146 | `expect(filters.post_type).toBe('VIGILANTE')` — assert |
| `src/hooks/useDashboard.ts` | 26 | `vigilantes_ativos: number` — interface KPIData |
| `src/hooks/__tests__/usePosts.test.ts` | 74 | `post_type: 'vigilante'` — mock |
| `src/hooks/__tests__/usePosts.test.ts` | 234 | `by_type: { vigilante: 30, porteiro: 20 }` — mock |
| `src/hooks/__tests__/useDashboard.test.ts` | 51 | `vigilantes_ativos: 30` — mock |
| `src/components/operacional/post-form-types.ts` | 22 | `post_type: 'vigilante' as PostType` — DEFAULT_FORM_DATA |
| `src/components/operacional/post-form-modal.tsx.backup` | 53 | `post_type: 'vigilante'` — arquivo .backup (lixo) |
| `src/components/operacional/post-form-modal.tsx.backup` | 107 | `post_type: 'vigilante'` — arquivo .backup (lixo) |
| `src/features/escalas/USAGE_EXAMPLES.md` | 212 | `'Escala padrão para vigilantes'` — docs exemplo |
| `src/features/escalas/USAGE_EXAMPLES.md` | 348 | `search: 'vigilante'` — docs exemplo |
| `src/app/modulos/operacional/ferias/page.tsx` | 163 | `'Dia do vigilante — 20 de junho...'` — dado mock hardcoded |
| `src/app/modulos/operacional/ferias/page.tsx` | 207 | `'...laudo de aptidão visual exigido...vigilantes armados'` — dado mock |
| `src/app/modulos/operacional/colaboradores/page.tsx.bak` | 434 | `placeholder="Ex: Vigilante, Porteiro..."` — arquivo .bak (lixo) |
| `src/app/modulos/operacional/colaboradores/page.tsx` | 483 | `placeholder="Ex: Vigilante, Porteiro..."` — placeholder input |
| `src/app/modulos/operacional/colaboradores/page.tsx` | 557 | `placeholder="Ex: Vigilante, Porteiro..."` — placeholder input |
| `src/app/modulos/dp/funcionarios/page.tsx` | 57 | `curso_vigilante: 'Curso Vigilante'` — label de campo |
| `src/app/modulos/dp/funcionarios/page.tsx` | 489 | `{renderField('curso_vigilante')}` — campo de formulário |
| `src/app/modulos/dp/funcionarios/page.tsx` | 490 | `{renderField('curso_vigilante_validade', 'date')}` — campo |
| `src/app/modulos/dp/admissao/page.tsx` | 216 | `<option value="Vigilante">Vigilante</option>` — select option |
| `src/app/modulos/dp/admissao/[id]/page.tsx` | 355 | `<option value="Vigilante">Vigilante</option>` — select |
| `src/app/modulos/dp/admissao/[id]/page.tsx` | 461 | `<option value="curso_vigilante">Curso Vigilante</option>` |
| `src/app/modulos/dp/admissao/[id]/page.tsx` | 462 | `<option value="cnv_carteira_nacional_vigilante">CNV</option>` |
| `src/app/modulos/dp/contratos/page.tsx` | 559 | `placeholder="Ex: Vigilante"` — placeholder |
| `src/app/modulos/recrutamento/candidatos/page.tsx` | 552 | `placeholder="Ex: Vigilante Patrimonial"` — placeholder |
| `src/app/modulos/recrutamento/vagas/page.tsx` | 475 | `placeholder="Ex: Vigilante Patrimonial"` — placeholder |
| `src/app/modulos/licitacoes/ia/page.tsx` | 187 | `salario_base_vigilante: 1800.0` — payload IA Pricing |
| `src/api/generated/retention/retentionAPI.schemas.ts` | 1041 | `vigilante: 'vigilante'` — schema gerado Orval |
| `src/services/bidding/agents.service.ts` | 86 | `salario_base_vigilante?: number` — interface PricerRequest |
| `src/services/bidding/agents.service.ts` | 106 | `salario_base_vigilante?: number` — interface PipelineRequest |
| `src/test/fixtures/operacional.ts` | 261 | `'Cliente elogiou atendimento do vigilante José'` — fixture |
| `src/test/fixtures/operacional.ts` | 318 | `cargo: 'Vigilante'` — fixture |
| `src/test/fixtures/operacional.ts` | 336 | `cargo: 'Vigilante'` — fixture |
| `src/test/fixtures/operacional.ts` | 360 | `cargo: 'Vigilante'` — fixture |

**Arquivos lixo que podem ser deletados (não são código ativo):**
- `src/components/operacional/post-form-modal.tsx.backup` (2 ocorrências)
- `src/app/modulos/operacional/colaboradores/page.tsx.bak` (1 ocorrência)

---

## 7. Sumário Executivo

### 7.1 Telas que existem e funcionam

**CRM (9/9 rotas funcionam):**
- Dashboard com KPIs (funil, leads, tendências)
- Leads: CRUD completo com scoring e status pipeline
- Oportunidades: Kanban com drag-and-drop entre stages
- Clientes: Lista + detalhe com abas (contratos, oportunidades, contatos)
- Propostas: CRUD + workflow (rascunho → enviada → aprovada/rejeitada)
- Contratos: CRUD + renovação + suspensão + aditivos
- Contatos: CRUD completo
- Comissões: Tabelas com filtros e stats por vendedor
- Precificação: Simulador CLT integrado ao `/financial/precificacao/simulador`

**Marketing (3/4 rotas reais):**
- Funil: Stats de conversão de leads
- Campanhas: CRUD de campanhas de marketing
- Lead Magnet: Upload e gerenciamento de materiais
- Brand Voice: Estático (conteúdo da marca hardcoded — sem backend)

**Licitações (14/14 rotas funcionam):**
- Dashboard, Editais (+ detalhe), Propostas (+ detalhe), Documentos, Certidões
- Disputas com WebSocket real-time
- Contratos (+ detalhe + editar), IA Hub, Oportunidades, Resultados

### 7.2 Telas que existem mas estão quebradas ou incompletas

| Tela | Problema |
|------|----------|
| Marketing > Brand Voice | Conteúdo 100% hardcoded, sem backend, sem edição |
| CRM > Oportunidades | Drag-and-drop Kanban pode depender de lib não verificada no build atual |
| `operacional/ferias/page.tsx` | Dados mock hardcoded com texto de exemplo (linhas 163, 207) |

### 7.3 Telas que NÃO existem

| Funcionalidade | Observação |
|----------------|------------|
| **Módulo "Vendas"** | Não existe. Vendas = sub-área do CRM |
| Marketing > Automações | Sem página — apenas mencionado em docs |
| Marketing > Analytics/Dashboard | Sem dashboard dedicado de Marketing |
| CRM > Activities Timeline | Atividades recentes sem página própria (só API endpoint) |
| Licitações > Certidões (detalhe) | Sem rota `/certidoes/[id]` |

### 7.4 Score Visual 0-10 por módulo (referência: Financeiro = 10/10)

| Módulo | Score | Justificativa |
|--------|-------|---------------|
| **Licitações** | **8/10** | Módulo mais completo e bem estruturado. 14 páginas, 17 componentes, WebSocket, 6 testes. Perde pontos por ausência de Server Components e 31 `any`. |
| **CRM** | **7/10** | 9 páginas funcionais, 95+ hooks, Kanban, simulador de precificação. Perde pontos: cor de acento diverge do brand (#0A2540), 38 `any`, sem breadcrumbs. |
| **Marketing** | **5/10** | Apenas 3 páginas reais. Brand Voice estático. Sem dashboard. Sem hooks customizados próprios. Funcional mas raso. |
| **Vendas** | **N/A** | Módulo não existe como entidade separada. |

### 7.5 Saúde técnica geral

| Métrica | Valor |
|---------|-------|
| Total de páginas nos 3 módulos | 27 (CRM: 10, Marketing: 4, Licitações: 14) |
| Client Components | 100% |
| Server Components | 0% |
| `: any` nos módulos Negócios | 80 (CRM: 38, Marketing: 11, Licitações: 31) |
| `: any` em todo `src/` | 1.110 |
| `@ts-ignore` | 0 ✅ |
| TODOs/FIXMEs | 0 ✅ |
| `tsc --noEmit` | 2 erros totais (0 em Negócios) — erros em `fiscal/certidoes` e `gestao-pessoas/onvio-sync` |
| Testes (arquivos) | 6 (todos em Licitações) |
| Hooks customizados | 100+ (CRM) + 7 arquivos (Licitações) |
| Componentes dedicados | 4 (CRM) + 17 (Licitações) |
| Endpoints mapeados | ~70 |

### 7.6 Status do frontend em produção

```
Docker:  conecta-pro-frontend — Up 2 days (healthy) — porta 3001
PM2:     conecta-pro-frontend — online — 2D uptime — 2 restarts — 110.8mb
Build:   Último build válido ativo (container saudável há 2 dias)
```

### 7.7 Prioridades para próxima sprint de UI

1. **[P1]** Implementar dashboard de Marketing (atualmente inexistente)
2. **[P1]** Brand Voice: adicionar backend CRUD (não ser estático)
3. **[P2]** Corrigir 80 instâncias de `: any` nos módulos Negócios (CRM: 38, Licitações: 31, Marketing: 11) — o total em todo src/ é 1.110
4. **[P2]** Alinhar cores de acento do CRM ao brand canônico (#0A2540 / #FF6B35)
5. **[P3]** Adicionar breadcrumbs aos módulos de Negócios
6. **[P3]** Expandir testes para CRM e Marketing (hoje só Licitações tem)
7. **[LIMPEZA]** Deletar arquivos `.bak` e `.backup` em operacional/

---

*Gerado por CPRO11 T5 — 2026-04-20*
