# 🚀 GUIA DE OTIMIZAÇÃO E MELHORIAS FUTURAS - MÓDULO GED

## 📌 OBJETIVO
Este documento contém recomendações técnicas para otimizar performance, escalabilidade e experiência do usuário no módulo GED.

---

## ⚡ PERFORMANCE

### 1. Lazy Loading de Componentes
**Status:** ⚠️ A implementar

**Problema atual:**
Todos os componentes carregam na primeira renderização.

**Solução proposta:**
```typescript
// Usar Next.js dynamic imports
import dynamic from 'next/dynamic';

const UploadModal = dynamic(() => import('./UploadModal'), {
  loading: () => <LoadingSkeleton />,
  ssr: false
});

const DocumentPreview = dynamic(() => import('./DocumentPreview'), {
  loading: () => <PreviewSkeleton />
});
```

**Benefício:** Reduz bundle inicial em ~30%

---

### 2. Paginação Infinita (Infinite Scroll)
**Status:** ⚠️ A implementar

**Atual:** Paginação tradicional (botões Anterior/Próxima)

**Melhoria:**
```typescript
import { useInfiniteQuery } from '@tanstack/react-query';

const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['documents'],
  queryFn: ({ pageParam = 1 }) => documentService.list({ page: pageParam }),
  getNextPageParam: (lastPage) => lastPage.next_page,
});

// Usar Intersection Observer
const loadMoreRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasNextPage) {
        fetchNextPage();
      }
    }
  );

  if (loadMoreRef.current) {
    observer.observe(loadMoreRef.current);
  }
}, [hasNextPage, fetchNextPage]);
```

**Benefício:** UX mais fluida, melhor para mobile

---

### 3. Cache com React Query
**Status:** ⚠️ A implementar

**Problema:** Cada navegação refaz todas as requisições

**Solução:**
```typescript
// setup/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
      refetchOnWindowFocus: false,
    },
  },
});

// Em cada serviço
const { data: folders } = useQuery({
  queryKey: ['folders', filters],
  queryFn: () => folderService.list(filters),
});
```

**Benefício:** Reduz chamadas API em 70%, UX instantânea

---

### 4. Virtualização de Listas
**Status:** ⚠️ A implementar para listas grandes

**Quando usar:** Mais de 100 itens na lista

**Biblioteca:** `@tanstack/react-virtual`

```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

const rowVirtualizer = useVirtualizer({
  count: documents.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 60, // altura estimada por item
  overscan: 5, // quantos itens renderizar fora da view
});

return (
  <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
    <div style={{ height: `${rowVirtualizer.getTotalSize()}px` }}>
      {rowVirtualizer.getVirtualItems().map((virtualRow) => (
        <div
          key={virtualRow.index}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            transform: `translateY(${virtualRow.start}px)`,
          }}
        >
          <DocumentRow document={documents[virtualRow.index]} />
        </div>
      ))}
    </div>
  </div>
);
```

**Benefício:** Renderiza apenas itens visíveis, suporta listas de 10k+ itens

---

### 5. Otimização de Imagens
**Status:** ⚠️ A implementar

**Problema:** Thumbnails carregam imagem completa

**Solução:**
```typescript
// Backend: Gerar thumbnails ao fazer upload
from PIL import Image

def generate_thumbnail(file_path: str, size=(200, 200)):
    img = Image.open(file_path)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    thumb_path = f"{file_path}_thumb.jpg"
    img.save(thumb_path, "JPEG", quality=85)
    return thumb_path

// Frontend: Usar next/image
import Image from 'next/image';

<Image
  src={doc.thumbnail_url || doc.file_url}
  alt={doc.title}
  width={200}
  height={200}
  placeholder="blur"
  blurDataURL="/placeholder.svg"
/>
```

**Benefício:** Reduz tráfego de rede em 90%

---

## 🔍 BUSCA E FILTROS

### 6. Debounce na Busca
**Status:** ⚠️ A implementar

