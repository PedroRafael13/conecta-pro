# Arquitetura de Hooks e Providers - Conecta Plus

## Diagrama de Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│                         ROOT LAYOUT                               │
│                      /src/app/layout.tsx                          │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    PROVIDERS HIERARCHY                            │
│                  /src/contexts/providers.tsx                      │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ThemeProvider (dark/light)                               │   │
│  │  └── QueryClientProvider (React Query)                   │   │
│  │       └── PushNotificationProvider ✨ NOVO                │   │
│  │            └── DraftCleanupProvider                       │   │
│  │                 └── ProductivityProvider                  │   │
│  │                      └── {children}                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Funcionalidades Globais:                                        │
│  • cleanupExpiredDrafts() → useEffect                           │
│  • Theme management → ThemeProvider                              │
│  • Data fetching → QueryClientProvider                          │
│  • Push notifications → PushNotificationProvider                │
│  • Draft cleanup → DraftCleanupProvider                         │
│  • Keyboard shortcuts → ProductivityProvider                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Barrel Export System

```
┌──────────────────────────────────────────────────────────────────┐
│                   BARREL EXPORT CENTRAL                           │
│                    /src/hooks/index.ts                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  // Import único para desenvolvedores                   │    │
│  │  import { useAuth, usePosts, useNotifications } from    │    │
│  │         '@/hooks';                                       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Organização:                                                    │
│  ├── 🔐 Autenticação (useAuth, usePermission)                   │
│  ├── 🏢 Operacional (usePosts, useScales, etc.)                 │
│  ├── 🎯 CRM (useLeads)                                          │
│  ├── 📊 Dashboard (useDashboardStats, useKPITrends)             │
│  ├── 🚀 Produtividade (useAutoSave, useKeyboardShortcuts)       │
│  ├── 🔔 Notificações (useNotifications, usePushNotifications)   │
│  └── 🎓 Onboarding (useTour)                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Hooks por Categoria

### 1. Autenticação e Autorização

```
┌────────────────────┐
│    useAuth()       │ ──► Login/Logout/User
├────────────────────┤
│  usePermission()   │ ──► Check permissions
└────────────────────┘
```

### 2. Módulo Operacional

```
                    ┌─────────────────────────────┐
                    │   MÓDULO OPERACIONAL        │
                    └─────────────┬───────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐      ┌───────────────┐       ┌──────────────┐
│    POSTOS     │      │    ESCALAS    │       │ COLABORADORES│
├───────────────┤      ├───────────────┤       ├──────────────┤
│ usePosts      │      │ useScales     │       │ useEmployees │
│ usePost       │      │ useScale      │       │ useAllocations│
│ usePostStats  │      │ useScaleStats │       └──────────────┘
└───────────────┘      │ useTemplates  │
                       │ useTemplate   │
                       └───────────────┘
        │                         │
        │                         ▼
        │              ┌───────────────────┐
        │              │    OPERAÇÕES      │
        │              ├───────────────────┤
        │              │ useShifts         │
        │              │ usePatrolRounds   │
        │              │ useOccurrences    │
        │              │ useDisciplinary   │
        │              │ useReimbursements │
        │              └───────────────────┘
        │
        └─────────────────────────────────────────┐
                                                  │
                                                  ▼
                                    ┌──────────────────────┐
                                    │   SUB-OPERATIONS     │
                                    ├──────────────────────┤
                                    │ useScaleOperations   │
                                    │ useShiftOperations   │
                                    │ useOccurrenceMutations│
                                    │ usePatrolRoundMutations│
                                    └──────────────────────┘
