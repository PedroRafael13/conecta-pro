# Workflows Module - Guia de Uso

## Visão Geral

Módulo completo de Workflows e Automações do Conecta PRO com **100% de cobertura** dos 9 endpoints do backend.

## Instalação

Tipos TypeScript já estão gerados. Para regenerar:

```bash
npm run orval:workflows
```

## Imports

```typescript
// Services
import { WorkflowService, ExecutionService } from '@/services/workflows';

// Hooks
import {
  useWorkflowList,
  useWorkflow,
  useCreateWorkflow,
  useUpdateWorkflow,
  useDeleteWorkflow,
  useActivateWorkflow,
  useDeactivateWorkflow,
  useExecutionList,
  useCancelExecution,
  useExecutionStats,
} from '@/hooks/workflows';

// Types
import type {
  WorkflowResponse,
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowStatus,
  WorkflowCategory,
  ExecutionResponse,
  ExecutionStatus,
} from '@/hooks/workflows';
```

## Exemplos de Uso

### 1. Listar Workflows

```typescript
function WorkflowList() {
  const tenantId = 'your-tenant-id';

  const { data, isLoading, error } = useWorkflowList({
    tenant_id: tenantId,
    status: 'ACTIVE',
    skip: 0,
    limit: 20,
  });

  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;

  const workflows = data?.data || [];

  return (
    <div>
      {workflows.map((workflow) => (
        <WorkflowCard key={workflow.id} workflow={workflow} />
      ))}
    </div>
  );
}
```

### 2. Criar Workflow

```typescript
function CreateWorkflowForm() {
  const createWorkflow = useCreateWorkflow({
    onSuccess: (response) => {
      toast.success(`Workflow ${response.data.name} criado!`);
    },
    onError: (error) => {
      toast.error('Erro ao criar workflow');
    },
  });

  const handleSubmit = (formData: any) => {
    const workflowData: WorkflowCreate = {
      tenant_id: 'your-tenant-id',
      name: formData.name,
      description: formData.description,
      category: formData.category as WorkflowCategory,
      tags: formData.tags,
    };

    createWorkflow.mutate(workflowData);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={createWorkflow.isPending}>
        {createWorkflow.isPending ? 'Criando...' : 'Criar Workflow'}
      </button>
    </form>
  );
}
```

### 3. Atualizar Workflow

```typescript
function EditWorkflow({ workflowId }: { workflowId: string }) {
  const { data: workflow } = useWorkflow(workflowId);
  const updateWorkflow = useUpdateWorkflow();

  const handleUpdate = (updates: Partial<WorkflowUpdate>) => {
    updateWorkflow.mutate({
      workflowId,
      data: updates,
    });
  };

  return (
    <div>
      <h2>{workflow?.data.name}</h2>
      <button onClick={() => handleUpdate({ name: 'Novo Nome' })}>
        Atualizar Nome
      </button>
    </div>
  );
}
```

### 4. Ativar/Desativar Workflow

```typescript
function WorkflowActions({ workflowId }: { workflowId: string }) {
  const { data: workflow } = useWorkflow(workflowId);
  const activateWorkflow = useActivateWorkflow();
  const deactivateWorkflow = useDeactivateWorkflow();

  const isActive = workflow?.data.status === 'ACTIVE';

  const handleToggle = () => {
    if (isActive) {
      deactivateWorkflow.mutate(workflowId);
    } else {
      activateWorkflow.mutate(workflowId);
    }
  };

  return (
    <button onClick={handleToggle}>
      {isActive ? 'Desativar' : 'Ativar'}
    </button>
  );
}
```

### 5. Deletar Workflow

```typescript
function DeleteWorkflowButton({ workflowId }: { workflowId: string }) {
  const deleteWorkflow = useDeleteWorkflow({
    onSuccess: () => {
      toast.success('Workflow deletado!');
      router.push('/workflows');
    },
  });

  const handleDelete = () => {
    if (confirm('Tem certeza que deseja deletar este workflow?')) {
      deleteWorkflow.mutate(workflowId);
    }
  };

  return (
    <button onClick={handleDelete} disabled={deleteWorkflow.isPending}>
      {deleteWorkflow.isPending ? 'Deletando...' : 'Deletar'}
    </button>
  );
}
```

### 6. Listar Execuções

```typescript
function ExecutionList({ workflowId }: { workflowId: string }) {
  const { data, isLoading } = useExecutionList(workflowId, {
    skip: 0,
    limit: 50,
  });

  const executions = data?.data || [];

  return (
    <div>
      <h3>Histórico de Execuções</h3>
      {executions.map((execution) => (
        <ExecutionRow key={execution.id} execution={execution} />
      ))}
    </div>
  );
}
```

### 7. Monitorar Execuções em Tempo Real

```typescript
function ExecutionMonitor({ workflowId }: { workflowId: string }) {
  // Auto-refresh a cada 5 segundos
  const { data } = useRunningExecutions(workflowId, {
    refetchInterval: 5000,
  });

  const runningExecutions = data?.data || [];

  return (
    <div>
      <h3>Execuções em Andamento ({runningExecutions.length})</h3>
      {runningExecutions.map((execution) => (
        <div key={execution.id}>
          <Progress
            value={ExecutionService.getExecutionProgress(execution)}
          />
          <span>{ExecutionService.formatStatus(execution.status)}</span>
        </div>
      ))}
    </div>
  );
}
```

