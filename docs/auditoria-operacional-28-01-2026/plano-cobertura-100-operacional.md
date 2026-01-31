# PLANO DE COBERTURA 100% - MÓDULO OPERACIONAL
## Conecta PRO - Estratégias de Implementação

**Objetivo:** Alcançar 100% de cobertura do backend no frontend
**Escopo:** Módulo OPERACIONAL (130 endpoints)
**Status Atual:** 75-80% implementado (~100 endpoints)
**Gap:** ~30 endpoints ausentes

---

## 📊 NÚMEROS CONCRETOS

| Métrica | Valor |
|---------|-------|
| **Total OpenAPI Conecta PRO** | 1.246 endpoints |
| **Módulo OPERACIONAL** | 130 endpoints |
| **Implementados no Frontend** | ~100 endpoints |
| **Faltantes** | ~30 endpoints |
| **Taxa de Cobertura** | 77% |

---

## 🎯 ESTRATÉGIA 1: ORVAL ESCOPADO (RECOMENDADA)

### ✅ Vantagens
- ✅ Geração automática de tipos TypeScript
- ✅ Geração automática de hooks React Query
- ✅ Sincronização garantida com backend
- ✅ Reduz erro humano
- ✅ Facilita manutenção futura

### ⚠️ Desafios
- ⚠️ Configuração inicial trabalhosa
- ⚠️ Pode gerar código diferente do padrão atual do projeto
- ⚠️ Requer refatoração do código existente

### 📋 Plano de Execução

#### PASSO 1: Extrair OpenAPI do Módulo OPERACIONAL (1h)
```bash
# Criar OpenAPI spec apenas do módulo operacional
python3 script_extrai_operacional_spec.py \
  --input openapi-conecta-pro.json \
  --output openapi-operacional.json \
  --filter "/api/v1/operacional/"
```

#### PASSO 2: Configurar Orval (2h)
```typescript
// orval.config.ts
module.exports = {
  operacional: {
    input: {
      target: './openapi-operacional.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/lib/api/generated/operacional',
      client: 'react-query',
      mock: false,
      override: {
        mutator: {
          path: './src/lib/api/custom-instance.ts',
          name: 'customInstance',
        },
      },
    },
    hooks: {
      afterAllFilesWrite: 'prettier --write',
    },
  },
};
```

#### PASSO 3: Gerar Código (30min)
```bash
npm install -D orval
npm install @tanstack/react-query
npx orval --config orval.config.ts
```

#### PASSO 4: Integrar Gradualmente (40-60h)
- Manter código antigo funcionando
- Importar tipos gerados onde necessário
- Substituir services manualmente um por um
- Testar cada substituição

### ⏱️ Tempo Total Estimado
**SETUP:** 3-4 horas
**IMPLEMENTAÇÃO:** 40-60 horas
**TOTAL:** 43-64 horas (~6-8 dias úteis)

### 💰 Custo-Benefício
**MÉDIO** - Setup trabalhoso mas benefício de longo prazo

---

## 🎯 ESTRATÉGIA 2: IMPLEMENTAÇÃO MANUAL PROGRESSIVA

### ✅ Vantagens
- ✅ Mantém padrão atual do projeto
- ✅ Controle total sobre o código gerado
- ✅ Implementação incremental
- ✅ Menor risco de quebrar código existente
- ✅ Equipe já conhece o padrão

### ⚠️ Desafios
- ⚠️ Trabalhoso e repetitivo
- ⚠️ Propenso a erros humanos
- ⚠️ Difícil manter sincronizado com backend
- ⚠️ Manutenção futura trabalhosa

### 📋 Plano de Execução

#### FASE 1: GAPS CRÍTICOS (40-60h)

##### 1.1 Módulo de Comunicação (40h)

