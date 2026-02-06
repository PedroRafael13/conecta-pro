# Próximos Passos - Pós Migração Orval

**Data:** 2026-01-31
**Status da Migração:** ✅ COMPLETO

---

## Sprint Atual - Finalização

### ✅ Concluído

- [x] Migrar todos os módulos com Orval disponível
- [x] Criar hooks wrappers para 24 módulos
- [x] Organizar estrutura de diretórios
- [x] Criar documentação completa
- [x] Validar TypeScript (0 erros em produção)

### ⏳ Pendente (Esta Sprint)

- [ ] Marcar services obsoletos como `@deprecated`
- [ ] Criar PR com as mudanças
- [ ] Code review

---

## Sprint Futura - Refatoração

### Fase 1: Marcar Deprecated (1-2 dias)

#### 1. Services de Alta Prioridade

**recruitment.service.ts**
```typescript
/**
 * @deprecated desde 2026-01-31
 * Use hooks Orval de @/hooks/recruitment ao invés
 *
 * Migração:
 * - useJobPositions() para vagas
 * - useCandidates() para candidatos
 * - useApplications() para candidaturas
 * - useInterviews() para entrevistas
 *
 * Documentação: /docs/MIGRACAO_MODULOS_SECUNDARIOS.md
 */
export const recruitmentService = { ... }
```

**Arquivos:**
- [ ] `src/services/recruitment.service.ts`
- [ ] `src/services/scheduler/*.service.ts`
- [ ] `src/services/notifications/*.service.ts`

#### 2. Services de Média Prioridade

**Arquivos:**
- [ ] `src/services/government/*.service.ts`
- [ ] `src/services/bidding/*.service.ts`

#### 3. Services de Baixa Prioridade (Parcial)

**Arquivos:**
- [ ] `src/services/ai/*.service.ts` (apenas endpoints com hooks)

### Fase 2: Refatorar Código Existente (3-5 dias)

#### Buscar Imports Antigos

```bash
# Encontrar uso de services antigos
grep -r "from '@/services/recruitment'" src/
grep -r "from '@/services/scheduler'" src/
grep -r "from '@/services/notifications'" src/
grep -r "from '@/services/government'" src/
grep -r "from '@/services/bidding'" src/
```

#### Pattern de Refatoração

**Antes:**
```typescript
import { recruitmentService } from '@/services/recruitment';

const candidates = await recruitmentService.getCandidates();
```

**Depois:**
```typescript
import { useCandidates } from '@/hooks/recruitment';

const { data: candidates } = useCandidates();
```

#### Arquivos a Refatorar (Estimativa)

- [ ] Páginas de recruitment (~5-10 arquivos)
- [ ] Páginas de scheduler (~3-5 arquivos)
- [ ] Páginas de notifications (~5-8 arquivos)
- [ ] Páginas de government (~8-12 arquivos)
- [ ] Páginas de bidding (~6-10 arquivos)

**Total estimado:** ~30-50 arquivos

### Fase 3: Remover Services Obsoletos (1 dia)

Após 100% de migração do código:

```bash
# Verificar se ainda há uso
grep -r "recruitment.service" src/
grep -r "scheduler.*service" src/
grep -r "notifications.*service" src/

# Se não houver uso, remover
rm -rf src/services/recruitment.service.ts
rm -rf src/services/scheduler/
rm -rf src/services/notifications/
# etc...
```

---

## Sprint Futura - Otimizações

### Cache do React Query

#### 1. Configurar Stale Times Globais

