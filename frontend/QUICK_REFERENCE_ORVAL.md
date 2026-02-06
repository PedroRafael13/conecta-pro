# QUICK REFERENCE: HOOKS ORVAL

**Referência rápida para uso de hooks Orval no Conecta Plus**

---

## 🎯 CONVENÇÕES DE NOMENCLATURA

### Hooks Orval (gerados automaticamente):

```
use<Action><Resource>ApiV1<Module><Path><Method>
```

**Exemplos:**
- `useListClientsApiV1ClientsClientsGet` → GET /api/v1/clients/clients
- `useCreateClientApiV1ClientsClientsPost` → POST /api/v1/clients/clients
- `useUpdateClientApiV1ClientsClientsClientIdPut` → PUT /api/v1/clients/clients/{client_id}
- `useDeleteClientApiV1ClientsClientsClientIdDelete` → DELETE /api/v1/clients/clients/{client_id}

---

## 📁 ESTRUTURA DE ARQUIVOS

```
src/
├── types/generated/           # Hooks Orval gerados
│   ├── clients/
│   │   ├── clients-cadastro/
│   │   │   └── clients-cadastro.ts  # Hooks de clientes
│   │   └── ...
│   ├── financial/
│   ├── notifications/
│   └── ...
│
├── hooks/                     # Hooks custom (wrapper dos Orval)
│   ├── clients/
│   │   └── useClients.ts
│   ├── notifications/
│   │   └── useNotifications.ts
│   └── ...
│
└── services/                  # Services manuais (deprecados)
    └── ...
```

---

## 🔧 PADRÕES DE USO

### 1. QUERY (GET) - Buscar dados

```typescript
import { useListItemsApiV1ItemsGet } from '@/types/generated/module/module';

function MyComponent() {
  const {
    data,           // Dados retornados
    isLoading,      // Loading state
    error,          // Error state
    refetch,        // Função para recarregar
    isFetching,     // Fetching state (background)
  } = useListItemsApiV1ItemsGet({
    skip: 0,
    limit: 50,
    status: 'active',
  });

  if (isLoading) return <Spinner />;
  if (error) return <Error error={error} />;

  return <div>{data?.items.map(...)}</div>;
}
```

### 2. MUTATION (POST/PUT/DELETE) - Modificar dados

```typescript
import { useCreateItemApiV1ItemsPost } from '@/types/generated/module/module';

function MyComponent() {
  const createMutation = useCreateItemApiV1ItemsPost();

  const handleCreate = async (formData) => {
    try {
      const result = await createMutation.mutateAsync({
        data: {
          name: formData.name,
          description: formData.description,
        },
      });

      console.log('Created:', result);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <button
      onClick={() => handleCreate({ name: 'Test', description: 'Desc' })}
      disabled={createMutation.isLoading}
    >
      {createMutation.isLoading ? 'Criando...' : 'Criar'}
    </button>
  );
}
```

### 3. MUTATION COM INVALIDAÇÃO DE CACHE

```typescript
import { useQueryClient } from '@tanstack/react-query';
import {
  useListItemsApiV1ItemsGet,
  useCreateItemApiV1ItemsPost,
} from '@/types/generated/module/module';

function MyComponent() {
  const queryClient = useQueryClient();

  // Query
  const { data, refetch } = useListItemsApiV1ItemsGet({ skip: 0, limit: 50 });

  // Mutation
  const createMutation = useCreateItemApiV1ItemsPost();

  const handleCreate = async (formData) => {
    await createMutation.mutateAsync(
      { data: formData },
      {
        onSuccess: () => {
          // Opção 1: Refetch direto
          refetch();

          // Opção 2: Invalidar cache (melhor para múltiplas queries)
          queryClient.invalidateQueries({
            queryKey: ['items'], // Chave da query
          });
        },
        onError: (error) => {
          console.error('Erro ao criar:', error);
        },
      }
    );
  };

  return (
    <div>
      <button onClick={() => handleCreate({ name: 'Test' })}>
        Criar
      </button>
      {data?.items.map(...)}
    </div>
  );
}
```

### 4. QUERY COM PARÂMETROS DINÂMICOS

