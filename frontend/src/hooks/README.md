# Hooks - Conecta Plus

Documentação completa de todos os hooks disponíveis no sistema.

## Índice

- [Autenticação](#autenticação)
- [Módulo Operacional](#módulo-operacional)
- [CRM](#crm)
- [Dashboard](#dashboard)
- [Produtividade](#produtividade)
- [Notificações](#notificações)
- [Onboarding](#onboarding)

---

## Como Importar

### Importação Centralizada (Recomendado)

```typescript
import { useAuth, usePosts, useAutoSave, useNotifications } from '@/hooks';
```

### Importação Direta (Quando necessário)

```typescript
import { useAuth } from '@/hooks/useAuth';
import { usePosts } from '@/hooks/usePosts';
```

---

## Autenticação

### useAuth

Gerencia autenticação de usuários.

```typescript
const { user, isAuthenticated, isLoading, login, logout, refreshUser } = useAuth();
```

**Retorno:**
- `user`: Dados do usuário autenticado
- `isAuthenticated`: Status de autenticação
- `isLoading`: Carregamento
- `login(credentials)`: Função de login
- `logout()`: Função de logout
- `refreshUser()`: Atualiza dados do usuário

### usePermission

Verifica permissões do usuário.

```typescript
const { hasPermission, isAdmin, canEdit } = usePermission();
```

---

## Módulo Operacional

### usePosts

Gerenciamento de postos de trabalho.

```typescript
const {
  posts,
  total,
  page,
  pageSize,
  isLoading,
  error,
  filters,
  setFilters,
  refresh
} = usePosts({
  autoLoad: true,
  initialPage: 1,
  initialPageSize: 20,
  initialFilters: { status: 'ATIVO' }
});
```

**Opções:**
- `autoLoad`: Carrega automaticamente ao montar (default: true)
- `initialPage`: Página inicial
- `initialPageSize`: Tamanho da página
- `initialFilters`: Filtros iniciais

### useScales

Gerenciamento de escalas.

```typescript
const {
  scales,
  total,
  page,
  isLoading,
  error,
  refresh
} = useScales(1, 20, { status: 'ATIVO' });
```

### useScaleTemplates

Templates de escalas reutilizáveis.

```typescript
// Listar templates
const { templates, total, isLoading, refresh } = useTemplates(1, 50);

// Template individual
const { template, isLoading, error } = useTemplate(templateId);

// Operações (create, update, delete, apply)
const {
  isLoading,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  applyTemplate,
  previewTemplate
} = useTemplateOperations();
```

**Exemplo de Aplicação:**

```typescript
const { applyTemplate } = useTemplateOperations();

const handleApply = async () => {
  const scale = await applyTemplate(templateId, {
    posto_id: 'posto-123',
    data_inicio: '2025-02-01',
    data_fim: '2025-02-28'
  });

  if (scale) {
    console.log('Escala criada:', scale);
  }
};
```

### useAllocations

Alocação de colaboradores.

```typescript
const { allocations, isLoading, refresh } = useAllocations();
```

### useEmployees

Gerenciamento de colaboradores.

```typescript
const { employees, total, isLoading, refresh } = useEmployees();
```

### useShifts

Turnos de trabalho.

```typescript
const { shifts, isLoading, error, refresh } = useShifts();
```

### usePatrolRounds

Rondas de patrulha.

```typescript
const { rounds, isLoading, createRound, completeRound } = usePatrolRounds();
```

### useOccurrences

Ocorrências operacionais.

```typescript
const { occurrences, total, isLoading, createOccurrence } = useOccurrences();
```

### useDisciplinary

Processos disciplinares.

```typescript
const { processes, isLoading, createProcess } = useDisciplinary();
```

### useReimbursement

Reembolsos.

```typescript
const { reimbursements, isLoading, submitReimbursement } = useReimbursement();
```

---

## CRM

### useLeads

Gerenciamento de leads.

```typescript
const {
  leads,
  total,
  isLoading,
  createLead,
  updateLead,
  convertLead
} = useLeads();
```

---

## Dashboard

### useDashboard

Dados consolidados do dashboard.

```typescript
const { data, isLoading, error, refresh } = useDashboard();
```

### useKPITrends

Tendências de KPIs.

```typescript
const { data, isLoading, error, refresh } = useKPITrends({
  period: '30d', // '7d' | '30d' | '90d'
  autoLoad: true
});
```

**Dados retornados:**
- `postos_ativos`: Array de números
- `colaboradores_ativos`: Array de números
- `escalas_em_andamento`: Array de números
- `ocorrencias_mes`: Array de números
- `cobertura_percentual`: Array de números

---

## Produtividade

### useAutoSave

Salvamento automático de formulários.

```typescript
const {
  saving,
  lastSaved,
  error,
  hasDraft,
  restore,
  clear
} = useAutoSave({
  key: 'posto_form',
  data: formData,
  debounceMs: 2000,
  enabled: isOpen && !isEditing,
  excludeFields: ['password', 'token']
});
```

**Características:**
- Auto-save com debounce
- localStorage com expiração (7 dias)
- Sanitização de campos sensíveis
- Suporte a backup no backend

**Exemplo Completo:**

```typescript
function PostFormModal({ isOpen, onClose }) {
  const [formData, setFormData] = useState({
    nome: '',
    endereco: '',
    responsavel: ''
  });

  const autoSave = useAutoSave({
    key: 'posto_form',
    data: formData,
    debounceMs: 2000,
    enabled: isOpen
  });

  // Restaurar rascunho ao abrir
  useEffect(() => {
    if (isOpen && autoSave.hasDraft) {
      const draft = autoSave.restore();
      if (draft) {
        setFormData(draft);
        toast.info('Rascunho restaurado');
      }
    }
  }, [isOpen]);

  // Limpar ao enviar com sucesso
  const handleSubmit = async () => {
    await createPost(formData);
    autoSave.clear();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      {autoSave.saving && <span>Salvando...</span>}
      {autoSave.lastSaved && (
        <span>Último save: {autoSave.lastSaved.toLocaleTimeString()}</span>
      )}
      {/* Form fields */}
    </Dialog>
  );
}
```

**Limpeza de Rascunhos:**

```typescript
// No app/layout.tsx ou providers.tsx
import { cleanupExpiredDrafts } from '@/hooks';

useEffect(() => {
  cleanupExpiredDrafts();
}, []);
```

### useKeyboardShortcuts

Atalhos de teclado customizados.

```typescript
const shortcuts: KeyboardShortcut[] = [
  {
    key: 's',
    ctrl: true,
    description: 'Salvar formulário',
    action: handleSave,
    preventDefault: true
  },
  {
    key: 'Escape',
    description: 'Fechar modal',
    action: handleClose
  }
];

useKeyboardShortcuts({ shortcuts, enabled: isModalOpen });
```

### useGlobalShortcuts

Atalhos globais do sistema (já integrado no ProductivityProvider).

```typescript
const shortcuts = useGlobalShortcuts({
  onSearchOpen: () => setSearchOpen(true),
  onCommandPaletteOpen: () => setPaletteOpen(true),
  onSidebarToggle: () => toggleSidebar(),
  onHelpOpen: () => setHelpOpen(true),
  onModalClose: () => closeModals()
});
```

**Atalhos Padrão:**
- `/` - Busca global
- `Ctrl+K` - Command palette
- `Ctrl+B` - Toggle sidebar
- `Alt+1` - Dashboard
- `Alt+2` - Operacional
- `Alt+3` - Financeiro
- `Alt+4` - CRM
- `Shift+?` - Ajuda

---

## Notificações

### useNotifications

Gerenciamento de notificações push.

```typescript
const {
  notifications,
  unreadCount,
  loading,
  error,
  refresh,
  markAsRead,
  markAllAsRead,
  subscribeToPush
} = useNotifications();
```

**Auto-refresh:** Atualiza a cada 30 segundos automaticamente.

**Exemplo:**

```typescript
function NotificationBell() {
  const { unreadCount, markAsRead, notifications } = useNotifications();

  return (
    <div>
      <Badge count={unreadCount} />
      {notifications.map(notif => (
        <div key={notif.id} onClick={() => markAsRead(notif.id)}>
          {notif.title}
        </div>
      ))}
    </div>
  );
}
```

### usePushNotifications

Inicialização de push notifications.

```typescript
const {
  isSupported,
  isSubscribed,
  permission,
  subscribe,
  unsubscribe
} = usePushNotifications();
```

**Auto-inicialização:**
- Registra service worker automaticamente
- Verifica suporte do navegador
- Checa permissões existentes

**Exemplo:**

```typescript
function PushNotificationButton() {
  const { isSupported, isSubscribed, permission, subscribe } = usePushNotifications();

  if (!isSupported) {
    return <div>Notificações não suportadas</div>;
  }

  if (permission === 'denied') {
    return <div>Permissão negada</div>;
  }

  return (
    <button onClick={subscribe} disabled={isSubscribed}>
      {isSubscribed ? 'Inscrito' : 'Ativar Notificações'}
    </button>
  );
}
```

---

## Onboarding

### useTour

Tour guiado para onboarding.

```typescript
const {
  isCompleted,
  isActive,
  currentStep,
  totalSteps,
  startTour,
  resetTour,
  cancelTour
} = useTour('USUARIO', true); // role, autoStart
```

**Roles disponíveis:**
- `'ADMIN'` - Tour completo
- `'USUARIO'` - Tour básico

**Exemplo:**

```typescript
function TourButton() {
  const { isCompleted, startTour, resetTour } = useTour('USUARIO');

  return (
    <div>
      {!isCompleted ? (
        <button onClick={startTour}>Iniciar Tour</button>
      ) : (
        <button onClick={resetTour}>Refazer Tour</button>
      )}
    </div>
  );
}
```

### useShouldShowTour

Verifica se deve mostrar tour.

```typescript
const shouldShow = useShouldShowTour();

if (shouldShow) {
  // Mostrar botão de tour
}
```

### useTourProgress

Tracking de progresso do tour.

```typescript
const {
  progress,
  markStarted,
  markCompleted,
  incrementCancelCount
} = useTourProgress();

// progress: { started, completed, startedAt, completedAt, cancelCount }
```

---

## Providers Necessários

Alguns hooks dependem de providers. Verifique se estão configurados em `/src/contexts/providers.tsx`:

```typescript
export function Providers({ children }) {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <DraftCleanupProvider>  {/* Para useAutoSave */}
          <ProductivityProvider>  {/* Para useKeyboardShortcuts */}
            {children}
          </ProductivityProvider>
        </DraftCleanupProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
```

---

## Padrões de Uso

### 1. Sempre use barrel exports

```typescript
// ✅ BOM
import { usePosts, useAutoSave } from '@/hooks';

// ❌ EVITE
import { usePosts } from '@/hooks/usePosts';
import { useAutoSave } from '@/hooks/useAutoSave';
```

### 2. Destruture apenas o necessário

```typescript
// ✅ BOM
const { posts, isLoading } = usePosts();

// ❌ EVITE
const allData = usePosts();
const posts = allData.posts;
```

### 3. Handle loading e error states

```typescript
const { data, isLoading, error } = useDashboard();

if (isLoading) return <Spinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return <EmptyState />;

return <Dashboard data={data} />;
```

### 4. Memoize callbacks quando passar para hooks

```typescript
const handleSave = useCallback(async (data) => {
  await saveData(data);
}, []);

const autoSave = useAutoSave({
  key: 'form',
  data: formData,
  onSave: handleSave  // Memoizado
});
```

---

## Troubleshooting

### Hook não encontrado

```
Error: Cannot find module '@/hooks/useXxx'
```

**Solução:** Verifique se o hook está exportado em `/src/hooks/index.ts`

### Provider não encontrado

```
Error: useXxx must be used within XxxProvider
```

**Solução:** Adicione o provider necessário em `/src/contexts/providers.tsx`

### Auto-save não funciona

**Checklist:**
- [ ] `DraftCleanupProvider` está no providers.tsx?
- [ ] `enabled` está `true`?
- [ ] `key` é único por formulário?
- [ ] `data` está mudando?

### Notificações não chegam

**Checklist:**
- [ ] Service Worker registrado?
- [ ] Permissão concedida?
- [ ] Navegador suporta Push API?
- [ ] Backend enviando corretamente?

---

## Contribuindo

Ao criar novos hooks:

1. Coloque em `/src/hooks/` (hooks globais) ou `/src/features/xxx/hooks/` (hooks específicos)
2. Adicione export no barrel (`/src/hooks/index.ts`)
3. Documente neste README
4. Adicione exemplos de uso
5. Inclua types exportados
6. Teste em ambiente real

---

## Changelog

### 2025-01-26
- ✅ Criado barrel export centralizado
- ✅ Integrado hooks de notificações
- ✅ Integrado hooks de produtividade
- ✅ Integrado hooks de onboarding
- ✅ Documentação completa

---

**Dúvidas?** Consulte a documentação do hook específico ou abra uma issue.