**Problema:** Busca dispara requisição a cada tecla

**Solução:**
```typescript
import { useDebouncedCallback } from 'use-debounce';

const [searchInput, setSearchInput] = useState('');
const [searchQuery, setSearchQuery] = useState('');

const debouncedSearch = useDebouncedCallback(
  (value: string) => {
    setSearchQuery(value);
  },
  500 // 500ms de delay
);

<Input
  value={searchInput}
  onChange={(e) => {
    setSearchInput(e.target.value);
    debouncedSearch(e.target.value);
  }}
/>
```

**Benefício:** Reduz requisições em 80%

---

### 7. Elasticsearch para Busca Full-Text
**Status:** 📋 Planejamento

**Atual:** Busca simples via SQL LIKE

**Proposta:**
```python
# Backend: Indexar documentos no Elasticsearch
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

# Ao criar documento
es.index(
    index='documents',
    id=str(document.id),
    document={
        'title': document.title,
        'description': document.description,
        'content': extract_text(document.file_path),  # OCR
        'tags': document.tags,
        'created_at': document.created_at,
    }
)

# Busca
results = es.search(
    index='documents',
    body={
        'query': {
            'multi_match': {
                'query': search_term,
                'fields': ['title^3', 'description^2', 'content', 'tags^2'],
                'fuzziness': 'AUTO'
            }
        },
        'highlight': {
            'fields': {
                'content': {}
            }
        }
    }
)
```

**Benefício:**
- Busca em conteúdo (não só metadata)
- Resultados relevantes (score)
- Autocomplete
- Sugestões de correção

---

## 📁 UPLOAD

### 8. Resumable Upload (Upload Pausável)
**Status:** 📋 Planejamento

**Problema:** Upload grande falha se conexão cair

**Biblioteca:** `tus-js-client` (protocolo TUS)

```typescript
import * as tus from 'tus-js-client';

const upload = new tus.Upload(file, {
  endpoint: '/api/v1/ged/documents/upload-resumable',
  retryDelays: [0, 3000, 5000, 10000],
  metadata: {
    filename: file.name,
    filetype: file.type,
  },
  onProgress: (bytesUploaded, bytesTotal) => {
    const percentage = (bytesUploaded / bytesTotal * 100).toFixed(2);
    setProgress(percentage);
  },
  onSuccess: () => {
    toast({ title: 'Upload completo!' });
  },
  onError: (error) => {
    // Upload pode ser retomado
    toast({ title: 'Erro no upload. Retomando...' });
  }
});

upload.start();

// Pausar
const handlePause = () => upload.abort();

// Retomar
const handleResume = () => upload.start();
```

**Benefício:** Arquivos grandes (>100MB) com segurança

---

### 9. Compressão de Imagens Client-Side
**Status:** ⚠️ A implementar

**Biblioteca:** `browser-image-compression`

```typescript
import imageCompression from 'browser-image-compression';

const handleImageUpload = async (file: File) => {
  if (file.type.startsWith('image/')) {
    const options = {
      maxSizeMB: 1,
      maxWidthOrHeight: 1920,
      useWebWorker: true,
    };

    try {
      const compressedFile = await imageCompression(file, options);
      uploadFile(compressedFile);

      toast({
        title: 'Imagem comprimida',
        description: `Tamanho reduzido de ${formatFileSize(file.size)} para ${formatFileSize(compressedFile.size)}`,
      });
    } catch (error) {
      uploadFile(file); // Fallback para original
    }
  } else {
    uploadFile(file);
  }
};
```

**Benefício:** Reduz upload de imagens em 60-80%

---

## 📊 ANALYTICS E MONITORAMENTO

### 10. Event Tracking
**Status:** 📋 Planejamento

**Biblioteca:** PostHog ou Plausible

