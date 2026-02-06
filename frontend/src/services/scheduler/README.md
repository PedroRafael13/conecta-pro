# Scheduler Services & Hooks

Módulo de Agendamento e Background Jobs - Sprint 35 Task Scheduler

## 📋 Visão Geral

Implementação completa de service layer + hooks React Query para gerenciamento de tarefas agendadas, filas de execução, workers e locks distribuídos.

**Cobertura:** 26 endpoints
- **Tasks:** 9 endpoints (CRUD, controle, stats)
- **Executions:** 4 endpoints (histórico, logs, cancelamento)
- **Queue:** 4 endpoints (enqueue, listagem, stats)
- **Workers:** 3 endpoints (monitoramento, stats)
- **Locks:** 4 endpoints (adquirir, liberar, renovar)
- **Operations:** 2 endpoints (admin)

## 🏗️ Arquitetura

```
scheduler/
├── services/          # Service Layer (axios)
│   ├── tasks.service.ts
│   ├── executions.service.ts
│   ├── queue.service.ts
│   ├── workers.service.ts
│   ├── locks.service.ts
│   ├── operations.service.ts
│   └── index.ts
│
├── hooks/            # React Query Hooks
│   ├── useTasks.ts
│   ├── useExecutions.ts
│   ├── useQueue.ts
│   ├── useWorkers.ts
│   ├── useLocks.ts
│   ├── useOperations.ts
│   └── index.ts
│
└── types/            # TypeScript (Orval)
    └── generated/scheduler/
```

## 🚀 Uso Rápido

### Tasks (Tarefas Agendadas)

```typescript
import {
  useTasks,
  useCreateTask,
  useTriggerTask,
  useTaskStats
} from '@/hooks/scheduler';

function TasksPage() {
  // Listar tarefas
  const { data: tasks, isLoading } = useTasks({
    status: 'active',
    category: 'REPORT',
    page: 1,
    page_size: 20
  });

  // Criar nova tarefa
  const createMutation = useCreateTask();

  const handleCreate = async () => {
    await createMutation.mutateAsync({
      name: 'Relatório Diário',
      description: 'Gerar relatório automático',
      task_type: 'CRON',
      category: 'REPORT',
      cron_expression: '0 8 * * *', // Todo dia às 8h
      handler: 'generate_daily_report',
      timeout_seconds: 3600,
      max_retries: 3,
      priority: 5,
      queue_name: 'default',
      notify_on_failure: true
    });
  };

  // Disparar manualmente
  const triggerMutation = useTriggerTask();

  const handleTrigger = async (taskId: string) => {
    await triggerMutation.mutateAsync({
      taskId,
      body: {
        override_args: { force: true },
        priority: 10
      }
    });
  };

  // Estatísticas
  const { data: stats } = useTaskStats(30);

  return (
    <div>
      <h1>Total: {stats?.total_tasks}</h1>
      {tasks?.items.map(task => (
        <TaskCard
          key={task.id}
          task={task}
          onTrigger={() => handleTrigger(task.id)}
        />
      ))}
    </div>
  );
}
```

### Executions (Histórico)

```typescript
import {
  useExecutions,
  useExecution,
  useExecutionLogs,
  useCancelExecution
} from '@/hooks/scheduler';

function ExecutionDetail({ executionId }: Props) {
  // Dados da execução (auto-refresh 30s)
  const { data: execution } = useExecution(executionId);

  // Logs em tempo real
  const { data: logs } = useExecutionLogs(executionId, {
    level: 'ERROR',
    limit: 100
  });

  // Cancelar execução
  const cancelMutation = useCancelExecution();

  const handleCancel = async () => {
    await cancelMutation.mutateAsync({
      executionId,
      reason: 'Cancelado pelo usuário'
    });
  };

  return (
    <div>
      <h2>Status: {execution?.status}</h2>
      <p>Duração: {execution?.duration_seconds}s</p>
      <p>Progresso: {execution?.progress_percent}%</p>

      <LogViewer logs={logs} />

      {execution?.status === 'PENDING' && (
        <button onClick={handleCancel}>Cancelar</button>
      )}
    </div>
  );
}
```

### Queue (Filas)

