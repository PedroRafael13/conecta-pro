# Configuração Orval - Módulo Mobile

## Status: ✅ Backend Registrado e Funcionando

### 1. Módulo Registrado
- ✅ Router registrado em `main_production.py` (linha 610-616)
- ✅ Backend reiniciado com sucesso
- ✅ Endpoints disponíveis em `/api/v1/mobile/*`
- ✅ Health check funcionando: `http://localhost:8080/api/v1/mobile/health`

### 2. Correções Aplicadas
**Problemas resolvidos:**
1. Import incorreto: `core.database.base` → `core.models.base`
2. Conflito de tabela: `sync_queue` → `mobile_sync_queue`
3. Relationship incorreto: Removido `back_populates="device_tokens"` no DeviceToken
4. Enum faltando: Adicionado `ConflictResolution` ao sync_queue.py

### 3. Endpoints Disponíveis (17 total)

#### Health & Config
- `GET /api/v1/mobile/health` - Health check do serviço
- `GET /api/v1/mobile/config` - Configuração do app mobile

#### Dashboard
- `GET /api/v1/mobile/dashboard` - Dashboard otimizado mobile

#### Sincronização Offline
- `POST /api/v1/mobile/sync` - Sincronizar dados offline
- `GET /api/v1/mobile/sync/status` - Status de sincronização
- `POST /api/v1/mobile/sync/resolve-conflict` - Resolver conflitos
- `GET /api/v1/mobile/offline-data` - Dados essenciais offline

#### Batch Operations
- `POST /api/v1/mobile/batch` - Executar operações em batch

#### Device Management
- `POST /api/v1/mobile/devices/register` - Registrar dispositivo
- `DELETE /api/v1/mobile/devices/{device_id}` - Remover dispositivo

#### Push Notifications
- `GET /api/v1/mobile/notifications` - Listar notificações
- `POST /api/v1/mobile/notifications/{id}/read` - Marcar como lida
- `POST /api/v1/mobile/notifications/{id}/delivered` - Marcar como entregue
- `GET /api/v1/mobile/notifications/preferences` - Preferências
- `PUT /api/v1/mobile/notifications/preferences` - Atualizar preferências

#### Admin
- `POST /api/v1/mobile/admin/notifications/broadcast` - Broadcast
- `GET /api/v1/mobile/admin/notifications/stats` - Estatísticas

### 4. Configuração Orval

#### Adicionar ao `orval.config.ts`:

```typescript
  mobile: {
    input: {
      target: './openapi-snapshot.json',
      filters: {
        tags: ['Mobile - API Nativa', 'Mobile API'],
      },
    },
    output: {
      target: './src/api/generated/mobile.ts',
      schemas: './src/api/generated/models',
      client: 'react-query',
      mode: 'single',
      prettier: false,
      override: {
        mutator: {
          path: './src/lib/api.ts',
          name: 'axiosInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
        },
      },
    },
  },
```

### 5. Comandos para Geração Orval

```bash
# 1. Atualizar OpenAPI snapshot
cd /opt/conecta-pro/frontend
curl -s http://localhost:8080/openapi.json > openapi-snapshot.json

# 2. Gerar código mobile
npx orval --config orval.config.ts --project mobile

# 3. Verificar arquivos gerados
ls -la src/api/generated/mobile.ts
```

### 6. Arquivos Gerados

Após a geração, você terá:
- `src/api/generated/mobile.ts` - Hooks e funções React Query
- `src/api/generated/models/` - Tipos TypeScript compartilhados

### 7. Exemplo de Uso

```typescript
import {
  useHealthCheckApiV1MobileHealthGet,
  useGetMobileConfigApiV1MobileConfigGet,
  useGetMobileDashboardApiV1MobileDashboardGet,
  useSyncDataApiV1MobileSyncPost,
} from '@/api/generated/mobile';

// Health Check
const { data: healthData } = useHealthCheckApiV1MobileHealthGet();

// Mobile Config
const { data: config } = useGetMobileConfigApiV1MobileConfigGet();

// Dashboard
const { data: dashboard } = useGetMobileDashboardApiV1MobileDashboardGet();

// Sync (Mutation)
const { mutate: syncData } = useSyncDataApiV1MobileSyncPost();

syncData({
  data: {
    device_id: 'device-123',
    operations: [],
    last_sync: new Date().toISOString(),
  }
});
```

