# Arquitetura - Conecta PRO Frontend

## Visao Geral

O frontend do Conecta PRO segue uma arquitetura modular baseada em **Feature-Sliced Design** adaptada, com separacao clara entre o nucleo da aplicacao (`core`) e os modulos de dominio (`modules`).

```
┌─────────────────────────────────────────────────────────────────────┐
│                           App (React 19)                             │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Dashboard  │  │  Compliance │  │     CRM     │  │ Operations  │ │
│  │   Module    │  │   Module    │  │   Module    │  │   Module    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                         Core Layer                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   Auth   │  │   API    │  │  Stores  │  │Components│             │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │
├─────────────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                              │
│  React Query │ Zustand │ React Router │ Axios │ Tailwind            │
└─────────────────────────────────────────────────────────────────────┘
```

## Estrutura de Pastas Explicada

### `/src/core` - Nucleo da Aplicacao

Contem tudo que e compartilhado e reutilizavel entre modulos.

#### `/core/api`
```typescript
// client.ts - Instancia Axios configurada
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

// endpoints.ts - Centralizacao de URLs
export const ENDPOINTS = {
  AUTH: { LOGIN: '/auth/login', REFRESH: '/auth/refresh' },
  USERS: { LIST: '/users', DETAIL: (id: string) => `/users/${id}` },
  // ...
};

// interceptors.ts - Tratamento global
// - Adiciona token automaticamente
// - Refresh token transparente
// - Tratamento de erros 401/403
```

#### `/core/auth`
```typescript
// AuthProvider.tsx - Contexto de autenticacao
// - Gerencia estado do usuario logado
// - Persiste sessao no localStorage
// - Expoe metodos login/logout

// ProtectedRoute.tsx - Guard de rotas
// - Verifica autenticacao
// - Redireciona para login se necessario
// - Verifica permissoes por rota
```

#### `/core/components`
Componentes UI genericos organizados por categoria:

| Pasta | Componentes | Descricao |
|-------|-------------|-----------|
| `/ui` | Button, Card, Modal, Input, Badge, Avatar, Spinner | Componentes atomicos |
| `/feedback` | Toast, Skeleton, ErrorBoundary, EmptyState, ConfirmDialog | Feedback ao usuario |
| `/forms` | FormField, Select, DatePicker, Textarea, Checkbox | Componentes de formulario |

#### `/core/stores`
```typescript
// Zustand stores para estado global

// authStore.ts - Estado de autenticacao
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials: LoginDTO) => Promise<void>;
  logout: () => void;
}

// uiStore.ts - Estado da interface
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
}

// toastStore.ts - Sistema de notificacoes
interface ToastState {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}
```

#### `/core/hooks`
```typescript
// useAuth.ts - Acesso ao contexto de auth
const { user, login, logout, isAuthenticated } = useAuth();

// useApi.ts - Wrapper para React Query
const { data, isLoading, error } = useApi('/users', options);

// useToast.ts - Notificacoes
const { success, error, warning, info } = useToast();

// usePermissions.ts - Verificacao de permissoes
const { can, canAny, canAll } = usePermissions();
```

### `/src/modules` - Modulos de Dominio

Cada modulo e auto-contido com sua propria estrutura:

```
modules/
└── [module-name]/
    ├── components/       # Componentes especificos do modulo
    ├── hooks/           # Hooks do modulo (queries, mutations)
    ├── types/           # Tipos TypeScript
    ├── utils/           # Utilitarios especificos
    ├── index.ts         # Barrel export
    └── [Module]Dashboard.tsx  # Componente principal
```

#### Exemplo: Modulo Compliance
```
compliance/
├── audit/
│   ├── components/
│   │   ├── ComplianceScoreCard.tsx
│   │   ├── AnomalyCard.tsx
│   │   ├── RuleCard.tsx
│   │   └── ExecutionList.tsx
│   ├── hooks/
│   │   └── useAudit.ts
│   ├── types/
│   │   └── audit.types.ts
│   └── AuditDashboard.tsx
├── lgpd/
├── government/
└── bidding/
```