```typescript
import { useState } from 'react';
import { useListItemsApiV1ItemsGet } from '@/types/generated/module/module';

function MyComponent() {
  const [filters, setFilters] = useState({ status: 'active', skip: 0 });

  const { data, isLoading } = useListItemsApiV1ItemsGet({
    ...filters,
    limit: 50,
  });

  return (
    <div>
      <select onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
        <option value="active">Ativo</option>
        <option value="inactive">Inativo</option>
      </select>

      {isLoading ? <Spinner /> : <List items={data?.items} />}
    </div>
  );
}
```

### 5. QUERY CONDICIONAL (enabled)

```typescript
import { useGetItemApiV1ItemsItemIdGet } from '@/types/generated/module/module';

function MyComponent({ itemId }: { itemId: string | null }) {
  const {
    data,
    isLoading,
  } = useGetItemApiV1ItemsItemIdGet(
    { itemId: itemId! },
    {
      query: {
        enabled: !!itemId, // Só executa se itemId existir
      },
    }
  );

  if (!itemId) return <div>Selecione um item</div>;
  if (isLoading) return <Spinner />;

  return <div>{data?.name}</div>;
}
```

### 6. HOOK CUSTOM (Wrapper)

```typescript
// src/hooks/items/useItems.ts
import { useQueryClient } from '@tanstack/react-query';
import {
  useListItemsApiV1ItemsGet,
  useCreateItemApiV1ItemsPost,
  useUpdateItemApiV1ItemsItemIdPut,
  useDeleteItemApiV1ItemsItemIdDelete,
  type ItemCreate,
  type ItemUpdate,
} from '@/types/generated/module/module';

export function useItems() {
  const queryClient = useQueryClient();

  // Query
  const {
    data: items,
    isLoading,
    error,
    refetch,
  } = useListItemsApiV1ItemsGet({ skip: 0, limit: 50 });

  // Mutations
  const createMutation = useCreateItemApiV1ItemsPost();
  const updateMutation = useUpdateItemApiV1ItemsItemIdPut();
  const deleteMutation = useDeleteItemApiV1ItemsItemIdDelete();

  // Wrapper functions
  const createItem = async (item: ItemCreate) => {
    return await createMutation.mutateAsync(
      { data: item },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ['items'] });
        },
      }
    );
  };

  const updateItem = async (id: string, item: ItemUpdate) => {
    return await updateMutation.mutateAsync(
      { itemId: id, data: item },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ['items'] });
        },
      }
    );
  };

  const deleteItem = async (id: string) => {
    await deleteMutation.mutateAsync(
      { itemId: id },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: ['items'] });
        },
      }
    );
  };

  return {
    // Data
    items,
    isLoading,
    error,

    // Actions
    createItem,
    updateItem,
    deleteItem,

    // States
    isCreating: createMutation.isLoading,
    isUpdating: updateMutation.isLoading,
    isDeleting: deleteMutation.isLoading,

    // Errors
    createError: createMutation.error,
    updateError: updateMutation.error,
    deleteError: deleteMutation.error,

    // Utils
    refetch,
  };
}

// USO:
function MyComponent() {
  const {
    items,
    isLoading,
    createItem,
    isCreating,
  } = useItems();

  const handleCreate = () => {
    createItem({ name: 'New Item', description: 'Description' });
  };

  return (
    <div>
      {isLoading ? <Spinner /> : <List items={items?.items} />}
      <button onClick={handleCreate} disabled={isCreating}>
        Criar
      </button>
    </div>
  );
}
```

---

## 🎨 TIPOS TYPESCRIPT

### Importar tipos dos schemas:

```typescript
import type {
  ItemCreate,          // Payload de criação
  ItemUpdate,          // Payload de update
  ItemResponse,        // Response de item individual
  ItemListResponse,    // Response de lista
  ItemStatus,          // Enum de status
} from '@/types/generated/module/module.schemas';
```

### Usar tipos em componentes:

```typescript
interface Props {
  item: ItemResponse;
  onUpdate: (id: string, data: ItemUpdate) => void;
}

function ItemCard({ item, onUpdate }: Props) {
  const handleStatusChange = (status: ItemStatus) => {
    onUpdate(item.id, { status });
  };

  return <div>...</div>;
}
```

---

## 🔄 REACT QUERY - CACHE & REVALIDATION

