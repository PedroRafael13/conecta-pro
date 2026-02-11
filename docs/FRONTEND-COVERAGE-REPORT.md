# Relatório de Cobertura Frontend - ERP Conecta Mais

**Data:** 2026-02-11
**Gerado por:** Kimi
**Ferramenta:** Vitest + v8 coverage

---

## Resumo Geral

| Métrica | Atual | Meta | Status |
|---------|-------|------|--------|
| Statements | 84.46% | ≥80% | ✅ |
| Branches | 78.16% | ≥80% | ❌ |
| Functions | 77.65% | ≥80% | ❌ |
| Lines | 84.40% | ≥80% | ✅ |

**Status Geral:** ⚠️ Próximo da meta, precisa melhorar branches e functions

---

## C2 — Áreas Sem Cobertura (Prioritárias)

### 🔴 Crítico (< 50%)

| Arquivo | Stmts | Branches | Funcs | Motivo |
|---------|-------|----------|-------|--------|
| `services/bidding/*.service.ts` | ~3-4% | 0% | 0% | Serviços de licitação não testados |
| `lib/api.ts` | 22% | 15% | 16% | Cliente HTTP base não testado |

### 🟡 Médio (50-80%)

| Arquivo | Stmts | Branches | Funcs | Ações |
|---------|-------|----------|-------|-------|
| `utils/export.ts` | 54.41% | 40.62% | 58.33% | Adicionar testes de exportação |
| `hooks/useRecruitment.ts` | 43.71% | 100% | 37.69% | Expandir testes de recrutamento |
| `hooks/useDisciplinary.ts` | 82.92% | 58.49% | 76.92% | Melhorar branch coverage |
| `hooks/useOccurrences.ts` | 86.95% | 61.40% | 82.35% | Melhorar branch coverage |
| `hooks/useControlRounds.ts` | 82% | 52.94% | 90% | Melhorar branch coverage |
| `hooks/useScales.ts` | 84.82% | 54.54% | 100% | Melhorar branch coverage |
| `hooks/useShifts.ts` | 88.57% | 65.62% | 100% | Melhorar branch coverage |

### 🟢 Bom (> 80%)

Hooks principais já bem cobertos:
- `useAuth.ts` - 100%
- `useDashboard.ts` - 100%
- `useDebounce.ts` - 100%
- `useKPITrends.ts` - 100%
- `useKeyboardShortcuts.ts` - 100%
- `usePermission.ts` - 97.84%
- `useAutoSave.ts` - 94.56%

---

## C3 — Plano de Ação

### Fase 1: Hooks Críticos (Quick Wins)

1. **useRecruitment.ts** - Adicionar testes para:
   - `fetchCandidates()` com filtros
   - `updateCandidateStatus()` transições
   - `scheduleInterview()` validações

2. **useDisciplinary.ts** - Melhorar branches:
   - Error handling em `createOccurrence()`
   - Estados de loading
   - Casos de edge em validações

3. **useOccurrences.ts** - Melhorar branches:
   - Filtros combinados
   - Paginação
   - Refresh de dados

### Fase 2: Serviços

4. **lib/api.ts** - Testar:
   - Interceptors de request/response
   - Retry logic
   - Error handling

5. **services/bidding/** - Criar suites de teste para:
   - BiddingCertificatesService
   - BiddingDetailsService
   - BiddingFiltersService

### Fase 3: Utils

6. **utils/export.ts** - Testar:
   - Exportação CSV
   - Exportação Excel
   - Tratamento de erros

---

## C4 — Testes a Criar

### Template para Novos Testes

```typescript
// __tests__/useExample.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useExample } from '../useExample';

describe('useExample', () => {
  it('deve carregar dados inicialmente', async () => {
    const { result } = renderHook(() => useExample());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });

  it('deve tratar erros corretamente', async () => {
    // Mock error
    const { result } = renderHook(() => useExample());

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });
  });
});
```

### Arquivos de Teste Prioritários

| Prioridade | Arquivo | Estimativa |
|------------|---------|------------|
| P0 | `src/hooks/__tests__/useRecruitment.test.ts` | 2h |
| P1 | `src/lib/__tests__/api.test.ts` | 1.5h |
| P1 | `src/utils/__tests__/export.test.ts` | 1h |
| P2 | `src/hooks/__tests__/useDisciplinary.test.ts` (expandir) | 1h |
| P2 | `src/hooks/__tests__/useOccurrences.test.ts` (expandir) | 1h |

**Tempo Estimado Total:** ~6.5h

---

## C5 — Meta de Cobertura

### Meta Atual: ≥80% em todas as métricas

| Métrica | Atual | Meta | Gap |
|---------|-------|------|-----|
| Statements | 84.46% | 80% | ✅ +4.46% |
| Branches | 78.16% | 80% | ❌ -1.84% |
| Functions | 77.65% | 80% | ❌ -2.35% |
| Lines | 84.40% | 80% | ✅ +4.40% |

### Para Atingir Meta:

**Branches (precisa +1.84%):**
- Focus em hooks com < 60% branch coverage
- Adicionar testes para error boundaries
- Testar todos os caminhos condicionais

**Functions (precisa +2.35%):**
- Testar callbacks e funções anônimas
- Cobrir funções de utilitários
- Mock de funções em hooks

---

## Comandos Úteis

```bash
# Rodar coverage completo
cd /opt/conecta-pro/frontend && npm run test:coverage

# Rodar apenas testes de um arquivo
npm run test -- src/hooks/__tests__/useAuth.test.ts

# Rodar com watch mode
npm run test -- --watch

# Gerar relatório HTML
npm run test:coverage -- --reporter=html
```

---

## Próximos Passos

1. ✅ C1: Medir cobertura atual (CONCLUÍDO)
2. ✅ C2: Identificar áreas sem cobertura (CONCLUÍDO)
3. ⏳ C3: Escrever testes para hooks críticos (PENDENTE)
4. ⏳ C4: Escrever testes para componentes core (PENDENTE)
5. ⏳ C5: Validar meta de 80% (PENDENTE)

**Nota:** Priorizar após deploy ou em momento de menor pressão.
