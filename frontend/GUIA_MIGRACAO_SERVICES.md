# GUIA DE MIGRAÇÃO: SERVICES MANUAIS → HOOKS ORVAL

**Complemento:** AUDITORIA_SERVICES_MANUAIS.md
**Data:** 2026-01-31

---

## 📚 ÍNDICE

1. [Como Identificar Service a Migrar](#como-identificar)
2. [Padrão de Migração](#padrao-migracao)
3. [Exemplos Práticos](#exemplos-praticos)
4. [Checklist de Migração](#checklist)
5. [Troubleshooting](#troubleshooting)

---

## 🔍 COMO IDENTIFICAR SERVICE A MIGRAR

### Verificar se existe hook Orval:

```bash
# 1. Procurar módulo em types/generated
ls -la src/types/generated/ | grep <modulo>

# 2. Listar hooks disponíveis
ls -la src/types/generated/<modulo>/

# 3. Ver funções disponíveis
grep -E "export.*use.*Api" src/types/generated/<modulo>/*.ts
```

### Exemplos:

```bash
# Security LGPD
ls src/types/generated/security-lgpd/

# Notifications
ls src/types/generated/notifications/

# Scheduler
ls src/types/generated/scheduler/
```

---

## 🔄 PADRÃO DE MIGRAÇÃO

### ANTES (Service Manual):

```typescript
// src/services/notifications/notification.service.ts
import api from '@/lib/api';

export const notificationService = {
  async list(params) {
    const { data } = await api.get('/api/v1/notifications', { params });
    return data;
  },

  async markAsRead(id: string) {
    const { data } = await api.put(`/api/v1/notifications/${id}/read`);
    return data;
  },
};
```

### DEPOIS (Hook Orval):

```typescript
// src/hooks/notifications/useNotifications.ts
import {
  useListNotificationsApiV1NotificationsGet,
  useMarkAsReadApiV1NotificationsNotificationIdReadPut,
} from '@/types/generated/notifications/notifications';

export function useNotifications() {
  // Lista notificações (GET)
  const { data, isLoading, error } = useListNotificationsApiV1NotificationsGet({
    skip: 0,
    limit: 50,
  });

  // Marca como lida (PUT) - mutation
  const markAsRead = useMarkAsReadApiV1NotificationsNotificationIdReadPut();

  const handleMarkAsRead = async (id: string) => {
    await markAsRead.mutateAsync({ notificationId: id });
  };

  return {
    notifications: data,
    isLoading,
    error,
    markAsRead: handleMarkAsRead,
    isMarkingAsRead: markAsRead.isLoading,
  };
}
```

---

## 💡 EXEMPLOS PRÁTICOS

### EXEMPLO 1: Security LGPD - Encryption

#### ANTES (Service Manual):

```typescript
// src/services/security-lgpd/encryptionService.ts
import api from '@/lib/api';

export class EncryptionService {
  static async encrypt(data: string, algorithm: string) {
    const response = await api.post('/api/v1/security-lgpd/encrypt', {
      data,
      algorithm,
    });
    return response.data;
  }

  static async decrypt(encryptedData: string) {
    const response = await api.post('/api/v1/security-lgpd/decrypt', {
      encrypted_data: encryptedData,
    });
    return response.data;
  }
}
```

#### DEPOIS (Hook Orval):

```typescript
// src/hooks/security-lgpd/useEncryption.ts
import {
  useEncryptDataApiV1SecurityLgpdEncryptPost,
  useDecryptDataApiV1SecurityLgpdDecryptPost,
  type EncryptDataRequest,
  type DecryptDataRequest,
} from '@/types/generated/security-lgpd/security-lgpd';

export function useEncryption() {
  const encryptMutation = useEncryptDataApiV1SecurityLgpdEncryptPost();
  const decryptMutation = useDecryptDataApiV1SecurityLgpdDecryptPost();

  const encrypt = async (data: string, algorithm: EncryptDataRequest['algorithm']) => {
    return await encryptMutation.mutateAsync({
      data: {
        data,
        algorithm,
      },
    });
  };

  const decrypt = async (encryptedData: string) => {
    return await decryptMutation.mutateAsync({
      data: {
        encrypted_data: encryptedData,
      },
    });
  };

  return {
    encrypt,
    decrypt,
    isEncrypting: encryptMutation.isLoading,
    isDecrypting: decryptMutation.isLoading,
    encryptError: encryptMutation.error,
    decryptError: decryptMutation.error,
  };
}
```

#### USO NO COMPONENTE:

```typescript
'use client';

import { useState } from 'react';
import { useEncryption } from '@/hooks/security-lgpd/useEncryption';

export function EncryptionForm() {
  const [text, setText] = useState('');
  const { encrypt, isEncrypting } = useEncryption();

  const handleEncrypt = async () => {
    const result = await encrypt(text, 'AES-256');
    console.log('Encrypted:', result.encrypted_data);
  };

  return (
    <div>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <button onClick={handleEncrypt} disabled={isEncrypting}>
        {isEncrypting ? 'Criptografando...' : 'Criptografar'}
      </button>
    </div>
  );
}
```

---

### EXEMPLO 2: Notifications - List & Mark as Read

#### ANTES (Service Manual):

```typescript
// src/services/notifications/notification.service.ts
export const notificationService = {
  async list(params: { skip?: number; limit?: number; unread_only?: boolean }) {
    const { data } = await api.get('/api/v1/notifications', { params });
    return data;
  },

  async markAsRead(id: string) {
    const { data } = await api.put(`/api/v1/notifications/${id}/read`);
    return data;
  },

  async markAllAsRead() {
    const { data } = await api.post('/api/v1/notifications/mark-all-read');
    return data;
  },
};
```

#### DEPOIS (Hook Orval):

```typescript
// src/hooks/notifications/useNotifications.ts
import {
  useListNotificationsApiV1NotificationsGet,
  useMarkAsReadApiV1NotificationsNotificationIdReadPut,
  useMarkAllAsReadApiV1NotificationsMarkAllReadPost,
} from '@/types/generated/notifications/notifications';

export function useNotifications(params?: { unreadOnly?: boolean }) {
  // Query - Lista notificações
  const {
    data: notifications,
    isLoading,
    error,
    refetch,
  } = useListNotificationsApiV1NotificationsGet({
    skip: 0,
    limit: 50,
    unread_only: params?.unreadOnly,
  });

  // Mutation - Marca como lida
  const markAsReadMutation = useMarkAsReadApiV1NotificationsNotificationIdReadPut();

  // Mutation - Marca todas como lidas
  const markAllAsReadMutation = useMarkAllAsReadApiV1NotificationsMarkAllReadPost();

  const markAsRead = async (id: string) => {
    await markAsReadMutation.mutateAsync(
      { notificationId: id },
      {
        onSuccess: () => {
          refetch(); // Recarrega lista
        },
      }
    );
  };

  const markAllAsRead = async () => {
    await markAllAsReadMutation.mutateAsync(
      {},
      {
        onSuccess: () => {
          refetch();
        },
      }
    );
  };

  return {
    notifications,
    isLoading,
    error,
    markAsRead,
    markAllAsRead,
    isMarkingAsRead: markAsReadMutation.isLoading,
    isMarkingAllAsRead: markAllAsReadMutation.isLoading,
    refetch,
  };
}
```

#### USO NO COMPONENTE:

```typescript
'use client';

import { useNotifications } from '@/hooks/notifications/useNotifications';

export function NotificationList() {
  const {
    notifications,
    isLoading,
    markAsRead,
    markAllAsRead,
    isMarkingAsRead,
  } = useNotifications({ unreadOnly: true });

  if (isLoading) return <div>Carregando...</div>;

  return (
    <div>
      <button onClick={markAllAsRead}>Marcar todas como lidas</button>

      {notifications?.items.map((notif) => (
        <div key={notif.id}>
          <p>{notif.message}</p>
          <button
            onClick={() => markAsRead(notif.id)}
            disabled={isMarkingAsRead}
          >
            Marcar como lida
          </button>
        </div>
      ))}
    </div>
  );
}
```

---

### EXEMPLO 3: Scheduler - Tasks (Query Params)

#### ANTES (Service Manual):

```typescript
// src/services/scheduler/tasks.service.ts
export const tasksService = {
  async list(params: { status?: string; page?: number; limit?: number }) {
    const { data } = await api.get('/api/v1/scheduler/tasks', { params });
    return data;
  },

  async create(task: TaskCreate) {
    const { data } = await api.post('/api/v1/scheduler/tasks', task);
    return data;
  },

  async execute(taskId: string) {
    const { data } = await api.post(`/api/v1/scheduler/tasks/${taskId}/execute`);
    return data;
  },
};
```

#### DEPOIS (Hook Orval):

```typescript
// src/hooks/scheduler/useTasks.ts
import {
  useListTasksApiV1SchedulerTasksGet,
  useCreateTaskApiV1SchedulerTasksPost,
  useExecuteTaskApiV1SchedulerTasksTaskIdExecutePost,
  type TaskCreate,
} from '@/types/generated/scheduler/scheduler';

export function useTasks(filters?: { status?: string }) {
  // Query com filtros
  const {
    data: tasks,
    isLoading,
    error,
    refetch,
  } = useListTasksApiV1SchedulerTasksGet({
    status: filters?.status,
    page: 1,
    limit: 50,
  });

  // Mutation - Criar task
  const createMutation = useCreateTaskApiV1SchedulerTasksPost();

  // Mutation - Executar task
  const executeMutation = useExecuteTaskApiV1SchedulerTasksTaskIdExecutePost();

  const createTask = async (task: TaskCreate) => {
    return await createMutation.mutateAsync(
      { data: task },
      {
        onSuccess: () => {
          refetch(); // Atualiza lista
        },
      }
    );
  };

  const executeTask = async (taskId: string) => {
    return await executeMutation.mutateAsync(
      { taskId },
      {
        onSuccess: () => {
          refetch();
        },
      }
    );
  };

  return {
    tasks,
    isLoading,
    error,
    createTask,
    executeTask,
    isCreating: createMutation.isLoading,
    isExecuting: executeMutation.isLoading,
    refetch,
  };
}
```

---

### EXEMPLO 4: Reimbursement - CRUD Completo

#### ANTES (Service Manual):

```typescript
// src/services/reimbursement/reimbursementRequestService.ts
export const reimbursementRequestService = {
  async list(params) {
    const { data } = await api.get('/api/v1/reimbursement/requests', { params });
    return data;
  },

  async getById(id: string) {
    const { data } = await api.get(`/api/v1/reimbursement/requests/${id}`);
    return data;
  },

  async create(request) {
    const { data } = await api.post('/api/v1/reimbursement/requests', request);
    return data;
  },

  async update(id: string, request) {
    const { data } = await api.put(`/api/v1/reimbursement/requests/${id}`, request);
    return data;
  },

  async delete(id: string) {
    await api.delete(`/api/v1/reimbursement/requests/${id}`);
  },
};
```

#### DEPOIS (Hook Orval):

```typescript
// src/hooks/reimbursement/useReimbursementRequests.ts
import {
  useListRequestsApiV1ReimbursementRequestsGet,
  useGetRequestApiV1ReimbursementRequestsRequestIdGet,
  useCreateRequestApiV1ReimbursementRequestsPost,
  useUpdateRequestApiV1ReimbursementRequestsRequestIdPut,
  useDeleteRequestApiV1ReimbursementRequestsRequestIdDelete,
  type ReimbursementRequestCreate,
  type ReimbursementRequestUpdate,
} from '@/types/generated/reimbursement/reimbursement';

export function useReimbursementRequests() {
  // Query - Lista
  const {
    data: requests,
    isLoading,
    error,
    refetch,
  } = useListRequestsApiV1ReimbursementRequestsGet({
    skip: 0,
    limit: 50,
  });

  // Mutations
  const createMutation = useCreateRequestApiV1ReimbursementRequestsPost();
  const updateMutation = useUpdateRequestApiV1ReimbursementRequestsRequestIdPut();
  const deleteMutation = useDeleteRequestApiV1ReimbursementRequestsRequestIdDelete();

  const createRequest = async (request: ReimbursementRequestCreate) => {
    return await createMutation.mutateAsync(
      { data: request },
      { onSuccess: () => refetch() }
    );
  };

  const updateRequest = async (id: string, request: ReimbursementRequestUpdate) => {
    return await updateMutation.mutateAsync(
      { requestId: id, data: request },
      { onSuccess: () => refetch() }
    );
  };

  const deleteRequest = async (id: string) => {
    await deleteMutation.mutateAsync(
      { requestId: id },
      { onSuccess: () => refetch() }
    );
  };

  return {
    requests,
    isLoading,
    error,
    createRequest,
    updateRequest,
    deleteRequest,
    isCreating: createMutation.isLoading,
    isUpdating: updateMutation.isLoading,
    isDeleting: deleteMutation.isLoading,
    refetch,
  };
}

// Hook individual para buscar por ID
export function useReimbursementRequest(id: string | null) {
  const { data, isLoading, error } = useGetRequestApiV1ReimbursementRequestsRequestIdGet(
    { requestId: id! },
    {
      query: {
        enabled: !!id, // Só executa se ID existir
      },
    }
  );

  return {
    request: data,
    isLoading,
    error,
  };
}
```

---

## ✅ CHECKLIST DE MIGRAÇÃO

### 1. PREPARAÇÃO

- [ ] Identificar service manual a migrar
- [ ] Verificar se existe módulo Orval equivalente
- [ ] Listar todos os métodos do service
- [ ] Identificar todos os imports do service no código

### 2. CRIAÇÃO DO HOOK

- [ ] Criar arquivo em `src/hooks/<modulo>/use<Nome>.ts`
- [ ] Importar hooks Orval de `@/types/generated/<modulo>/`
- [ ] Importar tipos TypeScript necessários
- [ ] Criar hook custom que encapsula hooks Orval
- [ ] Adicionar lógica de refetch/invalidação
- [ ] Adicionar tratamento de erros
- [ ] Exportar interface limpa e consistente

### 3. MIGRAÇÃO DO CÓDIGO

- [ ] Buscar todos imports do service manual
- [ ] Substituir import do service pelo novo hook
- [ ] Adaptar código para usar hook (useState, useEffect, etc.)
- [ ] Remover chamadas `.then()` e trocar por hooks
- [ ] Testar funcionalidade

### 4. LIMPEZA

- [ ] Marcar service manual como `@deprecated`
- [ ] Adicionar comentário com mapeamento de funções
- [ ] Após confirmar migração, deletar service manual
- [ ] Remover imports não utilizados
- [ ] Atualizar documentação

### 5. VALIDAÇÃO

- [ ] Build sem erros TypeScript
- [ ] Testes unitários passando
- [ ] Teste funcional manual
- [ ] Performance OK (React Query cache)
- [ ] Logs de erro limpos

---

## 🔧 TROUBLESHOOTING

### Problema 1: Hook não encontrado

**Sintoma:**
```
Cannot find module '@/types/generated/<modulo>/<arquivo>'
```

**Solução:**
```bash
# Verificar se módulo foi gerado
ls src/types/generated/<modulo>/

# Regenerar hooks Orval
npm run orval

# Verificar orval.config.ts
cat orval.config.ts
```

### Problema 2: Tipos incompatíveis

**Sintoma:**
```
Type 'X' is not assignable to type 'Y'
```

**Solução:**
- Verificar schema no backend (`backend/routers/<modulo>.py`)
- Regenerar tipos Orval
- Usar type assertion temporária: `as Type`
- Criar interface de adaptação

### Problema 3: Mutation não reflete na UI

**Sintoma:**
- Mutação executada com sucesso
- UI não atualiza

**Solução:**
```typescript
const mutation = useMutationHook();

await mutation.mutateAsync(
  { data },
  {
    onSuccess: () => {
      queryClient.invalidateQueries(['key']); // Invalida cache
      // OU
      refetch(); // Recarrega query
    },
  }
);
```

### Problema 4: Parâmetros de query não funcionam

**Sintoma:**
- Query retorna dados, mas filtros não aplicam

**Solução:**
```typescript
// ❌ ERRADO
const { data } = useQueryHook({
  filters: { status: 'active' },
});

// ✅ CORRETO
const { data } = useQueryHook({
  status: 'active', // Parâmetros diretos
  skip: 0,
  limit: 50,
});
```

### Problema 5: Hook não recarrega dados

**Sintoma:**
- Dados ficam stale após mutation

**Solução:**
```typescript
import { useQueryClient } from '@tanstack/react-query';

const queryClient = useQueryClient();

// Após mutation
await mutation.mutateAsync(data, {
  onSuccess: () => {
    // Invalida cache do React Query
    queryClient.invalidateQueries({
      queryKey: ['chave-da-query'],
    });
  },
});
```

---

## 📚 REFERÊNCIAS

- [React Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [Orval Docs](https://orval.dev/)
- [AUDITORIA_SERVICES_MANUAIS.md](./AUDITORIA_SERVICES_MANUAIS.md)

---

**Última atualização:** 2026-01-31
