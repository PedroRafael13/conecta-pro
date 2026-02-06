# Sistema de Produtividade e Atalhos

## Componentes Criados

### 1. useKeyboardShortcuts Hook
**Arquivo:** `/hooks/useKeyboardShortcuts.ts`

Hook para gerenciar atalhos de teclado com suporte a:
- Combinações Ctrl/Alt/Shift
- Prevenção de atalhos em inputs
- Enable/disable dinâmico

**Exemplo de uso:**
```tsx
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

const shortcuts = [
  {
    key: 'p',
    ctrl: true,
    description: 'Imprimir',
    action: () => window.print(),
  },
];

useKeyboardShortcuts({ shortcuts, enabled: true });
```

### 2. CommandPalette
**Arquivo:** `/components/CommandPalette.tsx`

Modal de comandos rápidos com:
- Busca fuzzy
- Categorização (navigation, action, search)
- Navegação com teclado
- Ícones personalizados

**Props:**
- `isOpen: boolean` - Estado de abertura
- `onClose: () => void` - Callback ao fechar

### 3. GlobalSearch
**Arquivo:** `/components/GlobalSearch.tsx`

Busca global no sistema com:
- Debounce de 300ms
- Agrupamento por tipo
- Navegação com teclado
- Métricas de performance

**Props:**
- `isOpen: boolean` - Estado de abertura
- `onClose: () => void` - Callback ao fechar

**API Endpoint:** `GET /api/v1/search?q={query}&limit={limit}`

### 4. HelpOverlay
**Arquivo:** `/components/HelpOverlay.tsx`

Overlay de ajuda mostrando todos os atalhos disponíveis.

**Props:**
- `isOpen: boolean` - Estado de abertura
- `onClose: () => void` - Callback ao fechar
- `shortcuts: KeyboardShortcut[]` - Lista de atalhos

### 5. ProductivityProvider
**Arquivo:** `/components/ProductivityProvider.tsx`

Provider que gerencia todos os estados de produtividade:
- Busca global
- Command palette
- Help overlay
- Atalhos globais

**Context exportado:**
```tsx
{
  openSearch: () => void;
  closeSearch: () => void;
  openCommandPalette: () => void;
  closeCommandPalette: () => void;
  openHelp: () => void;
  closeHelp: () => void;
  toggleSidebar: () => void;
}
```

**Hook:**
```tsx
import { useProductivity } from '@/components/ProductivityProvider';

const { openSearch, openCommandPalette } = useProductivity();
```

### 6. SearchTrigger
**Arquivo:** `/components/SearchTrigger.tsx`

Botão trigger para abrir busca global.
Mostra atalho "/" no desktop.

## Integração

### 1. Providers (já integrado)

```tsx
// src/contexts/providers.tsx
<ProductivityProvider>
  {children}
</ProductivityProvider>
```

### 2. Layout (já integrado)

```tsx
// src/app/modulos/layout.tsx
import { SearchTrigger } from '@/components/SearchTrigger';

// No header:
<SearchTrigger />
```

## Atalhos Disponíveis

| Atalho | Ação |
|--------|------|
| `/` | Abrir busca global |
| `Ctrl+K` | Abrir command palette |
| `Ctrl+B` | Toggle sidebar |
| `Esc` | Fechar modal/dropdown |
| `Shift+?` | Mostrar ajuda |
| `Alt+1` | Ir para Dashboard |
| `Alt+2` | Ir para Operacional |
| `Alt+3` | Ir para Financeiro |
| `Alt+4` | Ir para CRM |

## Uso Programático

### Abrir busca programaticamente

```tsx
import { useProductivity } from '@/components/ProductivityProvider';

function MeuComponente() {
  const { openSearch } = useProductivity();

  return (
    <button onClick={openSearch}>
      Buscar
    </button>
  );
}
```

### Adicionar comandos customizados

Edite `/components/CommandPalette.tsx` e adicione no array `commands`:

```tsx
{
  id: 'meu-comando',
  title: 'Meu Comando',
  description: 'Descrição do comando',
  icon: <Icon className="w-4 h-4" />,
  category: 'action',
  action: () => {
    // Sua lógica
  },
}
```

### Adicionar atalhos personalizados

```tsx
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

const customShortcuts = [
  {
    key: 'e',
    ctrl: true,
    shift: true,
    description: 'Exportar',
    action: () => handleExport(),
  },
];

useKeyboardShortcuts({ shortcuts: customShortcuts });
```

## Backend - Busca Global

### Endpoint

**GET** `/api/v1/search`

**Query Params:**
- `q` (required) - Query de busca
- `limit` (optional, default: 20)

**Response:**
```json
{
  "results": [
    {
      "type": "colaborador",
      "id": "uuid",
      "title": "Nome",
      "description": "Descrição",
      "url": "/path"
    }
  ],
  "total": 5,
  "took_ms": 87
}
```

### Tipos de busca

1. **colaborador** - Busca em nome, CPF, matrícula
2. **posto** - Busca em nome, código
3. **escala** - Busca em nome, código
4. **ocorrencia** - Busca em título, descrição
5. **ronda** - Busca em código, inspetor

### Performance

- Target: < 200ms
- Implementa: LIMIT no SQL
- Busca paralela em múltiplas tabelas
- Máximo 5 resultados por tipo

## Testes

### Testar atalhos

1. Pressione `/` - deve abrir busca global
2. Pressione `Ctrl+K` - deve abrir command palette
3. Pressione `Shift+?` - deve abrir help overlay
4. Pressione `Esc` - deve fechar qualquer modal aberto

### Testar busca

1. Pressione `/`
2. Digite nome de colaborador
3. Aguarde 300ms (debounce)
4. Verifique resultados
5. Use ↑↓ para navegar
6. Pressione Enter para abrir

### Testar command palette

1. Pressione `Ctrl+K`
2. Digite "novo"
3. Verifique comandos filtrados
4. Use ↑↓ para navegar
5. Pressione Enter para executar

## Troubleshooting

### Atalhos não funcionam
- Verifique se ProductivityProvider está no topo da árvore
- Verifique console para erros
- Teste em input vs fora de input (atalhos ignorados em inputs exceto Esc)

### Busca não retorna resultados
- Verifique endpoint `/api/v1/search` no DevTools
- Verifique permissões de acesso aos dados
- Verifique se backend está rodando

### Command Palette vazio
- Verifique imports no CommandPalette.tsx
- Verifique se router está funcionando

## Próximas Melhorias

- [ ] Cache de buscas recentes
- [ ] Ranking de relevância
- [ ] Highlighting de termos
- [ ] Preview de resultados
- [ ] Atalhos personalizáveis por usuário
- [ ] Métricas de uso
