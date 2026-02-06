# 🎯 PLANO DE MANUTENÇÃO E OTIMIZAÇÃO - MÓDULO GED

**Data:** 28/01/2026
**Módulo:** GED (Gestão Eletrônica de Documentos)
**Status Atual:** ✅ 100% COBERTURA
**Objetivo:** MANTER 100% + OTIMIZAR QUALIDADE

---

## 📊 SITUAÇÃO ATUAL

```
╔═══════════════════════════════════════════════════════╗
║  MÓDULO GED - STATUS ATUAL                            ║
╠═══════════════════════════════════════════════════════╣
║  ✅ Cobertura Backend→Frontend:  100% (138/138)       ║
║  ✅ Todos endpoints implementados                     ║
║  ⚠️  Tipos TypeScript:            MANUAL              ║
║  ⚠️  Sincronização:               RISCO DE DRIFT      ║
║  ⚠️  Testes:                      INCOMPLETO          ║
║  ⚠️  Cache:                       AUSENTE             ║
╚═══════════════════════════════════════════════════════╝
```

**Diferencial:** Enquanto OPERACIONAL precisa implementar 30 endpoints (64h), GED já tem cobertura completa.

**Foco:** MANTER sincronização automática + OTIMIZAR performance e qualidade.

---

## 🎯 ESTRATÉGIA HÍBRIDA PARA GED

### Por que Orval mesmo com 100% de cobertura?

| Problema Atual | Solução Orval |
|----------------|---------------|
| ❌ Tipos TypeScript podem desatualizar quando backend muda | ✅ Tipos gerados automaticamente do OpenAPI |
| ❌ Interfaces manuais podem ter typos | ✅ Zero erro, sincronização perfeita |
| ❌ Adicionar novo endpoint = atualizar vários arquivos | ✅ Executar `npm run orval:ged` e pronto |
| ❌ Mudança de schema quebra silenciosamente | ✅ TypeScript detecta na hora |
| ❌ Documentação pode ficar desatualizada | ✅ OpenAPI é fonte única da verdade |

### O que a estratégia híbrida entrega?

```typescript
// ANTES (manual, propenso a erro):
interface Document {
  id: string;
  nome: string; // Ops! Backend mudou para "title"
  tipo: DocumentType; // Ops! Adicionaram novos tipos
}

// DEPOIS (gerado automaticamente):
import type { Document } from '@/types/generated/ged';
// Sempre 100% sincronizado com backend!
```

---

## 📋 ROADMAP DE 4 FASES (100h / 3 semanas)

### FASE 1: FUNDAÇÃO - SINCRONIZAÇÃO AUTOMÁTICA (12h)

**Objetivo:** Garantir que tipos TypeScript estejam 100% sincronizados com backend

#### 1.1 Setup Orval (1h)
```bash
cd /opt/conecta-pro/frontend

# Copiar arquivos
cp /tmp/claude/-root/20db7f31-a283-49f2-ab70-05ad865a33a4/scratchpad/openapi-ged.json ./
cp /tmp/claude/-root/20db7f31-a283-49f2-ab70-05ad865a33a4/scratchpad/orval.config.ged.ts ./

# Instalar Orval
npm install -D orval

# Adicionar script no package.json
# "orval:ged": "orval --config orval.config.ged.ts"
```

**Entregável:** Orval configurado e funcionando

#### 1.2 Gerar Tipos (30min)
```bash
npm run orval:ged
```

**Resultado esperado:**
```
✨ Gerados em src/types/generated/ged/
   - documents.ts
   - folders.ts
   - document-versions.ts
   - document-tags.ts
   - document-shares.ts
   - document-signatures.ts
   - ged-stats.ts
   - common.ts (tipos compartilhados)
```

**Entregável:** 53 schemas TypeScript gerados automaticamente

#### 1.3 Refatorar Services para Usar Tipos Gerados (8h)

