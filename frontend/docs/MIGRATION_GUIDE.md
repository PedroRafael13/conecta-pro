# Guia de Migração - Services para Orval Hooks

## Visão Geral

Migração de services customizados para hooks React Query gerados automaticamente pelo Orval. Benefícios:

- **Type-safety completo**: Types inferidos do OpenAPI
- **Cache automático**: React Query gerencia cache
- **Loading states**: Sem useState manual
- **Error handling**: Configurado globalmente
- **DevTools**: Inspecione queries no React Query DevTools
- **Invalidation**: Cache invalidation automática

## Passo a Passo

### 1. Identificar Service Atual

Localize o service que você quer migrar:

```bash
# Exemplo: service de documentos
/opt/conecta-pro/frontend/src/services/ged/documentService.ts
```

### 2. Encontrar Hook Equivalente

Mapeie a função do service para o hook Orval correspondente:

**Regra geral:**
- `GET /api/v1/ged/documents` → `useListDocumentsApiV1GedDocumentsGet`
- `POST /api/v1/ged/documents` → `useCreateDocumentApiV1GedDocumentsPost`
- `GET /api/v1/ged/documents/{id}` → `useGetDocumentApiV1GedDocumentsDocumentIdGet`
- `PUT /api/v1/ged/documents/{id}` → `useUpdateDocumentApiV1GedDocumentsDocumentIdPut`
- `DELETE /api/v1/ged/documents/{id}` → `useDeleteDocumentApiV1GedDocumentsDocumentIdDelete`

### 3. Atualizar Imports

```typescript
// ❌ ANTES: Service customizado
import { documentService } from '@/services/ged/documentService';

// ✅ DEPOIS: Hooks Orval
import {
  useListDocumentsApiV1GedDocumentsGet,
  useCreateDocumentApiV1GedDocumentsPost,
  useGetDocumentApiV1GedDocumentsDocumentIdGet
} from '@/api/ged/ged';
import type { DocumentResponse, DocumentCreate } from '@/api/ged/ged';
```

### 4. Substituir Lógica

Veja exemplos antes/depois na seção seguinte.

### 5. Remover States Manuais

```typescript
// ❌ ANTES: States manuais
const [loading, setLoading] = useState(false);
const [error, setError] = useState<Error | null>(null);
const [data, setData] = useState<DocumentResponse[] | null>(null);

// ✅ DEPOIS: Hook fornece tudo
const { data, isLoading, error } = useListDocumentsApiV1GedDocumentsGet(params);
```

### 6. Testar

- Verificar tipos compilam
- Testar loading states
- Testar error handling
- Verificar cache funciona
- Testar invalidation

## Exemplos Antes/Depois

### Exemplo 1: Listar Recursos (GET)

#### ❌ ANTES: Service Customizado

```typescript
'use client';

import { useState, useEffect } from 'react';
import { documentService } from '@/services/ged/documentService';
import type { DocumentResponse } from '@/types/ged';

export function DocumentList() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchDocuments = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await documentService.list({ skip: 0, limit: 50 });
        setDocuments(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      {documents.map(doc => (
        <DocumentCard key={doc.id} document={doc} />
      ))}
    </div>
  );
}
```

#### ✅ DEPOIS: Hook Orval

```typescript
'use client';

import { useListDocumentsApiV1GedDocumentsGet } from '@/api/ged/ged';

export function DocumentList() {
  const { data, isLoading, error } = useListDocumentsApiV1GedDocumentsGet({
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
    </div>
  );
}
```

**Diferenças:**
- ✅ Sem useState manual
- ✅ Sem useEffect
- ✅ Sem try/catch
- ✅ Cache automático
- ✅ Types inferidos

---

### Exemplo 2: Buscar por ID (GET)

#### ❌ ANTES

```typescript
'use client';

import { useState, useEffect } from 'react';
import { documentService } from '@/services/ged/documentService';

export function DocumentDetail({ documentId }: { documentId: string }) {
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchDocument = async () => {
      setLoading(true);
      try {
        const data = await documentService.getById(documentId);
        setDocument(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    if (documentId) {
      fetchDocument();
    }
  }, [documentId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!document) return <NotFound />;

  return <DocumentView document={document} />;
}
```

#### ✅ DEPOIS

