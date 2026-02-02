# Módulo de Propostas - Licitações

Módulo completo para gestão de propostas comerciais de licitações.

## Estrutura de Arquivos

```
src/
├── app/modulos/licitacoes/propostas/
│   ├── page.tsx                    # Lista de propostas
│   ├── [id]/
│   │   └── page.tsx                # Detalhe de proposta individual
│   └── README.md
│
├── components/licitacoes/
│   ├── ProposalStatusBadge.tsx     # Badge de status com ícones
│   ├── ProposalFilters.tsx         # Filtros de busca
│   ├── ProposalFormModal.tsx       # Modal de criação/edição
│   ├── ProposalItemsManager.tsx    # Gerenciador de itens
│   ├── SubmitProposalDialog.tsx    # Diálogo de submissão
│   └── index.ts                    # Exports centralizados
│
├── hooks/bidding/
│   └── useProposals.ts             # React Query hooks
│
└── services/bidding/
    └── proposals.service.ts         # API service layer
```

## Páginas

### Lista de Propostas (`/propostas/page.tsx`)

**Funcionalidades:**
- Tabela completa com todas as propostas
- Colunas: Número, Edital, Razão Social, Valor Proposto, Data Submissão, Status, Ações
- Filtros por: Status, Edital, Data início/fim, Valor min/max
- Paginação server-side
- Ações disponíveis:
  - Ver detalhes
  - Submeter proposta
  - Editar proposta
  - Remover proposta (apenas rascunho)
- Loading e empty states
- Controle de permissões por status

**Regras de negócio:**
- Apenas propostas em rascunho podem ser removidas
- Submissão disponível para status: rascunho, em_analise
- Edição disponível para: rascunho, em_analise, rejeitada

### Detalhe de Proposta (`/propostas/[id]/page.tsx`)

**Funcionalidades:**
- Header com informações principais e status
- Cards de resumo: Valor Global, Prazo Entrega, Validade, Status
- 4 Abas principais:

#### Aba 1: Dados Gerais
- Informações do Edital
- Dados da Empresa (CNPJ, Razão Social)
- Alteração de status (dropdown)
- Observações técnicas e comerciais

#### Aba 2: Itens da Proposta
- Tabela de itens com: Descrição, Unidade, Quantidade, Valor Unit., Valor Total
- Adicionar/Editar/Remover itens
- Cálculo automático de valor total
- Validação de campos obrigatórios

#### Aba 3: Documentos
- Placeholder para integração futura com módulo de documentos

#### Aba 4: Histórico
- Timeline de mudanças de status
- Data de criação e última atualização

**Ações disponíveis:**
- Submeter proposta
- Editar dados gerais
- Atualizar status
- Refresh dos dados

## Componentes

### ProposalStatusBadge

Badge colorido com ícone para status de proposta.

**10 Status disponíveis:**
- `rascunho` - Cinza (FileText)
- `em_analise` - Azul (Eye)
- `aprovada` - Verde (CheckCircle)
- `rejeitada` - Vermelho (XCircle)
- `submetida` - Azul (Send)
- `aguardando_documentacao` - Amarelo (AlertTriangle)
- `em_negociacao` - Azul (Clock)
- `vencedora` - Verde (TrendingUp)
- `perdida` - Cinza (Archive)
- `cancelada` - Vermelho (Ban)

**Uso:**
```tsx
import { ProposalStatusBadge } from '@/components/licitacoes';

<ProposalStatusBadge status="aprovada" />
```

### ProposalFilters

Card de filtros com múltiplas opções de busca.

**Campos:**
- Status (select)
- Data Início (date)
- Data Fim (date)
- Valor Mínimo (number)
- Valor Máximo (number)

**Uso:**
```tsx
import { ProposalFilters } from '@/components/licitacoes';

const [filters, setFilters] = useState({});

<ProposalFilters
  filters={filters}
  onFiltersChange={setFilters}
  onClearFilters={() => setFilters({})}
/>
```

### ProposalFormModal

Modal completo para criar/editar proposta.

**Seções do formulário:**
1. Informações do Edital (tender_id)
2. Dados da Empresa (CNPJ com máscara, Razão Social)
3. Dados da Proposta (Número, Valor, Prazos, Status)
4. Observações (Técnicas e Comerciais)

**Validações:**
- Edital obrigatório
- CNPJ obrigatório com formatação
- Razão Social obrigatória
- Valor Global > 0

**Uso:**
```tsx
import { ProposalFormModal } from '@/components/licitacoes';

<ProposalFormModal
  isOpen={isOpen}
  onClose={onClose}
  proposal={proposal} // null para criar nova
  onSubmit={handleSubmit}
  isLoading={isLoading}
/>
```

### ProposalItemsManager

Gerenciador completo de itens da proposta com tabela e modals.

**Funcionalidades:**
- Tabela de itens com colunas formatadas
- Adicionar novo item (modal)
- Editar item existente (modal)
- Remover item (confirmação)
- Cálculo automático de valor total do item
- Cálculo automático de valor global da proposta
- Empty state quando sem itens

**Campos do item:**
- Descrição (obrigatório)
- Unidade de medida (default: UN)
- Quantidade (obrigatório, > 0)
- Valor unitário (obrigatório, > 0)
- Valor total (calculado automaticamente)

