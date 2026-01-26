# Índice Rápido de Hooks - Conecta Plus

**Última atualização:** 2026-01-26

---

## Como Usar Este Índice

Todos os hooks podem ser importados via:

```typescript
import { useNomeDoHook } from '@/hooks';
```

---

## 🔐 Autenticação e Autorização

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useAuth` | `useAuth.ts` | Login, logout, usuário atual |
| `usePermission` | `usePermission.ts` | Verificação de permissões |

---

## 🏢 Módulo Operacional - Postos

| Hook | Arquivo | Uso |
|------|---------|-----|
| `usePosts` | `usePosts.ts` | Lista de postos com paginação |
| `usePost` | `usePosts.ts` | Posto individual por ID |
| `usePostStats` | `usePosts.ts` | Estatísticas de postos |

---

## 📅 Módulo Operacional - Escalas

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useScales` | `useScales.ts` | Lista de escalas com filtros |
| `useScale` | `useScales.ts` | Escala individual por ID |
| `useScaleStats` | `useScales.ts` | Estatísticas de escalas |
| `useScaleOperations` | `useScales.ts` | CRUD de escalas |
| `useCurrentMonthScales` | `useScales.ts` | Escalas do mês atual |

---

## 📋 Módulo Operacional - Templates de Escala

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useTemplates` | `useScaleTemplates.ts` | Lista de templates |
| `useTemplate` | `useScaleTemplates.ts` | Template individual |
| `useTemplateOperations` | `useScaleTemplates.ts` | CRUD + preview + apply |

---

## 👥 Módulo Operacional - Colaboradores

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useAllocations` | `useAllocations.ts` | Alocações de colaboradores |
| `useEmployees` | `useEmployees.ts` | Lista de colaboradores |

---

## ⏰ Módulo Operacional - Turnos

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useShifts` | `useShifts.ts` | Lista de turnos |
| `useTodayShifts` | `useShifts.ts` | Turnos do dia |
| `useShiftOperations` | `useShifts.ts` | CRUD de turnos |

---

## 🚶 Módulo Operacional - Rondas

| Hook | Arquivo | Uso |
|------|---------|-----|
| `usePatrolRounds` | `usePatrolRounds.ts` | Lista de rondas |
| `usePatrolRoundStats` | `usePatrolRounds.ts` | Estatísticas de rondas |
| `usePatrolRoundDetail` | `usePatrolRounds.ts` | Detalhes de ronda |
| `usePatrolRoundMutations` | `usePatrolRounds.ts` | CRUD de rondas |

---

## 📝 Módulo Operacional - Ocorrências

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useOccurrences` | `useOccurrences.ts` | Lista de ocorrências |
| `useOccurrenceStats` | `useOccurrences.ts` | Estatísticas |
| `useOccurrenceDetail` | `useOccurrences.ts` | Detalhes de ocorrência |
| `usePostOccurrences` | `useOccurrences.ts` | Ocorrências por posto |
| `useOccurrenceMutations` | `useOccurrences.ts` | CRUD de ocorrências |

---

## ⚖️ Módulo Operacional - Disciplinar

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useDisciplinary` | `useDisciplinary.ts` | Lista de processos |
| `useDisciplinaryStats` | `useDisciplinary.ts` | Estatísticas |
| `useDisciplinaryDetail` | `useDisciplinary.ts` | Detalhes de processo |
| `usePendingDisciplinaryApprovals` | `useDisciplinary.ts` | Aprovações pendentes |
| `useEmployeeDisciplinary` | `useDisciplinary.ts` | Processos por colaborador |

---

## 💰 Módulo Operacional - Reembolsos

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useReimbursements` | `useReimbursement.ts` | Lista de reembolsos |
| `useReimbursementStats` | `useReimbursement.ts` | Estatísticas |
| `useReimbursementDetail` | `useReimbursement.ts` | Detalhes |
| `usePendingReimbursementApprovals` | `useReimbursement.ts` | Aprovações pendentes |
| `useReimbursementCategories` | `useReimbursement.ts` | Categorias |
| `useReadyForPayment` | `useReimbursement.ts` | Prontos para pagamento |

---

## 🎯 Módulo CRM - Leads

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useLeads` | `useLeads.ts` | Lista de leads |
| `useLead` | `useLeads.ts` | Lead individual |
| `useCreateLead` | `useLeads.ts` | Criar lead |
| `useUpdateLead` | `useLeads.ts` | Atualizar lead |
| `useDeleteLead` | `useLeads.ts` | Deletar lead |
| `useLeadsStats` | `useLeads.ts` | Estatísticas |

---

## 📊 Dashboard e Analytics

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useDashboardStats` | `useDashboard.ts` | Estatísticas dashboard |
| `useRecentActivities` | `useDashboard.ts` | Atividades recentes |
| `useHealthCheck` | `useDashboard.ts` | Health check do sistema |
| `useKPITrends` | `useKPITrends.ts` | Tendências de KPIs (7d/30d/90d) |