### `/src/pages`

Paginas da aplicacao que compoem os modulos:

```typescript
// DashboardPage.tsx
import { ExecutiveDashboard } from '@modules/dashboards/executive';

export default function DashboardPage() {
  return <ExecutiveDashboard />;
}
```

## Padroes Utilizados

### 1. Component Composition

Componentes complexos sao compostos de partes menores:

```typescript
// Card com subcomponentes
<Card>
  <CardHeader>
    <CardTitle>Titulo</CardTitle>
  </CardHeader>
  <CardContent>
    Conteudo...
  </CardContent>
</Card>
```

### 2. Custom Hooks para Logica

Separacao de logica de negocios da UI:

```typescript
// hooks/useAudit.ts
export function useAudit() {
  const query = useQuery({
    queryKey: ['audit', 'executions'],
    queryFn: () => api.get('/audit/executions'),
  });

  const runAudit = useMutation({
    mutationFn: (ruleId: string) => api.post(`/audit/run/${ruleId}`),
    onSuccess: () => queryClient.invalidateQueries(['audit']),
  });

  return { executions: query.data, isLoading: query.isLoading, runAudit };
}

// components/AuditDashboard.tsx
function AuditDashboard() {
  const { executions, isLoading, runAudit } = useAudit();
  // Apenas renderizacao
}
```

### 3. Render Props / Children as Function

Para componentes altamente reutilizaveis:

```typescript
<DataTable
  data={users}
  columns={columns}
  renderRow={(user) => <UserRow user={user} />}
/>
```

### 4. Compound Components

Para APIs flexiveis:

```typescript
<Modal>
  <Modal.Trigger>Abrir</Modal.Trigger>
  <Modal.Content>
    <Modal.Header>Titulo</Modal.Header>
    <Modal.Body>Conteudo</Modal.Body>
    <Modal.Footer>
      <Modal.Close>Fechar</Modal.Close>
    </Modal.Footer>
  </Modal.Content>
</Modal>
```

## Fluxo de Dados

### React Query para Server State

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Component  │────>│ React Query │────>│   Backend   │
│             │<────│   Cache     │<────│     API     │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          ▼
                    ┌───────────┐
                    │ Automatic │
                    │  Refetch  │
                    │  & Cache  │
                    └───────────┘
```

**Configuracao padrao:**
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,    // 5 minutos
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

### Zustand para Client State

```
┌─────────────┐     ┌─────────────┐
│  Component  │────>│   Zustand   │
│             │<────│    Store    │
└─────────────┘     └─────────────┘
       │                  │
       │                  ▼
       │           ┌─────────────┐
       └──────────>│ Subscriber  │
                   │ Components  │
                   └─────────────┘
```

**Uso:**
```typescript
// Store
const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));

// Component
function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore();
}
```

## Roteamento

### Estrutura de Rotas

```typescript
// React Router v7 com lazy loading
const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    element: <ProtectedRoute />,  // Guard
    children: [
      {
        element: <MainLayout />,   // Layout
        children: [
          { path: '/dashboard', element: <LazyPage component={DashboardPage} /> },
          { path: '/audit', element: <LazyPage component={AuditPage} /> },
          // ...
        ],
      },
    ],
  },
]);
```

### Lazy Loading

Todas as paginas sao carregadas sob demanda:

```typescript
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));

