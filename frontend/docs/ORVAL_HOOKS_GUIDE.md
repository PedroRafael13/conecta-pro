# Guia de Uso - Orval React Query Hooks

## Visão Geral

Hooks React Query gerados automaticamente a partir do OpenAPI spec do backend FastAPI. Fornece type-safety completo, cache automático e error handling global.

## Estrutura de Imports

```typescript
// Hooks de um módulo específico
import {
  useListDocumentsApiV1GedDocumentsGet,
  useCreateDocumentApiV1GedDocumentsPost,
  useGetDocumentApiV1GedDocumentsDocumentIdGet,
  useUpdateDocumentApiV1GedDocumentsDocumentIdPut,
  useDeleteDocumentApiV1GedDocumentsDocumentIdDelete
} from '@/api/ged/ged';

// Types gerados
import type {
  DocumentResponse,
  DocumentCreate,
  DocumentUpdate,
  ListDocumentsParams
} from '@/api/ged/ged';
```

## Naming Convention

### Padrão de Nomenclatura

```
use<Operation><Path>
```

**Exemplos:**
- `useListDocumentsApiV1GedDocumentsGet` → GET /api/v1/ged/documents
- `useCreateDocumentApiV1GedDocumentsPost` → POST /api/v1/ged/documents
- `useGetDocumentApiV1GedDocumentsDocumentIdGet` → GET /api/v1/ged/documents/{document_id}
- `useUpdateDocumentApiV1GedDocumentsDocumentIdPut` → PUT /api/v1/ged/documents/{document_id}
- `useDeleteDocumentApiV1GedDocumentsDocumentIdDelete` → DELETE /api/v1/ged/documents/{document_id}

### Identificação Rápida

- **Queries (GET)**: Terminam com `Get`
- **Mutations (POST)**: Terminam com `Post`
- **Mutations (PUT)**: Terminam com `Put`
- **Mutations (DELETE)**: Terminam com `Delete`
- **Mutations (PATCH)**: Terminam com `Patch`

## Queries (GET)

### Hook Básico

```typescript
'use client';

import { useListDocumentsApiV1GedDocumentsGet } from '@/api/ged/ged';

export function DocumentList() {
  const { data, isLoading, error, refetch } = useListDocumentsApiV1GedDocumentsGet({
    skip: 0,
    limit: 50
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      {data?.map(doc => (
        <DocumentCard key={doc.id} document={doc} />
      ))}
      <button onClick={() => refetch()}>Atualizar</button>
    </div>
  );
}
```

### Query com Path Params

```typescript
import { useGetDocumentApiV1GedDocumentsDocumentIdGet } from '@/api/ged/ged';

export function DocumentDetail({ documentId }: { documentId: string }) {
  const { data, isLoading, error } = useGetDocumentApiV1GedDocumentsDocumentIdGet(
    documentId  // Path parameter
  );

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return <NotFound />;

  return <DocumentView document={data} />;
}
```

### Query com Múltiplos Parâmetros

```typescript
import { useSearchDocumentsApiV1GedDocumentsSearchGet } from '@/api/ged/ged';
import { useState } from 'react';

export function DocumentSearch() {
  const [filters, setFilters] = useState({
    search: '',
    tipo: undefined,
    status: undefined,
    skip: 0,
    limit: 20
  });

  const { data, isLoading } = useSearchDocumentsApiV1GedDocumentsSearchGet({
    ...filters
  });

  return (
    <div>
      <SearchInput
        value={filters.search}
        onChange={(value) => setFilters(prev => ({ ...prev, search: value }))}
      />
      <DocumentGrid documents={data?.items} loading={isLoading} />
    </div>
  );
}
```

### Query com Conditional Fetching

```typescript
import { useGetDocumentApiV1GedDocumentsDocumentIdGet } from '@/api/ged/ged';

export function ConditionalDocument({ documentId }: { documentId?: string }) {
  const { data, isLoading } = useGetDocumentApiV1GedDocumentsDocumentIdGet(
    documentId!,
    {
      query: {
        enabled: !!documentId  // Só busca se documentId existir
      }
    }
  );

  if (!documentId) return <EmptyState />;
  if (isLoading) return <LoadingSpinner />;

  return <DocumentView document={data} />;
}
```

