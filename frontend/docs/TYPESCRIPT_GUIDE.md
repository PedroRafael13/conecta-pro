# Guia TypeScript - Conecta PRO v2.0

## Status: 0 Erros TypeScript (Migrado 100%)

Data da migração completa: 2026-02-05
De: 227+ erros → 0 erros
`ignoreBuildErrors: false` (validação ativa no build)

---

## Arquitetura de Tipos

### Geração Automática (Orval)
- **Ferramenta:** Orval v7.13.2 com `tags-split` mode
- **Fonte:** OpenAPI spec do backend FastAPI
- **Destino:** `src/types/generated/<módulo>/`
- **Client:** React Query (TanStack Query v5)
- **Mutator:** `src/lib/api-client.ts`

### Módulos Gerados (26)
```
financial/          - 15 submódulos (payables, receivables, cashflow, etc.)
operacional/        - Escalas, turnos, colaboradores
crm/                - Leads, contatos, propostas, oportunidades
equipment/          - Patrimônio, manutenção, comodato
bidding/            - Editais, propostas, certidões
recruitment/        - Vagas, candidatos, entrevistas
security-lgpd/      - LGPD, consentimento, auditoria
ai/                 - Bartolo AI assistant
config/             - Feature flags, notificações, tenants
documents/          - GED, document kits
scheduler/          - Agendamentos
search/             - Busca global
```

### Como Regenerar Tipos
```bash
# Todos os módulos
npm run api:generate

# Módulo específico
npm run orval:operacional
npm run orval:bidding
# etc.
```

---

## Padrões de Código

### 1. Hooks Orval (gerados)
```typescript
// Import via hook consolidado
import { usePayables, useCreatePayable, payableKeys } from '@/hooks/financial/useFinancial';

// Uso direto
const { data, isLoading } = usePayables({ condominio_id: condominioId });
```

### 2. Response Patterns
```typescript
// Orval retorna arrays diretamente (NÃO wrappados)
const { data: items } = usePayables({ condominio_id: id });
// items é PayableItem[] diretamente

// Para dashboards/stats, é um objeto direto
const { data: stats } = usePayableDashboard({ condominio_id: id });
```

### 3. StandardResponse do Backend
```typescript
// Quando o backend retorna StandardResponse com data genérico:
const response = await api.get('/endpoint');
const data = response.data as Record<string, unknown>;
```

### 4. Tratamento de undefined (noUncheckedIndexedAccess)
```typescript
// tsconfig tem noUncheckedIndexedAccess: true
// Arrays indexados retornam T | undefined

// ERRADO:
const first = items[0].name;

// CORRETO:
const first = items[0]?.name;
// ou com non-null assertion quando temos certeza:
const first = items[0]!.name;

// split() retorna string | undefined
const date = isoString.split('T')[0] ?? '';
```

### 5. Tipos Gerados com {} (body vazio)
```typescript
// Orval gera {} quando o schema é genérico
// Use cast quando necessário:
const data = response.data as Record<string, unknown>;
```

---

## Validação e CI

### Comandos
```bash
# Type check (deve passar com 0 erros)
npm run type-check

# Build de produção (inclui type check)
npm run build

# Lint
npm run lint
```

### Pre-commit Hook
O hook `.husky/pre-commit` executa:
1. `lint-staged` (ESLint + Prettier nos arquivos staged)
2. `tsc --noEmit` (validação de tipos completa)

### Regras de Ouro
1. **NUNCA** reativar `ignoreBuildErrors: true`
2. **NUNCA** usar `@ts-ignore` sem justificativa em comentário
3. **Evitar** `as any` - preferir casts específicos
4. **Não modificar** arquivos em `src/types/generated/` manualmente (são regenerados)
5. **Sempre** rodar `npm run type-check` antes de push

---

## Erros Comuns e Soluções

| Erro | Causa | Solução |
|------|-------|---------|
| TS2339 | Property não existe no tipo Orval | Verificar schema, usar cast ou `as Record<string, unknown>` |
| TS2532 | Objeto possivelmente undefined | `?.` ou `!` (non-null assertion) |
| TS2345 | Argumento incompatível | Verificar tipos dos parâmetros do hook |
| TS2322 | Tipo não assignable | `?? ''` para string\|undefined, cast quando necessário |
| TS2304 | Nome não encontrado | Verificar imports |
| TS2769 | No overload matches | Verificar assinatura da função/hook |

## Arquivos-Chave
- `tsconfig.json` - Configuração TypeScript (strict mode ativo)
- `next.config.ts` - `ignoreBuildErrors: false`
- `orval.config.ts` - Configuração principal do Orval
- `src/lib/api-client.ts` - Axios mutator para Orval
- `src/hooks/financial/useFinancial.ts` - Hook consolidado financeiro (483 endpoints)
- `.husky/pre-commit` - Hook de validação pré-commit
