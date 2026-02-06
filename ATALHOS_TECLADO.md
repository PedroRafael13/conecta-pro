# Sistema de Atalhos de Teclado e Produtividade

## Visão Geral

Sistema completo de atalhos de teclado, Command Palette e Busca Global para navegação rápida e eficiente no Conecta PRO.

## Atalhos de Teclado

### Atalhos Gerais

| Atalho | Descrição |
|--------|-----------|
| `/` | Abrir busca global |
| `Ctrl+K` | Abrir command palette |
| `Ctrl+B` | Alternar sidebar (desktop) |
| `Esc` | Fechar modal/dropdown aberto |
| `Shift+?` | Mostrar todos os atalhos disponíveis |

### Navegação entre Módulos

| Atalho | Destino |
|--------|---------|
| `Alt+1` | Dashboard |
| `Alt+2` | Módulo Operacional |
| `Alt+3` | Módulo Financeiro |
| `Alt+4` | Módulo CRM |

### Atalhos Contextuais (futuros)

| Atalho | Descrição |
|--------|-----------|
| `Ctrl+N` | Novo (contexto atual) |
| `Ctrl+S` | Salvar formulário |

## Busca Global (/)

### Funcionalidades

- Busca unificada em tempo real
- Resultados < 200ms
- Máximo 20 resultados
- Debounce de 300ms
- Navegação com teclado

### Entidades Pesquisadas

1. **Colaboradores**
   - Nome
   - CPF
   - Matrícula

2. **Postos**
   - Nome
   - Código

3. **Escalas**
   - Nome
   - Código
   - Período

4. **Ocorrências**
   - Título
   - Descrição

5. **Rondas**
   - Código
   - Nome do inspetor

### Navegação

- `↑↓` - Navegar entre resultados
- `Enter` - Abrir resultado selecionado
- `Esc` - Fechar busca

## Command Palette (Ctrl+K)

### Funcionalidades

- Comandos rápidos
- Busca fuzzy
- Categorização automática
- Navegação com teclado

### Comandos Disponíveis

#### Navegação
- Novo Posto
- Novo Colaborador
- Nova Ocorrência

#### Ações
- Nova Escala
- Exportar Dados

#### Busca
- Buscar Colaborador

### Navegação

- `↑↓` - Navegar entre comandos
- `Enter` - Executar comando
- `Esc` - Fechar palette

## Help Overlay (Shift+?)

### Funcionalidades

- Lista completa de atalhos
- Categorização por tipo
- Formatação visual das teclas
- Sempre atualizado

### Categorias

1. **Geral** - Atalhos globais do sistema
2. **Navegação** - Atalhos entre módulos
3. **Ações Contextuais** - Atalhos específicos

## Arquitetura

### Frontend

```
/frontend/src/
├── hooks/
│   └── useKeyboardShortcuts.ts    # Hook para atalhos
├── components/
│   ├── CommandPalette.tsx         # Command Palette
│   ├── GlobalSearch.tsx           # Busca Global
│   ├── HelpOverlay.tsx            # Overlay de ajuda
│   ├── SearchTrigger.tsx          # Botão de busca
│   └── ProductivityProvider.tsx   # Provider global
└── contexts/
    └── providers.tsx               # Integração providers
```

### Backend

```
/backend/modules/search/
├── __init__.py
└── search_controller.py           # Controller de busca
```

### API Endpoint

**GET** `/api/v1/search`

**Query Parameters:**
- `q` (required) - Query de busca
- `limit` (optional) - Limite de resultados (default: 20, max: 100)

**Response:**
```json
{
  "results": [
    {
      "type": "colaborador",
      "id": "uuid",
      "title": "João Silva",
      "description": "Portaria - Matriz",
      "url": "/modulos/operacional/colaboradores/uuid"
    }
  ],
  "total": 5,
  "took_ms": 87
}
```

## Performance

### Benchmarks

- Busca Global: < 200ms
- Debounce Input: 300ms
- Máximo Resultados: 20
- Cache: Não implementado (performance nativa suficiente)

### Otimizações

1. **Debounce** - Reduz chamadas à API
2. **LIMIT** - Limita resultados no banco
3. **Índices** - Busca em campos indexados
4. **Paralelo** - Busca simultânea em múltiplas tabelas

## Acessibilidade

### ARIA Labels

- Todos os botões possuem `aria-label`
- Modais possuem `role="dialog"`
- Navegação com teclado 100% funcional

### Keyboard Navigation

- Sem uso de mouse necessário
- Todos os elementos focáveis
- Indicadores visuais de foco

## Configuração

### Desabilitar Atalhos

```tsx
// Em componente específico
useKeyboardShortcuts({ shortcuts: [], enabled: false });
```

### Adicionar Novos Atalhos

```tsx
const customShortcuts: KeyboardShortcut[] = [
  {
    key: 'p',
    ctrl: true,
    description: 'Imprimir',
    action: () => window.print(),
  },
];

useKeyboardShortcuts({ shortcuts: customShortcuts });
```

### Adicionar Comandos no Command Palette

Editar `/frontend/src/components/CommandPalette.tsx`:

```tsx
const commands: Command[] = [
  // ... comandos existentes
  {
    id: 'novo-comando',
    title: 'Novo Comando',
    description: 'Descrição',
    icon: <Icon className="w-4 h-4" />,
    category: 'action',
    action: () => {
      // Lógica do comando
    },
  },
];
```

## Troubleshooting

### Atalhos não funcionam

1. Verificar se está dentro de input (atalhos ignorados exceto ESC)
2. Verificar conflitos com atalhos do navegador
3. Verificar console para erros

### Busca retorna vazio

1. Verificar query mínima (1 caractere)
2. Verificar conectividade backend
3. Verificar permissões de acesso aos dados

### Performance lenta

1. Verificar índices no banco
2. Verificar quantidade de registros
3. Ajustar LIMIT se necessário

## Próximos Passos

### Features Futuras

- [ ] Cache de busca recente
- [ ] Histórico de comandos
- [ ] Atalhos personalizáveis por usuário
- [ ] Ctrl+N/Ctrl+S contextuais
- [ ] Busca semântica com IA
- [ ] Sugestões inteligentes

### Melhorias

- [ ] Ranking de relevância nos resultados
- [ ] Highlighting de termos buscados
- [ ] Preview de resultados
- [ ] Métricas de uso de atalhos
- [ ] Onboarding de atalhos para novos usuários

## Suporte

Para reportar bugs ou sugerir melhorias:
1. Verificar este documento primeiro
2. Testar em ambiente de desenvolvimento
3. Reportar com detalhes (browser, OS, passos)

---

**Versão:** 1.0.0
**Última Atualização:** 2026-01-26
**Autor:** Agente #3 - Especialista em Produtividade e UX
