# Exemplos de Uso - Templates de Escalas

## Importação

```typescript
// Importar componente principal
import { TemplateManager } from '@/features/escalas/components/TemplateManager';

// Ou importar componentes individuais
import {
  TemplateCard,
  CreateTemplateDialog,
  EditTemplateDialog,
  ApplyTemplateDialog,
} from '@/features/escalas/components';
```

## Uso Básico

### 1. Usar TemplateManager (Recomendado)

```tsx
import { TemplateManager } from '@/features/escalas/components';

export default function MyPage() {
  return (
    <div className="container">
      <TemplateManager />
    </div>
  );
}
```

### 2. Em Modal (Como na Página de Escalas)

```tsx
import { useState } from 'react';
import { Modal } from '@/components/ui/modal';
import { TemplateManager } from '@/features/escalas/components';

export default function EscalasPage() {
  const [showTemplates, setShowTemplates] = useState(false);

  return (
    <>
      <Button onClick={() => setShowTemplates(true)}>
        Ver Templates
      </Button>

      <Modal
        isOpen={showTemplates}
        onClose={() => setShowTemplates(false)}
        size="full"
      >
        <TemplateManager />
      </Modal>
    </>
  );
}
```

## Uso de Hooks

### useTemplates - Listar Templates

```typescript
import { useTemplates } from '@/hooks/useScaleTemplates';

function MyComponent() {
  const {
    templates,      // Array de templates
    total,          // Total de templates
    page,           // Página atual
    pageSize,       // Itens por página
    totalPages,     // Total de páginas
    isLoading,      // Estado de loading
    error,          // Mensagem de erro
    setPage,        // Mudar página
    setFilters,     // Aplicar filtros
    refresh,        // Recarregar dados
  } = useTemplates(1, 50);

  if (isLoading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error}</div>;

  return (
    <div>
      <h2>Total: {total} templates</h2>
      {templates.map(template => (
        <div key={template.id}>{template.name}</div>
      ))}
    </div>
  );
}
```

### useTemplate - Buscar Template Individual

```typescript
import { useTemplate } from '@/hooks/useScaleTemplates';

function TemplateDetail({ id }: { id: string }) {
  const { template, isLoading, refresh } = useTemplate(id);

  if (isLoading) return <div>Carregando...</div>;
  if (!template) return <div>Template não encontrado</div>;

  return (
    <div>
      <h1>{template.name}</h1>
      <p>{template.description}</p>
      <button onClick={refresh}>Atualizar</button>
    </div>
  );
}
```

### useTemplateOperations - Operações de Template

```typescript
import { useTemplateOperations } from '@/hooks/useScaleTemplates';

function TemplateActions() {
  const {
    createTemplate,
    updateTemplate,
    deleteTemplate,
    applyTemplate,
    previewTemplate,
    isLoading,
  } = useTemplateOperations();

  // Criar template
  const handleCreate = async () => {
    const template = await createTemplate({
      name: 'Meu Template',
      description: 'Descrição do template',
      source_scale_id: 'scale-id-123',
    });

    if (template) {
      console.log('Template criado:', template.id);
    }
  };

  // Editar template
  const handleEdit = async (id: string) => {
    const template = await updateTemplate(id, {
      name: 'Nome Atualizado',
      description: 'Nova descrição',
    });

    if (template) {
      console.log('Template atualizado');
    }
  };

  // Excluir template
  const handleDelete = async (id: string) => {
    const success = await deleteTemplate(id);
    if (success) {
      console.log('Template excluído');
    }
  };

  // Aplicar template
  const handleApply = async (id: string) => {
    const scale = await applyTemplate(id, {
      month: 12,
      year: 2024,
      post_id: 'post-id-456',
    });

    if (scale) {
      console.log('Escala criada:', scale.id);
    }
  };

  // Preview de aplicação
  const handlePreview = async (id: string) => {
    const scale = await previewTemplate(id, {
      month: 12,
      year: 2024,
    });

    if (scale) {
      console.log('Preview:', scale);
    }
  };

  return (
    <div>
      <button onClick={handleCreate} disabled={isLoading}>
        Criar
      </button>
    </div>
  );
}
```

## Uso de Componentes Individuais

### TemplateCard

```tsx
import { TemplateCard } from '@/features/escalas/components';

function MyTemplates() {
  const template = {
    id: '1',
    name: 'Template 12x36',
    description: 'Escala padrão para vigilantes',
    scale_type: '12x36',
    total_employees: 8,
    coverage_percentage: 95,
    pattern_days: 30,
    times_used: 5,
    created_at: '2024-01-01',
    // ... outros campos
  };

  return (
    <TemplateCard
      template={template}
      onUse={(t) => console.log('Usar:', t)}
      onEdit={(t) => console.log('Editar:', t)}
      onDelete={(t) => console.log('Excluir:', t)}
    />
  );
}
```

### CreateTemplateDialog

```tsx
import { useState } from 'react';
import { CreateTemplateDialog } from '@/features/escalas/components';
import { useScales } from '@/hooks/useScales';

function CreateTemplate() {
  const [isOpen, setIsOpen] = useState(false);
  const { scales } = useScales(1, 100);

  const handleCreate = async (data) => {
    console.log('Criar template:', data);
    // Lógica de criação
    setIsOpen(false);
  };

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        Criar Template
      </button>

      <CreateTemplateDialog
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        scales={scales}
        onSubmit={handleCreate}
      />
    </>
  );
}
```

### EditTemplateDialog

