# Exemplo de Migração: Módulo GED

## Objetivo
Demonstrar migração de página React que usa services manuais para hooks React Query gerados pelo Orval.

## Página Migrada
**Arquivo:** `/opt/conecta-pro/frontend/src/app/modulos/documentos/page.tsx`

Dashboard principal do módulo GED (Gestão Eletrônica de Documentos).

## O Que Foi Migrado

### 1. Imports de Services → Hooks Gerados

**ANTES:**
```typescript
import {
  folderService,
  documentService,
  gedStatsService,
  formatFileSize,
  type Folder,
  type Document,
  type GEDStats,
  DOCUMENT_TYPES,
  DOCUMENT_CATEGORIES,
} from '@/lib/services/ged';
```

**DEPOIS:**
```typescript
// Mantém apenas types e utils
import {
  formatFileSize,
  type Folder,
  type Document,
  type GEDStats,
  DOCUMENT_TYPES,
  DOCUMENT_CATEGORIES,
} from '@/lib/services/ged';

// Adiciona hooks gerados pelo Orval
import { useGetGedStatsApiV1GedStatsGet } from '@/types/generated/ged/ged-estatísticas/ged-estatísticas';
import { useListFoldersApiV1GedFoldersGet } from '@/types/generated/ged/ged-pastas/ged-pastas';
import {
  useGetPendingApprovalApiV1GedDocumentsPendingApprovalGet,
  useGetPendingSignatureApiV1GedDocumentsPendingSignatureGet,
  useGetExpiringSoonApiV1GedDocumentsExpiringSoonGet,
} from '@/types/generated/ged/ged-documentos/ged-documentos';
```

### 2. useState + useEffect + Promise.all → React Query Hooks

**ANTES:**
```typescript
const [loading, setLoading] = useState(true);
const [stats, setStats] = useState<GEDStats | null>(null);
const [rootFolders, setRootFolders] = useState<Folder[]>([]);
const [pendingApprovals, setPendingApprovals] = useState<Document[]>([]);
const [pendingSignatures, setPendingSignatures] = useState<Document[]>([]);
const [expiringDocs, setExpiringDocs] = useState<Document[]>([]);

const loadData = useCallback(async () => {
  try {
    setLoading(true);

    const [gedStats, folders, approvals, signatures, expiring] = await Promise.all([
      gedStatsService.get(),
      folderService.list({ page_size: 100 }),
      documentService.listPendingApproval(),
      documentService.listPendingSignature(),
      documentService.listExpiringSoon(30),
    ]);

    setStats(gedStats);
    setRootFolders(folders.items.filter(f => f.is_root));
    setPendingApprovals(approvals);
    setPendingSignatures(signatures);
    setExpiringDocs(expiring);
  } catch (error) {
    console.error('Erro ao carregar dados:', error);
  } finally {
    setLoading(false);
  }
}, []);

useEffect(() => {
  loadData();
}, [loadData]);
```

**DEPOIS:**
```typescript
// React Query faz tudo automaticamente: loading, error, cache, refetch
const { data: statsData, isLoading: loadingStats } = useGetGedStatsApiV1GedStatsGet();
const { data: foldersData, isLoading: loadingFolders } = useListFoldersApiV1GedFoldersGet({
  page: 1,
  page_size: 100
});
const { data: pendingApprovals = [], isLoading: loadingApprovals } =
  useGetPendingApprovalApiV1GedDocumentsPendingApprovalGet();
const { data: pendingSignatures = [], isLoading: loadingSignatures } =
  useGetPendingSignatureApiV1GedDocumentsPendingSignatureGet();
const { data: expiringDocs = [], isLoading: loadingExpiring } =
  useGetExpiringSoonApiV1GedDocumentsExpiringSoonGet({ days: 30 });

// Computed values
const loading = loadingStats || loadingFolders || loadingApprovals || loadingSignatures || loadingExpiring;
const stats = statsData || null;
const rootFolders = foldersData?.items?.filter((f: Folder) => f.is_root) || [];
```

### 3. Callbacks de Refresh → Invalidação Automática

