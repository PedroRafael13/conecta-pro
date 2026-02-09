# Análise de Cobertura de Testes - Conecta PRO

## Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de páginas** | 117 |
| **Testes E2E existentes** | 33 arquivos |
| **Cobertura estimada** | ~28% |
| **Módulos** | 22 |

---

## Módulos e Páginas

### 1. Módulo CRM (6 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/crm/clientes` | **CRÍTICA** | ❌ | GET /api/clientes, POST, PUT, DELETE | Tabela, Filtros, Form Modal, Detail Modal, Stats Cards |
| `/crm/leads` | **CRÍTICA** | ❌ | GET /api/leads, useLeadsStats | Tabela, Filtros, Stats Cards, Status badges |
| `/crm/oportunidades` | **ALTA** | ❌ | GET /api/opportunities | Kanban, Cards, Filtros |
| `/crm/propostas` | **ALTA** | ❌ | GET /api/proposals | Tabela, PDF Viewer, Aprovação |
| `/crm/contatos` | **MÉDIA** | ❌ | GET /api/contacts | Lista, Form |
| `/crm` (dashboard) | **BAIXA** | ❌ | - | Cards resumo, navegação |

**Elementos Interativos Identificados:**
- Formulários modais (ClienteFormModal, LeadForm)
- Tabelas com paginação e sorting
- Filtros de busca e status
- Cards de estatísticas
- Exportação de dados

---

### 2. Módulo Financeiro (14 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/financeiro/contas-pagar` | **CRÍTICA** | ✅ financial-contas-pagar.spec.ts | usePayables, usePayableDashboard, useCreatePayable, useUpdatePayable, useProcessPayment | Tabela, Filtros, Form Modal, Payment Modal, Stats Cards |
| `/financeiro/contas-receber` | **CRÍTICA** | ✅ financial-contas-receber.spec.ts | useReceivables | Tabela, Filtros, Form Modal |
| `/financeiro/faturamento` | **CRÍTICA** | ✅ financial-faturamento.spec.ts | useInvoices | Tabela, Emissão NFS-e, Cancelamento |
| `/financeiro/fluxo-caixa` | **ALTA** | ✅ financial-fluxo-caixa.spec.ts | useCashFlow | Gráficos, Projeções, Filtros |
| `/financeiro/conciliacao` | **ALTA** | ✅ financial-conciliacao.spec.ts | useConciliation | Matching interface, Importação |
| `/financeiro/contabilidade` | **ALTA** | ✅ financial-contabilidade.spec.ts | useAccounting | Lançamentos, Balanço, DRE |
| `/financeiro/custeio` | **ALTA** | ✅ financial-custeio.spec.ts | useCostAllocation | Rateio, Centros de Custo |
| `/financeiro/clientes` | **MÉDIA** | ✅ financial-clientes.spec.ts | useClients | Tabela, Faturamento por cliente |
| `/financeiro/fornecedores` | **MÉDIA** | ✅ financial-fornecedores.spec.ts | useSuppliers | Tabela, Compras |
| `/financeiro/compras` | **ALTA** | ✅ financial-compras.spec.ts | usePurchases | Pedidos, Cotações |
| `/financeiro/estoque` | **MÉDIA** | ✅ financial-estoque.spec.ts | useInventory | Movimentações, Saldo |
| `/financeiro/fiscal` | **ALTA** | ✅ financial-fiscal.spec.ts | useTaxes | Apuração, Guias |
| `/financeiro` (dashboard) | **MÉDIA** | ✅ financial-dashboard.spec.ts | useFinancialDashboard | Charts, KPIs, Resumo |

**Elementos Interativos Identificados:**
- Formulários complexos com múltiplos steps
- Tabelas com ações em massa
- Modais de confirmação (exclusão, pagamento)
- Gráficos e dashboards
- Filtros avançados por período
- Exportação (Excel, PDF)

---