**Antes:**
```typescript
// src/lib/services/ged.ts
interface Document {
  id: string;
  title: string;
  // ... definição manual
}

export const documentService = {
  list: async (filters?: any): Promise<Document[]> => {
    // ...
  },
};
```

**Depois:**
```typescript
// src/lib/services/ged.ts
import type {
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentFilter,
  DocumentResponse,
} from '@/types/generated/ged/documents';

import type {
  Folder,
  FolderCreate,
  FolderUpdate,
} from '@/types/generated/ged/folders';

export const documentService = {
  list: async (filters?: DocumentFilter): Promise<DocumentResponse> => {
    return api.get<DocumentResponse>('/api/v1/ged/documents', { params: filters });
  },

  create: async (data: DocumentCreate): Promise<Document> => {
    return api.post<Document>('/api/v1/ged/documents', data);
  },
};
```

**Checklist:**
- [ ] documentService (32 métodos)
- [ ] folderService (22 métodos)
- [ ] documentVersionService (10 métodos)
- [ ] documentTagService (20 métodos)
- [ ] documentShareService (22 métodos)
- [ ] documentSignatureService (25 métodos)
- [ ] documentAIService (7 métodos)
- [ ] gedStatsService (1 método)

**Entregável:** Todos os 161 métodos usando tipos gerados

#### 1.4 Validar Build (2h)
```bash
# Verificar erros de tipo
npm run types:check

# Build completo
npm run build

# Se houver erros, corrigir até passar
```

**Entregável:** Zero erros TypeScript

**Total Fase 1: 12h**

---

### FASE 2: OTIMIZAÇÃO - REACT QUERY (40h)

**Objetivo:** Cache inteligente, refetch automático, loading states

#### 2.1 Instalar Dependências (15min)
```bash
npm install @tanstack/react-query
npm install @tanstack/react-query-devtools
```

#### 2.2 Configurar React Query Provider (30min)
```typescript
// src/app/providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5min
      cacheTime: 10 * 60 * 1000, // 10min
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

export function Providers({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

#### 2.3 Criar Hooks React Query (32h)

##### 2.3.1 Documents Hooks (8h)
```typescript
// src/hooks/ged/useDocuments.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { DocumentFilter, DocumentCreate } from '@/types/generated/ged/documents';
import { documentService } from '@/lib/services/ged';

// Query: Listar documentos
export function useDocuments(filters?: DocumentFilter) {
  return useQuery({
    queryKey: ['ged', 'documents', filters],
    queryFn: () => documentService.list(filters),
  });
}

// Query: Buscar documento por ID
export function useDocument(id: string) {
  return useQuery({
    queryKey: ['ged', 'documents', id],
    queryFn: () => documentService.get(id),
    enabled: !!id,
  });
}

// Mutations: Criar, atualizar, deletar
export function useDocumentMutations() {
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: (data: DocumentCreate) => documentService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ged', 'documents'] });
    },
  });

  const update = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<DocumentCreate> }) =>
      documentService.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ged', 'documents', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['ged', 'documents'] });
    },
  });

  const remove = useMutation({
    mutationFn: (id: string) => documentService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ged', 'documents'] });
    },
  });

  const approve = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      documentService.approve(id, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ged', 'documents', variables.id] });
    },
  });

  return { create, update, remove, approve };
}

// Query: Documentos pendentes de aprovação
export function usePendingApprovalDocuments() {
  return useQuery({
    queryKey: ['ged', 'documents', 'pending-approval'],
    queryFn: () => documentService.listPendingApproval(),
  });
}

// Query: Documentos expirando em breve
export function useExpiringSoonDocuments(days = 30) {
  return useQuery({
    queryKey: ['ged', 'documents', 'expiring-soon', days],
    queryFn: () => documentService.listExpiringSoon(days),
  });
}
```

**Entregável:** 15+ hooks para documentos

##### 2.3.2 Folders Hooks (6h)
```typescript
// src/hooks/ged/useFolders.ts
export function useFolders(filters?: FolderFilter) {
  return useQuery({
    queryKey: ['ged', 'folders', filters],
    queryFn: () => folderService.list(filters),
  });
}