**Uso:**
```tsx
import { ProposalItemsManager } from '@/components/licitacoes';

<ProposalItemsManager
  items={items}
  isLoading={isLoading}
  onAddItem={handleAddItem}
  onUpdateItem={handleUpdateItem}
  onRemoveItem={handleRemoveItem}
/>
```

### SubmitProposalDialog

Dialog de confirmação para submissão de proposta.

**Funcionalidades:**
- Confirmação com número da proposta
- Campo opcional para observações
- Loading state durante submissão
- Texto explicativo sobre a ação

**Uso:**
```tsx
import { SubmitProposalDialog } from '@/components/licitacoes';

<SubmitProposalDialog
  isOpen={isOpen}
  onClose={onClose}
  onConfirm={handleConfirm}
  proposalNumber="PROP-2024-001"
  isSubmitting={isSubmitting}
/>
```

## Hooks Disponíveis

Todos os hooks estão em `@/hooks/bidding/useProposals`:

### Queries
- `useListarPropostas(params?)` - Lista com filtros e paginação
- `useBuscarProposta(proposalId)` - Busca por ID
- `useListarPropostasPorEdital(tenderId, params?)` - Filtra por edital
- `useListarPropostasEmAndamento(params?)` - Apenas em andamento
- `useListarPropostasAprovadas(params?)` - Apenas aprovadas
- `useProposalsDashboard(params?)` - Métricas e estatísticas
- `useListarItens(proposalId)` - Itens de uma proposta

### Mutations
- `useCriarProposta()` - Cria nova proposta
- `useAtualizarProposta()` - Atualiza proposta existente
- `useRemoverProposta()` - Remove proposta (soft delete)
- `useSubmeterProposta()` - Submete para análise
- `useAlterarStatusProposta()` - Altera status
- `useAdicionarItem()` - Adiciona item à proposta
- `useAtualizarItem()` - Atualiza item existente
- `useRemoverItem()` - Remove item da proposta

**Exemplo de uso:**
```tsx
const { data, isLoading } = useListarPropostas({ status: 'aprovada' });
const criarProposta = useCriarProposta();

await criarProposta.mutateAsync({
  tender_id: '123',
  cnpj: '00.000.000/0000-00',
  razao_social: 'Empresa Exemplo',
  valor_global: 100000,
});
```

## Service Layer

`@/services/bidding/proposals.service`

**Endpoints principais:**
- `GET /api/v1/bidding/proposals/` - Listar com filtros
- `GET /api/v1/bidding/proposals/:id` - Buscar por ID
- `POST /api/v1/bidding/proposals/` - Criar
- `PUT /api/v1/bidding/proposals/:id` - Atualizar
- `DELETE /api/v1/bidding/proposals/:id` - Remover
- `POST /api/v1/bidding/proposals/:id/submeter` - Submeter
- `POST /api/v1/bidding/proposals/:id/status` - Alterar status
- `GET /api/v1/bidding/proposals/tender/:tenderId` - Por edital
- `GET /api/v1/bidding/proposals/em-andamento` - Em andamento
- `GET /api/v1/bidding/proposals/aprovadas` - Aprovadas
- `GET /api/v1/bidding/proposals/dashboard` - Dashboard

**Endpoints de itens:**
- `GET /api/v1/bidding/proposals/:id/items` - Listar itens
- `POST /api/v1/bidding/proposals/:id/items` - Adicionar item
- `PUT /api/v1/bidding/proposals/:id/items/:itemId` - Atualizar item
- `DELETE /api/v1/bidding/proposals/:id/items/:itemId` - Remover item

## Tipos TypeScript

```typescript
interface BiddingProposalCreate {
  tender_id: string;
  cnpj: string;
  razao_social: string;
  valor_global: number;
  prazo_entrega?: number;
  proposta_tecnica?: string;
}

interface ProposalItemCreate {
  item_edital_id?: string;
  descricao: string;
  quantidade: number;
  valor_unitario: number;
}

type ProposalStatus =
  | 'rascunho'
  | 'em_analise'
  | 'aprovada'
  | 'rejeitada'
  | 'submetida'
  | 'aguardando_documentacao'
  | 'em_negociacao'
  | 'vencedora'
  | 'perdida'
  | 'cancelada';
```

## Próximas Melhorias

- [ ] Integração com módulo de documentos (anexos)
- [ ] Upload de arquivos da proposta técnica
- [ ] Notificações de mudança de status
- [ ] Exportação para PDF
- [ ] Histórico completo de alterações
- [ ] Comentários e discussões
- [ ] Aprovação em múltiplas etapas
- [ ] Integração com workflow de aprovação
- [ ] Relatórios e analytics

## Testes

Para testar o módulo:

1. Acesse `/modulos/licitacoes/propostas`
2. Crie uma nova proposta
3. Adicione itens à proposta
4. Submeta a proposta
5. Altere o status
6. Verifique filtros e paginação

## Dependências

- Next.js 16
- React 19
- React Query (TanStack Query)
- Lucide React (ícones)
- Tailwind CSS
- Shadcn UI components
- Radix UI primitives