---

## 🚀 Produtividade - Auto-Save

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useAutoSave` | `useAutoSave.ts` | Auto-save de formulários |
| `cleanupExpiredDrafts` | `useAutoSave.ts` | Limpeza de drafts (função) |

**Exemplo:**
```typescript
const { saving, lastSaved, hasDraft, restore, clear } = useAutoSave({
  key: 'form_key',
  data: formData,
  debounceMs: 2000
});
```

---

## ⌨️ Produtividade - Atalhos

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useKeyboardShortcuts` | `useKeyboardShortcuts.ts` | Atalhos customizados |
| `useGlobalShortcuts` | `useKeyboardShortcuts.ts` | Atalhos globais do sistema |

**Atalhos Globais:**
- `/` - Busca global
- `Ctrl+K` - Command palette
- `Ctrl+B` - Toggle sidebar
- `Alt+1/2/3/4` - Navegação entre módulos
- `Shift+?` - Ajuda

---

## 🔔 Notificações

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useNotifications` | `features/notifications` | Gestão de notificações |
| `usePushNotifications` | `features/notifications` | Push notifications |

**Exemplo:**
```typescript
const {
  notifications,
  unreadCount,
  markAsRead,
  markAllAsRead
} = useNotifications();

const {
  isSupported,
  isSubscribed,
  subscribe,
  unsubscribe
} = usePushNotifications();
```

---

## 🎓 Onboarding

| Hook | Arquivo | Uso |
|------|---------|-----|
| `useTour` | `features/onboarding` | Tour guiado |
| `useShouldShowTour` | `features/onboarding` | Verificar se deve mostrar |
| `useTourProgress` | `features/onboarding` | Progresso do tour |

**Exemplo:**
```typescript
const {
  isCompleted,
  isActive,
  startTour,
  resetTour,
  cancelTour
} = useTour('USUARIO', autoStart);
```

---

## 📚 Referências Rápidas

### Por Funcionalidade

**Listagem com Paginação:**
- `usePosts` - Postos
- `useScales` - Escalas
- `useTemplates` - Templates
- `useOccurrences` - Ocorrências
- `useLeads` - Leads

**Item Individual:**
- `usePost(id)` - Posto
- `useScale(id)` - Escala
- `useTemplate(id)` - Template
- `useLead(id)` - Lead

**Estatísticas:**
- `usePostStats()` - Postos
- `useScaleStats()` - Escalas
- `useKPITrends()` - KPIs
- `useDashboardStats()` - Dashboard

**CRUD Operations:**
- `useScaleOperations()` - Escalas
- `useTemplateOperations()` - Templates
- `useShiftOperations()` - Turnos
- `useOccurrenceMutations()` - Ocorrências

---

## 🔍 Busca Rápida

### Por Nome
- **use + Auth** → Autenticação
- **use + Posts** → Postos
- **use + Scales** → Escalas
- **use + Templates** → Templates de Escala
- **use + Employees** → Colaboradores
- **use + Shifts** → Turnos
- **use + PatrolRounds** → Rondas
- **use + Occurrences** → Ocorrências
- **use + Disciplinary** → Disciplinar
- **use + Reimbursement** → Reembolsos
- **use + Leads** → Leads CRM
- **use + Dashboard** → Dashboard
- **use + KPI** → Analytics
- **use + AutoSave** → Auto-save
- **use + Keyboard** → Atalhos
- **use + Notifications** → Notificações
- **use + Tour** → Onboarding

---

## 💡 Dicas de Uso

### 1. IntelliSense
```typescript
import { use... } from '@/hooks';
// Ctrl+Space mostra todos os hooks disponíveis
```

### 2. Documentação
```typescript
// Hover sobre o hook para ver JSDoc
const { data } = usePosts(); // ← Hover aqui
```

### 3. Tipos
```typescript
import type { UseAutoSaveOptions } from '@/hooks';
```

### 4. Re-exports
```typescript
// Também pode importar de features
import { useNotifications } from '@/features/notifications';
// Mas preferir via @/hooks para consistência
```

---

## 📖 Documentação Completa

Ver `/src/hooks/README.md` para:
- Exemplos detalhados
- Padrões de uso
- Troubleshooting
- API completa de cada hook

---

**Total de Hooks:** 50+
**Categorias:** 9
**Arquivos:** 20+

**Atualizado em:** 2026-01-26