export function useFolderTree() {
  return useQuery({
    queryKey: ['ged', 'folders', 'tree'],
    queryFn: () => folderService.getTree(),
  });
}

export function useFolderMutations() {
  // ... create, update, delete, move, archive, etc
}
```

**Entregável:** 10+ hooks para pastas

##### 2.3.3 Document Versions Hooks (4h)
```typescript
// src/hooks/ged/useDocumentVersions.ts
export function useDocumentVersions(documentId: string) {
  return useQuery({
    queryKey: ['ged', 'document-versions', documentId],
    queryFn: () => documentVersionService.listByDocument(documentId),
  });
}

export function useVersionComparison(documentId: string, v1: string, v2: string) {
  return useQuery({
    queryKey: ['ged', 'document-versions', 'compare', documentId, v1, v2],
    queryFn: () => documentVersionService.compare(documentId, v1, v2),
  });
}
```

**Entregável:** 5+ hooks para versões

##### 2.3.4 Tags Hooks (4h)
```typescript
// src/hooks/ged/useDocumentTags.ts
export function useDocumentTags(filters?: TagFilter) {
  return useQuery({
    queryKey: ['ged', 'tags', filters],
    queryFn: () => documentTagService.list(filters),
  });
}

export function useTagTree() {
  return useQuery({
    queryKey: ['ged', 'tags', 'tree'],
    queryFn: () => documentTagService.getTree(),
  });
}

export function useMostUsedTags(limit = 10) {
  return useQuery({
    queryKey: ['ged', 'tags', 'most-used', limit],
    queryFn: () => documentTagService.getMostUsed(limit),
  });
}
```

**Entregável:** 8+ hooks para tags

##### 2.3.5 Shares Hooks (4h)
```typescript
// src/hooks/ged/useDocumentShares.ts
export function useDocumentShares(documentId: string) {
  return useQuery({
    queryKey: ['ged', 'shares', documentId],
    queryFn: () => documentShareService.listByDocument(documentId),
  });
}

export function useShareMutations() {
  // ... create, revoke, extend, etc
}
```

**Entregável:** 6+ hooks para compartilhamentos

##### 2.3.6 Signatures Hooks (4h)
```typescript
// src/hooks/ged/useDocumentSignatures.ts
export function useDocumentSignatures(documentId: string) {
  return useQuery({
    queryKey: ['ged', 'signatures', documentId],
    queryFn: () => documentSignatureService.listByDocument(documentId),
  });
}

export function usePendingSignatures() {
  return useQuery({
    queryKey: ['ged', 'signatures', 'pending'],
    queryFn: () => documentSignatureService.listPendingBySigner(),
  });
}

export function useSignatureMutations() {
  // ... sign, refuse, cancel, etc
}
```

**Entregável:** 8+ hooks para assinaturas

##### 2.3.7 AI Hooks (2h)
```typescript
// src/hooks/ged/useDocumentAI.ts
export function useDocumentClassification(documentId: string) {
  return useMutation({
    mutationFn: () => documentAIService.classify(documentId),
  });
}