**Comunicados (20h)**
```typescript
// 1. Criar tipos (2h)
// src/types/operacional-communication.ts
interface Announcement {
  id: string;
  title: string;
  content: string;
  status: AnnouncementStatus;
  priority: AnnouncementPriority;
  // ... outros campos
}

// 2. Criar service (4h)
// src/lib/services/announcements.ts
export const announcementsService = {
  list: (filters) => api.get('/operacional/comunicados', { params: filters }),
  getById: (id) => api.get(`/operacional/comunicados/${id}`),
  create: (data) => api.post('/operacional/comunicados', data),
  update: (id, data) => api.patch(`/operacional/comunicados/${id}`, data),
  delete: (id) => api.delete(`/operacional/comunicados/${id}`),
  publish: (id) => api.post(`/operacional/comunicados/${id}/publicar`),
  acknowledge: (id) => api.post(`/operacional/comunicados/${id}/confirmar`),
  getReadStats: (id) => api.get(`/operacional/comunicados/${id}/leituras`),
};

// 3. Criar hooks (4h)
// src/hooks/useAnnouncements.ts
export function useAnnouncements(filters) {
  return useQuery({
    queryKey: ['announcements', filters],
    queryFn: () => announcementsService.list(filters),
  });
}

// 4. Criar componentes (6h)
// - AnnouncementFormModal.tsx
// - AnnouncementDetailModal.tsx
// - AnnouncementCard.tsx
// - AnnouncementList.tsx

// 5. Criar página (4h)
// src/app/modulos/operacional/comunicados/page.tsx
```

**Notificações e Alertas (20h)**
```typescript
// Mesma estrutura:
// 1. Tipos (2h)
// 2. Services notifications.ts + alerts.ts (6h)
// 3. Hooks (4h)
// 4. Componentes (4h)
// 5. Página (4h)
```

##### 1.2 WebSocket Client (16h)
```typescript
// src/lib/websocket/operacional-ws.ts
class OperacionalWebSocket {
  private wsAlerts: WebSocket | null = null;
  private wsNotifications: WebSocket | null = null;

  connect(token: string) {
    this.wsAlerts = new WebSocket(
      `ws://localhost:8080/ws/operacional/alertas?token=${token}`
    );
    this.wsNotifications = new WebSocket(
      `ws://localhost:8080/ws/operacional/notifications?token=${token}`
    );

    // Setup listeners, heartbeat, reconnect
  }

  // ... métodos de gerenciamento
}
```

##### 1.3 Completar Features Disciplinares (8h)
- Botão "Validar Conformidade CLT" (2h)
- Botão "Verificar Proporcionalidade" (2h)
- Visualização de assinaturas verificadas (4h)

##### 1.4 Expandir Relatórios (8h)
- Filtros avançados (3h)
- Visualizações gráficas (3h)
- Exportação múltiplos formatos (2h)

#### FASE 2: MELHORIAS E REFATORAÇÃO (16h)
- Consolidar dashboard (8h)
- Auditar fiscal (8h)

### ⏱️ Tempo Total Estimado
**FASE 1 (Crítico):** 64 horas (~8 dias úteis)
**FASE 2 (Melhoria):** 16 horas (~2 dias úteis)
**TOTAL:** 80 horas (~10 dias úteis)

### 💰 Custo-Benefício
**ALTO** - Rápido de começar, mas trabalhoso de manter

---

## 🎯 ESTRATÉGIA 3: HÍBRIDA (ORVAL + MANUAL)

### Conceito
Usar **Orval APENAS para gerar tipos TypeScript**, mas **implementar services/hooks manualmente** seguindo o padrão do projeto.

### ✅ Vantagens
- ✅ Tipos sempre sincronizados com backend
- ✅ Services/hooks no padrão do projeto
- ✅ Melhor dos dois mundos
- ✅ Reduz erro em tipos mas mantém controle do código
- ✅ Transição suave

### ⚠️ Desafios
- ⚠️ Requer configuração Orval para gerar apenas tipos
- ⚠️ Ainda precisa implementar manualmente services/hooks

### 📋 Plano de Execução

#### PASSO 1: Configurar Orval para Tipos (2h)
```typescript
// orval.config.ts
module.exports = {
  operacional: {
    input: {
      target: './openapi-operacional.json',
    },
    output: {
      mode: 'tags-split',
      target: './src/types/generated/operacional',
      client: 'axios', // Gera apenas tipos, sem hooks
      mock: false,
    },
  },
};
```

#### PASSO 2: Gerar Tipos (30min)
```bash
npx orval --config orval.config.ts
```

Resultado:
```
src/types/generated/operacional/
├── announcements.ts      # Tipos de comunicados
├── notifications.ts      # Tipos de notificações
├── allocations.ts        # Tipos de alocações
├── posts.ts              # Tipos de postos
└── ... (um arquivo por tag)
```

#### PASSO 3: Implementar Services Manualmente (40h)
Usar os tipos gerados mas escrever services à mão:

```typescript
// src/lib/services/announcements.ts
import type {
  Announcement,
  AnnouncementCreate,
  AnnouncementUpdate,
  AnnouncementFilter,
  AnnouncementListResponse
} from '@/types/generated/operacional/announcements'; // <-- TIPOS GERADOS

