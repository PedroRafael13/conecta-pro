# Comandos Úteis - Tour Guiado

Comandos para testar, debugar e gerenciar o sistema de onboarding.

## 🧪 Testes e Debug

### Resetar Tour (Console do Browser)

```javascript
// Limpar localStorage do tour
localStorage.removeItem('tour_operacional_completed');
localStorage.removeItem('tour_operacional_completed_at');
localStorage.removeItem('tour_operacional_started_at');
localStorage.removeItem('tour_operacional_cancel_count');

// Ou limpar tudo
localStorage.clear();

// Recarregar página
location.reload();
```

### Verificar Status do Tour

```javascript
// Verificar se tour foi completado
console.log('Completado:', localStorage.getItem('tour_operacional_completed'));

// Ver quando foi completado
console.log('Data:', localStorage.getItem('tour_operacional_completed_at'));

// Contar cancelamentos
console.log('Cancelamentos:', localStorage.getItem('tour_operacional_cancel_count'));
```

### Iniciar Tour Manualmente

```javascript
// No console do browser (se usou o hook)
// Não funciona diretamente, use o componente TourTrigger
```

### Simular Diferentes Roles

Edite temporariamente o componente:

```tsx
<OperacionalTourProvider userRole="CEO">        // Analytics
<OperacionalTourProvider userRole="GERENTE">    // Gestão
<OperacionalTourProvider userRole="SUPERVISOR"> // Operações
<OperacionalTourProvider userRole="USUARIO">    // Base
```

---

## 🔧 Build e Desenvolvimento

### Instalar Dependências

```bash
cd /opt/conecta-pro/frontend
npm install
```

### Rebuild (se necessário)

```bash
cd /opt/conecta-pro/frontend
npm run build
```

### Dev Server

```bash
cd /opt/conecta-pro/frontend
npm run dev
```

---

## 📁 Arquivos e Estrutura

### Ver Arquivos do Tour

```bash
ls -la /opt/conecta-pro/frontend/src/features/onboarding/
```

### Contar Linhas de Código

```bash
wc -l /opt/conecta-pro/frontend/src/features/onboarding/**/*.{ts,tsx,css,md}
```

### Buscar por Data Attributes

```bash
grep -r "data-tour" /opt/conecta-pro/frontend/src/app/modulos/
```

---

## 🐛 Debug

### Ver Erros no Console

Abra DevTools (F12) e veja:
- Console → Erros JavaScript
- Network → CSS carregando?
- Application → LocalStorage

### Verificar CSS

```javascript
// No console
const link = document.querySelector('link[href*="shepherd"]');
console.log('CSS carregado:', !!link);
```

### Verificar se Elemento Existe

```javascript
// No console
const element = document.querySelector('[data-tour="dashboard-kpis"]');
console.log('Elemento encontrado:', !!element);
```

### Forçar Início do Tour

No código, adicione:

```tsx
useEffect(() => {
  setTimeout(() => {
    startTour();
  }, 2000); // 2 segundos
}, []);
```

---

## 📊 Analytics e Tracking

### Verificar Progresso

```javascript
// No console
const progress = {
  completed: localStorage.getItem('tour_operacional_completed'),
  started: localStorage.getItem('tour_operacional_started_at'),
  finished: localStorage.getItem('tour_operacional_completed_at'),
  cancels: localStorage.getItem('tour_operacional_cancel_count') || 0
};

console.table(progress);
```

### Tempo Médio de Conclusão

```javascript
const started = new Date(localStorage.getItem('tour_operacional_started_at'));
const finished = new Date(localStorage.getItem('tour_operacional_completed_at'));
const duration = (finished - started) / 1000 / 60; // minutos

console.log(`Duração: ${duration.toFixed(2)} minutos`);
```

---

## 🎨 Customização Rápida

### Alterar Cores (CSS)

Edite `/frontend/src/features/onboarding/styles/shepherd-custom.css`:

```css
/* Botão primário */
.shepherd-button-primary {
  background: #SUA_COR;
}

/* Overlay */
.shepherd-modal-overlay {
  background-color: rgba(0, 0, 0, 0.7); /* Mais escuro */
}
```