```typescript
'use client';

import { useGetDocumentApiV1GedDocumentsDocumentIdGet } from '@/api/ged/ged';

export function DocumentDetail({ documentId }: { documentId: string }) {
  const { data, isLoading, error } = useGetDocumentApiV1GedDocumentsDocumentIdGet(
    documentId,
    {
      query: {
        enabled: !!documentId  // Conditional fetching
      }
    }
  );

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return <NotFound />;

  return <DocumentView document={data} />;
}
```

**Diferenças:**
- ✅ Conditional fetching nativo
- ✅ Refetch automático ao mudar documentId
- ✅ Cache por documentId

---

### Exemplo 3: Criar Recurso (POST)

#### ❌ ANTES

```typescript
'use client';

import { useState } from 'react';
import { documentService } from '@/services/ged/documentService';
import { toast } from 'sonner';

export function CreateDocumentForm() {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (formData: DocumentCreate) => {
    setLoading(true);
    try {
      const newDoc = await documentService.create(formData);
      toast.success('Documento criado');
      // Manualmente refresh da lista
      window.location.reload();
    } catch (error) {
      toast.error('Erro ao criar documento');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      handleSubmit(getFormData(e));
    }}>
      <input name="titulo" required />
      <button type="submit" disabled={loading}>
        {loading ? 'Criando...' : 'Criar'}
      </button>
    </form>
  );
}
```

#### ✅ DEPOIS

```typescript
'use client';

import { useCreateDocumentApiV1GedDocumentsPost } from '@/api/ged/ged';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export function CreateDocumentForm() {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useCreateDocumentApiV1GedDocumentsPost({
    mutation: {
      onSuccess: (data) => {
        toast.success('Documento criado');
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
    mutate({ data: formData });
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      handleSubmit(getFormData(e));
    }}>
      <input name="titulo" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Criando...' : 'Criar'}
      </button>
    </form>
  );
}
```

**Diferenças:**
- ✅ Mutation hook
- ✅ Loading state (isPending)
- ✅ Cache invalidation automática
- ✅ Sem reload da página
- ✅ onSuccess/onError callbacks

---

### Exemplo 4: Atualizar Recurso (PUT)

#### ❌ ANTES

```typescript
'use client';

import { useState } from 'react';
import { documentService } from '@/services/ged/documentService';

export function EditDocumentForm({ documentId, initialData }: Props) {
  const [loading, setLoading] = useState(false);
  const [document, setDocument] = useState(initialData);

  const handleUpdate = async (updates: DocumentUpdate) => {
    setLoading(true);
    try {
      const updated = await documentService.update(documentId, updates);
      setDocument(updated);
      toast.success('Documento atualizado');
    } catch (error) {
      toast.error('Erro ao atualizar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      handleUpdate(getFormData(e));
    }}>
      <input defaultValue={document.titulo} />
      <button disabled={loading}>Salvar</button>
    </form>
  );
}
```

#### ✅ DEPOIS

```typescript
'use client';

import { useUpdateDocumentApiV1GedDocumentsDocumentIdPut } from '@/api/ged/ged';
import { useQueryClient } from '@tanstack/react-query';

export function EditDocumentForm({ documentId, initialData }: Props) {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useUpdateDocumentApiV1GedDocumentsDocumentIdPut({
    mutation: {
      onSuccess: () => {
        toast.success('Documento atualizado');
        queryClient.invalidateQueries({
          queryKey: ['getDocumentApiV1GedDocumentsDocumentIdGet', documentId]
        });
      }
    }
  });

  const handleUpdate = (updates: DocumentUpdate) => {
    mutate({ documentId, data: updates });
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      handleUpdate(getFormData(e));
    }}>
      <input defaultValue={initialData.titulo} />
      <button disabled={isPending}>Salvar</button>
    </form>
  );
}
```

**Diferenças:**
- ✅ Sem state local do documento
- ✅ Cache invalidation automática
- ✅ Mutation hook

---

### Exemplo 5: Deletar Recurso (DELETE)

#### ❌ ANTES

```typescript
'use client';

import { useState } from 'react';
import { documentService } from '@/services/ged/documentService';
import { useRouter } from 'next/navigation';

export function DeleteButton({ documentId }: { documentId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleDelete = async () => {
    if (!confirm('Confirma exclusão?')) return;

    setLoading(true);
    try {
      await documentService.delete(documentId);
      toast.success('Documento excluído');
      router.push('/ged/documents');
    } catch (error) {
      toast.error('Erro ao excluir');
      setLoading(false);
    }
  };

  return (
    <button onClick={handleDelete} disabled={loading}>
      {loading ? 'Excluindo...' : 'Excluir'}
    </button>
  );
}
```