```

### 3. Dashboard e Analytics

```
┌─────────────────────────┐
│     DASHBOARD           │
├─────────────────────────┤
│ useDashboardStats       │ ──► Estatísticas gerais
│ useRecentActivities     │ ──► Atividades recentes
│ useHealthCheck          │ ──► Status do sistema
│ useKPITrends            │ ──► Tendências (7d/30d/90d)
└─────────────────────────┘
```

### 4. Produtividade

```
┌──────────────────────────────────────────────────────┐
│               PRODUTIVIDADE                          │
├──────────────────────────────────────────────────────┤
│  useAutoSave                                         │
│  ├── Auto-save com debounce                          │
│  ├── localStorage com expiração                      │
│  ├── Sanitização de campos sensíveis                │
│  └── cleanupExpiredDrafts()                          │
│                                                       │
│  useKeyboardShortcuts                                │
│  ├── Atalhos customizados                            │
│  ├── Ignorar inputs/textareas                        │
│  └── useGlobalShortcuts                              │
│       ├── / → Busca global                           │
│       ├── Ctrl+K → Command palette                   │
│       ├── Ctrl+B → Toggle sidebar                    │
│       ├── Alt+1/2/3/4 → Navegação módulos            │
│       └── Shift+? → Ajuda                            │
└──────────────────────────────────────────────────────┘
```

### 5. Notificações

```
┌────────────────────────────────────────────────┐
│          SISTEMA DE NOTIFICAÇÕES               │
├────────────────────────────────────────────────┤
│                                                 │
│  PushNotificationProvider                      │
│  └── Auto-inicializa Service Worker            │
│                                                 │
│  useNotifications                               │
│  ├── Lista de notificações                     │
│  ├── Contagem não lidas                        │
│  ├── Marcar como lida                          │
│  ├── Marcar todas como lidas                   │
│  └── Auto-refresh (30s)                        │
│                                                 │
│  usePushNotifications                           │
│  ├── Verificar suporte do navegador            │
│  ├── Gerenciar permissões                      │
│  ├── Subscribe/Unsubscribe                     │
│  └── Service Worker registration               │
└────────────────────────────────────────────────┘
```

### 6. Onboarding

```
┌──────────────────────────────────────────┐
│         TOUR DE ONBOARDING               │
├──────────────────────────────────────────┤
│  useTour                                 │
│  ├── Controle completo do tour           │
│  ├── Shepherd.js integration             │
│  ├── Auto-start configurável             │
│  └── Roles: ADMIN, USUARIO               │
│                                           │
│  useShouldShowTour                        │
│  └── Verificação se deve mostrar         │
│                                           │
│  useTourProgress                          │
│  ├── Tracking de progresso               │
│  ├── markStarted()                        │
│  ├── markCompleted()                      │
│  └── incrementCancelCount()              │
└──────────────────────────────────────────┘
```

---

## Fluxo de Dados

### 1. Autenticação

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Login   │────▶│ useAuth  │────▶│   API    │────▶│  Store   │
│  Page    │     │          │     │          │     │  Cookie  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                      │
                      ▼
              ┌──────────────┐
              │ Layout/Pages │
              │ Check Auth   │
              └──────────────┘
```

### 2. Notificações Push

```
┌──────────────────┐     ┌─────────────────────┐
│  PushNotification│────▶│  Service Worker     │
│  Provider        │     │  /public/sw.js      │
└──────────────────┘     └─────────────────────┘
         │                         │
         ▼                         ▼
┌──────────────────┐     ┌─────────────────────┐
│ useNotifications │◀────│  Backend API        │
│ Auto-refresh 30s │     │  POST /subscribe    │
└──────────────────┘     │  GET /notifications │
         │               └─────────────────────┘
         ▼
┌──────────────────┐
│ NotificationBell │
│ Component        │
└──────────────────┘
```

### 3. Auto-Save

```
┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│  Form Data   │────▶│  useAutoSave   │────▶│ localStorage │
│  Changes     │     │  debounce 2s   │     │  draft_*     │
└──────────────┘     └────────────────┘     └──────────────┘
                             │
                             ├─────► sanitize (remove secrets)
                             └─────► onSave() optional backend

On Mount:
┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│ Form Open    │────▶│  restore()     │────▶│ Populate Form│
└──────────────┘     │  check draft   │     └──────────────┘
                     └────────────────┘

On App Init:
┌──────────────┐     ┌──────────────────────┐
│ Providers    │────▶│ cleanupExpiredDrafts │
│ useEffect    │     │ remove > 7 days      │
└──────────────┘     └──────────────────────┘
```

### 4. Keyboard Shortcuts