```typescript
import {
  useQueueItems,
  useEnqueueItem,
  useQueueStats
} from '@/hooks/scheduler';

function QueueMonitor() {
  // Listar itens (auto-refresh 30s)
  const { data: items } = useQueueItems({
    queue_name: 'default',
    status: 'PENDING',
    limit: 50
  });

  // Adicionar à fila
  const enqueueMutation = useEnqueueItem();

  const handleEnqueue = async () => {
    await enqueueMutation.mutateAsync({
      handler: 'process_invoice',
      payload: { invoice_id: '123' },
      queue_name: 'billing',
      priority: 'HIGH',
      timeout_seconds: 1800,
      max_attempts: 3
    });
  };

  // Estatísticas da fila
  const { data: stats } = useQueueStats('default');

  return (
    <div>
      <h2>Fila: {stats?.queue_name}</h2>
      <p>Pendentes: {stats?.by_status.pending}</p>
      <p>Idade mais antiga: {stats?.oldest_pending_age_seconds}s</p>
    </div>
  );
}
```

### Workers (Monitoramento)

```typescript
import {
  useWorkers,
  useWorkerStats
} from '@/hooks/scheduler';

function WorkersMonitor() {
  // Listar workers (auto-refresh 1min)
  const { data: workers } = useWorkers({
    status: 'BUSY',
    queue_name: 'default'
  });

  // Estatísticas consolidadas
  const { data: stats } = useWorkerStats();

  return (
    <div>
      <h2>Workers: {stats?.total_workers}</h2>
      <p>Ativos: {stats?.active_workers}</p>
      <p>Ocupados: {stats?.busy_workers}</p>
      <p>Utilização: {stats?.avg_utilization.toFixed(1)}%</p>

      {workers?.map(worker => (
        <WorkerCard
          key={worker.id}
          worker={worker}
          utilization={(worker.tasks_in_progress / worker.concurrency) * 100}
        />
      ))}
    </div>
  );
}
```

### Locks (Controle Distribuído)

```typescript
import {
  useLocks,
  useAcquireLock,
  useReleaseLock,
  useRenewLock
} from '@/hooks/scheduler';

function LockManager() {
  const { data: locks } = useLocks();
  const acquireMutation = useAcquireLock();
  const releaseMutation = useReleaseLock();
  const renewMutation = useRenewLock();

  const handleAcquire = async () => {
    try {
      const lock = await acquireMutation.mutateAsync({
        lock_key: 'billing:invoice-generation',
        lock_name: 'Geração de Faturas',
        ttl_seconds: 3600,
        reason: 'Processamento batch de faturas'
      });
      console.log('Lock adquirido:', lock.id);
    } catch (error) {
      console.error('Lock já em uso');
    }
  };

  const handleRenew = async (lockKey: string) => {
    await renewMutation.mutateAsync({
      lockKey,
      ttlSeconds: 1800
    });
  };

  return (
    <div>
      {locks?.map(lock => (
        <LockCard
          key={lock.id}
          lock={lock}
          onRenew={() => handleRenew(lock.lock_key)}
          onRelease={() => releaseMutation.mutate(lock.lock_key)}
        />
      ))}
    </div>
  );
}
```

## 📊 Tipos de Tarefas

### CRON (Agendamento Periódico)

```typescript
{
  task_type: 'CRON',
  cron_expression: '0 8 * * *', // Todo dia às 8h
  timezone: 'America/Sao_Paulo'
}
```

### INTERVAL (Intervalo Fixo)

```typescript
{
  task_type: 'INTERVAL',
  interval_seconds: 3600 // A cada hora
}
```

### ONE_TIME (Execução Única)

```typescript
{
  task_type: 'ONE_TIME',
  scheduled_at: new Date('2024-12-31T23:59:59')
}
```

## 🎯 Categorias

- `REPORT` - Relatórios
- `SYNC` - Sincronizações
- `NOTIFICATION` - Notificações
- `CLEANUP` - Limpeza de dados
- `BACKUP` - Backups
- `INTEGRATION` - Integrações externas
- `CUSTOM` - Personalizado

## 🔄 Auto-Refresh

Os hooks implementam auto-refresh inteligente:

- **Tasks List:** 30s staleTime
- **Executions:** 10s staleTime, 30s refetchInterval
- **Queue Items:** 10s staleTime, 30s refetchInterval
- **Workers:** 30s staleTime, 1min refetchInterval
- **Stats:** 1-2min staleTime

## 🔐 Permissões

### Operações Admin

Requerem role `admin` ou `system`:

```typescript
import { useRunSchedulerCycle } from '@/hooks/scheduler';

// Apenas admin pode executar
const runCycleMutation = useRunSchedulerCycle();
```