### 8. Cobertura de Tipos

#### Request Types
- `MobileSyncRequest` - Sincronização offline
- `BatchRequest` - Operações em batch
- `DeviceTokenCreate` - Registro de dispositivo
- `NotificationPreferencesUpdate` - Atualização de preferências
- `BroadcastNotificationRequest` - Broadcast admin

#### Response Types
- `HealthCheckResponse`
- `MobileConfigResponse`
- `MobileDashboardResponse`
- `MobileSyncResponse`
- `BatchResponse`
- `DeviceTokenResponse`
- `NotificationListResponse`
- `NotificationPreferences`
- `BroadcastNotificationResponse`

### 9. Service Layer (Opcional)

Criar `src/services/mobile.service.ts`:

```typescript
import {
  syncDataApiV1MobileSyncPost,
  getOfflineDataApiV1MobileOfflineDataGet,
  executeBatchApiV1MobileBatchPost,
} from '@/api/generated/mobile';
import type { MobileSyncRequest, BatchRequest } from '@/api/generated/models';

export class MobileService {
  // Sincronização offline com retry
  static async syncWithRetry(request: MobileSyncRequest, maxRetries = 3) {
    let attempt = 0;
    while (attempt < maxRetries) {
      try {
        return await syncDataApiV1MobileSyncPost(request);
      } catch (error) {
        attempt++;
        if (attempt >= maxRetries) throw error;
        await new Promise(r => setTimeout(r, 1000 * attempt));
      }
    }
  }

  // Download dados offline
  static async downloadOfflineData(modules?: string[]) {
    return getOfflineDataApiV1MobileOfflineDataGet({
      modules: modules?.join(','),
    });
  }

  // Batch operations
  static async executeBatch(operations: BatchRequest) {
    return executeBatchApiV1MobileBatchPost(operations);
  }
}
```

### 10. Hooks Personalizados

Criar `src/hooks/useMobileSync.ts`:

```typescript
import { useSyncDataApiV1MobileSyncPost } from '@/api/generated/mobile';
import { useQueryClient } from '@tanstack/react-query';

export function useMobileSync() {
  const queryClient = useQueryClient();
  const { mutate, isLoading, error } = useSyncDataApiV1MobileSyncPost({
    onSuccess: () => {
      // Invalidar queries relacionadas
      queryClient.invalidateQueries(['mobile', 'dashboard']);
      queryClient.invalidateQueries(['mobile', 'offline-data']);
    },
  });

  return {
    sync: mutate,
    isSyncing: isLoading,
    syncError: error,
  };
}
```

### 11. Validação Final

```bash
# Testar endpoints mobile
curl http://localhost:8080/api/v1/mobile/health | jq .

# Verificar OpenAPI spec
curl http://localhost:8080/openapi.json | jq '.paths | keys | map(select(startswith("/api/v1/mobile")))'

# Contar endpoints mobile
curl -s http://localhost:8080/openapi.json | jq '.paths | keys | map(select(startswith("/api/v1/mobile"))) | length'
# Resultado esperado: 17
```

### 12. Próximos Passos

1. ✅ Módulo registrado e funcionando
2. ⏭️ Atualizar OpenAPI snapshot
3. ⏭️ Adicionar configuração mobile ao orval.config.ts
4. ⏭️ Gerar código Orval
5. ⏭️ Criar service layer
6. ⏭️ Criar hooks personalizados
7. ⏭️ Validar tipos e hooks gerados

### 13. Notas Técnicas

**Performance:**
- Sincronização offline com compressão (Gateway)
- Batch operations para reduzir requisições
- Cache inteligente com React Query

**Segurança:**
- Rate limiting via MobileSecurity
- Validação de device tokens
- Auth obrigatório (exceto /health)

**Offline-First:**
- Sync queue para operações offline
- Resolução automática de conflitos
- Dados essenciais em cache

---

**Data:** 28/01/2026
**Status:** Backend 100% funcional, Frontend pendente
**Prioridade:** BAIXA (APIs mobile nativas)