export function useAIDashboard() {
  return useQuery({
    queryKey: ['ged', 'ai', 'dashboard'],
    queryFn: () => documentAIService.getDashboard(),
  });
}
```

**Entregável:** 4+ hooks para IA

#### 2.4 Refatorar Componentes para Usar Hooks (8h)

**Antes:**
```typescript
// src/app/modulos/documentos/page.tsx
export default function DocumentosPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await documentService.list();
        setDocuments(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <div>Carregando...</div>;

  return <div>{/* render documents */}</div>;
}
```

**Depois:**
```typescript
// src/app/modulos/documentos/page.tsx
export default function DocumentosPage() {
  const { data, isLoading, error } = useDocuments();
  const { create, update, remove } = useDocumentMutations();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <Button onClick={() => create.mutate(newDocData)}>
        Criar Documento
      </Button>
      {data?.items.map((doc) => (
        <DocumentCard
          key={doc.id}
          document={doc}
          onUpdate={(data) => update.mutate({ id: doc.id, data })}
          onDelete={() => remove.mutate(doc.id)}
        />
      ))}
    </div>
  );
}
```

**Componentes a refatorar:**
- [ ] DocumentosPage
- [ ] PastasPage
- [ ] DocumentShareDialog
- [ ] DocumentSignatureDialog
- [ ] DocumentVersionHistory
- [ ] DocumentTagManager
- [ ] EditDocumentDialog

**Entregável:** Todos os componentes usando hooks React Query

**Total Fase 2: 40h**

---

### FASE 3: QUALIDADE - TESTES E DOCUMENTAÇÃO (24h)

#### 3.1 Testes de Integração (16h)

##### 3.1.1 Setup de Testes (1h)
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});
```

##### 3.1.2 Testar Services (8h)
```typescript
// tests/services/ged/documents.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { documentService } from '@/lib/services/ged';

describe('GED - Document Service', () => {
  let testDocumentId: string;

  it('should upload document', async () => {
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const result = await documentService.upload(file, {
      folder_id: 'test-folder-id',
      title: 'Test Document',
    });

    expect(result.id).toBeDefined();
    expect(result.title).toBe('Test Document');
    testDocumentId = result.id;
  });

  it('should list documents with filters', async () => {
    const result = await documentService.list({
      status: 'published',
      limit: 10,
    });

    expect(result.items).toBeInstanceOf(Array);
    expect(result.total).toBeGreaterThanOrEqual(0);
  });

  it('should get document by ID', async () => {
    const result = await documentService.get(testDocumentId);

    expect(result.id).toBe(testDocumentId);
    expect(result.title).toBe('Test Document');
  });

  it('should update document', async () => {
    const result = await documentService.update(testDocumentId, {
      title: 'Updated Title',
    });

    expect(result.title).toBe('Updated Title');
  });

  it('should approve document', async () => {
    await documentService.approve(testDocumentId, 'Approved for testing');
    const doc = await documentService.get(testDocumentId);

    expect(doc.status).toBe('approved');
  });

  it('should delete document', async () => {
    await documentService.delete(testDocumentId);

    await expect(documentService.get(testDocumentId)).rejects.toThrow();
  });
});
```

**Cobertura de Testes:**
- [ ] documentService (32 métodos)
- [ ] folderService (22 métodos)
- [ ] documentVersionService (10 métodos)
- [ ] documentTagService (20 métodos)
- [ ] documentShareService (22 métodos)
- [ ] documentSignatureService (25 métodos)
- [ ] documentAIService (7 métodos)

**Meta:** 80%+ de cobertura

##### 3.1.3 Testar Hooks React Query (4h)
```typescript
// tests/hooks/ged/useDocuments.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { useDocuments } from '@/hooks/ged/useDocuments';

describe('useDocuments', () => {
  it('should fetch documents', async () => {
    const { result } = renderHook(() => useDocuments());

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toBeDefined();
    expect(result.current.data.items).toBeInstanceOf(Array);
  });
});
```

##### 3.1.4 Testes E2E com Playwright (3h)
```typescript
// e2e/ged/documents.spec.ts
import { test, expect } from '@playwright/test';

test('upload document workflow', async ({ page }) => {
  await page.goto('/modulos/documentos');

  // Click upload button
  await page.click('[data-testid="upload-button"]');

  // Fill form
  await page.fill('[name="title"]', 'E2E Test Document');
  await page.setInputFiles('[name="file"]', 'test-file.pdf');

  // Submit
  await page.click('[type="submit"]');

  // Verify success
  await expect(page.locator('text=Documento enviado com sucesso')).toBeVisible();
});
```

**Entregável:** Suite de testes completa

#### 3.2 Documentação (4h)