### Query com Refetch Interval

```typescript
export function LiveDocumentStatus({ documentId }: { documentId: string }) {
  const { data } = useGetDocumentApiV1GedDocumentsDocumentIdGet(
    documentId,
    {
      query: {
        refetchInterval: 5000  // Refetch a cada 5 segundos
      }
    }
  );

  return <StatusBadge status={data?.status} />;
}
```

## Mutations (POST, PUT, DELETE)

### POST - Criar Recurso

```typescript
import { useCreateDocumentApiV1GedDocumentsPost } from '@/api/ged/ged';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export function CreateDocumentForm() {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useCreateDocumentApiV1GedDocumentsPost({
    mutation: {
      onSuccess: (data) => {
        toast.success('Documento criado com sucesso');
        // Invalidar cache da lista
        queryClient.invalidateQueries({
          queryKey: ['listDocumentsApiV1GedDocumentsGet']
        });
      },
      onError: (error) => {
        toast.error('Erro ao criar documento');
        console.error(error);
      }
    }
  });

  const handleSubmit = (formData: DocumentCreate) => {
    mutate({
      data: formData
    });
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      handleSubmit(getFormData(e));
    }}>
      <input name="titulo" required />
      <textarea name="descricao" />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Criando...' : 'Criar Documento'}
      </button>
    </form>
  );
}
```

### PUT - Atualizar Recurso

```typescript
import { useUpdateDocumentApiV1GedDocumentsDocumentIdPut } from '@/api/ged/ged';
import { useQueryClient } from '@tanstack/react-query';

export function EditDocumentForm({ documentId, initialData }: Props) {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useUpdateDocumentApiV1GedDocumentsDocumentIdPut({
    mutation: {
      onSuccess: (data) => {
        toast.success('Documento atualizado');
        // Invalidar cache específico
        queryClient.invalidateQueries({
          queryKey: ['getDocumentApiV1GedDocumentsDocumentIdGet', documentId]
        });
        // Invalidar lista também
        queryClient.invalidateQueries({
          queryKey: ['listDocumentsApiV1GedDocumentsGet']
        });
      }
    }
  });

  const handleUpdate = (updates: DocumentUpdate) => {
    mutate({
      documentId,
      data: updates
    });
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      handleUpdate(getFormData(e));
    }}>
      {/* Form fields */}
      <button type="submit" disabled={isPending}>Salvar</button>
    </form>
  );
}
```

### DELETE - Remover Recurso

```typescript
import { useDeleteDocumentApiV1GedDocumentsDocumentIdDelete } from '@/api/ged/ged';
import { useRouter } from 'next/navigation';

export function DeleteDocumentButton({ documentId }: { documentId: string }) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { mutate, isPending } = useDeleteDocumentApiV1GedDocumentsDocumentIdDelete({
    mutation: {
      onSuccess: () => {
        toast.success('Documento excluído');
        queryClient.invalidateQueries({
          queryKey: ['listDocumentsApiV1GedDocumentsGet']
        });
        router.push('/ged/documents');
      },
      onError: (error) => {
        toast.error('Erro ao excluir documento');
      }
    }
  });

  const handleDelete = async () => {
    if (!confirm('Confirma exclusão?')) return;
    mutate({ documentId });
  };

  return (
    <button
      onClick={handleDelete}
      disabled={isPending}
      className="btn-danger"
    >
      {isPending ? 'Excluindo...' : 'Excluir'}
    </button>
  );
}
```

## Retorno dos Hooks

### Query (GET)

```typescript
const {
  data,           // Dados retornados pela API (tipo inferido)
  isLoading,      // true durante primeira carga
  isFetching,     // true durante qualquer fetch (incluindo refetch)
  error,          // Erro se houver
  refetch,        // Função para refetch manual
  isError,        // true se houver erro
  isSuccess       // true se sucesso
} = useListDocumentsApiV1GedDocumentsGet(params);
```