### 3. Módulo Fiscal (7 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/fiscal/nfse` | **CRÍTICA** | ✅ fiscal-nfse.spec.ts | useListarNFSe, useEmitirNFSeNacional, useCancelarNFSeNacional | Tabela, Form Emissão, Cancelamento |
| `/fiscal/certidoes` | **ALTA** | ✅ fiscal-certidoes.spec.ts | useCertidoes | Consulta, Download PDF |
| `/fiscal/esocial` | **CRÍTICA** | ✅ fiscal-esocial.spec.ts | useESocial | Eventos, XML, Transmissão |
| `/fiscal/sped` | **ALTA** | ❌ | useSped | EFD, Geração arquivo |
| `/fiscal/reinf` | **ALTA** | ❌ | useReinf | Eventos, Retenções |
| `/fiscal/dctfweb` | **ALTA** | ❌ | useDCTFWeb | Declaração, Débitos |
| `/fiscal` (dashboard) | **MÉDIA** | ✅ fiscal-dashboard.spec.ts | useFiscalDashboard | Resumo obrigações |

**Elementos Interativos Identificados:**
- Emissão de documentos fiscais
- Transmissão de eventos
- Download de arquivos XML/PDF
- Consulta de status na receita

---

### 4. Módulo Operacional (20 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/operacional/postos` | **CRÍTICA** | ✅ operacional-postos.spec.ts | usePosts, useDeletePost | Tabela, Filtros avançados, Form Modal, Detail Modal, Export |
| `/operacional/escalas` | **CRÍTICA** | ✅ operacional-escalas.spec.ts | useScales, useScaleOperations, usePosts | Grid de escalas, Geração, Aprovação |
| `/operacional/escalas/[id]` | **CRÍTICA** | ✅ operacional-escalas.spec.ts | useScaleDetail | Visualização escala, Edição células |
| `/operacional/escalas/templates` | **MÉDIA** | ✅ operacional-escalas.spec.ts | useScaleTemplates | Templates, CRUD |
| `/operacional/colaboradores` | **CRÍTICA** | ❌ | useEmployees | Tabela, Ficha, Documentos |
| `/operacional/agentes` | **ALTA** | ❌ | useAgents | Tabela, Status, Localização |
| `/operacional/turnos` | **MÉDIA** | ❌ | useShifts | Tabela, Configuração |
| `/operacional/alocacoes` | **ALTA** | ❌ | useAllocations | Mapa, Timeline, Drag-drop |
| `/operacional/ocorrencias` | **CRÍTICA** | ✅ operacional-ocorrencias.spec.ts | useOccurrences | Tabela, Form, Anexos, Workflow |
| `/operacional/rondas` | **MÉDIA** | ❌ | useRounds | Lista, QR Code, Checkpoints |
| `/operacional/comunicados` | **MÉDIA** | ❌ | useCommunications | Lista, Envio, Confirmação leitura |
| `/operacional/notificacoes` | **MÉDIA** | ❌ | useNotifications | Lista, Configurações |
| `/operacional/diaristas` | **ALTA** | ❌ | useDailyWorkers | Cadastro, Escala, Fechamento |
| `/operacional/diaristas/escala` | **ALTA** | ❌ | useDailySchedule | Calendário, Alocação |
| `/operacional/diaristas/fechamento` | **ALTA** | ❌ | useDailyPayment | Cálculo, Pagamento |
| `/operacional/banco-horas` | **ALTA** | ❌ | useTimeBank | Saldo, Extrato, Compensação |
| `/operacional/substituicoes` | **ALTA** | ❌ | useSubstitutions | Solicitação, Aprovação |
| `/operacional/reembolsos` | **MÉDIA** | ❌ | useReimbursements | Solicitação, Anexos |
| `/operacional/disciplinar` | **ALTA** | ❌ | useDisciplinary | Registro, Processo |
| `/operacional/medidas-administrativas` | **ALTA** | ❌ | useAdministrativeMeasures | Registro, Acompanhamento |