##### 3.2.1 README do Módulo GED (2h)
```markdown
# Módulo GED - Gestão Eletrônica de Documentos

## Estrutura

- `src/lib/services/ged.ts` - Services (161 métodos)
- `src/hooks/ged/` - React Query hooks
- `src/types/generated/ged/` - Tipos gerados automaticamente
- `src/components/ged/` - Componentes React

## Como usar

### Listar documentos
```typescript
import { useDocuments } from '@/hooks/ged/useDocuments';

function MyComponent() {
  const { data, isLoading } = useDocuments({ status: 'published' });
  // ...
}
```

## Manutenção

Quando o backend mudar:
```bash
npm run orval:ged
npm run types:check
```
```

##### 3.2.2 Documentar Hooks (2h)
```typescript
/**
 * Hook para listar documentos com cache automático.
 *
 * @param filters - Filtros opcionais para busca
 * @returns Query result com lista de documentos
 *
 * @example
 * ```tsx
 * const { data, isLoading } = useDocuments({ status: 'published' });
 * ```
 */
export function useDocuments(filters?: DocumentFilter) {
  return useQuery({
    queryKey: ['ged', 'documents', filters],
    queryFn: () => documentService.list(filters),
  });
}
```

**Entregável:** Documentação completa com exemplos

#### 3.3 Performance Monitoring (4h)
```typescript
// src/lib/performance/ged-monitoring.ts
export function trackGedPerformance() {
  // Track API call duration
  const start = performance.now();

  return () => {
    const duration = performance.now() - start;
    if (duration > 1000) {
      console.warn(`GED API call took ${duration}ms`);
    }
  };
}
```

**Entregável:** Monitoring de performance implementado

**Total Fase 3: 24h**

---

### FASE 4: EVOLUÇÃO - FEATURES AVANÇADAS (24h)

#### 4.1 WebSocket Real-Time (16h)

##### 4.1.1 Backend WebSocket Endpoint (8h)
```python
# backend/modules/ged/websocket.py
from fastapi import WebSocket

@router.websocket("/ws/ged")
async def ged_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            # Handle messages
            await websocket.send_json({
                "type": "document:updated",
                "document_id": "xxx",
            })
    except WebSocketDisconnect:
        pass
```

##### 4.1.2 Frontend WebSocket Client (4h)
```typescript
// src/lib/websocket/ged-ws.ts
import { useQueryClient } from '@tanstack/react-query';

class GedWebSocket {
  private ws: WebSocket | null = null;

  connect(token: string) {
    this.ws = new WebSocket(`ws://localhost:8080/ws/ged?token=${token}`);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // Invalidate cache quando documento for atualizado
      if (data.type === 'document:updated') {
        queryClient.invalidateQueries(['ged', 'documents', data.document_id]);
      }
    };

    // Heartbeat
    setInterval(() => {
      this.ws?.send(JSON.stringify({ type: 'ping' }));
    }, 30000);
  }

  disconnect() {
    this.ws?.close();
  }
}

export const gedWS = new GedWebSocket();
```

##### 4.1.3 Hook useGedWebSocket (2h)
```typescript
// src/hooks/ged/useGedWebSocket.ts
export function useGedWebSocket() {
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      gedWS.connect(token);
    }

    return () => {
      gedWS.disconnect();
    };
  }, [token]);
}
```

##### 4.1.4 Integração com UI (2h)
```typescript
// src/app/layout.tsx
export default function Layout({ children }) {
  useGedWebSocket(); // Conectar automaticamente

  return <div>{children}</div>;
}
```

**Entregável:** Real-time updates funcionando

#### 4.2 Batch Operations (8h)

##### 4.2.1 Backend Endpoints (4h)
```python
# backend/modules/ged/controllers/document_controller.py
@router.post("/documents/batch/archive")
async def archive_multiple(
    document_ids: List[str],
    db: Session = Depends(get_db)
):
    """Arquivar múltiplos documentos de uma vez."""
    results = []
    for doc_id in document_ids:
        result = await document_service.archive(db, doc_id)
        results.append(result)
    return {"archived": len(results), "results": results}