### Alterar Textos

Edite `/frontend/src/features/onboarding/tours/operacionalTour.ts`:

```typescript
{
  id: 'welcome',
  title: 'SEU TÍTULO',
  text: 'SUA DESCRIÇÃO',
}
```

### Adicionar Novo Step

```typescript
const newStep: TourStep = {
  id: 'meu-step',
  title: 'Meu Título',
  text: 'Descrição',
  attachTo: {
    element: '[data-tour="meu-elemento"]',
    on: 'bottom',
  },
  buttons: [btns.back, btns.next],
};

// Adicionar ao array de steps
steps.push(newStep);
```

---

## 🔄 Git Commands

### Ver Mudanças

```bash
cd /opt/conecta-pro
git status
git diff
```

### Commit

```bash
git add frontend/src/features/onboarding/
git commit -m "feat: implementar sistema de onboarding com tour guiado"
```

---

## 📦 Exportar/Importar Tour

### Exportar Configuração

```bash
# Copiar feature inteira
cp -r /opt/conecta-pro/frontend/src/features/onboarding /backup/
```

### Importar em Outro Projeto

```bash
# Copiar para novo projeto
cp -r /backup/onboarding /novo-projeto/src/features/

# Instalar dependência
npm install shepherd.js
```

---

## 🚀 Deploy

### Verificar Build

```bash
cd /opt/conecta-pro/frontend
npm run build
```

### Verificar Tamanho

```bash
du -sh .next/static/chunks/*shepherd*
```

---

## 🧹 Limpeza

### Remover Tour (se necessário)

```bash
# Remover arquivos
rm -rf /opt/conecta-pro/frontend/src/features/onboarding/

# Desinstalar dependência
npm uninstall shepherd.js

# Remover imports nos componentes
```

### Limpar Cache do Next.js

```bash
cd /opt/conecta-pro/frontend
rm -rf .next
npm run build
```

---

## 📝 Logs Úteis

### Habilitar Logs de Debug

No componente:

```tsx
tour.on('show', () => {
  console.log('[TOUR] Step shown:', tour.getCurrentStep()?.id);
});

tour.on('complete', () => {
  console.log('[TOUR] Tour completed!');
});

tour.on('cancel', () => {
  console.log('[TOUR] Tour cancelled');
});
```

### Ver Eventos do Shepherd

```javascript
// No console
window.addEventListener('shepherd', (e) => {
  console.log('Shepherd event:', e.detail);
});
```

---

## 🔍 Troubleshooting Commands

### Problema: CSS não carrega

```bash
# Verificar se arquivo existe
ls -la /opt/conecta-pro/frontend/src/features/onboarding/styles/shepherd-custom.css

# Verificar import no componente
grep -n "shepherd-custom.css" /opt/conecta-pro/frontend/src/features/onboarding/components/OperacionalTourProvider.tsx
```

### Problema: Elemento não encontrado

```javascript
// No console, verificar todos os data-tour
const elements = document.querySelectorAll('[data-tour]');
console.log('Elementos com data-tour:', elements.length);
elements.forEach(el => console.log(el.getAttribute('data-tour')));
```

### Problema: Tour em loop

```javascript
// Forçar completar
localStorage.setItem('tour_operacional_completed', 'true');
location.reload();
```

---

## 📱 Teste em Dispositivos

### Responsividade

```javascript
// Simular mobile no DevTools
// Ctrl+Shift+M (Chrome) ou Cmd+Shift+M (Mac)

// Ou resize manual
window.innerWidth; // ver largura atual
```

### Dark Mode

```javascript
// Forçar dark mode (console)
document.documentElement.classList.add('dark');

// Forçar light mode
document.documentElement.classList.remove('dark');
```

---

## 💡 Dicas

1. **Sempre teste com localStorage limpo** para simular novo usuário
2. **Use Incognito Mode** para testes rápidos sem cache
3. **Console.log é seu amigo** para debug
4. **DevTools → Application → LocalStorage** para ver dados salvos
5. **F12 → Elements** para inspecionar data-tour attributes

---

**Referência Completa:** Veja `README.md` para documentação detalhada.
