# Conecta PRO - Frontend

## Projeto
Sistema ERP completo para gestão empresarial com foco em vigilância e segurança patrimonial.

**Empresa:** JORDAN SANTOS DE JESUS LTDA
**CNPJ:** 35.710.481/0001-03
**Setor:** Vigilância e Segurança

## Stack Técnico

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| React | 19.2 | Framework UI |
| TypeScript | 5.x | Tipagem estática |
| Vite | 7.x | Build tool |
| TailwindCSS | 4.x | Estilização |
| TanStack Query | 5.x | Data fetching |
| Zustand | 5.x | State management |
| React Router | 7.x | Roteamento |
| React Hook Form | 7.x | Formulários |
| Zod | 4.x | Validação |
| Framer Motion | 12.x | Animações |
| Recharts | 3.x | Gráficos |
| Lucide React | 0.562 | Ícones |

## Estrutura do Projeto

```
frontend/src/
├── app/                    # App principal e providers
├── core/                   # Funcionalidades core
│   ├── api/               # Cliente API base
│   ├── auth/              # Autenticação
│   ├── components/        # Componentes core
│   ├── hooks/             # Hooks globais
│   ├── navigation/        # Rotas e navegação
│   ├── stores/            # Zustand stores
│   ├── types/             # Tipos globais
│   └── utils/             # Utilitários
├── design-system/         # Design system
│   ├── components/        # Componentes UI reutilizáveis
│   ├── hooks/             # Hooks do design system
│   └── patterns/          # Padrões de composição
├── features/              # Módulos por domínio
│   ├── ai/               # IA e automação
│   ├── auth/             # Login, registro, recuperação
│   ├── bidding/          # Licitações
│   ├── campo/            # Serviços de campo
│   ├── clients/          # Gestão de clientes
│   ├── compliance/       # LGPD, compliance
│   ├── crm/              # CRM completo
│   ├── dashboard/        # Dashboards
│   ├── equipment/        # Equipamentos
│   ├── extras/           # Funcionalidades extras
│   ├── financial/        # Módulo financeiro
│   ├── ged/              # Gestão eletrônica docs
│   ├── health-safety/    # Saúde e segurança
│   ├── hr/               # Recursos humanos
│   ├── integrations/     # Integrações externas
│   ├── notifications/    # Notificações
│   ├── operations/       # Operações
│   ├── reports/          # Relatórios
│   ├── services/         # Serviços
│   └── settings/         # Configurações
├── layouts/               # Layouts da aplicação
├── modules/               # Módulos legados (migrar)
├── pages/                 # Páginas standalone
└── shared/                # Código compartilhado
```

## Padrões de Código

### Estrutura de Feature Module

```
features/[modulo]/
├── api/
│   ├── endpoints.ts      # Definição de endpoints
│   ├── services.ts       # Serviços de API
│   └── index.ts          # Exports
├── hooks/
│   └── index.ts          # React Query hooks
├── types/
│   └── index.ts          # TypeScript types
├── components/           # Componentes específicos
└── [Pagina]Page.tsx      # Páginas do módulo
```

### Exemplo de Hook com React Query

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { leadService } from './api/services';

export function useLeads(params?: LeadListParams) {
  return useQuery({
    queryKey: ['leads', params],
    queryFn: () => leadService.list(params),
  });
}

export function useCreateLead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: leadService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}
```

### Componente de Página

```typescript
'use client';

import { useState } from 'react';
import { MainLayout } from '@/layouts/MainLayout';
import { Card, CardHeader, CardBody, Button } from '@/design-system/components';
import { useLeads } from './hooks';

export function LeadsPage() {
  const { data, isLoading } = useLeads();

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-display font-bold text-text-primary">
            Leads
          </h1>
          <Button variant="primary">Novo Lead</Button>
        </div>

        {/* Content */}
        <Card>
          <CardHeader title="Lista de Leads" />
          <CardBody>
            {/* ... */}
          </CardBody>
        </Card>
      </div>
    </MainLayout>
  );
}

export default LeadsPage;
```

## Design System - Componentes

### Componentes Disponíveis

| Componente | Arquivo | Uso |
|------------|---------|-----|
| Button | `Button.tsx` | Botões com variantes |
| Input | `Input.tsx` | Campos de texto |
| Card | `Card.tsx` | Containers |
| Badge | `Badge.tsx` | Tags e status |
| Modal | `Modal.tsx` | Diálogos |
| DataTable | `Table.tsx` | Tabelas de dados |
| StatCard | `StatCard.tsx` | Cards de estatísticas |
| Tabs | `Tabs.tsx` | Navegação por abas |
| Select | `Select.tsx` | Dropdowns |
| Dropdown | `Dropdown.tsx` | Menus dropdown |
| EmptyState | `EmptyState.tsx` | Estados vazios |
| Progress | `Progress.tsx` | Barras de progresso |
| Textarea | `Textarea.tsx` | Campos multiline |
| Tooltip | `Tooltip.tsx` | Tooltips |

### Variantes de Button

```typescript
<Button variant="primary">Primário</Button>
<Button variant="secondary">Secundário</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="danger">Perigo</Button>
<Button variant="success">Sucesso</Button>
<Button variant="warning">Alerta</Button>
```

### Variantes de Badge

```typescript
<Badge variant="primary">Primário</Badge>
<Badge variant="success">Sucesso</Badge>
<Badge variant="warning">Alerta</Badge>
<Badge variant="danger">Erro</Badge>
<Badge variant="info">Info</Badge>
<Badge variant="neutral">Neutro</Badge>
```

## Tokens de Design

### Cores (CSS Variables)

```css
/* Background */
--bg-primary: #0a0a0f;
--bg-secondary: #12121a;
--bg-tertiary: #1a1a24;