**Elementos Interativos Identificados:**
- Calendários interativos
- Kanban de escalas
- Mapas de alocação
- Workflow de aprovação
- Upload de anexos
- QR Code para rondas
- Chat/Comunicação

---

### 5. Módulo Licitações (7 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/licitacoes/editais` | **CRÍTICA** | ✅ bidding-editais-crud.spec.ts | useListarEditais, useRemoverEdital, useMarcarParticipacao, useAlterarStatusEdital, useSincronizarPNCP, useBuscarPNCPMutation | Tabela, Filtros avançados, Form Modal, Integração PNCP |
| `/licitacoes/editais/[id]` | **CRÍTICA** | ❌ | useEditalDetail | Detalhes, Timeline, Documentos |
| `/licitacoes/propostas` | **CRÍTICA** | ✅ bidding-propostas.spec.ts | useProposals | Lista, Editor proposta, Composição de preços |
| `/licitacoes/propostas/[id]` | **CRÍTICA** | ❌ | useProposalDetail | Editor completo, Revisão |
| `/licitacoes/contratos` | **ALTA** | ❌ | useContracts | Lista, Editor, Vigência |
| `/licitacoes/contratos/[id]` | **ALTA** | ❌ | useContractDetail | Cláusulas, Aditivos |
| `/licitacoes/certidoes` | **MÉDIA** | ❌ | useCertidoesLicitacao | Consulta, Validade |
| `/licitacoes/documentos` | **MÉDIA** | ❌ | useDocuments | Gerenciamento, Checklist |
| `/licitacoes` (dashboard) | **MÉDIA** | ✅ bidding-dashboard.spec.ts | useBiddingDashboard | Cards, Gráficos |

**Elementos Interativos Identificados:**
- Editor de propostas rich text
- Timeline de editais
- Upload de documentos
- Calculadora de preços
- Assinatura digital
- Integração PNCP

---

### 6. Módulo Assistente/Bartolo (1 página)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/assistente` | **ALTA** | ✅ 8 testes: bartolo-assistente-page.spec.ts, bartolo-conversation.spec.ts, bartolo-wizard.spec.ts, bartolo-action-flow.spec.ts, bartolo-data-queries.spec.ts, bartolo-error-handling.spec.ts, bartolo-feedback.spec.ts, bartolo-floating-chat.spec.ts | useBartoloStats, useBartoloLearningStats, useBartoloModules, useBartoloWizards | Chat widget, Tabs, Stats cards, Módulos, Wizards |

**Elementos Interativos Identificados:**
- Chat em tempo real
- Streaming de respostas
- Assistentes guiados (wizards)
- Feedback thumbs up/down
- Modo flutuante

---

### 7. Módulo Recrutamento (5 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/recrutamento/vagas` | **ALTA** | ❌ | useJobs | Tabela, Form, Status |
| `/recrutamento/candidatos` | **ALTA** | ❌ | useCandidates | Lista, Filtros, Pipeline |
| `/recrutamento/candidaturas` | **MÉDIA** | ❌ | useApplications | Tabela, Status |
| `/recrutamento/entrevistas` | **MÉDIA** | ❌ | useInterviews | Calendário, Agendamento |
| `/recrutamento` (dashboard) | **BAIXA** | ❌ | - | Resumo, KPIs |

---

### 8. Módulo Documentos (4 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/documentos` | **MÉDIA** | ❌ | useDocuments | Lista, Upload |
| `/documentos/pastas` | **MÉDIA** | ❌ | useFolders | Árvore, CRUD |
| `/documentos/arquivos` | **MÉDIA** | ❌ | useFiles | Grid, Preview |
| `/documentos/kits` | **MÉDIA** | ❌ | useKits | Pacotes de documentos |

---

### 9. Módulo Relatórios (5 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/relatorios` (dashboard) | **MÉDIA** | ❌ | - | Navegação |
| `/relatorios/dashboards` | **ALTA** | ❌ | useDashboards | Builder, Widgets |
| `/relatorios/operacional` | **ALTA** | ❌ | useOperationalReports | Tabela, Filtros, Export |
| `/relatorios/financeiro` | **ALTA** | ❌ | useFinancialReports | Tabela, Gráficos |
| `/relatorios/comercial` | **ALTA** | ❌ | useCommercialReports | Funnel, Pipeline |