```
┌─────────────────┐
│ window.keydown  │
└────────┬────────┘
         │
         ▼
┌────────────────────────┐
│ useKeyboardShortcuts   │
│ • Check if input       │
│ • Match shortcut       │
│ • Execute action       │
└────────┬───────────────┘
         │
         ├────▶ / → openSearch()
         ├────▶ Ctrl+K → openCommandPalette()
         ├────▶ Ctrl+B → toggleSidebar()
         ├────▶ Alt+1 → navigate('/dashboard')
         └────▶ Shift+? → openHelp()
```

---

## Dependências Entre Hooks

```
useNotifications
    │
    └──► usePushNotifications
             └──► registerServiceWorker()

useTemplateOperations
    │
    └──► useToast (shadcn/ui)
    └──► scaleTemplatesService

useAutoSave
    │
    └──► localStorage
    └──► DraftCleanupProvider

useTour
    │
    └──► Shepherd.js
    └──► localStorage (progress)

useKeyboardShortcuts
    │
    └──► useRouter (next/navigation)
    └──► ProductivityProvider
```

---

## Estrutura de Arquivos

```
/opt/conecta-pro/frontend/
│
├── src/
│   ├── hooks/
│   │   ├── index.ts ✨ NOVO (Barrel export)
│   │   ├── README.md ✨ NOVO (Documentação)
│   │   ├── HOOKS_INDEX.md ✨ NOVO (Índice rápido)
│   │   ├── useAuth.ts
│   │   ├── usePermission.ts
│   │   ├── usePosts.ts
│   │   ├── useScales.ts
│   │   ├── useScaleTemplates.ts ✅ Integrado
│   │   ├── useAllocations.ts
│   │   ├── useEmployees.ts
│   │   ├── useShifts.ts
│   │   ├── usePatrolRounds.ts
│   │   ├── useOccurrences.ts
│   │   ├── useDisciplinary.ts
│   │   ├── useReimbursement.ts
│   │   ├── useLeads.ts
│   │   ├── useDashboard.ts
│   │   ├── useKPITrends.ts ✅ Integrado
│   │   ├── useAutoSave.ts ✅ Integrado
│   │   └── useKeyboardShortcuts.ts ✅ Integrado
│   │
│   ├── features/
│   │   ├── notifications/
│   │   │   ├── hooks/
│   │   │   │   ├── useNotifications.ts ✅ Integrado
│   │   │   │   └── usePushNotifications.ts ✅ Integrado
│   │   │   ├── components/
│   │   │   │   ├── NotificationBell.tsx
│   │   │   │   ├── NotificationCenter.tsx
│   │   │   │   ├── PushNotificationProvider.tsx ✨ NOVO
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   │
│   │   └── onboarding/
│   │       ├── hooks/
│   │       │   └── useTour.ts ✅ Integrado
│   │       ├── components/
│   │       │   ├── TourTrigger.tsx
│   │       │   └── OperacionalTourProvider.tsx
│   │       └── index.ts
│   │
│   └── contexts/
│       └── providers.tsx ✅ Modificado (+ PushNotificationProvider)
│
├── INTEGRATION_REPORT.md ✨ NOVO
├── HOOKS_INTEGRATION_SUMMARY.md ✨ NOVO
└── HOOKS_STATUS.txt ✨ NOVO
```

---

## Checklist de Integração

### ✅ Hooks Órfãos
- [x] useNotifications
- [x] usePushNotifications
- [x] useAutoSave
- [x] useKPITrends
- [x] useScaleTemplates
- [x] useTour
- [x] useKeyboardShortcuts

### ✅ Infraestrutura
- [x] Barrel export criado
- [x] Providers configurados
- [x] TypeScript sem erros
- [x] Documentação completa

### ✅ Funcionalidades
- [x] Notificações push operacionais
- [x] Auto-save funcionando
- [x] Atalhos de teclado ativos
- [x] Tour de onboarding pronto
- [x] KPI trends disponível
- [x] Templates de escala operacionais

---

## Métricas

| Métrica | Valor |
|---------|-------|
| Total de Hooks | 50+ |
| Hooks Integrados | 7 |
| Providers | 5 |
| Linhas de Documentação | 1500+ |
| Arquivos Criados | 6 |
| Arquivos Modificados | 4 |
| Erros TypeScript | 0 |

---

**Status:** ✅ INTEGRAÇÃO COMPLETA
**Data:** 2026-01-26
**Agente:** #2 - Especialista em React e Arquitetura Frontend