```typescript
// src/lib/query-client.ts
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

#### 2. Configurar Stale Times por Módulo

```typescript
// hooks/recruitment/useCandidates.ts
export const useCandidates = (params) => {
  return useListCandidatesApiV1RecruitmentCandidatesGet(params, {
    query: {
      staleTime: 2 * 60 * 1000, // 2 minutos (dados mais dinâmicos)
    },
  });
};
```

#### 3. Implementar Invalidação Inteligente

```typescript
// hooks/recruitment/useCreateCandidate.ts
export const useCreateCandidate = () => {
  const queryClient = useQueryClient();

  return useCreateCandidateApiV1RecruitmentCandidatesPost({
    mutation: {
      onSuccess: () => {
        // Invalidar lista de candidatos
        queryClient.invalidateQueries({
          queryKey: ['candidates'],
        });
      },
    },
  });
};
```

### Performance

#### 1. Lazy Loading de Módulos Pesados

```typescript
// app/recruitment/page.tsx
const RecruitmentModule = lazy(() => import('@/features/recruitment'));
```

#### 2. Prefetching de Dados Críticos

```typescript
// app/recruitment/page.tsx
export async function generateMetadata() {
  const queryClient = new QueryClient();

  // Prefetch dados críticos
  await queryClient.prefetchQuery({
    queryKey: ['candidates'],
    queryFn: () => fetchCandidates(),
  });

  return { ... };
}
```

#### 3. Pagination Otimizada

```typescript
// hooks/recruitment/useCandidates.ts
export const useCandidatesPaginated = (page: number) => {
  return useCandidates({ skip: page * 20, limit: 20 }, {
    query: {
      keepPreviousData: true, // Evita flicker na paginação
    },
  });
};
```

---

## Sprint Futura - Testes

### Unit Tests

```typescript
// hooks/recruitment/__tests__/useCandidates.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCandidates } from '../useCandidates';

describe('useCandidates', () => {
  it('deve buscar candidatos com sucesso', async () => {
    const { result } = renderHook(() => useCandidates(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={new QueryClient()}>
          {children}
        </QueryClientProvider>
      ),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
  });
});
```

**Arquivos a testar:**
- [ ] Hooks críticos de recruitment
- [ ] Hooks críticos de operacional
- [ ] Hooks críticos de fase5

---

## Sprint Futura - Documentação

### Para Desenvolvedores

#### 1. Guia de Uso dos Hooks

```markdown
# Como Usar os Hooks Orval

## Importação
\`\`\`typescript
import { useCandidates, useCreateCandidate } from '@/hooks/recruitment';
\`\`\`

## Query (GET)
\`\`\`typescript
const { data, isLoading, error } = useCandidates({ active: true });
\`\`\`

## Mutation (POST/PUT/DELETE)
\`\`\`typescript
const createCandidate = useCreateCandidate();

await createCandidate.mutateAsync({
  data: { nome: 'João', email: 'joao@example.com' }
});
\`\`\`
```

#### 2. Migration Guide

Para cada desenvolvedor, criar guia de como migrar código existente.

#### 3. Best Practices

- Quando usar `useQuery` vs `useMutation`
- Como configurar cache
- Como lidar com erros
- Patterns de otimistic updates

---

## Checklist de Validação

### Antes de Marcar como Completo

- [ ] Todos os services obsoletos marcados como `@deprecated`
- [ ] Código existente refatorado para usar hooks
- [ ] Tests criados para hooks críticos
- [ ] Documentação atualizada
- [ ] Code review aprovado
- [ ] QA validado
- [ ] Performance validada
- [ ] Services obsoletos removidos

---

## Cronograma Estimado

### Sprint 1 (Atual)
- Migração hooks: ✅ COMPLETO
- Documentação: ✅ COMPLETO
- PR & Review: ⏳ PENDENTE

### Sprint 2
- Marcar deprecated: 2 dias
- Refatorar código: 3-5 dias

### Sprint 3
- Testes: 3 dias
- Otimizações: 2 dias

### Sprint 4
- Remover obsoletos: 1 dia
- Validação final: 1 dia

**Total estimado:** 3-4 sprints

---

## Riscos e Mitigações

### Risco 1: Breaking Changes
**Mitigação:** Manter services antigos durante período de transição

### Risco 2: Performance Degradada
**Mitigação:** Monitorar métricas, ajustar cache do React Query

### Risco 3: Bugs em Produção
**Mitigação:** Deploy gradual, feature flags, testes extensivos

---

## Métricas de Sucesso

### KPIs

- [ ] 100% dos hooks funcionais
- [ ] 0 erros TypeScript em produção
- [ ] Performance igual ou melhor que antes
- [ ] 0 services manuais obsoletos em uso
- [ ] Redução de 60%+ em código manual
- [ ] Melhoria de 40%+ em type-safety

### Monitoramento

- Bundle size antes vs depois
- TTI (Time to Interactive) antes vs depois
- Cache hit rate do React Query
- Error rate em produção

---

## Contato

**Responsável:** Jordan (Admin)
**Documentação:** `/docs/MIGRACAO_*.md`
**Status:** Acompanhar via Jira/Linear

---

**Última atualização:** 2026-01-31