---

### 10. Módulo Equipamentos (4 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/equipamentos` | **MÉDIA** | ❌ | useEquipment | Lista, QR Code |
| `/equipamentos/patrimonio` | **ALTA** | ❌ | useAssets | Cadastro, Depreciação |
| `/equipamentos/manutencoes` | **ALTA** | ❌ | useMaintenance | OS, Cronograma |
| `/equipamentos/comodatos` | **MÉDIA** | ❌ | useLoans | Contratos, Controle |

---

### 11. Módulo Integrações (7 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/integracoes` | **BAIXA** | ❌ | - | Dashboard |
| `/integracoes/solides` | **ALTA** | ❌ | useSolides | Config, Sincronização |
| `/integracoes/api-keys` | **MÉDIA** | ❌ | useApiKeys | Gerenciamento |
| `/integracoes/webhooks` | **MÉDIA** | ❌ | useWebhooks | Configuração |
| `/integracoes/sync` | **MÉDIA** | ❌ | useSync | Status, Histórico |
| `/integracoes/logs` | **MÉDIA** | ❌ | useIntegrationLogs | Visualização |
| `/integracoes/conectores` | **MÉDIA** | ❌ | useConnectors | Lista, Config |

---

### 12. Módulo Configurações (5 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/configuracoes` | **BAIXA** | ❌ | - | Menu |
| `/configuracoes/configuracoes-sistema` | **ALTA** | ❌ | useSystemConfig | Form completo |
| `/configuracoes/tenants` | **ALTA** | ❌ | useTenants | Multi-tenant |
| `/configuracoes/feature-flags` | **MÉDIA** | ❌ | useFeatureFlags | Toggle |
| `/configuracoes/templates-notificacao` | **MÉDIA** | ❌ | useNotificationTemplates | Editor |

---

### 13. Módulo Agendador (3 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/agendador` | **MÉDIA** | ❌ | useScheduler | Dashboard |
| `/agendador/tarefas` | **ALTA** | ❌ | useTasks | CRUD, Cron |
| `/agendador/execucoes` | **MÉDIA** | ❌ | useExecutions | Logs, Retry |

---

### 14. Módulo Automações (3 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/automacoes` | **MÉDIA** | ❌ | useAutomations | Dashboard |
| `/automacoes/workflows` | **ALTA** | ❌ | useWorkflows | Builder, Nodes |
| `/automacoes/execucoes` | **MÉDIA** | ❌ | useWorkflowExecutions | Logs, Debug |

---

### 15. Módulo Campo (4 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/campo` | **MÉDIA** | ❌ | useField | Dashboard |
| `/campo/checkin` | **ALTA** | ❌ | useCheckin | Mapa, Geolocalização |
| `/campo/monitoramento` | **ALTA** | ❌ | useMonitoring | Mapa em tempo real |
| `/campo/comunicados` | **MÉDIA** | ❌ | useFieldCommunications | Lista, Envio |

---

### 16. Módulo Saúde Ocupacional (4 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/saude-ocupacional` | **MÉDIA** | ❌ | useOccupationalHealth | Dashboard |
| `/saude-ocupacional/exames` | **ALTA** | ❌ | useExams | Agenda, Controle |
| `/saude-ocupacional/epi` | **ALTA** | ❌ | usePPE | Controle, Estoque |
| `/saude-ocupacional/riscos` | **MÉDIA** | ❌ | useRisks | Matriz, Gestão |

---