### Mutation (POST/PUT/DELETE)

```typescript
const {
  mutate,         // Função para executar mutation
  mutateAsync,    // Versão async (retorna Promise)
  isPending,      // true durante execução
  isError,        // true se erro
  isSuccess,      // true se sucesso
  error,          // Erro se houver
  data,           // Dados retornados
  reset           // Reset do estado
} = useCreateDocumentApiV1GedDocumentsPost(options);
```

## Cache e Invalidation

### Invalidar Cache Específico

```typescript
import { useQueryClient } from '@tanstack/react-query';

const queryClient = useQueryClient();

// Invalidar uma query específica
queryClient.invalidateQueries({
  queryKey: ['getDocumentApiV1GedDocumentsDocumentIdGet', documentId]
});

// Invalidar todas as queries de um endpoint
queryClient.invalidateQueries({
  queryKey: ['listDocumentsApiV1GedDocumentsGet']
});
```

### Atualizar Cache Manualmente

```typescript
const { mutate } = useUpdateDocumentApiV1GedDocumentsDocumentIdPut({
  mutation: {
    onSuccess: (updatedDoc) => {
      // Atualizar cache diretamente
      queryClient.setQueryData(
        ['getDocumentApiV1GedDocumentsDocumentIdGet', documentId],
        updatedDoc
      );

      // Atualizar lista também
      queryClient.setQueryData(
        ['listDocumentsApiV1GedDocumentsGet'],
        (old: DocumentResponse[] | undefined) =>
          old?.map(doc => doc.id === documentId ? updatedDoc : doc)
      );
    }
  }
});
```

### Refetch On Focus

```typescript
const { data } = useListDocumentsApiV1GedDocumentsGet(
  { skip: 0, limit: 50 },
  {
    query: {
      refetchOnWindowFocus: true  // Refetch quando janela ganha foco
    }
  }
);
```

## Error Handling

### Global Error Handler

Configurado em `@/lib/api-client.ts`:

```typescript
// Já configurado globalmente
// - Network errors
// - 401: Redirect para login
// - 403: Toast de permissão negada
// - 500: Toast de erro do servidor
```

### Custom Error Handling

```typescript
const { data, error } = useListDocumentsApiV1GedDocumentsGet(params);

if (error) {
  // Error já tem tipo inferido
  if (error.response?.status === 404) {
    return <NotFoundPage />;
  }

  if (error.response?.status === 403) {
    return <PermissionDenied />;
  }

  return <ErrorPage message={error.message} />;
}
```

### Mutation Error Handling

```typescript
const { mutate } = useCreateDocumentApiV1GedDocumentsPost({
  mutation: {
    onError: (error) => {
      // Error tipado
      if (error.response?.status === 400) {
        const validationErrors = error.response.data;
        toast.error('Dados inválidos');
        setFormErrors(validationErrors);
      } else if (error.response?.status === 409) {
        toast.error('Documento já existe');
      } else {
        toast.error('Erro ao criar documento');
      }
    }
  }
});
```

## Exemplos Práticos Completos

### Exemplo 1: Lista com Paginação

```typescript
'use client';

import { useState } from 'react';
import { useListDocumentsApiV1GedDocumentsGet } from '@/api/ged/ged';

export function DocumentListPage() {
  const [page, setPage] = useState(1);
  const limit = 20;

  const { data, isLoading, error } = useListDocumentsApiV1GedDocumentsGet({
    skip: (page - 1) * limit,
    limit
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <DocumentGrid documents={data} />
      <Pagination
        page={page}
        onPageChange={setPage}
        hasMore={data?.length === limit}
      />
    </div>
  );
}
```

### Exemplo 2: Form com Mutation

