# Demonstração Visual - Sistema de Produtividade

## 1. SearchTrigger no Header

```
┌─────────────────────────────────────────────────────────────┐
│ [☰] Operacional              [🔍 Buscar...  /]    [🌙]      │
└─────────────────────────────────────────────────────────────┘
                                      ↑
                              SearchTrigger aqui
```

**Estados:**
- Normal: Cinza claro com borda
- Hover: Fundo accent
- Click: Abre GlobalSearch

---

## 2. GlobalSearch Modal (/)

```
╔═══════════════════════════════════════════════════════════╗
║                    BUSCA GLOBAL                           ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  🔍 [joão silva___________________]  ⊗                   ║
║                                                           ║
╟───────────────────────────────────────────────────────────╢
║  👤 COLABORADOR (3)                                       ║
║  ┌───────────────────────────────────────────────────┐   ║
║  │ 👤  João Silva                              Enter │   ║ ← Selecionado
║  │     Portaria - Matriz                             │   ║
║  ├───────────────────────────────────────────────────┤   ║
║  │ 👤  João da Silva Santos                          │   ║
║  │     Segurança - Filial 1                          │   ║
║  └───────────────────────────────────────────────────┘   ║
║                                                           ║
║  📍 POSTO (2)                                             ║
║  ┌───────────────────────────────────────────────────┐   ║
║  │ 📍  Portaria João XXIII                           │   ║
║  │     Cliente: Condomínio Central                   │   ║
║  └───────────────────────────────────────────────────┘   ║
║                                                           ║
╟───────────────────────────────────────────────────────────╢
║  ↑↓ Navegar    Enter Abrir    Esc Fechar    5 em 87ms   ║
╚═══════════════════════════════════════════════════════════╝
```

**Features:**
- Input com auto-focus
- Loading spinner durante busca
- Resultados agrupados por tipo
- Seleção com teclado ou mouse
- Métricas de performance

---

## 3. Command Palette (Ctrl+K)

```
╔═══════════════════════════════════════════════════════════╗
║                  COMMAND PALETTE                          ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  🔍 [novo___________________]  ⊗                         ║
║                                                           ║
╟───────────────────────────────────────────────────────────╢
║  NAVEGAÇÃO                                                ║
║  ┌───────────────────────────────────────────────────┐   ║
║  │ 📄  Novo Posto                            Enter   │   ║ ← Selecionado
║  │     Cadastrar novo posto de trabalho              │   ║
║  ├───────────────────────────────────────────────────┤   ║
║  │ 👥  Novo Colaborador                              │   ║
║  │     Cadastrar novo colaborador                    │   ║
║  └───────────────────────────────────────────────────┘   ║
║                                                           ║
║  AÇÕES                                                    ║
║  ┌───────────────────────────────────────────────────┐   ║
║  │ 📅  Nova Escala                                   │   ║
║  │     Criar nova escala de trabalho                 │   ║
║  └───────────────────────────────────────────────────┘   ║
║                                                           ║
╟───────────────────────────────────────────────────────────╢
║  ↑↓ Navegar    Enter Executar    Esc Fechar              ║
╚═══════════════════════════════════════════════════════════╝
```

**Features:**
- Busca fuzzy em comandos
- Categorização automática
- Descrições detalhadas
- Ícones personalizados
- Feedback visual de seleção

---

## 4. Help Overlay (Shift+?)

```
╔═══════════════════════════════════════════════════════════╗
║                 ATALHOS DE TECLADO                  ⊗    ║
║  Navegue rapidamente pelo sistema                        ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  GERAL                                                    ║
║  ┌───────────────────────────────────────────────────┐   ║
║  │ Abrir busca global                           [ / ]│   ║
║  │ Abrir command palette                    [Ctrl+K]│   ║
║  │ Alternar sidebar                         [Ctrl+B]│   ║
║  │ Fechar modal/dropdown                      [Esc] │   ║
║  │ Mostrar atalhos disponíveis             [Shift+?]│   ║
║  └───────────────────────────────────────────────────┘   ║
║                                                           ║
║  NAVEGAÇÃO                                                ║
║  ┌───────────────────────────────────────────────────┐   ║
║  │ Dashboard                                  [Alt+1]│   ║
║  │ Operacional                                [Alt+2]│   ║
║  │ Financeiro                                 [Alt+3]│   ║
║  │ CRM                                        [Alt+4]│   ║
║  └───────────────────────────────────────────────────┘   ║
║                                                           ║
╟───────────────────────────────────────────────────────────╢
║  Pressione [Esc] para fechar        9 atalhos disponíveis║
╚═══════════════════════════════════════════════════════════╝
```

**Features:**
- Lista completa de atalhos
- Agrupamento por categoria
- Formatação visual de teclas
- Auto-atualizado com novos atalhos
- Contador de atalhos

---

## 5. Fluxo de Uso - Busca

```
1. Usuário no sistema
   │
   ├─→ Pressiona "/"
   │   │
   │   └─→ GlobalSearch abre
   │       │
   │       ├─→ Input recebe foco
   │       │
   │       ├─→ Digita "joão"
   │       │   │
   │       │   └─→ Debounce 300ms
   │       │       │
   │       │       └─→ API /search?q=joão
   │       │           │
   │       │           └─→ Resultados aparecem < 200ms
   │       │               │
   │       │               ├─→ Agrupados por tipo
   │       │               │
   │       │               └─→ Usa ↓ para selecionar
   │       │                   │
   │       │                   └─→ Pressiona Enter
   │       │                       │
   │       └───────────────────────┘
   │                               │
   └─→ Navega para URL do resultado
       │
       └─→ Modal fecha automaticamente
```