### Configuração global (layout.tsx):

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function Providers({ children }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutos
            cacheTime: 10 * 60 * 1000, // 10 minutos
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

### Invalidar cache específico:

```typescript
import { useQueryClient } from '@tanstack/react-query';

const queryClient = useQueryClient();

// Invalidar todas queries de items
queryClient.invalidateQueries({ queryKey: ['items'] });

// Invalidar query específica
queryClient.invalidateQueries({ queryKey: ['items', itemId] });

// Resetar cache
queryClient.resetQueries({ queryKey: ['items'] });

// Remover query do cache
queryClient.removeQueries({ queryKey: ['items', itemId] });
```

### Prefetch (otimização):

```typescript
const queryClient = useQueryClient();

// Prefetch de dados
await queryClient.prefetchQuery({
  queryKey: ['item', itemId],
  queryFn: () => fetchItem(itemId),
});
```

---

## 🚨 TRATAMENTO DE ERROS

### Erro em Query:

```typescript
const { data, error, isError } = useListItemsApiV1ItemsGet();

if (isError) {
  return <ErrorBoundary error={error} />;
}
```

### Erro em Mutation:

```typescript
const mutation = useCreateItemApiV1ItemsPost();

const handleCreate = async () => {
  try {
    await mutation.mutateAsync({ data: formData });
    toast.success('Item criado!');
  } catch (error) {
    if (error.response?.status === 400) {
      toast.error('Dados inválidos');
    } else if (error.response?.status === 401) {
      toast.error('Não autorizado');
    } else {
      toast.error('Erro ao criar item');
    }
  }
};
```

### Error Boundary global:

```typescript
mutation.mutateAsync(
  { data },
  {
    onError: (error) => {
      // Tratamento global
      console.error('Mutation error:', error);

      // Exibir toast/notificação
      toast.error(error.message || 'Erro desconhecido');
    },
  }
);
```

---

## ⚡ PERFORMANCE

### Loading States:

```typescript
const { isLoading, isFetching } = useListItemsApiV1ItemsGet();

// isLoading: true APENAS no primeiro carregamento
// isFetching: true SEMPRE que estiver buscando (inclusive background)

return (
  <div>
    {isLoading && <Spinner />}
    {isFetching && <RefreshIndicator />}
    <List items={data?.items} />
  </div>
);
```

### Paginação:

```typescript
const [page, setPage] = useState(1);
const limit = 50;

const { data } = useListItemsApiV1ItemsGet({
  skip: (page - 1) * limit,
  limit,
});

const totalPages = Math.ceil((data?.total || 0) / limit);

return (
  <div>
    <List items={data?.items} />
    <Pagination
      currentPage={page}
      totalPages={totalPages}
      onPageChange={setPage}
    />
  </div>
);
```

### Debounce em Search:

```typescript
import { useState, useEffect } from 'react';
import { useDebounce } from '@/hooks/useDebounce';

function SearchComponent() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 500);

  const { data } = useListItemsApiV1ItemsGet({
    search: debouncedSearch,
    skip: 0,
    limit: 20,
  });

  return (
    <div>
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Buscar..."
      />
      <List items={data?.items} />
    </div>
  );
}
```

---

## 📚 MÓDULOS DISPONÍVEIS

| Módulo | Path | Hooks |
|--------|------|-------|
| **Clients** | `@/types/generated/clients/clients-cadastro` | 15+ |
| **Equipment** | `@/types/generated/equipment/` | 10+ |
| **Financial** | `@/types/generated/financial/` | 100+ |
| **GED** | `@/types/generated/ged/` | 50+ |
| **Government** | `@/types/generated/government/` | 10+ |
| **Mobile** | `@/types/generated/mobile/` | 5+ |
| **Notifications** | `@/types/generated/notifications/` | 20+ |
| **Reimbursement** | `@/types/generated/reimbursement/` | 100+ |
| **Scheduler** | `@/types/generated/scheduler/` | 50+ |
| **Search** | `@/types/generated/search/` | 5+ |
| **Security LGPD** | `@/types/generated/security-lgpd/` | 15+ |
| **Workflows** | `@/types/generated/workflows/` | 10+ |

---

## 🛠️ COMANDOS ÚTEIS

```bash
# Regenerar hooks Orval
npm run orval

# Ver hooks disponíveis de um módulo
ls -la src/types/generated/<modulo>/

# Buscar hook específico
grep -r "useList.*Get" src/types/generated/<modulo>/

# Ver types de um módulo
cat src/types/generated/<modulo>/<modulo>.schemas.ts | grep "export type"
```

---

**Última atualização:** 2026-01-31