```typescript
import posthog from 'posthog-js';

// Ao criar pasta
posthog.capture('folder_created', {
  folder_type: formData.folder_type,
  is_public: formData.is_public,
});

// Ao fazer upload
posthog.capture('document_uploaded', {
  file_type: file.type,
  file_size_mb: file.size / 1024 / 1024,
  upload_duration_seconds: uploadTime,
});

// Ao fazer download
posthog.capture('document_downloaded', {
  document_type: doc.document_type,
  file_extension: doc.file_extension,
});
```

**Métricas úteis:**
- Tipos de arquivo mais usados
- Pastas mais acessadas
- Horários de pico de upload
- Taxa de erro em uploads

---

### 11. Error Boundary
**Status:** ⚠️ A implementar

```typescript
// components/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);

    // Enviar para serviço de monitoramento
    // Sentry.captureException(error);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-6 text-center">
          <h2 className="text-xl font-bold text-red-600">Algo deu errado</h2>
          <p className="mt-2 text-muted-foreground">
            {this.state.error?.message}
          </p>
          <Button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4"
          >
            Tentar novamente
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Uso em layout
<ErrorBoundary>
  <PastasContent />
</ErrorBoundary>
```

---

## 🔐 SEGURANÇA

### 12. Validação de Tipo de Arquivo (Server-Side)
**Status:** ⚠️ A implementar

**Problema:** Confia apenas em extensão de arquivo

**Solução:**
```python
import magic

def validate_file_type(file: UploadFile) -> bool:
    """Valida tipo de arquivo via magic bytes, não extensão"""

    # Ler primeiros bytes
    file_head = file.file.read(2048)
    file.file.seek(0)

    # Detectar tipo real
    mime = magic.from_buffer(file_head, mime=True)

    # Whitelist de tipos permitidos
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
        'text/plain',
    ]

    if mime not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido: {mime}"
        )

    return True
```

**Benefício:** Previne upload de malware disfarçado

---

### 13. Antivírus Scan
**Status:** 📋 Planejamento

**Biblioteca:** ClamAV

```python
import pyclamd

cd = pyclamd.ClamdUnixSocket()

def scan_file(file_path: str) -> bool:
    """Escaneia arquivo por malware"""

    scan_result = cd.scan_file(file_path)

    if scan_result is None:
        return True  # Arquivo limpo

    # Arquivo infectado
    virus_name = scan_result[file_path][1]
    raise HTTPException(
        status_code=400,
        detail=f"Arquivo contém malware: {virus_name}"
    )
```

---

## 🎨 UX MELHORIAS

### 14. Keyboard Shortcuts
**Status:** ⚠️ A implementar

**Biblioteca:** `react-hotkeys-hook`

```typescript
import { useHotkeys } from 'react-hotkeys-hook';

// Em PastasPage
useHotkeys('ctrl+n', (e) => {
  e.preventDefault();
  setDialogOpen(true); // Abrir modal de nova pasta
});

useHotkeys('ctrl+f', (e) => {
  e.preventDefault();
  searchInputRef.current?.focus(); // Focar na busca
});

useHotkeys('esc', () => {
  setDialogOpen(false); // Fechar modal
});

// Em ArquivosPage
useHotkeys('ctrl+u', (e) => {
  e.preventDefault();
  setUploadDialogOpen(true); // Abrir upload
});
```

**Atalhos sugeridos:**
- `Ctrl+N` - Nova pasta
- `Ctrl+U` - Upload
- `Ctrl+F` - Buscar
- `Ctrl+K` - Command palette (futuro)
- `ESC` - Fechar modal

---

### 15. Command Palette (Pesquisa Universal)
**Status:** 📋 Planejamento

**Biblioteca:** `cmdk`