---

## 6. Fluxo de Uso - Command Palette

```
1. Usuário no sistema
   │
   ├─→ Pressiona "Ctrl+K"
   │   │
   │   └─→ Command Palette abre
   │       │
   │       ├─→ Input recebe foco
   │       │
   │       ├─→ Digita "novo posto"
   │       │   │
   │       │   └─→ Busca fuzzy filtra comandos
   │       │       │
   │       │       └─→ "Novo Posto" aparece
   │       │           │
   │       │           └─→ Pressiona Enter
   │       │               │
   │       └───────────────┘
   │                       │
   └─→ Executa ação (navega para /postos/novo)
       │
       └─→ Modal fecha automaticamente
```

---

## 7. Estados Visuais

### SearchTrigger
```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ 🔍 Buscar...  /  │ →  │ 🔍 Buscar...  /  │ →  │ 🔍 Buscar...  /  │
│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │    │ ████████████████ │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
   Normal                   Hover                  Clicked
```

### Resultado Selecionado
```
┌─────────────────────────────┐    ┌─────────────────────────────┐
│ 👤  João Silva              │    │ 👤  João Silva        Enter │
│     Portaria - Matriz       │ →  │     Portaria - Matriz       │
│                             │    │ ███████████████████████████ │
└─────────────────────────────┘    └─────────────────────────────┘
   Normal                             Selecionado
```

### Loading State
```
┌───────────────────────────────────┐
│ 🔍 [joão_______] ⭮ Carregando... │
│                                   │
│   [Sem resultados ainda]          │
└───────────────────────────────────┘
```

---

## 8. Responsividade

### Desktop (> 1024px)
```
┌────────────────────────────────────────────────────┐
│ Sidebar │ Header: [🔍 Buscar... /] [🌙] [👤]      │
│   Nav   │─────────────────────────────────────────│
│  [●]    │                                          │
│  [ ]    │           Conteúdo Principal            │
│  [ ]    │                                          │
└────────────────────────────────────────────────────┘
```

### Tablet (768-1024px)
```
┌────────────────────────────────────────────────────┐
│ Sidebar │ Header: [🔍] [🌙] [👤]                  │
│   Nav   │─────────────────────────────────────────│
│  [●]    │                                          │
│  [ ]    │           Conteúdo Principal            │
└────────────────────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌──────────────────────────────┐
│ [☰] Header [🌙] [👤]        │
├──────────────────────────────┤
│                              │
│     Conteúdo Principal       │
│                              │
│  (Busca via menu mobile)     │
└──────────────────────────────┘
```

---

## 9. Animações

### Abertura de Modal
```
Frame 1:  opacity: 0,    scale: 0.95
Frame 2:  opacity: 0.3,  scale: 0.97
Frame 3:  opacity: 0.7,  scale: 0.99
Frame 4:  opacity: 1,    scale: 1

Duração: 200ms
Easing: ease-out
```

### Seleção de Item
```
Antes:  background: transparent
Hover:  background: accent/50      (150ms)
Active: background: accent          (100ms)
```

---

## 10. Paleta de Cores (Dark Mode)

```
Background:      hsl(222, 47%, 11%)  #0a0c10
Foreground:      hsl(210, 40%, 98%)  #f8fafc
Muted:          hsl(217, 33%, 17%)   #1e293b
Border:         hsl(217, 33%, 20%)   #232d3f
Accent:         hsl(217, 91%, 60%)   #3b82f6
Primary:        hsl(222, 84%, 40%)   #1e40af
Destructive:    hsl(0, 84%, 60%)     #ef4444
```

---

## 11. Tipografia

```
Title (Modal):     font-size: 1.125rem (18px)  font-weight: 600
Command:           font-size: 0.875rem (14px)  font-weight: 500
Description:       font-size: 0.75rem  (12px)  font-weight: 400
Shortcut (kbd):    font-size: 0.75rem  (12px)  font-family: mono
Footer:            font-size: 0.75rem  (12px)  font-weight: 400
```

---

## 12. Spacing

```
Modal Padding:     24px (1.5rem)
Item Padding:      12px 16px (0.75rem 1rem)
Gap between items: 8px  (0.5rem)
Modal Border:      1px
Border Radius:     8px  (0.5rem)
```

---

## 13. Acessibilidade - Focus States

```
Normal:
┌─────────────────────┐
│ Novo Posto          │
└─────────────────────┘

Focused (Tab):
┏━━━━━━━━━━━━━━━━━━━━━┓  ← Borda azul 2px
┃ Novo Posto          ┃
┗━━━━━━━━━━━━━━━━━━━━━┛

Selected (Arrow key):
┌─────────────────────┐
│ Novo Posto          │  ← Background accent
└─────────────────────┘
```

---

**LEGENDA:**
- `[ ]` = Input field
- `[🔍]` = Ícone
- `[Ctrl+K]` = Tecla/Atalho
- `→` = Transição
- `│` = Borda vertical
- `─` = Borda horizontal
- `▒` = Hover state
- `█` = Active/Selected state
- `⊗` = Botão fechar
- `⭮` = Loading spinner

---

**Versão:** 1.0.0
**Data:** 2026-01-26
**Agente:** #3 - Produtividade e UX