### 8. Cancelar Execução

```typescript
function CancelExecutionButton({ executionId }: { executionId: string }) {
  const cancelExecution = useCancelExecution({
    onSuccess: () => {
      toast.success('Execução cancelada');
    },
  });

  return (
    <button
      onClick={() => cancelExecution.mutate(executionId)}
      disabled={cancelExecution.isPending}
    >
      Cancelar Execução
    </button>
  );
}
```

### 9. Estatísticas de Execuções

```typescript
function ExecutionStats({ workflowId }: { workflowId: string }) {
  const { data: stats } = useExecutionStats(workflowId);

  if (!stats) return null;

  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard
        label="Total"
        value={stats.total}
        icon="FileText"
      />
      <StatCard
        label="Taxa de Sucesso"
        value={`${stats.successRate.toFixed(1)}%`}
        icon="CheckCircle"
        color="success"
      />
      <StatCard
        label="Taxa de Falha"
        value={`${stats.failureRate.toFixed(1)}%`}
        icon="XCircle"
        color="error"
      />
      <StatCard
        label="Tempo Médio"
        value={ExecutionService.formatExecutionTime(stats.avgExecutionTime)}
        icon="Clock"
      />
    </div>
  );
}
```

### 10. Filtros e Helpers

```typescript
function WorkflowFilters() {
  const tenantId = 'your-tenant-id';

  // Listar workflows ativos
  const { data: activeWorkflows } = useActiveWorkflows(tenantId);

  // Listar workflows por categoria
  const { data: crmWorkflows } = useWorkflowsByCategory(tenantId, 'CRM');

  // Listar workflows por status
  const { data: draftWorkflows } = useWorkflowsByStatus(tenantId, 'DRAFT');

  // Usar helpers do service
  const workflows = activeWorkflows?.data || [];
  const successRate = workflows.map(w => WorkflowService.getSuccessRate(w));
  const topPerformers = WorkflowService.sortBySuccessRate(workflows);

  return (
    <div>
      <h3>Workflows com Melhor Performance</h3>
      {topPerformers.slice(0, 5).map((workflow) => (
        <WorkflowCard
          key={workflow.id}
          workflow={workflow}
          successRate={WorkflowService.getSuccessRate(workflow)}
        />
      ))}
    </div>
  );
}
```

## Helpers Disponíveis

### WorkflowService

```typescript
// Status e validação
WorkflowService.isWorkflowActive(workflow);
WorkflowService.validateCreateData(data);

// Métricas
WorkflowService.getSuccessRate(workflow);
WorkflowService.getFailureRate(workflow);

// Formatação
WorkflowService.formatCategory(category);
WorkflowService.formatStatus(status);
WorkflowService.getStatusColor(status);
WorkflowService.getStatusIcon(status);

// Utilitários
WorkflowService.generateSlug(name);
WorkflowService.filterByCategory(workflows, 'CRM');
WorkflowService.filterByStatus(workflows, 'ACTIVE');
WorkflowService.sortBySuccessRate(workflows);
```

### ExecutionService

```typescript
// Status
ExecutionService.isExecutionRunning(execution);
ExecutionService.isExecutionCompleted(execution);
ExecutionService.canCancelExecution(execution);

// Métricas
ExecutionService.getExecutionProgress(execution);
ExecutionService.getExecutionStats(executions);

// Formatação
ExecutionService.formatStatus(status);
ExecutionService.formatExecutionTime(ms);
ExecutionService.getStatusColor(status);
ExecutionService.getStatusIcon(status);

// Filtros
ExecutionService.filterByStatus(executions, 'COMPLETED');
ExecutionService.filterSuccessful(executions);
ExecutionService.filterFailed(executions);
ExecutionService.groupByStatus(executions);
```

## Enums e Tipos

### WorkflowStatus

```typescript
'DRAFT' | 'ACTIVE' | 'INACTIVE' | 'PAUSED' | 'ARCHIVED' | 'ERROR'
```

### WorkflowCategory

```typescript
'CRM' | 'HR' | 'FINANCE' | 'OPERATIONS' | 'ONBOARDING' | 'MARKETING' |
'SUPPORT' | 'COMMUNICATION' | 'DOCUMENT' | 'INTEGRATION' | 'MAINTENANCE' |
'SECURITY' | 'ANALYTICS' | 'CUSTOM'
```

### ExecutionStatus

```typescript
'PENDING' | 'QUEUED' | 'RUNNING' | 'PAUSED' | 'WAITING' | 'RETRYING' |
'COMPLETED' | 'FAILED' | 'CANCELLED' | 'TIMEOUT'
```

## Performance

- Hooks com cache otimizado (React Query)
- Auto-invalidação de cache em mutations
- Refetch automático para monitoring
- Stale time configurável
- Background refetch para monitoring

## Próximos Passos

1. Implementar componentes UI
2. Criar workflow designer visual
3. Adicionar validação de schemas
4. Implementar webhooks
5. Analytics avançado
