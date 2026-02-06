# Teste do Error Handling Global React Query

## Configuração Implementada

Arquivo modificado: `/opt/conecta-pro/frontend/src/contexts/providers.tsx`

### 1. Helper getErrorMessage

```typescript
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message);
  }
  return 'Erro desconhecido';
}
```

### 2. Configuração Global de Mutations

```typescript
mutations: {
  retry: 0,
  onError: (error) => {
    toast({
      title: "Erro na operação",
      description: getErrorMessage(error),
      variant: "destructive",
    });
  },
  // onSuccess pode ser sobrescrito por mutation individual
  // usando meta: { showSuccessToast: false } nas options
}
```

## Como Funciona

### 1. Erro Automático
Todas as mutations que falharem exibirão automaticamente um toast de erro:

```typescript
// Exemplo de mutation - erro será tratado automaticamente
const mutation = useMutation({
  mutationFn: async (data) => {
    const response = await fetch('/api/endpoint', {
      method: 'POST',
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Falha na requisição');
    return response.json();
  }
});
```

### 2. Sobrescrever Comportamento
Para desabilitar o toast de erro em uma mutation específica:

```typescript
const mutation = useMutation({
  mutationFn: async (data) => {
    // ... código da mutation
  },
  onError: () => {
    // Implementação customizada ou silenciar erro
  }
});
```

### 3. Tratamento Adicional
Para adicionar lógica extra além do toast global:

```typescript
const mutation = useMutation({
  mutationFn: async (data) => {
    // ... código da mutation
  },
  onError: (error, variables, context) => {
    // Toast global será exibido automaticamente
    // Adicione lógica extra aqui
    console.error('Erro detalhado:', error);
    // Redirecionar, limpar estado, etc.
  }
});
```

## Tipos de Erro Suportados

| Tipo de Erro | Mensagem Extraída |
|--------------|-------------------|
| `Error` | `error.message` |
| `string` | Próprio valor |
| `{ message: string }` | `error.message` |
| Outros | "Erro desconhecido" |

## Validação

### Build TypeScript
✅ Sem erros relacionados ao providers.tsx
✅ Imports corretos
✅ Tipagem adequada

### Teste Manual
Para testar, force um erro em qualquer mutation:

1. Abra uma página com mutation (ex: cadastro de morador)
2. Modifique temporariamente a URL da API para uma inválida
3. Execute a mutation
4. Verifique se o toast de erro aparece automaticamente

## Benefícios

1. **DRY**: Elimina necessidade de toast em cada mutation
2. **Consistência**: Todas as mutations têm feedback de erro
3. **UX**: Usuário sempre recebe feedback visual
4. **Flexibilidade**: Pode ser sobrescrito quando necessário
5. **Type-safe**: Tipagem completa do TypeScript

## Próximos Passos (Opcional)

1. Adicionar `onSuccess` global para feedback positivo
2. Categorizar erros (403 = "Sem permissão", 500 = "Erro interno")
3. Logging automático de erros no Sentry/Analytics
4. Rate limiting de toasts para evitar spam