@router.post("/documents/batch/move")
async def move_multiple(
    document_ids: List[str],
    target_folder_id: str,
    db: Session = Depends(get_db)
):
    """Mover múltiplos documentos para outra pasta."""
    # ...
```

##### 4.2.2 Frontend Service (2h)
```typescript
// src/lib/services/ged.ts
export const documentService = {
  // ... métodos existentes

  batchArchive: async (documentIds: string[]): Promise<BatchResult> => {
    return api.post('/api/v1/ged/documents/batch/archive', {
      document_ids: documentIds,
    });
  },

  batchMove: async (documentIds: string[], targetFolderId: string): Promise<BatchResult> => {
    return api.post('/api/v1/ged/documents/batch/move', {
      document_ids: documentIds,
      target_folder_id: targetFolderId,
    });
  },
};
```

##### 4.2.3 UI com Seleção Múltipla (2h)
```typescript
// src/components/ged/DocumentList.tsx
export function DocumentList() {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const { data } = useDocuments();
  const batchArchive = useMutation({
    mutationFn: documentService.batchArchive,
  });

  return (
    <div>
      <Button
        onClick={() => batchArchive.mutate(selectedIds)}
        disabled={selectedIds.length === 0}
      >
        Arquivar Selecionados ({selectedIds.length})
      </Button>

      {data?.items.map((doc) => (
        <div key={doc.id}>
          <input
            type="checkbox"
            checked={selectedIds.includes(doc.id)}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedIds([...selectedIds, doc.id]);
              } else {
                setSelectedIds(selectedIds.filter((id) => id !== doc.id));
              }
            }}
          />
          {doc.title}
        </div>
      ))}
    </div>
  );
}
```

**Entregável:** Operações em lote funcionando

**Total Fase 4: 24h**

---

## 📊 CRONOGRAMA

### Semana 1: Fundação + Início Otimização (32h)
- [ ] Dias 1-2: Setup Orval e geração de tipos (12h)
- [ ] Dias 3-5: Início implementação React Query hooks (20h)

### Semana 2: Otimização + Início Qualidade (40h)
- [ ] Dias 1-3: Conclusão React Query hooks (20h)
- [ ] Dias 4-5: Início testes de integração (20h)

### Semana 3: Qualidade + Evolução (28h)
- [ ] Dias 1-2: Conclusão testes e documentação (12h)
- [ ] Dias 3-5: Features avançadas (WebSocket + Batch) (16h)

**TOTAL: 100h (~3 semanas)**

---

## 🎯 PRIORIZAÇÃO

### 🔴 CRÍTICO (Fazer Imediatamente)
**Fase 1: Fundação (12h)**
- Setup Orval
- Gerar tipos
- Refatorar services
- Validar build

**Por quê:** Previne dessincronia entre backend e frontend.

### 🟡 ALTO (Fazer em até 1 semana)
**Fase 2: Otimização (40h)**
- Implementar React Query hooks
- Refatorar componentes

**Por quê:** Melhora significativa de performance e DX.

### 🟢 MÉDIO (Fazer em até 2 semanas)
**Fase 3: Qualidade (24h)**
- Testes de integração
- Documentação
- Performance monitoring

**Por quê:** Garante qualidade e facilita manutenção.

### 🔵 BAIXO (Fazer em até 1 mês)
**Fase 4: Evolução (24h)**
- WebSocket real-time
- Batch operations

**Por quê:** Features nice-to-have, não críticas.

---

## 💰 CUSTO-BENEFÍCIO

| Fase | Tempo | Benefício | Prioridade |
|------|-------|-----------|-----------|
| 1 - Fundação | 12h | ⭐⭐⭐⭐⭐ Tipos sincronizados | 🔴 CRÍTICO |
| 2 - Otimização | 40h | ⭐⭐⭐⭐ Performance + DX | 🟡 ALTO |
| 3 - Qualidade | 24h | ⭐⭐⭐⭐ Confiabilidade | 🟢 MÉDIO |
| 4 - Evolução | 24h | ⭐⭐⭐ Features avançadas | 🔵 BAIXO |

**Recomendação:** Focar nas Fases 1 e 2 primeiro (52h / 1.5 semanas).

---

## 🔄 MANUTENÇÃO CONTÍNUA

### Processo após mudanças no backend:

```bash
# 1. Atualizar OpenAPI spec
cd /opt/conecta-pro/backend
curl -s http://localhost:8080/openapi.json -o /tmp/openapi-conecta-pro.json

