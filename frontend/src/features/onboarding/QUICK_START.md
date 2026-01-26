# Quick Start - Tour Guiado

Guia rápido para implementar o tour guiado em 5 minutos.

## 1️⃣ Importar CSS (Apenas 1x no app)

No seu layout root ou `_app.tsx`:

```tsx
import 'shepherd.js/dist/css/shepherd.css';
import '@/features/onboarding/styles/shepherd-custom.css';
```

## 2️⃣ Envolver Página com Provider

```tsx
import { OperacionalTourProvider } from '@/features/onboarding';

export default function MinhaPage() {
  return (
    <OperacionalTourProvider
      userRole="USUARIO"
      autoStart={true}
    >
      {/* Seu conteúdo aqui */}
    </OperacionalTourProvider>
  );
}
```

## 3️⃣ Adicionar Data Attributes

Marque os elementos que quer destacar no tour:

```tsx
<div data-tour="dashboard-kpis">
  {/* KPIs */}
</div>

<nav data-tour="sidebar-nav">
  {/* Menu */}
</nav>

<input data-tour="global-search" />

<button data-tour="notifications">
  🔔
</button>

<div data-tour="quick-actions">
  {/* Ações */}
</div>
```

## 4️⃣ Adicionar Botão de Refazer (Opcional)

```tsx
import { TourTrigger } from '@/features/onboarding';

// No menu de ajuda
<TourTrigger variant="menu-item" />

// Como botão
<TourTrigger variant="button" />
```

## 5️⃣ Testar

1. Abra o navegador
2. Limpe localStorage: `localStorage.clear()`
3. Recarregue a página
4. O tour deve iniciar automaticamente! 🎉

---

## Data Attributes Disponíveis

| Attribute | Onde usar |
|-----------|-----------|
| `data-tour="dashboard-kpis"` | Dashboard/KPIs |
| `data-tour="sidebar-nav"` | Menu lateral |
| `data-tour="global-search"` | Campo de busca |
| `data-tour="notifications"` | Sino de notificações |
| `data-tour="quick-actions"` | Botão de ações |
| `data-tour="analytics-charts"` | Gráficos (CEO) |
| `data-tour="team-panel"` | Painel equipe (Gerente) |
| `data-tour="operations-panel"` | Painel ops (Supervisor) |

---

## Roles Disponíveis

```tsx
<OperacionalTourProvider userRole="USUARIO">      {/* 7 steps */}
<OperacionalTourProvider userRole="SUPERVISOR">   {/* 8 steps */}
<OperacionalTourProvider userRole="GERENTE">      {/* 8 steps */}
<OperacionalTourProvider userRole="CEO">          {/* 8 steps */}
```

---

## Usar com Hook

```tsx
import { useTour } from '@/features/onboarding';

function MeuComponente() {
  const { isCompleted, startTour } = useTour('USUARIO');

  if (!isCompleted) {
    return <button onClick={startTour}>Fazer Tour</button>;
  }

  return <div>Tour já completado! ✓</div>;
}
```

---

## Resetar Tour

```tsx
import { resetTour } from '@/features/onboarding';

// Limpa localStorage e permite refazer
resetTour();
```

---

## Troubleshooting Rápido

**Tour não aparece?**
- Verifique se CSS foi importado
- Confirme que `autoStart={true}`
- Limpe localStorage

**Elemento não encontrado?**
- Verifique se `data-tour` está correto
- Elemento pode estar hidden
- Adicione delay: `setTimeout(() => startTour(), 1000)`

---

## Pronto! 🚀

Seu tour está funcionando. Para customização avançada, veja o README.md completo.