### 17. Módulo Segurança (7 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/seguranca` | **MÉDIA** | ❌ | useSecurity | Dashboard |
| `/seguranca/auditoria` | **ALTA** | ❌ | useAudit | Logs, Rastreamento |
| `/seguranca/consentimento` | **ALTA** | ❌ | useConsent | LGPD, Gestão |
| `/seguranca/criptografia` | **MÉDIA** | ❌ | useEncryption | Config |
| `/seguranca/mascaramento` | **MÉDIA** | ❌ | useMasking | Config PII |
| `/seguranca/esquecimento` | **ALTA** | ❌ | useForget | LGPD, Deleção |
| `/seguranca/pia-dpia` | **MÉDIA** | ❌ | useDPIA | Gestão riscos |

---

### 18. Módulo Serviços (4 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/servicos` | **MÉDIA** | ❌ | useServices | Dashboard |
| `/servicos/ordens` | **CRÍTICA** | ❌ | useServiceOrders | Tabela, Workflow |
| `/servicos/agendamentos` | **ALTA** | ❌ | useAppointments | Calendário |
| `/servicos/contratos` | **ALTA** | ❌ | useServiceContracts | Gestão |

---

### 19. Módulo Reembolso (2 páginas)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/reembolso` | **MÉDIA** | ❌ | useReimbursement | Dashboard |
| `/reembolso/aprovacoes` | **ALTA** | ❌ | useReimbursementApprovals | Fila, Aprovação |

---

### 20. Módulo Analytics (1 página)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/analytics` | **ALTA** | ❌ | useAnalytics | Dashboards, Insights |

---

### 21. Módulo OpenClaw (1 página)

| Página | Complexidade | Tem Teste | APIs | Elementos |
|--------|-------------|-----------|------|-----------|
| `/openclaw` | **MÉDIA** | ❌ | useOpenClaw | Admin |

---

## Resumo por Complexidade

| Complexidade | Quantidade | Com Teste | Sem Teste |
|--------------|-----------|-----------|-----------|
| **CRÍTICA** | 22 | 8 | 14 |
| **ALTA** | 38 | 6 | 32 |
| **MÉDIA** | 43 | 0 | 43 |
| **BAIXA** | 14 | 0 | 14 |
| **TOTAL** | 117 | 14 | 103 |

---

## Testes E2E Existentes (33 arquivos)

### Módulos Cobertos

| Módulo | Arquivos de Teste | Cobertura |
|--------|------------------|-----------|
| Login/Auth | login.spec.ts, auth.setup.ts | ✅ Básica |
| Financeiro | 12 arquivos (financial-*.spec.ts) | ✅ Alta |
| Fiscal | 4 arquivos (fiscal-*.spec.ts) | ✅ Média |
| Operacional | 4 arquivos (operacional-*.spec.ts) | ✅ Média |
| Licitações | 3 arquivos (bidding-*.spec.ts) | ✅ Média |
| Bartolo | 8 arquivos (bartolo-*.spec.ts) | ✅ Alta |

### Lista Completa de Testes

```
✅ login.spec.ts                    (6 testes)
✅ auth.setup.ts                    (2 testes)
✅ financial-contas-pagar.spec.ts   (6 testes)
✅ financial-contas-receber.spec.ts (5 testes)
✅ financial-faturamento.spec.ts    (6 testes)
✅ financial-fluxo-caixa.spec.ts    (6 testes)
✅ financial-conciliacao.spec.ts    (5 testes)
✅ financial-contabilidade.spec.ts  (6 testes)
✅ financial-custeio.spec.ts        (6 testes)
✅ financial-dashboard.spec.ts      (6 testes)
✅ financial-clientes.spec.ts       (6 testes)
✅ financial-fornecedores.spec.ts   (6 testes)
✅ financial-compras.spec.ts        (6 testes)
✅ financial-estoque.spec.ts        (6 testes)
✅ financial-fiscal.spec.ts         (6 testes)
✅ fiscal-nfse.spec.ts              (5 testes)
✅ fiscal-certidoes.spec.ts         (5 testes)
✅ fiscal-esocial.spec.ts           (4 testes)
✅ fiscal-dashboard.spec.ts         (7 testes)
✅ operacional-postos.spec.ts       (15 testes)
✅ operacional-escalas.spec.ts      (19 testes)
✅ operacional-ocorrencias.spec.ts  (24 testes)
✅ operacional-fluxo-completo.spec.ts (16 testes)
✅ operacional-health.spec.ts       (3 testes)
✅ bidding-dashboard.spec.ts        (7 testes)
✅ bidding-editais-crud.spec.ts     (6 testes)
✅ bidding-propostas.spec.ts        (14 testes)
✅ bartolo-assistente-page.spec.ts  (8 testes)
✅ bartolo-conversation.spec.ts     (5 testes)
✅ bartolo-wizard.spec.ts           (5 testes)
✅ bartolo-action-flow.spec.ts      (7 testes)
✅ bartolo-data-queries.spec.ts     (5 testes)
✅ bartolo-error-handling.spec.ts   (5 testes)
✅ bartolo-feedback.spec.ts         (5 testes)
✅ bartolo-floating-chat.spec.ts    (7 testes)
```