/* Text */
--text-primary: #ffffff;
--text-secondary: #a1a1aa;
--text-muted: #71717a;

/* Accent */
--accent-primary: #6366f1;
--accent-secondary: #8b5cf6;

/* Status */
--success: #22c55e;
--warning: #f59e0b;
--danger: #ef4444;
--info: #3b82f6;

/* Border */
--border-default: #27272a;
```

### Classes Tailwind Customizadas

```typescript
// Texto
className="text-text-primary"
className="text-text-secondary"
className="text-text-muted"

// Background
className="bg-bg-primary"
className="bg-bg-secondary"
className="bg-bg-tertiary"

// Bordas
className="border-border-default"

// Cores de destaque
className="text-accent-primary"
className="bg-accent-primary/10"
```

## API Integration

### Configuração Base

```typescript
// core/api/client.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Estrutura de Serviço

```typescript
// features/crm/api/services.ts
export const leadService = {
  list: async (params?: LeadListParams) => {
    const response = await apiClient.get<PaginatedResponse<Lead>>('/crm/leads', { params });
    return response.data;
  },

  getById: async (id: string) => {
    const response = await apiClient.get<Lead>(`/crm/leads/${id}`);
    return response.data;
  },

  create: async (data: LeadCreate) => {
    const response = await apiClient.post<Lead>('/crm/leads', data);
    return response.data;
  },

  update: async (id: string, data: LeadUpdate) => {
    const response = await apiClient.put<Lead>(`/crm/leads/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await apiClient.delete(`/crm/leads/${id}`);
  },
};
```

## Módulos Implementados

### CRM (100%)
- Dashboard CRM
- Leads (CRUD completo)
- Oportunidades
- Propostas (com timeline de atividades)
- Contratos
- Comissões

### Financeiro (100%)
- Dashboard Financeiro
- Contas a Pagar
- Contas a Receber
- Fluxo de Caixa
- Banking (contas bancárias)
- Clientes/Fornecedores

### RH (100%)
- Dashboard RH
- Colaboradores
- Folha de Pagamento
- Integração REP (ponto eletrônico)
- Férias e Licenças
- Benefícios

### Operações (100%)
- Dashboard Operações
- Escalas
- Substituições (implementado)
- Banco de Horas

### Autenticação (100%)
- Login
- Registro (multi-step)
- Recuperação de Senha
- Perfil do Usuário

### Configurações (100%)
- Feature Flags (toggle, edit, delete)
- Tenants
- Templates de Config

### Notificações (100%)
- Notificações Inteligentes (play/pause)
- Push Notifications
- Templates
- Canais

## Comandos Úteis

```bash
# Desenvolvimento
cd /opt/conecta-pro/frontend
npm run dev

# Build de produção
npm run build

# Preview do build
npm run preview

# Lint
npm run lint

# Verificar tipos
npx tsc --noEmit
```

## Pente Fino - Correções Realizadas (16/01/2026)

### PlaceholderPage Substituídas

| Rota | Página Criada | Status |
|------|---------------|--------|
| `/register` | RegisterPage | ✅ |
| `/forgot-password` | ForgotPasswordPage | ✅ |
| `/help` | HelpPage | ✅ |
| `/profile` | ProfilePage | ✅ Conectada |
| `/ged/search` | GEDSearchPage | ✅ Conectada |

### Handlers Vazios Corrigidos

| Arquivo | Handler | Implementação |
|---------|---------|---------------|
| FeatureFlagsPage | Toggle | `handleToggleFlag()` |
| FeatureFlagsPage | Edit | `handleEditFlag()` |
| FeatureFlagsPage | Delete | `handleDeleteFlag()` |
| IntelligentNotificationsPage | Play/Pause | `handleToggleCampaign()` |
| REPIntegrationPage | Sincronizar Todos | `handleSyncAll()` |

### Seções "Em Desenvolvimento" Implementadas

| Arquivo | Seção | Implementação |
|---------|-------|---------------|
| OperationsDashboard | Tab Substituições | Tabela completa com mock data |
| ProposalsPage | Tab Atividades | Timeline com histórico |

## Próximos Passos

1. [ ] Integrar APIs reais nos módulos CRM e Financeiro
2. [ ] Implementar autenticação real com JWT
3. [ ] Adicionar testes unitários com Vitest
4. [ ] Implementar PWA (offline support)
5. [ ] Adicionar i18n para internacionalização

---
*Última atualização: 16/01/2026*