function LazyPage({ component: Component }) {
  return (
    <Suspense fallback={<PageLoader />}>
      <Component />
    </Suspense>
  );
}
```

## Estilizacao

### Tailwind CSS

```typescript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'conecta-laranja': '#FF6B35',
        'conecta-escuro': '#0A2540',
        'conecta-medio': '#1A3550',
      },
      boxShadow: {
        'card': '0 2px 4px rgba(0,0,0,0.08)',
      },
    },
  },
};
```

### Class Variance Authority (CVA)

Para variantes de componentes:

```typescript
const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium',
  {
    variants: {
      variant: {
        primary: 'bg-conecta-laranja text-white hover:bg-orange-600',
        secondary: 'bg-conecta-escuro text-white hover:bg-conecta-medio',
        outline: 'border-2 border-conecta-escuro text-conecta-escuro',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);
```

### Tailwind Merge

Evita conflitos de classes:

```typescript
import { twMerge } from 'tailwind-merge';
import { clsx } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Uso
<div className={cn('p-4 text-sm', className)} />
```

## Integracao com API

### Estrutura de Requisicoes

```typescript
// 1. Definir tipos
interface User {
  id: string;
  name: string;
  email: string;
}

// 2. Criar hook com React Query
function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const { data } = await api.get<User[]>('/users');
      return data;
    },
  });
}

// 3. Usar no componente
function UserList() {
  const { data: users, isLoading, error } = useUsers();

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;

  return users.map(user => <UserCard key={user.id} user={user} />);
}
```

### Mutations

```typescript
function useCreateUser() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: (data: CreateUserDTO) => api.post('/users', data),
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
      toast.success('Usuario criado com sucesso!');
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });
}
```

## Diagrama de Modulos

```
                    ┌─────────────────────────────────────┐
                    │             DASHBOARDS              │
                    │  Executive │ Analytics │ Realtime   │
                    └─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   COMPLIANCE  │         │      CRM      │         │  OPERATIONS   │
├───────────────┤         ├───────────────┤         ├───────────────┤
│ - Audit       │         │ - Contacts    │         │ - Postos      │
│ - LGPD        │         │ - Deals       │         │ - Schedules   │
│ - Government  │         │ - Proposals   │         │ - Substitutions│
│ - Bidding     │         │ - Marketplace │         └───────────────┘
└───────────────┘         └───────────────┘                 │
                                                            ▼
                                                  ┌───────────────┐
                                                  │ FIELD SERVICE │
                                                  ├───────────────┤
                                                  │ - Orders      │
                                                  │ - Technicians │
                                                  └───────────────┘
                                                            │
                                                            ▼
                          ┌───────────────────────────────────────┐
                          │              FACILITIES               │
                          ├───────────────────────────────────────┤
                          │ Equipment │ IoT Sensors │ Maintenance │
                          └───────────────────────────────────────┘
```

## Performance

### Code Splitting

O Vite automaticamente divide o codigo em chunks:

```javascript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['react', 'react-dom', 'react-router-dom'],
        ui: ['framer-motion', '@headlessui/react', 'lucide-react'],
        data: ['@tanstack/react-query', 'zustand', 'axios'],
      },
    },
  },
},
```

### Lazy Loading de Rotas

Cada pagina e carregada apenas quando necessario:

```typescript
const AuditPage = lazy(() => import('@/pages/AuditPage'));
```

### Memoizacao

```typescript
// useMemo para calculos caros
const filteredData = useMemo(() =>
  data.filter(item => item.status === filter),
  [data, filter]
);

// useCallback para funcoes passadas como props
const handleClick = useCallback(() => {
  onSelect(item.id);
}, [item.id, onSelect]);

// memo para componentes puros
const UserCard = memo(function UserCard({ user }) {
  return <Card>{user.name}</Card>;
});
```

## Tratamento de Erros

### ErrorBoundary Global

```typescript
function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <RouterProvider router={router} />
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
```

### Erros de API

```typescript
// interceptors.ts
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Tentar refresh token
      // Se falhar, fazer logout
    }

    if (error.response?.status === 403) {
      // Redirecionar para pagina de acesso negado
    }

    return Promise.reject(error);
  }
);
```

## Testes (Estrutura Recomendada)

```
src/
├── __tests__/
│   ├── components/
│   │   └── Button.test.tsx
│   ├── hooks/
│   │   └── useAuth.test.ts
│   └── pages/
│       └── DashboardPage.test.tsx
├── __mocks__/
│   └── api.ts
└── test-utils/
    └── render.tsx
```

---

**Proxima leitura:** [Componentes](./COMPONENTS.md)