**Total estimado: ~240 testes E2E implementados**

---

## Matriz de Prioridades

### 🔴 CRÍTICAS (sem teste) - Prioridade 1

| Página | Motivo |
|--------|--------|
| `/crm/clientes` | Core do negócio, cadastro principal |
| `/crm/leads` | Pipeline comercial |
| `/crm/oportunidades` | Gestão de vendas |
| `/crm/propostas` | Fechamento de negócios |
| `/operacional/colaboradores` | Gestão de pessoas |
| `/operacional/agentes` | Força de trabalho |
| `/operacional/alocacoes` | Distribuição operacional |
| `/licitacoes/editais/[id]` | Detalhe de edital |
| `/licitacoes/propostas/[id]` | Editor de proposta |
| `/fiscal/sped` | Obrigação fiscal |
| `/fiscal/reinf` | Obrigação fiscal |
| `/servicos/ordens` | Operação diária |
| `/fiscal/dctfweb` | Obrigação fiscal |
| `/operacional/diaristas` | Mão de obra |

### 🟠 ALTA COMPLEXIDADE (sem teste) - Prioridade 2

| Página | Motivo |
|--------|--------|
| `/financeiro/sped` | Importação/exportação |
| `/operacional/banco-horas` | Cálculo trabalhista |
| `/operacional/substituicoes` | Workflow |
| `/operacional/disciplinar` | Processo disciplinar |
| `/licitacoes/contratos` | Gestão contratual |
| `/licitacoes/contratos/[id]` | Editor contratos |
| `/recrutamento/vagas` | RH |
| `/recrutamento/candidatos` | RH |
| `/campo/checkin` | Geolocalização |
| `/campo/monitoramento` | Tempo real |
| `/relatorios/dashboards` | Builder |
| `/automacoes/workflows` | Workflow builder |
| `/seguranca/auditoria` | Compliance |
| `/seguranca/esquecimento` | LGPD |
| `/saude-ocupacional/exames` | PCMSO |
| `/saude-ocupacional/epi` | PCMSO |
| `/equipamentos/patrimonio` | Ativo fixo |
| `/equipamentos/manutencoes` | Manutenção |

### 🟡 MÉDIA COMPLEXIDADE (sem teste) - Prioridade 3

Todas as 43 páginas de complexidade média.

---

## Estimativa de Testes Necessários

### Cobertura Prioritária (Próximos 30 dias)

| Prioridade | Páginas | Testes E2E por página | Total |
|------------|---------|----------------------|-------|
| P1 - Críticas sem teste | 14 | 8-15 | ~150 |
| P2 - Alta sem teste | 32 | 5-10 | ~220 |
| P3 - Média sem teste | 43 | 3-5 | ~170 |

### Estimativa Detalhada