```typescript
import { Command } from 'cmdk';

<Command.Dialog open={open} onOpenChange={setOpen}>
  <Command.Input placeholder="Digite um comando ou busca..." />
  <Command.List>
    <Command.Empty>Nenhum resultado encontrado.</Command.Empty>

    <Command.Group heading="Ações">
      <Command.Item onSelect={() => setDialogOpen(true)}>
        <FolderPlus /> Nova Pasta
      </Command.Item>
      <Command.Item onSelect={() => setUploadDialogOpen(true)}>
        <Upload /> Upload de Documento
      </Command.Item>
    </Command.Group>

    <Command.Group heading="Documentos Recentes">
      {recentDocs.map((doc) => (
        <Command.Item key={doc.id} onSelect={() => openDocument(doc)}>
          <FileIcon /> {doc.title}
        </Command.Item>
      ))}
    </Command.Group>
  </Command.List>
</Command.Dialog>
```

**Atalho:** `Ctrl+K` ou `Cmd+K`

---

### 16. Drag & Drop entre Pastas
**Status:** 📋 Planejamento

**Biblioteca:** `@dnd-kit/core`

```typescript
import { DndContext, closestCenter, useDraggable, useDroppable } from '@dnd-kit/core';

// Pasta como drop zone
const { setNodeRef: dropRef } = useDroppable({
  id: folder.id,
});

// Documento como draggable
const { attributes, listeners, setNodeRef: dragRef } = useDraggable({
  id: document.id,
  data: { type: 'document', ...document },
});

// Handler
const handleDragEnd = async (event) => {
  const { active, over } = event;

  if (over && active.data.current.type === 'document') {
    await documentService.update(active.id, {
      folder_id: over.id,
    });

    toast({
      variant: 'success',
      title: 'Documento movido',
      description: `"${active.data.current.title}" movido para nova pasta`,
    });
  }
};
```

---

## 📱 MOBILE

### 17. Gestos Touch
**Status:** 📋 Planejamento

```typescript
import { useSwipeable } from 'react-swipeable';

const handlers = useSwipeable({
  onSwipedLeft: () => openActionsMenu(), // Swipe left → menu de ações
  onSwipedRight: () => navigateBack(),   // Swipe right → voltar
  preventScrollOnSwipe: true,
});

<div {...handlers}>
  <DocumentCard />
</div>
```

---

### 18. PWA (Progressive Web App)
**Status:** 📋 Planejamento

**Features:**
- Instalável na home screen
- Funciona offline (cache)
- Push notifications
- Acesso à câmera (para scan de docs)

```typescript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
});

module.exports = withPWA({
  // ... config
});

// manifest.json
{
  "name": "Conecta PRO - GED",
  "short_name": "GED",
  "description": "Gestão Eletrônica de Documentos",
  "icons": [...],
  "start_url": "/modulos/documentos",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
```

---

## 🎯 PRIORIZAÇÃO

### Sprint 1 (1 semana) - Performance
1. ✅ Debounce na busca
2. ✅ React Query para cache
3. ✅ Lazy loading de modais

### Sprint 2 (1 semana) - Upload
4. ✅ Compressão de imagens client-side
5. ✅ Validação server-side de arquivos
6. ✅ Thumbnails otimizados

### Sprint 3 (2 semanas) - Busca
7. ✅ Elasticsearch
8. ✅ Busca full-text
9. ✅ Autocomplete

### Sprint 4 (1 semana) - UX
10. ✅ Keyboard shortcuts
11. ✅ Command palette
12. ✅ Drag & drop

### Sprint 5 (2 semanas) - Mobile
13. ✅ PWA
14. ✅ Gestos touch
15. ✅ Otimização mobile

---

## 📊 MÉTRICAS DE SUCESSO

### Performance
- Time to Interactive: <2s
- First Contentful Paint: <1s
- Largest Contentful Paint: <2.5s
- Cumulative Layout Shift: <0.1

### Engagement
- Taxa de upload bem-sucedido: >95%
- Taxa de erro em buscas: <2%
- Tempo médio de navegação: <30s para encontrar documento

### Escalabilidade
- Suportar 10.000+ documentos sem degradação
- Upload simultâneo de 10+ arquivos
- 100+ usuários simultâneos

---

**Documento criado em:** 23/01/2026
**Próxima revisão:** 23/02/2026
**Owner:** Equipe de Desenvolvimento Conecta PRO