## 🎨 Query Keys

Estrutura hierárquica para invalidação eficiente:

```typescript
// Tasks
['scheduler', 'tasks']
['scheduler', 'tasks', 'list']
['scheduler', 'tasks', 'list', { filters }]
['scheduler', 'tasks', 'detail', taskId]
['scheduler', 'tasks', 'stats']

// Executions
['scheduler', 'executions']
['scheduler', 'executions', 'list', { filters }]
['scheduler', 'executions', 'detail', executionId]

// Queue
['scheduler', 'queue']
['scheduler', 'queue', 'stats', queueName]

// Workers
['scheduler', 'workers']
['scheduler', 'workers', 'stats']

// Locks
['scheduler', 'locks']
```

## 📝 Exemplos de Handlers

### Python (Backend)

```python
# modules/scheduler/handlers/report_handler.py

@task_handler("generate_daily_report")
def generate_daily_report(tenant_id: str, **kwargs):
    """Gera relatório diário."""
    report = ReportService.generate(tenant_id)
    return {"report_id": report.id, "status": "success"}
```

### Registro no Frontend

```typescript
const task = await createTask({
  name: 'Relatório Diário',
  handler: 'generate_daily_report',
  handler_module: 'modules.scheduler.handlers.report_handler',
  handler_args: {},
  handler_kwargs: { format: 'pdf' },
  cron_expression: '0 8 * * *'
});
```

## 🚨 Tratamento de Erros

```typescript
const mutation = useCreateTask();

try {
  await mutation.mutateAsync(taskData);
  toast.success('Tarefa criada!');
} catch (error) {
  if (error.response?.status === 400) {
    toast.error('Dados inválidos');
  } else if (error.response?.status === 409) {
    toast.error('Conflito: tarefa já existe');
  } else {
    toast.error('Erro ao criar tarefa');
  }
}
```

## 🎯 Best Practices

### 1. Usar Debounce em Filtros

```typescript
const [filters, setFilters] = useState({});
const debouncedFilters = useDebounce(filters, 500);
const { data } = useTasks(debouncedFilters);
```

### 2. Invalidação Seletiva

```typescript
// Invalida apenas tasks lists
queryClient.invalidateQueries({
  queryKey: taskKeys.lists()
});

// Invalida task específica
queryClient.invalidateQueries({
  queryKey: taskKeys.detail(taskId)
});
```

### 3. Otimistic Updates

```typescript
const mutation = usePauseTask();

mutation.mutate(taskId, {
  onMutate: async (taskId) => {
    await queryClient.cancelQueries({ queryKey: taskKeys.detail(taskId) });

    const previousTask = queryClient.getQueryData(taskKeys.detail(taskId));

    queryClient.setQueryData(taskKeys.detail(taskId), (old) => ({
      ...old,
      status: 'PAUSED'
    }));

    return { previousTask };
  },
  onError: (err, taskId, context) => {
    queryClient.setQueryData(
      taskKeys.detail(taskId),
      context.previousTask
    );
  }
});
```

## 📦 Dependências

- `@tanstack/react-query`: ^5.90.19
- `axios`: ^1.13.2
- Tipos gerados via `Orval`: ^7.13.2

## 🔄 Regenerar Tipos

```bash
# Backend: Extrair OpenAPI
cd /opt/conecta-pro/backend
python3 scripts/extract_openapi_scheduler.py

# Frontend: Gerar tipos
cd /opt/conecta-pro/frontend
npm run orval:scheduler
```

## 📚 Recursos

- **Backend Controller:** `/opt/conecta-pro/backend/modules/scheduler/controllers/scheduler_controller.py`
- **Backend Service:** `/opt/conecta-pro/backend/modules/scheduler/services/scheduler_service.py`
- **OpenAPI Spec:** `/opt/conecta-pro/frontend/openapi-scheduler.json`
- **Tipos Gerados:** `/opt/conecta-pro/frontend/src/types/generated/scheduler/`

## ✅ Status

**Implementação:** 100% completa
- ✅ OpenAPI extraído (26 endpoints)
- ✅ Tipos TypeScript gerados (147 arquivos)
- ✅ Services criados (6 arquivos)
- ✅ Hooks React Query (6 arquivos)
- ✅ Documentação completa
- ✅ Auto-refresh configurado
- ✅ Query keys hierárquicos
- ✅ Type-safe

**Sprint 35 - Task Scheduler** 🚀