export const announcementsService = {
  list: async (filters: AnnouncementFilter): Promise<AnnouncementListResponse> => {
    return api.get('/operacional/comunicados', { params: filters });
  },

  create: async (data: AnnouncementCreate): Promise<Announcement> => {
    return api.post('/operacional/comunicados', data);
  },

  // ... resto manual seguindo padrão do projeto
};
```

#### PASSO 4: Criar Hooks Manualmente (16h)
```typescript
// src/hooks/useAnnouncements.ts
import type { AnnouncementFilter } from '@/types/generated/operacional/announcements';

export function useAnnouncements(filters: AnnouncementFilter) {
  return useQuery({
    queryKey: ['announcements', filters],
    queryFn: () => announcementsService.list(filters),
  });
}
```

#### PASSO 5: Implementar UI (40h)
Componentes e páginas conforme necessário.

### ⏱️ Tempo Total Estimado
**SETUP ORVAL:** 2-3 horas
**IMPLEMENTAÇÃO:** 64 horas
**TOTAL:** 66-67 horas (~8-9 dias úteis)

### 💰 Custo-Benefício
**MUITO ALTO** - Combina segurança de tipos com controle do código

---

## 📊 COMPARAÇÃO DAS ESTRATÉGIAS

| Critério | Orval Completo | Manual | Híbrida |
|----------|---------------|--------|---------|
| **Tempo Setup** | 3-4h | 0h | 2-3h |
| **Tempo Implementação** | 40-60h | 80h | 64h |
| **Tempo Total** | 43-64h | 80h | 66-67h |
| **Manutenção Futura** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Sincronização Backend** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ (tipos) |
| **Controle do Código** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Risco de Quebrar** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Curva de Aprendizado** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Custo-Benefício** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 RECOMENDAÇÃO FINAL

### **ESTRATÉGIA HÍBRIDA (3)**

**Razões:**
1. ✅ **Tipos sempre sincronizados** - Zero erro de tipagem
2. ✅ **Mantém padrão do projeto** - Services/hooks familiares
3. ✅ **Melhor custo-benefício** - 66h vs 80h da manual
4. ✅ **Manutenção futura facilitada** - Regeerar tipos é trivial
5. ✅ **Transição suave** - Não quebra código existente
6. ✅ **Escalável** - Pode expandir para outros módulos

---

## 📋 ROADMAP DE IMPLEMENTAÇÃO (HÍBRIDA)

### SPRINT 1: SETUP + COMUNICAÇÃO (SEMANA 1-2)
**Dias 1-2: Setup Orval**
- [ ] Extrair OpenAPI spec do módulo OPERACIONAL
- [ ] Configurar orval.config.ts
- [ ] Gerar tipos pela primeira vez
- [ ] Validar tipos gerados
- [ ] Commit: "feat(operacional): setup Orval para geração de tipos"

**Dias 3-7: Módulo de Comunicação - Comunicados**
- [ ] Criar service announcements.ts usando tipos gerados
- [ ] Criar hooks useAnnouncements
- [ ] Criar componente AnnouncementFormModal
- [ ] Criar componente AnnouncementDetailModal
- [ ] Criar componente AnnouncementCard
- [ ] Criar página /operacional/comunicados/page.tsx
- [ ] Testar CRUD completo
- [ ] Commit: "feat(operacional): implementar módulo de comunicados"

**Dias 8-10: Módulo de Comunicação - Notificações**
- [ ] Criar service notifications.ts
- [ ] Criar service alerts.ts
- [ ] Criar hooks useNotifications, useAlerts
- [ ] Criar NotificationCenter component
- [ ] Criar página /operacional/notificacoes/page.tsx
- [ ] Integrar com sistema global de notificações
- [ ] Commit: "feat(operacional): implementar notificações e alertas"

### SPRINT 2: WEBSOCKET + DISCIPLINAR (SEMANA 3)
**Dias 11-13: WebSocket Client**
- [ ] Criar classe OperacionalWebSocket
- [ ] Implementar conexão com autenticação JWT
- [ ] Implementar heartbeat (ping/pong 30s)
- [ ] Implementar reconexão automática
- [ ] Integrar com NotificationCenter
- [ ] Testar alertas em tempo real
- [ ] Commit: "feat(operacional): implementar WebSocket client"

**Dias 14-15: Completar Disciplinar**
- [ ] Adicionar botão "Validar Conformidade CLT"
- [ ] Adicionar botão "Verificar Proporcionalidade"
- [ ] Criar visualização de assinaturas verificadas
- [ ] Testar workflow completo
- [ ] Commit: "feat(operacional): completar features IA disciplinar"

### SPRINT 3: RELATÓRIOS + POLIMENTO (SEMANA 4)
**Dias 16-17: Expandir Relatórios**
- [ ] Adicionar filtros avançados (data range, múltiplos posts)
- [ ] Implementar visualizações gráficas (Chart.js/Recharts)
- [ ] Adicionar exportação CSV/Excel/PDF
- [ ] Commit: "feat(operacional): expandir sistema de relatórios"

**Dias 18-20: Consolidação e Testes**
- [ ] Consolidar dashboard (resolver duplicação)
- [ ] Auditar módulo fiscal
- [ ] Testes E2E de todos os fluxos críticos
- [ ] Documentação de endpoints consumidos
- [ ] Commit: "feat(operacional): finalizar cobertura 100%"

---

## 🔧 FERRAMENTAS NECESSÁRIAS

### NPM Packages
```bash
npm install -D orval
npm install @tanstack/react-query
npm install axios
npm install recharts  # Para gráficos em relatórios
```

### Scripts Úteis
```json
// package.json
{
  "scripts": {
    "orval:operacional": "orval --config orval.config.operacional.ts",
    "orval:watch": "orval --config orval.config.operacional.ts --watch",
    "types:check": "tsc --noEmit"
  }
}
```

---

## 📈 MÉTRICAS DE SUCESSO

### Cobertura de Endpoints
- ✅ **Meta:** 100% dos 130 endpoints implementados
- ✅ **Atual:** 77% (100/130)
- ✅ **Gap:** 30 endpoints

### Qualidade de Código
- ✅ Zero erros de TypeScript
- ✅ Todos os types sincronizados com backend
- ✅ 100% dos services com tratamento de erro
- ✅ 100% dos hooks com loading/error states

### Testes
- ✅ Fluxos críticos testados (seção 7 da doc)
- ✅ WebSocket com reconexão testado
- ✅ Workflows completos funcionais

---

## 🎓 PRÓXIMOS PASSOS

Após finalizar OPERACIONAL com 100%, expandir para outros módulos na ordem de prioridade:

1. **Financeiro** (se for próximo módulo prioritário)
2. **Comercial**
3. **Integrations**
4. etc.

Usando o mesmo processo:
1. Extrair OpenAPI spec do módulo
2. Gerar tipos com Orval
3. Implementar services manualmente
4. Criar UI

---

## 📝 NOTAS IMPORTANTES

### Versionamento do OpenAPI
- Sempre versionar o arquivo `openapi-operacional.json` no Git
- Atualizar tipos quando backend mudar: `npm run orval:operacional`
- CI/CD deve validar que tipos estão sincronizados

### Padrões de Código
- Manter padrão de nomenclatura existente no projeto
- Services sempre retornam Promises tipadas
- Hooks sempre usam React Query
- Componentes sempre TypeScript strict mode

### Documentação
- Atualizar CLAUDE.md do módulo após finalizar
- Documentar endpoints consumidos vs disponíveis
- Manter changelog de implementações

---

**FIM DO PLANO**