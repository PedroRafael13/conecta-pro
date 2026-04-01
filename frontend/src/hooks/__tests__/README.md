# Testes Unitários - Hooks Customizados

## Estrutura

Testes criados para os hooks prioritários do Conecta Pro:

### 1. useAuth.test.ts (7 testes)
- ✅ Estado inicial não autenticado
- ✅ Verificação de autenticação com token
- ✅ Limpeza de tokens quando falha
- ✅ Login com formato form-urlencoded
- ✅ Erro de login
- ✅ Logout e limpeza de tokens
- ✅ Logout mesmo quando API falha

### 2. useDebounce.test.ts (15 testes)
- ✅ Delay de execução
- ✅ Respeito a diferentes delays
- ✅ Funcionamento com números, objetos e arrays
- ✅ Cancelamento de timeout
- ✅ Múltiplas mudanças rápidas
- ✅ Edge cases (null, undefined, delay zero)

### 3. useLocalStorage.test.ts (19 testes)
- ✅ Get/Set/Remove
- ✅ JSON parsing (objetos, arrays, números, booleanos)
- ✅ Eventos de storage (sincronização entre abas)
- ✅ Valores nulos
- ✅ Dados JSON inválidos
- ✅ Erro ao salvar no localStorage

### 4. useFetch.test.ts (18 testes)
- ✅ GET, POST, PUT, DELETE
- ✅ Loading states
- ✅ Error handling (HTTP e rede)
- ✅ Callbacks onSuccess/onError
- ✅ Cache habilitado/desabilitado
- ✅ Invalidação de cache
- ✅ Refetch
- ✅ Mutate

### 5. useForm.test.ts (27 testes)
- ✅ Validação de campos obrigatórios
- ✅ Validação minLength/maxLength
- ✅ Validação de pattern (regex)
- ✅ Validação customizada
- ✅ Submit do formulário
- ✅ Reset do formulário
- ✅ Dirty state
- ✅ Manipulação de valores
- ✅ Handlers (change, blur)
- ✅ Validação em tempo real

### 6. usePagination.test.ts (29 testes)
- ✅ Cálculo de páginas
- ✅ Navegação (próxima, anterior, específica)
- ✅ Primeira e última página
- ✅ Page size dinâmico
- ✅ Estados de navegação (canGoNext, canGoPrevious)
- ✅ Texto de exibição
- ✅ Range de páginas com ellipsis

### 7. usePermission.test.ts (18 testes)
- ✅ Verificação de permissões
- ✅ Roles específicos
- ✅ Hierarquia de roles
- ✅ Administrador (todas permissões)
- ✅ Agente (permissões básicas)
- ✅ Verificadores específicos (canManagePosts, canCheckIn, etc.)

## Total: 133 testes

## Execução

```bash
# Todos os testes
npm run test:run -- src/hooks/__tests__/

# Teste específico
npm run test:run -- src/hooks/__tests__/useAuth.test.ts

# Com coverage
npm run test:coverage -- src/hooks/__tests__/
```

## Hooks Criados

Além dos testes, foram criados os seguintes hooks:

1. **useLocalStorage.ts** - Gerenciamento de localStorage com sincronização
2. **useFetch.ts** - Requisições HTTP com cache e estados
3. **useForm.ts** - Gerenciamento de formulários com validação
4. **usePagination.ts** - Paginação de dados em memória

Estes hooks foram adicionados ao `index.ts` para exportação centralizada.
