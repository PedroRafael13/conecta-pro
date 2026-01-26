# Feature: Templates de Escalas

## Visão Geral

Sistema completo de gerenciamento de templates de escalas de trabalho, permitindo criar, editar, aplicar e gerenciar templates reutilizáveis a partir de escalas existentes.

## Componentes

### TemplateManager
Componente principal que gerencia toda a interface de templates.

**Localização:** `/src/features/escalas/components/TemplateManager.tsx`

**Funcionalidades:**
- Listagem de templates em grid responsivo (1/2/3 colunas)
- Busca e filtros
- Estados de loading, empty e error
- Integração com todos os dialogs

### TemplateCard
Card visual que representa um template individual.

**Localização:** `/src/features/escalas/components/TemplateCard.tsx`

**Features:**
- Menu dropdown com ações (Usar, Editar, Excluir)
- Métricas visuais (colaboradores, cobertura, dias)
- Estatísticas de uso
- Formatação de datas relativas
- Hover effects e transições

### CreateTemplateDialog
Dialog wizard para criar novos templates.

**Localização:** `/src/features/escalas/components/CreateTemplateDialog.tsx`

**Workflow:**
1. Seleciona escala base (apenas publicadas/completas)
2. Preview da escala selecionada
3. Define nome e descrição
4. Validações client-side
5. Criação com feedback toast

### EditTemplateDialog
Dialog simples para editar templates existentes.

**Localização:** `/src/features/escalas/components/EditTemplateDialog.tsx`

**Features:**
- Edição de nome e descrição
- Validação de campos obrigatórios
- Feedback via toast

### ApplyTemplateDialog
Dialog wizard multi-step para aplicar templates.

**Localização:** `/src/features/escalas/components/ApplyTemplateDialog.tsx`

**Steps:**
1. **Período:** Seleção de mês/ano e posto (opcional)
2. **Preview:** Visualização da escala que será criada
3. **Confirmação:** Resumo e criação final

**Features:**
- Preview dinâmico via backend
- Navegação entre steps
- Loading states
- Redirecionamento automático após criação

## Hooks

### useTemplates
Hook para listagem de templates com paginação.

```typescript
const { templates, total, isLoading, refresh } = useTemplates();
```

### useTemplate
Hook para buscar template individual.

```typescript
const { template, isLoading, refresh } = useTemplate(id);
```

### useTemplateOperations
Hook para mutations (criar, editar, excluir, aplicar).

```typescript
const {
  createTemplate,
  updateTemplate,
  deleteTemplate,
  applyTemplate,
  previewTemplate,
  isLoading
} = useTemplateOperations();
```

**Features:**
- Toast automático para todas operações
- Error handling
- Loading states

## Serviços

### scaleTemplatesService
Serviço de integração com backend API.

**Localização:** `/src/lib/services/scale-templates.ts`

**Endpoints:**
- `GET /api/v1/operacional/scales/templates` - Listar
- `GET /api/v1/operacional/scales/templates/{id}` - Buscar
- `POST /api/v1/operacional/scales/templates` - Criar
- `PATCH /api/v1/operacional/scales/templates/{id}` - Atualizar
- `DELETE /api/v1/operacional/scales/templates/{id}` - Excluir
- `POST /api/v1/operacional/scales/templates/{id}/apply` - Aplicar
- `POST /api/v1/operacional/scales/templates/{id}/preview` - Preview

## Types

### ScaleTemplate
```typescript
interface ScaleTemplate {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  scale_type: ScaleType;
  post_id: string | null;
  post_name?: string | null;
  source_scale_id: string;
  total_employees: number;
  coverage_percentage: number;
  pattern_days: number;
  times_used: number;
  last_used_at: string | null;
  created_by: string | null;
  created_by_name?: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}
```

### ScaleTemplateCreate
```typescript
interface ScaleTemplateCreate {
  name: string;
  description?: string | null;
  source_scale_id: string;
}
```

### ScaleTemplateUpdate
```typescript
interface ScaleTemplateUpdate {
  name?: string;
  description?: string | null;
  is_active?: boolean;
}
```

### ScaleTemplateApply
```typescript
interface ScaleTemplateApply {
  month: number;
  year: number;
  post_id?: string | null;
  employee_substitutions?: Record<string, string>;
}
```

## Integração

### Na Página de Escalas

O TemplateManager está integrado na página principal de escalas via modal:

```typescript
// /src/app/modulos/operacional/escalas/page.tsx

<Button variant="outline" onClick={() => setShowTemplatesModal(true)}>
  <FileText className="w-4 h-4 mr-2" />
  Templates
</Button>

<Modal isOpen={showTemplatesModal} onClose={() => setShowTemplatesModal(false)}>
  <TemplateManager />
</Modal>
```

### Página Dedicada

Também existe uma rota dedicada para templates:

**URL:** `/modulos/operacional/escalas/templates`

**Arquivo:** `/src/app/modulos/operacional/escalas/templates/page.tsx`

## UX/UI

### Responsividade
- **Mobile:** 1 coluna
- **Tablet:** 2 colunas
- **Desktop:** 3 colunas

### Estados Visuais
- **Loading:** Skeleton cards animados
- **Empty (sem busca):** CTA para criar primeiro template
- **Empty (com busca):** Mensagem de nenhum resultado
- **Error:** Mensagens de erro via toast

### Feedback
- **Toast de sucesso:** Operações bem-sucedidas
- **Toast de erro:** Falhas com mensagem descritiva
- **Loading spinners:** Durante operações
- **Disabled states:** Botões durante loading

### Acessibilidade
- Keyboard navigation
- Focus management
- ARIA labels
- Modal overlay dismiss

## Fluxo de Uso

### 1. Criar Template
1. Usuário clica em "Novo Template"
2. Seleciona escala base (filtrada: apenas publicadas)
3. Visualiza preview da escala
4. Define nome e descrição
5. Confirma criação
6. Recebe feedback de sucesso

### 2. Aplicar Template
1. Usuário clica em "Usar Template" no card
2. Seleciona mês/ano destino
3. (Opcional) Seleciona posto diferente
4. Visualiza preview da escala que será criada
5. Confirma aplicação
6. Sistema cria escala em modo rascunho
7. Redirecionamento automático para edição

### 3. Editar Template
1. Menu dropdown → "Editar"
2. Altera nome/descrição
3. Salva alterações
4. Feedback de sucesso

### 4. Excluir Template
1. Menu dropdown → "Excluir"
2. Modal de confirmação
3. Confirmação → exclusão
4. Feedback de sucesso

## Dependências

- `lucide-react`: Ícones
- `date-fns`: Formatação de datas
- `react`: Framework
- `next`: Routing e SSR

## Backend Integration

O frontend espera que o backend implemente os endpoints conforme especificado no service. Ver documentação do Agente #6 para detalhes da implementação backend.

## Melhorias Futuras

- [ ] Filtros avançados (por tipo de escala, posto)
- [ ] Ordenação customizada
- [ ] Duplicar template
- [ ] Versionamento de templates
- [ ] Histórico de aplicações
- [ ] Compartilhamento entre tenants
- [ ] Templates favoritos
- [ ] Tags e categorias
- [ ] Preview side-by-side comparison