#### ✅ DEPOIS

```typescript
'use client';

import { useDeleteDocumentApiV1GedDocumentsDocumentIdDelete } from '@/api/ged/ged';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';

export function DeleteButton({ documentId }: { documentId: string }) {
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
      onError: () => {
        toast.error('Erro ao excluir');
      }
    }
  });

  const handleDelete = () => {
    if (!confirm('Confirma exclusão?')) return;
    mutate({ documentId });
  };

  return (
    <button onClick={handleDelete} disabled={isPending}>
      {isPending ? 'Excluindo...' : 'Excluir'}
    </button>
  );
}
```

**Diferenças:**
- ✅ Mutation hook
- ✅ Error handling automático
- ✅ Cache invalidation

---

## Checklist de Validação

Após migração, validar:

### Funcionalidade
- [ ] Dados carregam corretamente
- [ ] Loading states funcionam
- [ ] Error handling funciona
- [ ] Mutations executam com sucesso
- [ ] Cache invalida após mutations

### Performance
- [ ] Sem fetches duplicados
- [ ] Cache funciona (dados persistem entre navegações)
- [ ] Refetch só quando necessário

### Developer Experience
- [ ] Types compilam sem erros
- [ ] Autocomplete funciona
- [ ] React Query DevTools mostra queries
- [ ] Sem console errors

### Code Quality
- [ ] Removido código de service antigo
- [ ] Removido states manuais
- [ ] Removido useEffect desnecessários
- [ ] Imports atualizados

## Troubleshooting

### Problema: Types não encontrados

```typescript
// ❌ Erro
import { DocumentResponse } from '@/types/ged';

// ✅ Solução
import type { DocumentResponse } from '@/api/ged/ged';
```

### Problema: Hook não encontrado

```bash
# Regenerar hooks
npm run orval:ged
```

### Problema: Cache não invalida

```typescript
// ✅ Usar queryKey correta
queryClient.invalidateQueries({
  queryKey: ['listDocumentsApiV1GedDocumentsGet']  // Nome exato do hook
});
```

### Problema: Fetch condicional não funciona

```typescript
// ✅ Usar enabled
const { data } = useGetDocumentApiV1GedDocumentsDocumentIdGet(
  documentId!,
  {
    query: {
      enabled: !!documentId
    }
  }
);
```

### Problema: Mutation não executa

```typescript
// ❌ Falta data wrapper
mutate({ titulo: 'Teste' });

// ✅ Correto
mutate({ data: { titulo: 'Teste' } });
```

## Padrões de Substituição

| Service Pattern | Orval Hook Pattern |
|----------------|-------------------|
| `service.list(params)` | `useList*ApiV1*Get(params)` |
| `service.getById(id)` | `useGet*ApiV1*IdGet(id)` |
| `service.create(data)` | `useCreate*ApiV1*Post()` + `mutate({ data })` |
| `service.update(id, data)` | `useUpdate*ApiV1*IdPut()` + `mutate({ id, data })` |
| `service.delete(id)` | `useDelete*ApiV1*IdDelete()` + `mutate({ id })` |
| `useState` + `useEffect` | Hook query direto |
| `try/catch` | `error` do hook + global handler |
| Manual refresh | `queryClient.invalidateQueries()` |

## Migração Gradual

Não é necessário migrar tudo de uma vez:

1. **Começar por módulos novos**: Use hooks em features novas
2. **Migrar por módulo**: Um módulo de cada vez (ex: GED completo)
3. **Coexistência**: Services antigos e hooks podem coexistir
4. **Remover aos poucos**: Deletar services apenas quando não usados

## Próximos Passos

1. Escolher módulo para migrar
2. Identificar todos os services do módulo
3. Criar branch de migração
4. Migrar componente por componente
5. Testar cada componente
6. PR e review
7. Remover services antigos
8. Repetir para próximo módulo

## Recursos

- **Guia de Uso**: `/frontend/docs/ORVAL_HOOKS_GUIDE.md`
- **React Query Docs**: https://tanstack.com/query/latest
- **Orval Docs**: https://orval.dev