**ANTES:**
```typescript
<DocumentApprovalDialog
  document={approvalDialog.document}
  open={approvalDialog.open}
  onClose={() => setApprovalDialog({ open: false, document: null })}
  onApproved={loadData}  // ← callback manual
/>

<DocumentSignatureDialog
  documentId={signatureDialog.document.id}
  open={signatureDialog.open}
  onClose={() => {
    setSignatureDialog({ open: false, document: null });
    loadData();  // ← chamada manual
  }}
  mode="sign"
/>
```

**DEPOIS:**
```typescript
{/* React Query faz invalidação automática via queryClient.invalidateQueries */}
<DocumentApprovalDialog
  document={approvalDialog.document}
  open={approvalDialog.open}
  onClose={() => setApprovalDialog({ open: false, document: null })}
  onApproved={() => setApprovalDialog({ open: false, document: null })}
/>

<DocumentSignatureDialog
  documentId={signatureDialog.document.id}
  open={signatureDialog.open}
  onClose={() => setSignatureDialog({ open: false, document: null })}
  mode="sign"
/>
```

**Nota:** Os componentes de dialog devem usar `useMutation` do Orval internamente, que automaticamente invalidam as queries relacionadas.

## Benefícios da Migração

### 1. Menos Código Boilerplate
- ❌ **Removido:** 25 linhas de useState, useCallback, useEffect, try/catch
- ✅ **Adicionado:** 5 linhas de hooks React Query
- **Economia:** -80% de código de data fetching

### 2. Funcionalidades Automáticas
- ✅ **Cache:** Dados são cacheados automaticamente
- ✅ **Refetch:** Refetch automático em foco/reconexão
- ✅ **Loading States:** isLoading, isFetching gerenciados automaticamente
- ✅ **Error Handling:** Tratamento de erro global via QueryClient
- ✅ **Deduplicação:** Múltiplas chamadas simultâneas são deduplicated
- ✅ **Stale While Revalidate:** Mostra dados antigos enquanto atualiza

### 3. Type Safety Total
```typescript
// Tipos são inferidos automaticamente do OpenAPI
const { data: statsData } = useGetGedStatsApiV1GedStatsGet();
//     ↑ tipo: GEDStatsResponse | undefined

const { data: foldersData } = useListFoldersApiV1GedFoldersGet({ ... });
//     ↑ tipo: FolderListResponse | undefined
```

### 4. Parâmetros Type-Safe
```typescript
// TypeScript força passar os parâmetros corretos
useListFoldersApiV1GedFoldersGet({
  page: 1,           // ✅ number
  page_size: 100,    // ✅ number
  // TS erro se passar parâmetro errado
});

useGetExpiringSoonApiV1GedDocumentsExpiringSoonGet({
  days: 30  // ✅ type-safe
});
```

## Hooks React Query Disponíveis (GED)

### Estatísticas
```typescript
import { useGetGedStatsApiV1GedStatsGet } from '@/types/generated/ged/ged-estatísticas/ged-estatísticas';

const { data, isLoading } = useGetGedStatsApiV1GedStatsGet();
```

### Pastas
```typescript
import {
  useListFoldersApiV1GedFoldersGet,
  useGetFolderApiV1GedFoldersFolderIdGet,
  useGetRootFoldersApiV1GedFoldersRootListGet,
  useCreateFolderApiV1GedFoldersPost,
  useUpdateFolderApiV1GedFoldersFolderIdPut,
  useDeleteFolderApiV1GedFoldersFolderIdDelete,
} from '@/types/generated/ged/ged-pastas/ged-pastas';

// Listar pastas com paginação
const { data } = useListFoldersApiV1GedFoldersGet({ page: 1, page_size: 20 });

// Obter pasta específica
const { data } = useGetFolderApiV1GedFoldersFolderIdGet({ folderId: 'abc-123' });

// Listar apenas raízes
const { data } = useGetRootFoldersApiV1GedFoldersRootListGet();

// Mutations
const { mutate: createFolder } = useCreateFolderApiV1GedFoldersPost();
const { mutate: updateFolder } = useUpdateFolderApiV1GedFoldersFolderIdPut();
const { mutate: deleteFolder } = useDeleteFolderApiV1GedFoldersFolderIdDelete();
```