```
Testes E2E Críticos (P1):     ~150 testes
Testes E2E Alta (P2):         ~220 testes
Testes E2E Média (P3):        ~170 testes
Testes E2E Baixa:             ~40 testes
-------------------------------------------
TOTAL E2E NECESSÁRIOS:        ~580 testes

Testes Unitários (estimativa):
  - Componentes críticos:     ~120 testes
  - Hooks customizados:       ~80 testes
  - Utils/helpers:            ~40 testes
-------------------------------------------
TOTAL UNITÁRIOS:              ~240 testes

GRAND TOTAL:                  ~820 testes
```

### Gap Analysis

| Tipo | Existentes | Necessários | Gap |
|------|-----------|-------------|-----|
| E2E | ~240 | ~580 | +340 |
| Unitários | ~0 | ~240 | +240 |
| **Total** | **~240** | **~820** | **+580** |

---

## APIs por Módulo

### Financeiro
- `usePayables`, `usePayableDashboard`, `useCreatePayable`, `useUpdatePayable`, `useProcessPayment`
- `useReceivables`, `useCreateReceivable`
- `useCashFlow`, `useCashFlowProjection`
- `useConciliation`, `useImportBankStatement`
- `useInvoices`, `useCreateInvoice`, `useCancelInvoice`
- `useAccounting`, `useJournalEntries`, `useFinancialStatements`
- `useCostAllocation`, `useCostCenters`
- `usePurchases`, `usePurchaseOrders`, `useQuotations`
- `useInventory`, `useInventoryMovements`
- `useTaxes`, `useTaxApuracao`, `useTaxGuia`
- `useClients`, `useClientInvoices`
- `useSuppliers`, `useSupplierPurchases`

### Fiscal
- `useListarNFSe`, `useEmitirNFSeNacional`, `useCancelarNFSeNacional`
- `useCertidoes`, `useConsultarCertidao`
- `useESocial`, `useTransmitirESocial`, `useConsultarESocial`
- `useSped`, `useGerarSped`
- `useReinf`, `useTransmitirReinf`
- `useDCTFWeb`, `useDeclararDCTF`
- `useFiscalDashboard`

### Operacional
- `usePosts`, `useCreatePost`, `useUpdatePost`, `useDeletePost`
- `useScales`, `useScaleDetail`, `useGenerateScale`, `useScaleOperations`
- `useEmployees`, `useEmployeeDetail`
- `useAgents`, `useAgentLocation`
- `useShifts`, `useShiftConfig`
- `useAllocations`, `useAllocationMap`
- `useOccurrences`, `useCreateOccurrence`, `useOccurrenceWorkflow`
- `useRounds`, `useRoundCheckpoints`
- `useDailyWorkers`, `useDailySchedule`, `useDailyPayment`
- `useTimeBank`, `useTimeBankStatement`
- `useSubstitutions`, `useSubstitutionApproval`

### CRM
- `useClients`, `useCreateClient`, `useUpdateClient`, `useDeleteClient`
- `useLeads`, `useLeadsStats`, `useCreateLead`, `useUpdateLead`
- `useOpportunities`, `useOpportunityPipeline`
- `useProposals`, `useCreateProposal`, `useApproveProposal`
- `useContacts`

### Licitações
- `useListarEditais`, `useRemoverEdital`, `useMarcarParticipacao`
- `useAlterarStatusEdital`, `useSincronizarPNCP`, `useBuscarPNCPMutation`
- `useEditalDetail`, `useCreateEdital`
- `useProposals`, `useCreateProposal`, `useProposalDetail`
- `useContracts`, `useContractDetail`, `useContractClauses`

### Bartolo (AI)
- `useBartoloStats`, `useBartoloLearningStats`
- `useBartoloModules`, `useBartoloWizards`
- `useBartoloConversation`, `useBartoloSendMessage`
- `useBartoloActions`, `useBartoloDataQuery`

---

## Recomendações

### 1. Priorização de Testes
1. **Começar pelos CRUDs críticos**: Clientes, Contas a Pagar/Receber, Postos, Colaboradores
2. **Focar em workflows de negócio**: Fechamento fiscal, Geração de escala, Aprovação de proposta
3. **Testar integrações**: PNCP, Bancos, NFS-e