# 2. Extrair apenas GED
python3 extract-ged-spec.py

# 3. Gerar tipos
cd /opt/conecta-pro/frontend
cp /tmp/openapi-ged.json ./
npm run orval:ged

# 4. Verificar erros
npm run types:check

# 5. Corrigir erros se houver
# ... editar arquivos

# 6. Build
npm run build

# 7. Commit
git add .
git commit -m "chore: atualizar tipos GED"
```

**Automação (CI/CD):**
```yaml
# .github/workflows/sync-ged-types.yml
name: Sync GED Types

on:
  push:
    paths:
      - 'backend/modules/ged/**'

jobs:
  sync-types:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate OpenAPI
        run: curl -s http://localhost:8080/openapi.json -o openapi.json
      - name: Extract GED spec
        run: python3 extract-ged-spec.py
      - name: Generate types
        run: npm run orval:ged
      - name: Check types
        run: npm run types:check
```

---

## 📈 MÉTRICAS DE SUCESSO

### KPIs Técnicos
- [ ] ✅ 100% de cobertura backend→frontend MANTIDA
- [ ] ✅ Zero erros TypeScript após geração de tipos
- [ ] ✅ 80%+ de cobertura de testes
- [ ] ✅ <500ms de latência média em APIs
- [ ] ✅ 95%+ uptime no WebSocket

### KPIs de Qualidade
- [ ] ✅ Documentação completa de todos os hooks
- [ ] ✅ Exemplos de uso para cada funcionalidade
- [ ] ✅ CI/CD automatizado para sync de tipos

### KPIs de Performance
- [ ] ✅ Cache hit rate >70% no React Query
- [ ] ✅ Redução de 50% em requisições duplicadas
- [ ] ✅ Tempo de resposta da UI <100ms

---

## 🏆 RESULTADO ESPERADO

```
╔═══════════════════════════════════════════════════════════╗
║  MÓDULO GED - APÓS IMPLEMENTAÇÃO (100h / 3 semanas)      ║
╠═══════════════════════════════════════════════════════════╣
║  ✅ Cobertura:                100% MANTIDA                ║
║  ✅ Tipos TypeScript:         100% sincronizados          ║
║  ✅ React Query:              Implementado                ║
║  ✅ Cache inteligente:        Funcionando                 ║
║  ✅ Testes:                   80%+ cobertura              ║
║  ✅ Documentação:             Completa                    ║
║  ✅ WebSocket:                Real-time updates           ║
║  ✅ Batch operations:         Implementado                ║
║  ✅ Performance:              Otimizada                   ║
║  ✅ Manutenção:               Automatizada                ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🚀 PRÓXIMOS PASSOS

### Imediato (Agora)
1. Ler `/tmp/...scratchpad/EXECUTE-AGORA-GED.md`
2. Copiar arquivos para o frontend
3. Executar `npm run orval:ged`
4. Verificar tipos gerados

### Curto Prazo (Esta Semana)
1. Refatorar services para usar tipos gerados
2. Implementar primeiros hooks React Query
3. Testar em componentes

### Médio Prazo (Este Mês)
1. Concluir todos os hooks
2. Implementar testes
3. Documentar tudo

### Longo Prazo (Próximo Sprint)
1. WebSocket real-time
2. Batch operations
3. Expandir para outros módulos (Financeiro, Comercial, etc)

---

**Plano criado por:** Claude Sonnet 4.5
**Data:** 28 de Janeiro de 2026
**Versão:** 1.0