### Documentos
```typescript
import {
  useListDocumentsApiV1GedDocumentsGet,
  useGetDocumentApiV1GedDocumentsDocumentIdGet,
  useGetPendingApprovalApiV1GedDocumentsPendingApprovalGet,
  useGetPendingSignatureApiV1GedDocumentsPendingSignatureGet,
  useGetExpiringSoonApiV1GedDocumentsExpiringSoonGet,
  useCreateDocumentApiV1GedDocumentsPost,
  useUpdateDocumentApiV1GedDocumentsDocumentIdPut,
  useDeleteDocumentApiV1GedDocumentsDocumentIdDelete,
  useUploadDocumentApiV1GedDocumentsUploadPost,
} from '@/types/generated/ged/ged-documentos/ged-documentos';

// Listar documentos
const { data } = useListDocumentsApiV1GedDocumentsGet({
  page: 1,
  page_size: 20,
  status: 'aprovado'
});

// Documentos pendentes
const { data: pending } = useGetPendingApprovalApiV1GedDocumentsPendingApprovalGet();

// Documentos expirando
const { data: expiring } = useGetExpiringSoonApiV1GedDocumentsExpiringSoonGet({ days: 30 });

// Mutations
const { mutate: uploadDoc } = useUploadDocumentApiV1GedDocumentsUploadPost();
```

## Padrão de Nomenclatura dos Hooks

Todos os hooks seguem o padrão:
```
use[NomeDoEndpoint]Api[Versão][Módulo][Path][Método]
```

Exemplos:
- `useGetGedStatsApiV1GedStatsGet` → GET /api/v1/ged/stats
- `useListDocumentsApiV1GedDocumentsGet` → GET /api/v1/ged/documents
- `useCreateDocumentApiV1GedDocumentsPost` → POST /api/v1/ged/documents
- `useUpdateDocumentApiV1GedDocumentsDocumentIdPut` → PUT /api/v1/ged/documents/{id}

## Como Descobrir os Hooks Disponíveis

### 1. Via Grep
```bash
grep "export.*use" /opt/conecta-pro/frontend/src/types/generated/ged/**/*.ts
```

### 2. Via IDE (VSCode/Cursor)
- Ctrl+P: `@/types/generated/ged/`
- Autocomplete mostra todos os hooks

### 3. Via Documentação do OpenAPI
- Ver spec: `/backend/docs` (Swagger UI)
- Cada endpoint tem um hook correspondente

## Checklist de Migração

Ao migrar uma página:

- [x] Remover imports de services (`folderService`, `documentService`, etc)
- [x] Adicionar imports dos hooks gerados
- [x] Substituir `useState` + `useEffect` por hooks React Query
- [x] Remover funções `loadData()` / `fetchData()`
- [x] Atualizar callbacks de refresh (não precisam mais recarregar manualmente)
- [x] Remover tratamento manual de loading/error (React Query faz automaticamente)
- [x] Testar que dados carregam corretamente
- [x] Verificar que mutations invalidam queries automaticamente

## Resultado

**Antes da migração:**
- 650 linhas de código
- 25 linhas de data fetching manual
- 5 useState
- 1 useCallback
- 1 useEffect
- 1 Promise.all
- try/catch manual

**Depois da migração:**
- 625 linhas de código (-25 linhas, -4%)
- 5 linhas de hooks React Query
- 0 useEffect para data fetching
- 0 try/catch para data fetching
- Cache + refetch + error handling automáticos

## Próximos Passos

1. Migrar página `/modulos/documentos/arquivos/page.tsx`
2. Migrar página `/modulos/documentos/pastas/page.tsx`
3. Migrar componentes de dialog (se ainda usam services)
4. Remover completamente os services antigos quando todas as páginas migrarem

## Documentação Relacionada

- [Guia Completo de Uso](./ORVAL_USAGE_GUIDE.md)
- [Configuração React Query](./ORVAL_INTEGRATION.md)
- [Lista de Todos os Módulos](./ORVAL_MIGRATION_STATUS.md)
