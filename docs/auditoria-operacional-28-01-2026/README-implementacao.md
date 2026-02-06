# GUIA DE IMPLEMENTAÇÃO - COBERTURA 100% OPERACIONAL

## 🚀 QUICK START

### Passo 1: Extrair OpenAPI do Módulo OPERACIONAL
```bash
cd /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad

# Já temos o openapi-conecta-pro.json baixado (2.3MB)
# Agora vamos extrair apenas o módulo operacional

python3 extract-operacional-spec.py
```

**Resultado esperado:**
```
📊 Total de endpoints no spec completo: 1246
✅ Endpoints do módulo OPERACIONAL: 130
📦 Schemas referenciados: ~200
✨ EXTRAÇÃO CONCLUÍDA!
   Tamanho original: 2.30 MB
   Tamanho otimizado: ~0.50 MB
   Redução: ~78%
```

---

### Passo 2: Copiar Arquivos para o Projeto Frontend

```bash
# Ir para o diretório do frontend
cd /opt/conecta-pro/frontend

# Copiar spec do operacional
cp /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/openapi-operacional.json ./

# Copiar config do Orval
cp /tmp/claude/-root/4165f004-2cca-4e6e-a166-a6e595e62f28/scratchpad/orval.config.operacional.ts ./
```

---

### Passo 3: Instalar Dependências

```bash
cd /opt/conecta-pro/frontend

# Instalar Orval (dev dependency)
npm install -D orval

# Instalar React Query se ainda não tiver
npm install @tanstack/react-query

# Instalar Axios se ainda não tiver
npm install axios

# Instalar Recharts para gráficos em relatórios
npm install recharts
```

---

### Passo 4: Adicionar Scripts no package.json

```json
{
  "scripts": {
    "orval:operacional": "orval --config orval.config.operacional.ts",
    "orval:watch": "orval --config orval.config.operacional.ts --watch",
    "types:check": "tsc --noEmit"
  }
}
```

---

### Passo 5: Gerar Tipos pela Primeira Vez

```bash
npm run orval:operacional
```

**Resultado esperado:**
```
✨ Gerado em src/types/generated/operacional/
   - announcements.ts       (tipos de comunicados)
   - notifications.ts       (tipos de notificações)
   - allocations.ts         (tipos de alocações)
   - posts.ts              (tipos de postos)
   - scales.ts             (tipos de escalas)
   - shifts.ts             (tipos de turnos)
   - occurrences.ts        (tipos de ocorrências)
   - patrol-rounds.ts      (tipos de rondas)
   - disciplinary.ts       (tipos disciplinares)
   - diarists.ts           (tipos de diaristas)
   - ... (mais arquivos por tag)
```

---

### Passo 6: Verificar Tipos Gerados

```bash
# Listar arquivos gerados
ls -la src/types/generated/operacional/

# Ver exemplo de um arquivo gerado
cat src/types/generated/operacional/announcements.ts | head -50
```

---

## 📋 IMPLEMENTAÇÃO DOS GAPS CRÍTICOS

### GAP 1: Módulo de Comunicação (Prioridade CRÍTICA)

#### 1.1 Criar Service de Comunicados