### 2. Estratégia de Automação
- Usar Page Object Model para reutilização
- Criar fixtures para dados de teste
- Implementar testes de API para validação rápida
- Configurar CI/CD para execução automática

### 3. Métricas de Sucesso
- Cobertura E2E: 80% das páginas críticas em 60 dias
- Cobertura Unitária: 70% dos componentes em 90 dias
- Tempo de execução: < 15 minutos para suite completa
- Taxa de flaky tests: < 5%

---

## Anexos

### A. Páginas com Testes Existentes

| Página | Arquivo de Teste | Qualidade |
|--------|-----------------|-----------|
| `/login` | login.spec.ts | ⭐⭐⭐ |
| `/financeiro/contas-pagar` | financial-contas-pagar.spec.ts | ⭐⭐ |
| `/financeiro/contas-receber` | financial-contas-receber.spec.ts | ⭐⭐ |
| `/financeiro/faturamento` | financial-faturamento.spec.ts | ⭐⭐ |
| `/financeiro/fluxo-caixa` | financial-fluxo-caixa.spec.ts | ⭐⭐ |
| `/financeiro/conciliacao` | financial-conciliacao.spec.ts | ⭐⭐ |
| `/financeiro/contabilidade` | financial-contabilidade.spec.ts | ⭐⭐ |
| `/financeiro/custeio` | financial-custeio.spec.ts | ⭐⭐ |
| `/financeiro/dashboard` | financial-dashboard.spec.ts | ⭐⭐ |
| `/financeiro/clientes` | financial-clientes.spec.ts | ⭐⭐ |
| `/financeiro/fornecedores` | financial-fornecedores.spec.ts | ⭐⭐ |
| `/financeiro/compras` | financial-compras.spec.ts | ⭐⭐ |
| `/financeiro/estoque` | financial-estoque.spec.ts | ⭐⭐ |
| `/financeiro/fiscal` | financial-fiscal.spec.ts | ⭐⭐ |
| `/fiscal/nfse` | fiscal-nfse.spec.ts | ⭐⭐ |
| `/fiscal/certidoes` | fiscal-certidoes.spec.ts | ⭐⭐ |
| `/fiscal/esocial` | fiscal-esocial.spec.ts | ⭐⭐ |
| `/fiscal/dashboard` | fiscal-dashboard.spec.ts | ⭐⭐ |
| `/operacional/postos` | operacional-postos.spec.ts | ⭐⭐⭐ |
| `/operacional/escalas` | operacional-escalas.spec.ts | ⭐⭐⭐ |
| `/operacional/ocorrencias` | operacional-ocorrencias.spec.ts | ⭐⭐⭐ |
| `/licitacoes/editais` | bidding-editais-crud.spec.ts | ⭐⭐⭐ |
| `/licitacoes/propostas` | bidding-propostas.spec.ts | ⭐⭐⭐ |
| `/licitacoes/dashboard` | bidding-dashboard.spec.ts | ⭐⭐ |
| `/assistente` | 8 arquivos bartolo-*.spec.ts | ⭐⭐⭐ |

### B. Padrões de Páginas Identificados

1. **Padrão Listagem Completa**
   - Tabela com paginação
   - Filtros de busca
   - Filtros de status/tipo
   - Botão "Novo"
   - Ações: Ver, Editar, Excluir
   - Cards de estatísticas
   - Exportação

2. **Padrão CRUD Modal**
   - Lista na tabela
   - Form em modal
   - Confirmação de exclusão
   - Detail em modal ou página

3. **Padrão Dashboard**
   - Cards de KPIs
   - Gráficos
   - Atalhos para ações
   - Lista resumida

4. **Padrão Workflow**
   - Timeline/Kanban
   - Status indicators
   - Ações contextuais por status
   - Aprovações

---

*Documento gerado em: 05/02/2026*
*Versão: 1.0*
*Total de páginas analisadas: 117*