```typescript
'use client';

import { useCreateDocumentApiV1GedDocumentsPost } from '@/api/ged/ged';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';

export function CreateDocumentPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const form = useForm<DocumentCreate>();

  const { mutate, isPending } = useCreateDocumentApiV1GedDocumentsPost({
    mutation: {
      onSuccess: (data) => {
        toast.success('Documento criado');
        queryClient.invalidateQueries({ queryKey: ['listDocumentsApiV1GedDocumentsGet'] });
        router.push(`/ged/documents/${data.id}`);
      },
      onError: (error) => {
        toast.error('Erro ao criar documento');
      }
    }
  });

  const onSubmit = form.handleSubmit((data) => {
    mutate({ data });
  });

  return (
    <form onSubmit={onSubmit}>
      <input {...form.register('titulo')} required />
      <textarea {...form.register('descricao')} />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Criando...' : 'Criar'}
      </button>
    </form>
  );
}
```

### Exemplo 3: Detail com Actions

```typescript
'use client';

import {
  useGetDocumentApiV1GedDocumentsDocumentIdGet,
  useUpdateDocumentApiV1GedDocumentsDocumentIdPut,
  useDeleteDocumentApiV1GedDocumentsDocumentIdDelete
} from '@/api/ged/ged';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

export function DocumentDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const documentId = params.id;

  const { data, isLoading, error } = useGetDocumentApiV1GedDocumentsDocumentIdGet(documentId);

  const updateMutation = useUpdateDocumentApiV1GedDocumentsDocumentIdPut({
    mutation: {
      onSuccess: () => {
        toast.success('Documento atualizado');
        queryClient.invalidateQueries({
          queryKey: ['getDocumentApiV1GedDocumentsDocumentIdGet', documentId]
        });
      }
    }
  });

  const deleteMutation = useDeleteDocumentApiV1GedDocumentsDocumentIdDelete({
    mutation: {
      onSuccess: () => {
        toast.success('Documento excluído');
        router.push('/ged/documents');
      }
    }
  });

  const handleUpdate = (updates: DocumentUpdate) => {
    updateMutation.mutate({ documentId, data: updates });
  };

  const handleDelete = () => {
    if (confirm('Confirma exclusão?')) {
      deleteMutation.mutate({ documentId });
    }
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return <NotFound />;

  return (
    <div>
      <DocumentView document={data} />
      <EditButton onClick={() => handleUpdate({ titulo: 'Novo título' })} />
      <DeleteButton onClick={handleDelete} />
    </div>
  );
}
```

## Tips & Best Practices

### 1. Sempre Invalidar Cache Relacionado

```typescript
// ✅ Bom: Invalida lista após criar/atualizar/deletar
queryClient.invalidateQueries({ queryKey: ['listDocumentsApiV1GedDocumentsGet'] });

// ❌ Ruim: Não invalida, dados ficam desatualizados
// Sem invalidação
```

### 2. Use Conditional Fetching

```typescript
// ✅ Bom: Só busca quando necessário
const { data } = useGetDocumentApiV1GedDocumentsDocumentIdGet(
  documentId!,
  { query: { enabled: !!documentId } }
);

// ❌ Ruim: Busca mesmo sem documentId
const { data } = useGetDocumentApiV1GedDocumentsDocumentIdGet(documentId);
```

### 3. Combine Loading States

```typescript
// ✅ Bom: Loading state combinado
const isProcessing = createMutation.isPending || deleteMutation.isPending;

// ❌ Ruim: Não considera todos os loadings
const isProcessing = createMutation.isPending;
```

### 4. Use mutateAsync para Sequências

```typescript
// ✅ Bom: Aguarda criação antes de redirecionar
const handleCreate = async (data: DocumentCreate) => {
  try {
    const newDoc = await createMutation.mutateAsync({ data });
    router.push(`/documents/${newDoc.id}`);
  } catch (error) {
    console.error(error);
  }
};

// ❌ Ruim: Redireciona antes da criação
const handleCreate = (data: DocumentCreate) => {
  createMutation.mutate({ data });
  router.push('/documents'); // Executa antes da mutation
};
```

## Referências

- **React Query Docs**: https://tanstack.com/query/latest
- **Orval Docs**: https://orval.dev
- **OpenAPI Spec**: http://localhost:8000/docs
