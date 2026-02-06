# Sistema de Onboarding - Tour Guiado

Sistema completo de tour guiado para novos usuários do Módulo Operacional, utilizando Shepherd.js.

## Características

- ✅ Tour interativo com 7 steps principais
- ✅ Auto-start no primeiro acesso
- ✅ Persistência em localStorage
- ✅ Tours diferenciados por perfil (CEO, Gerente, Supervisor, Usuário)
- ✅ Suporte a modo escuro
- ✅ Responsivo (mobile e desktop)
- ✅ Opção de refazer tour
- ✅ Notificações para novos usuários

## Instalação

```bash
npm install shepherd.js
```

## Uso Básico

### 1. Importar CSS

No arquivo principal ou layout:

```typescript
import 'shepherd.js/dist/css/shepherd.css';
import '@/features/onboarding/styles/shepherd-custom.css';
```

### 2. Usar o Provider

Envolva sua página com o `OperacionalTourProvider`:

```tsx
import { OperacionalTourProvider } from '@/features/onboarding';

export default function OperacionalPage() {
  return (
    <OperacionalTourProvider
      userRole="USUARIO"
      autoStart={true}
      showNotification={true}
    >
      {/* Conteúdo da página */}
    </OperacionalTourProvider>
  );
}
```

### 3. Adicionar Data Attributes

Adicione `data-tour` nos elementos que o tour deve destacar:

```tsx
<div data-tour="dashboard-kpis">
  {/* KPIs */}
</div>

<nav data-tour="sidebar-nav">
  {/* Navegação */}
</nav>

<div data-tour="global-search">
  {/* Busca */}
</div>

<div data-tour="notifications">
  {/* Notificações */}
</div>

<div data-tour="quick-actions">
  {/* Ações Rápidas */}
</div>
```

## Data Attributes Disponíveis

| Attribute | Descrição |
|-----------|-----------|
| `data-tour="dashboard-kpis"` | Dashboard de KPIs principais |
| `data-tour="sidebar-nav"` | Navegação lateral |
| `data-tour="global-search"` | Busca global |
| `data-tour="notifications"` | Central de notificações |
| `data-tour="quick-actions"` | Menu de ações rápidas |
| `data-tour="analytics-charts"` | Gráficos e analytics (CEO) |
| `data-tour="team-panel"` | Painel de gestão de equipe (Gerente) |
| `data-tour="operations-panel"` | Painel de operações diárias (Supervisor) |

## Componentes

### OperacionalTourProvider

Provider principal que gerencia o tour.

```tsx
<OperacionalTourProvider
  userRole="USUARIO"  // 'CEO' | 'GERENTE' | 'SUPERVISOR' | 'USUARIO'
  autoStart={true}    // Auto-iniciar no primeiro acesso
  showNotification={true}  // Mostrar notificação de tour disponível
>
  {children}
</OperacionalTourProvider>
```

### TourTrigger

Botão para iniciar/refazer o tour.

```tsx
import { TourTrigger } from '@/features/onboarding';

// Variante button
<TourTrigger variant="button" role="USUARIO" />

// Variante menu-item
<TourTrigger variant="menu-item" role="USUARIO" />

// Variante badge
<TourTrigger variant="badge" role="USUARIO" />
```

### FloatingTourTrigger

Botão flutuante no canto da tela.

```tsx
import { FloatingTourTrigger } from '@/features/onboarding';

<FloatingTourTrigger role="USUARIO" />
```

### TourProgress

Barra de progresso do tour.

```tsx
import { TourProgress } from '@/features/onboarding';

<TourProgress />
```

### TourNotification

Notificação para usuários que ainda não fizeram o tour.

```tsx
import { TourNotification } from '@/features/onboarding';

<TourNotification role="USUARIO" />
```

## Hooks

### useTour

Hook principal para gerenciar o tour.

```tsx
import { useTour } from '@/features/onboarding';

function MyComponent() {
  const {
    isCompleted,     // Tour foi completado?
    isActive,        // Tour está ativo?
    currentStep,     // Step atual (número)
    totalSteps,      // Total de steps
    startTour,       // Iniciar tour
    resetTour,       // Resetar tour
    cancelTour,      // Cancelar tour
  } = useTour('USUARIO', false);

  return (
    <button onClick={startTour}>
      Iniciar Tour
    </button>
  );
}
```

### useShouldShowTour

Hook simples para verificar se deve mostrar tour.

```tsx
import { useShouldShowTour } from '@/features/onboarding';

function MyComponent() {
  const shouldShow = useShouldShowTour();

  if (!shouldShow) return null;

  return <div>Faça o tour!</div>;
}
```

