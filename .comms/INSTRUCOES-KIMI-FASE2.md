# Instruções para Kimi — Fase 2 do Plano Mestre (Frontend)

Leia `/opt/conecta-pro/.comms/tasks/PLANO-MESTRE-PRODUCAO.md` para contexto completo.

## Estado Atual
- Pytest backend: 6232 passed, 0 failed (100%) — NÃO TOQUE NO BACKEND
- ESLint: 0 errors, 510 warnings (meta: 0)
- console.log: 6 restantes (meta: 0)

## Sua Tarefa: ESLint 510 warnings + 6 console.log

### Tarefa 1: Auto-fix ESLint (2 min)

```bash
cd /opt/conecta-pro/frontend
npx eslint src/ --fix --ignore-pattern "src/types/generated/**" 2>&1 | tail -10
```

Isso deve corrigir ~95 warnings automaticamente. Commitar:
```bash
git add -u && git commit -m "fix(frontend): auto-fix 95 ESLint warnings"
```

Verificar quantos restam:
```bash
npx eslint src/ --ignore-pattern "src/types/generated/**" 2>&1 | tail -3
```

### Tarefa 2: Fix `react-hooks/immutability` (322 warnings — MAIOR VOLUME)

Este é o bulk do trabalho. O padrão é sempre o mesmo:

```typescript
// ERRADO — mutação direta de array/objeto
const items = [...state.items];
items.push(newItem);  // MUTAÇÃO
setState({ items });

// CORRETO — operação imutável
setState({ items: [...state.items, newItem] });
```

```typescript
// ERRADO — mutação de array com splice
const filtered = data.filter(x => x.id !== id);
data.splice(0, data.length, ...filtered);  // MUTAÇÃO

// CORRETO
setData(data.filter(x => x.id !== id));
```

```typescript
// ERRADO — mutação de objeto
obj.value = newValue;  // MUTAÇÃO

// CORRETO
const newObj = { ...obj, value: newValue };
```

**Estratégia:** Trabalhar por diretório. Listar os arquivos afetados:
```bash
npx eslint src/ --ignore-pattern "src/types/generated/**" -f compact 2>&1 | grep "immutability" | sed 's/:.*//' | sort -u
```

Para CADA arquivo:
1. Abrir e entender o contexto
2. Substituir mutações por operações imutáveis
3. Verificar TypeScript: `npx tsc --noEmit 2>&1 | tail -3`
4. Não quebre a lógica!

### Tarefa 3: Fix `react-hooks/static-components` (4 warnings)
- Componentes estáticos definidos dentro de render — extrair para fora do componente

### Tarefa 4: Fix `react-hooks/refs` (2 warnings)
- Refs devem usar useRef, não variáveis locais

### Tarefa 5: Remover 6 console.log
```bash
grep -rn "console.log" src/ --include="*.ts" --include="*.tsx" | grep -v node_modules | grep -v ".test."
```
- Se é debug: REMOVER
- Se é error handling: trocar para console.error
- Se é importante: manter com justificativa

### Verificação Final (OBRIGATÓRIA)
```bash
cd /opt/conecta-pro/frontend

# 1. ESLint
npx eslint src/ --ignore-pattern "src/types/generated/**" 2>&1 | tail -5
# ESPERADO: 0 errors, 0 warnings (ou ~86 que o Opus está cuidando)

# 2. TypeScript
npx tsc --noEmit 2>&1 | tail -5
# ESPERADO: 0 errors

# 3. Build
npx next build 2>&1 | tail -5
# ESPERADO: build OK
```

### REGRAS
- NÃO toque no backend (está 100% passando)
- NÃO edite `src/types/generated/` (auto-gerados pelo Orval)
- Commitar a cada ~20-30 fixes para não perder trabalho
- Se algo quebrar TypeScript, reverter e investigar

### Status
Após cada tarefa, escreva em `/opt/conecta-pro/.comms/messages/kimi-out.jsonl`:
```json
{"ts":"2026-02-10T...","from":"kimi","type":"status","task":"tarefa_N","result":"X warnings corrigidos"}
```