```typescript
// src/lib/services/announcements.ts
import type {
  Announcement,
  AnnouncementCreate,
  AnnouncementUpdate,
  AnnouncementFilter,
  AnnouncementListResponse,
} from '@/types/generated/operacional/announcements';

import { api } from '@/lib/api';

export const announcementsService = {
  /**
   * Lista todos os comunicados com filtros
   */
  list: async (filters?: AnnouncementFilter): Promise<AnnouncementListResponse> => {
    const response = await api.get('/api/v1/operacional/comunicados', {
      params: filters,
    });
    return response.data;
  },

  /**
   * Busca comunicado por ID
   */
  getById: async (id: string): Promise<Announcement> => {
    const response = await api.get(`/api/v1/operacional/comunicados/${id}`);
    return response.data;
  },

  /**
   * Cria novo comunicado
   */
  create: async (data: AnnouncementCreate): Promise<Announcement> => {
    const response = await api.post('/api/v1/operacional/comunicados', data);
    return response.data;
  },

  /**
   * Atualiza comunicado existente
   */
  update: async (id: string, data: AnnouncementUpdate): Promise<Announcement> => {
    const response = await api.patch(`/api/v1/operacional/comunicados/${id}`, data);
    return response.data;
  },

  /**
   * Remove comunicado
   */
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/operacional/comunicados/${id}`);
  },

  /**
   * Publica comunicado (muda status para PUBLISHED)
   */
  publish: async (id: string): Promise<Announcement> => {
    const response = await api.post(`/api/v1/operacional/comunicados/${id}/publicar`);
    return response.data;
  },

  /**
   * Confirma leitura de comunicado
   */
  acknowledge: async (id: string): Promise<void> => {
    await api.post(`/api/v1/operacional/comunicados/${id}/confirmar`);
  },

  /**
   * Obtém estatísticas de leituras do comunicado
   */
  getReadStats: async (id: string) => {
    const response = await api.get(`/api/v1/operacional/comunicados/${id}/leituras`);
    return response.data;
  },

  /**
   * Lista comunicados não lidos
   */
  listUnread: async () => {
    const response = await api.get('/api/v1/operacional/comunicados/nao-lidos');
    return response.data;
  },
};
```

#### 1.2 Criar Hook useAnnouncements

```typescript
// src/hooks/useAnnouncements.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { AnnouncementFilter } from '@/types/generated/operacional/announcements';
import { announcementsService } from '@/lib/services/announcements';
import { toast } from 'sonner';

/**
 * Hook para listar comunicados com filtros
 */
export function useAnnouncements(filters?: AnnouncementFilter) {
  return useQuery({
    queryKey: ['announcements', filters],
    queryFn: () => announcementsService.list(filters),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

/**
 * Hook para buscar comunicado por ID
 */
export function useAnnouncement(id: string) {
  return useQuery({
    queryKey: ['announcement', id],
    queryFn: () => announcementsService.getById(id),
    enabled: !!id,
  });
}

/**
 * Hook para operações de mutação (create, update, delete)
 */
export function useAnnouncementMutations() {
  const queryClient = useQueryClient();

  const create = useMutation({
    mutationFn: announcementsService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['announcements'] });
      toast.success('Comunicado criado com sucesso!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao criar comunicado');
    },
  });

  const update = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      announcementsService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['announcements'] });
      toast.success('Comunicado atualizado com sucesso!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao atualizar comunicado');
    },
  });

  const remove = useMutation({
    mutationFn: announcementsService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['announcements'] });
      toast.success('Comunicado removido com sucesso!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao remover comunicado');
    },
  });

  const publish = useMutation({
    mutationFn: announcementsService.publish,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['announcements'] });
      toast.success('Comunicado publicado com sucesso!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Erro ao publicar comunicado');
    },
  });

  const acknowledge = useMutation({
    mutationFn: announcementsService.acknowledge,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['announcements'] });
    },
  });

  return {
    create,
    update,
    remove,
    publish,
    acknowledge,
  };
}

/**
 * Hook para comunicados não lidos
 */
export function useUnreadAnnouncements() {
  return useQuery({
    queryKey: ['announcements', 'unread'],
    queryFn: announcementsService.listUnread,
    refetchInterval: 1000 * 60, // Refetch a cada 1 minuto
  });
}
```

#### 1.3 Criar Página de Comunicados

```typescript
// src/app/modulos/operacional/comunicados/page.tsx
'use client';

import { useState } from 'react';
import { useAnnouncements, useAnnouncementMutations } from '@/hooks/useAnnouncements';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
// ... imports de componentes

export default function ComunicadosPage() {
  const [filters, setFilters] = useState({});
  const { data, isLoading } = useAnnouncements(filters);
  const { create, update, remove } = useAnnouncementMutations();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Comunicados</h1>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Novo Comunicado
        </Button>
      </div>

      {/* Lista de comunicados */}
      {/* ... implementação */}
    </div>
  );
}
```

---

### GAP 2: WebSocket Client

```typescript
// src/lib/websocket/operacional-ws.ts
class OperacionalWebSocket {
  private wsAlerts: WebSocket | null = null;
  private wsNotifications: WebSocket | null = null;
  private token: string = '';
  private reconnectInterval = 5000;
  private heartbeatInterval = 30000;
  private heartbeatTimer: NodeJS.Timeout | null = null;

  connect(token: string) {
    this.token = token;
    this.connectAlerts();
    this.connectNotifications();
  }