### useTourProgress

Hook para tracking detalhado de progresso.

```tsx
import { useTourProgress } from '@/features/onboarding';

function MyComponent() {
  const {
    progress: {
      started,
      completed,
      startedAt,
      completedAt,
      cancelCount
    },
    markStarted,
    markCompleted,
    incrementCancelCount
  } = useTourProgress();

  return (
    <div>
      {completed ? 'Concluído' : 'Pendente'}
    </div>
  );
}
```

## Tours por Perfil

### USUARIO (Base)

Tour padrão com 7 steps:
1. Welcome
2. Dashboard KPIs
3. Sidebar Navigation
4. Busca Global
5. Notificações
6. Ações Rápidas
7. Finish

### CEO

Tour base + step adicional de **Analytics**:
- Foco em gráficos e análises aprofundadas
- Comparativos entre unidades
- Previsões baseadas em IA

### GERENTE

Tour base + step adicional de **Gestão de Equipe**:
- Aprovação de escalas
- Gestão de férias e licenças
- Avaliação de desempenho

### SUPERVISOR

Tour base + step adicional de **Operações Diárias**:
- Registro de ponto
- Reportar ocorrências
- Checklist de abertura/fechamento

## Customização

### CSS Customizado

O arquivo `shepherd-custom.css` contém toda a customização visual:

- Cores alinhadas com o design system
- Suporte a modo escuro
- Animações suaves
- Responsividade

Para customizar:

```css
/* Cores do botão primário */
.shepherd-button-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

/* Modal overlay */
.shepherd-modal-overlay {
  background-color: rgba(0, 0, 0, 0.5);
}
```

### Criar Tour Customizado

```typescript
import { createOperacionalTour } from '@/features/onboarding/tours/operacionalTour';

const tour = createOperacionalTour('USUARIO');

// Adicionar step customizado
tour.addStep({
  id: 'custom-step',
  title: 'Meu Step Customizado',
  text: 'Descrição aqui',
  attachTo: {
    element: '[data-tour="my-element"]',
    on: 'bottom',
  },
  buttons: [
    {
      text: 'Próximo',
      action: tour.next,
    }
  ],
});

tour.start();
```

## LocalStorage

O tour utiliza localStorage para persistência:

| Key | Descrição |
|-----|-----------|
| `tour_operacional_completed` | Tour foi completado? |
| `tour_operacional_completed_at` | Data/hora de conclusão |
| `tour_operacional_started_at` | Data/hora de início |
| `tour_operacional_cancel_count` | Quantidade de vezes cancelado |

## Responsividade

O tour é totalmente responsivo:

- **Desktop:** Steps com setas indicativas e posicionamento lateral
- **Mobile:** Steps adaptados para telas menores, modais centralizados
- **Tablet:** Layout intermediário

## Acessibilidade

- ✅ Navegação por teclado (Tab, Escape)
- ✅ Focus visível
- ✅ ARIA labels
- ✅ Contraste adequado

## Troubleshooting

### Tour não inicia

1. Verifique se `data-tour` attributes estão presentes
2. Confirme que CSS foi importado
3. Verifique console para erros

### Element não encontrado

O tour aguarda até 5 segundos pelo elemento. Se não aparecer:

```typescript
// Adicione delay antes de iniciar
setTimeout(() => startTour(), 1000);
```

### Tour não reseta

```typescript
import { resetTour } from '@/features/onboarding';

// Resetar manualmente
resetTour();
```

## Exemplos

### Tour com Detecção de Role Automática

```tsx
import { OperacionalTourProvider } from '@/features/onboarding';
import { useAuth } from '@/hooks/useAuth';

export default function Page() {
  const { user } = useAuth();

  return (
    <OperacionalTourProvider
      userRole={user?.role as UserRole}
      autoStart={true}
    >
      {/* Content */}
    </OperacionalTourProvider>
  );
}
```

### Tour Apenas para Novos Usuários

```tsx
import { useShouldShowTour } from '@/features/onboarding';

export default function Page() {
  const shouldShow = useShouldShowTour();

  return (
    <OperacionalTourProvider
      autoStart={shouldShow}
      showNotification={shouldShow}
    >
      {/* Content */}
    </OperacionalTourProvider>
  );
}
```

## Performance

- Tour só carrega quando necessário
- CSS minificado
- LocalStorage para evitar re-renders
- Lazy loading de steps

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contribuindo

Para adicionar novos steps ao tour:

1. Adicione o step em `operacionalTour.ts`
2. Adicione o `data-tour` attribute no componente
3. Teste em todos os roles
4. Atualize esta documentação

## License

MIT