```tsx
import { useState } from 'react';
import { EditTemplateDialog } from '@/features/escalas/components';

function EditTemplate({ template }) {
  const [isOpen, setIsOpen] = useState(false);

  const handleEdit = async (id, data) => {
    console.log('Editar:', id, data);
    setIsOpen(false);
  };

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        Editar
      </button>

      <EditTemplateDialog
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        template={template}
        onSubmit={handleEdit}
      />
    </>
  );
}
```

### ApplyTemplateDialog

```tsx
import { useState } from 'react';
import { ApplyTemplateDialog } from '@/features/escalas/components';
import { usePosts } from '@/hooks/usePosts';

function ApplyTemplate({ template }) {
  const [isOpen, setIsOpen] = useState(false);
  const { posts } = usePosts({ initialPageSize: 100 });

  const handleApply = async (data) => {
    console.log('Aplicar template:', data);
    // Retornar a escala criada
    return { id: '123', /* ... */ };
  };

  const handlePreview = async (data) => {
    console.log('Preview:', data);
    // Retornar preview da escala
    return { id: 'preview', /* ... */ };
  };

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        Aplicar Template
      </button>

      <ApplyTemplateDialog
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        template={template}
        posts={posts}
        onSubmit={handleApply}
        onPreview={handlePreview}
      />
    </>
  );
}
```

## Uso de Serviços Diretamente

```typescript
import { scaleTemplatesService } from '@/lib/services/scale-templates';

// Listar templates
const response = await scaleTemplatesService.list(1, 50, {
  scale_type: '12x36',
  search: 'vigilante',
});

console.log(response.items); // Array de templates
console.log(response.total); // Total

// Buscar por ID
const template = await scaleTemplatesService.getById('template-id');

// Criar
const newTemplate = await scaleTemplatesService.create({
  name: 'Novo Template',
  description: 'Descrição',
  source_scale_id: 'scale-id',
});

// Atualizar
const updated = await scaleTemplatesService.update('template-id', {
  name: 'Nome Atualizado',
});

// Excluir
await scaleTemplatesService.delete('template-id');

// Aplicar
const scale = await scaleTemplatesService.apply('template-id', {
  month: 12,
  year: 2024,
});

// Preview
const preview = await scaleTemplatesService.preview('template-id', {
  month: 12,
  year: 2024,
});
```

## Filtros

```typescript
import { useTemplates } from '@/hooks/useScaleTemplates';

function FilteredTemplates() {
  const { templates, setFilters } = useTemplates(1, 50);

  // Filtrar por tipo de escala
  const filterByType = () => {
    setFilters({ scale_type: '12x36' });
  };

  // Filtrar por posto
  const filterByPost = () => {
    setFilters({ post_id: 'post-id-123' });
  };

  // Busca textual
  const search = (term: string) => {
    setFilters({ search: term });
  };

  // Limpar filtros
  const clearFilters = () => {
    setFilters(undefined);
  };

  return <div>{/* UI */}</div>;
}
```

## Tratamento de Erros

```typescript
import { useTemplateOperations } from '@/hooks/useScaleTemplates';

function HandleErrors() {
  const { createTemplate, error } = useTemplateOperations();

  const handleCreate = async () => {
    const template = await createTemplate({
      name: 'Teste',
      source_scale_id: 'invalid-id',
    });

    if (!template) {
      // Toast de erro foi mostrado automaticamente
      console.error('Erro ao criar:', error);
    }
  };

  return <button onClick={handleCreate}>Criar</button>;
}
```

## Integração com Router

```typescript
import { useRouter } from 'next/navigation';
import { useTemplateOperations } from '@/hooks/useScaleTemplates';

function ApplyAndRedirect() {
  const router = useRouter();
  const { applyTemplate } = useTemplateOperations();

  const handleApply = async (templateId: string) => {
    const scale = await applyTemplate(templateId, {
      month: 12,
      year: 2024,
    });

    if (scale) {
      // Redirecionar para a escala criada
      router.push(`/modulos/operacional/escalas/${scale.id}`);
    }
  };

  return <div>{/* UI */}</div>;
}
```

## Customização de Styles

```tsx
// Customizar cores e estilos via Tailwind
import { TemplateCard } from '@/features/escalas/components';

function CustomCard({ template }) {
  return (
    <div className="custom-container">
      <TemplateCard
        template={template}
        onUse={handleUse}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}

// CSS customizado
const styles = `
  .custom-container {
    /* Seus estilos aqui */
  }
`;
```

## Boas Práticas

### 1. Sempre use hooks para state management
```typescript
// ✅ Bom
const { templates, isLoading } = useTemplates();

// ❌ Evite
const [templates, setTemplates] = useState([]);
// Reimplementar lógica que já existe no hook
```

### 2. Use o TemplateManager quando possível
```typescript
// ✅ Bom - Usa componente completo
<TemplateManager />

// ❌ Evite - Reimplementar tudo
// Criar sua própria lógica de listagem, cards, etc.
```

### 3. Trate erros apropriadamente
```typescript
// ✅ Bom
const template = await createTemplate(data);
if (!template) {
  // Tratar erro (toast já foi mostrado)
  return;
}

// ❌ Evite ignorar erros
await createTemplate(data); // Sem verificar resultado
```

### 4. Use TypeScript corretamente
```typescript
// ✅ Bom
import type { ScaleTemplate } from '@/types/operacional';

function MyComponent({ template }: { template: ScaleTemplate }) {
  // ...
}

// ❌ Evite any
function MyComponent({ template }: { template: any }) {
  // ...
}
```