  private connectAlerts() {
    const url = `ws://localhost:8080/ws/operacional/alertas?token=${this.token}`;
    this.wsAlerts = new WebSocket(url);

    this.wsAlerts.onopen = () => {
      console.log('✅ WebSocket Alertas conectado');
      this.startHeartbeat(this.wsAlerts!);
    };

    this.wsAlerts.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 Alerta recebido:', data);
      // Disparar evento customizado
      window.dispatchEvent(new CustomEvent('operacional:alert', { detail: data }));
    };

    this.wsAlerts.onerror = (error) => {
      console.error('❌ WebSocket Alertas erro:', error);
    };

    this.wsAlerts.onclose = () => {
      console.log('🔌 WebSocket Alertas desconectado, reconectando...');
      setTimeout(() => this.connectAlerts(), this.reconnectInterval);
    };
  }

  private connectNotifications() {
    const url = `ws://localhost:8080/ws/operacional/notifications?token=${this.token}`;
    this.wsNotifications = new WebSocket(url);

    this.wsNotifications.onopen = () => {
      console.log('✅ WebSocket Notificações conectado');
      this.startHeartbeat(this.wsNotifications!);
    };

    this.wsNotifications.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 Notificação recebida:', data);
      // Disparar evento customizado
      window.dispatchEvent(new CustomEvent('operacional:notification', { detail: data }));
    };

    this.wsNotifications.onerror = (error) => {
      console.error('❌ WebSocket Notificações erro:', error);
    };

    this.wsNotifications.onclose = () => {
      console.log('🔌 WebSocket Notificações desconectado, reconectando...');
      setTimeout(() => this.connectNotifications(), this.reconnectInterval);
    };
  }

  private startHeartbeat(ws: WebSocket) {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }

    this.heartbeatTimer = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, this.heartbeatInterval);
  }

  disconnect() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
    }
    this.wsAlerts?.close();
    this.wsNotifications?.close();
  }
}

export const operacionalWS = new OperacionalWebSocket();
```

---

## 📊 CHECKLIST DE IMPLEMENTAÇÃO

### Setup Inicial
- [ ] Extrair OpenAPI spec do módulo operacional
- [ ] Copiar arquivos para o projeto frontend
- [ ] Instalar dependências (Orval, React Query, Recharts)
- [ ] Configurar scripts no package.json
- [ ] Gerar tipos pela primeira vez
- [ ] Verificar tipos gerados

### Módulo de Comunicação
- [ ] Criar service `announcements.ts`
- [ ] Criar hooks `useAnnouncements.ts`
- [ ] Criar componente `AnnouncementFormModal`
- [ ] Criar componente `AnnouncementDetailModal`
- [ ] Criar componente `AnnouncementCard`
- [ ] Criar página `/operacional/comunicados/page.tsx`
- [ ] Testar CRUD completo

- [ ] Criar service `notifications.ts`
- [ ] Criar service `alerts.ts`
- [ ] Criar hooks `useNotifications.ts`
- [ ] Criar componente `NotificationCenter`
- [ ] Criar página `/operacional/notificacoes/page.tsx`
- [ ] Integrar com sistema global de notificações

### WebSocket
- [ ] Criar classe `OperacionalWebSocket`
- [ ] Implementar conexão com JWT
- [ ] Implementar heartbeat
- [ ] Implementar reconexão automática
- [ ] Integrar com NotificationCenter
- [ ] Testar alertas em tempo real

### Disciplinar
- [ ] Adicionar botão "Validar Conformidade CLT"
- [ ] Adicionar botão "Verificar Proporcionalidade"
- [ ] Criar visualização de assinaturas verificadas

### Relatórios
- [ ] Adicionar filtros avançados
- [ ] Implementar visualizações gráficas
- [ ] Adicionar exportação CSV/Excel/PDF

---

## 🎯 COMANDOS ÚTEIS

```bash
# Regerar tipos quando o backend mudar
npm run orval:operacional

# Verificar erros de TypeScript
npm run types:check

# Watch mode - regera automaticamente ao detectar mudanças
npm run orval:watch

# Formatar código gerado
npx prettier --write "src/types/generated/**/*.ts"
```

---

## 📚 DOCUMENTAÇÃO ADICIONAL

- **Plano Completo:** `plano-cobertura-100-operacional.md`
- **Auditoria:** `auditoria-operacional.md`
- **OpenAPI Spec:** `openapi-operacional.json`
- **Config Orval:** `orval.config.operacional.ts`

---

**Pronto para começar! 🚀**