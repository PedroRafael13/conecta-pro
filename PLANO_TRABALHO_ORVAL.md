# PLANO DE TRABALHO - COBERTURA ORVAL 100% FUNCIONAL
**Projeto:** Conecta PRO
**Data Criação:** 2026-01-31
**Status:** Pronto para execução
**Sessão:** Próxima sessão - Continuar daqui

---

## 📊 SITUAÇÃO ATUAL (ONDE PARAMOS)

### ✅ Conquistas da Sessão Atual

1. **Cobertura de Tipos: 100%**
   - 32 módulos com tipos TypeScript gerados
   - ~15,000 arquivos TypeScript
   - 35 configurações Orval criadas

2. **Módulos Cobertos Hoje (6 novos):**
   - ✅ CRM (73 endpoints, 571 arquivos)
   - ✅ HR (236 endpoints, 1.490 tipos) - MAIOR MÓDULO
   - ✅ CAMPO (160 endpoints, 805 arquivos)
   - ✅ Equipment (81 endpoints)
   - ✅ Services (63 endpoints)
   - ✅ Reimbursement (26 endpoints)
   - ✅ Integrations (63 endpoints)
   - ✅ Document Kits (37 endpoints)
   - ✅ Automation (6 endpoints)

3. **Infraestrutura Validada:**
   - ✅ React Query configurado
   - ✅ Axios instance com interceptors
   - ✅ Mutator customizado para Orval
   - ✅ Toast system funcionando

### ⚠️ Problemas Identificados

**PROBLEMA CRÍTICO:**
- **27 módulos** usam `client: 'axios'` ao invés de `client: 'react-query'`
- **Impacto:** Não geram hooks React Query prontos
- **Resultado:** 0% do código usa hooks gerados (todo código usa services manuais)

**CÓDIGO LEGADO:**
- 28 services manuais (~6,731 linhas)
- 21 hooks customizados
- Padrão ineficiente: Componente → Hook customizado → Service manual → Axios

---

## 🎯 OBJETIVO DA PRÓXIMA SESSÃO

**Transformar cobertura de TIPOS (100%) em cobertura FUNCIONAL (100%)**

**Resultado esperado:**
- ✅ Todos os 35 módulos gerando hooks React Query
- ✅ Código da aplicação usando hooks gerados
- ✅ Eliminação de services duplicados
- ✅ Error handling global configurado

---

## 📋 PLANO DE EXECUÇÃO - PRÓXIMA SESSÃO

### **FASE 1: PADRONIZAÇÃO ORVAL** (Prioridade CRÍTICA - 2h)

#### Objetivo
Atualizar 27 configs de `client: 'axios'` para `client: 'react-query'`

#### Lista de Arquivos a Modificar

```bash
# Configs que precisam atualização (27 arquivos):
/opt/conecta-pro/frontend/orval.config.operacional.ts
/opt/conecta-pro/frontend/orval.config.government.ts
/opt/conecta-pro/frontend/orval.config.recruitment.ts
/opt/conecta-pro/frontend/orval.config.audit.ts
/opt/conecta-pro/frontend/orval.config.notifications.ts
/opt/conecta-pro/frontend/orval.config.mobile.ts
/opt/conecta-pro/frontend/orval.config.clients.ts
/opt/conecta-pro/frontend/orval.config.security-lgpd.ts
/opt/conecta-pro/frontend/orval.config.scheduler.ts
/opt/conecta-pro/frontend/orval.config.search.ts
/opt/conecta-pro/frontend/orval.config.bidding.ts
/opt/conecta-pro/frontend/orval.config.health-occupational.ts
/opt/conecta-pro/frontend/orval.config.contracts.ts
/opt/conecta-pro/frontend/orval.config.diarists.ts
/opt/conecta-pro/frontend/orval.config.workflows.ts
/opt/conecta-pro/frontend/orval.config.financial.ts
/opt/conecta-pro/frontend/orval.config.ai.ts
/opt/conecta-pro/frontend/orval.config.equipment.ts
/opt/conecta-pro/frontend/orval.config.services.ts
/opt/conecta-pro/frontend/orval.config.integrations.ts
/opt/conecta-pro/frontend/orval.config.document-kits.ts
/opt/conecta-pro/frontend/orval.config.automation.ts
/opt/conecta-pro/frontend/orval.config.crm.ts
/opt/conecta-pro/frontend/orval.config.campo.ts
/opt/conecta-pro/frontend/orval.config.documents.ts
/opt/conecta-pro/frontend/orval.config.reimbursement.ts
/opt/conecta-pro/frontend/orval.config.hr.ts
```

#### Mudança Necessária

**ANTES:**
```typescript
export default {
  [moduleName]: {
    output: {
      client: 'axios',  // ❌ Apenas tipos
      // ...
    }
  }
}
```

**DEPOIS:**
```typescript
export default {
  [moduleName]: {
    output: {
      client: 'react-query',  // ✅ Tipos + Hooks
      override: {
        mutator: {
          path: './src/lib/api-client.ts',
          name: 'customInstance',
        },
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,
        },
      },
      // ...
    }
  }
}
```

#### Script de Automação

```bash
#!/bin/bash
# /opt/conecta-pro/frontend/scripts/update-orval-configs.sh

CONFIGS=(
  "operacional" "government" "recruitment" "audit" "notifications"
  "mobile" "clients" "security-lgpd" "scheduler" "search"
  "bidding" "health-occupational" "contracts" "diarists" "workflows"
  "financial" "ai" "equipment" "services" "integrations"
  "document-kits" "automation" "crm" "campo" "documents"
  "reimbursement" "hr"
)

for module in "${CONFIGS[@]}"; do
  echo "Atualizando orval.config.${module}.ts..."

  # Substituir client: 'axios' por client: 'react-query'
  sed -i "s/client: 'axios'/client: 'react-query'/g" "orval.config.${module}.ts"

  # Adicionar override.query se não existir
  # (implementar lógica mais robusta se necessário)
done

echo "✅ Todos os configs atualizados!"
```

#### Comandos para Executar

```bash
cd /opt/conecta-pro/frontend

# 1. Criar script de atualização
vim scripts/update-orval-configs.sh
# (colar script acima)

# 2. Dar permissão
chmod +x scripts/update-orval-configs.sh

# 3. Executar atualização
./scripts/update-orval-configs.sh

# 4. Validar mudanças (sample)
grep -n "client:" orval.config.operacional.ts
grep -n "client:" orval.config.financial.ts
grep -n "client:" orval.config.crm.ts
```

#### Regenerar Todos os Módulos

```bash
# Opção 1: Paralelo (mais rápido, mas usa mais memória)
npm run orval:operacional & \
npm run orval:government & \
npm run orval:recruitment & \
npm run orval:audit & \
wait

# Opção 2: Sequencial (mais seguro)
for module in operacional government recruitment audit notifications mobile clients security-lgpd scheduler search bidding health-occupational contracts diarists workflows financial ai equipment services integrations document-kits automation crm campo documents reimbursement hr; do
  echo "Gerando $module..."
  npm run orval:$module
done

# Opção 3: Criar script orval:all
npm run orval:all  # (criar esse script no package.json)
```

#### Validação

```bash
# Verificar que hooks foram gerados
find src/types/generated -name "*.ts" -exec grep -l "useQuery" {} \; | wc -l
# Esperado: > 100 arquivos com useQuery

# Verificar imports do React Query
find src/types/generated -name "*.ts" -exec grep -l "@tanstack/react-query" {} \; | wc -l
# Esperado: > 50 arquivos

# Build sem erros
npm run build
```

---

### **FASE 2: MIGRAÇÃO PILOTO** (Prioridade ALTA - 1h)

#### Objetivo
Migrar 1 módulo completo para usar hooks gerados (prova de conceito)

#### Módulo Piloto Recomendado: **GED**

**Por quê GED:**
- ✅ Já tem hooks gerados (config usa react-query)
- ✅ 19 hooks disponíveis
- ✅ Módulo bem isolado
- ✅ Menos risco de breaking changes

#### Página Alvo
`/opt/conecta-pro/frontend/src/app/modulos/documentos/page.tsx`

#### Migração Passo a Passo

**1. Identificar imports atuais:**
```bash
grep -n "import.*from.*services/ged" src/app/modulos/documentos/page.tsx
```

**2. Ver hooks gerados disponíveis:**
```bash
ls src/types/generated/ged/ged-documentos/
grep "export.*use" src/types/generated/ged/ged-documentos/*.ts
```

**3. Fazer migração:**

**ANTES:**
```typescript
// src/app/modulos/documentos/page.tsx
import { documentService } from '@/lib/services/ged';

export default function DocumentosPage() {
  const { data, isLoading } = useQuery(['documents'],
    () => documentService.list({ page: 1, page_size: 20 })
  );

  // ...
}
```

**DEPOIS:**
```typescript
// src/app/modulos/documentos/page.tsx
import {
  useListDocumentsApiV1GedDocumentsGet,
  useCreateDocumentApiV1GedDocumentsPost,
  useDeleteDocumentApiV1GedDocumentsDocumentIdDelete
} from '@/types/generated/ged/ged-documentos/ged-documentos';

export default function DocumentosPage() {
  // Hook gerado já tem cache, retry, tipos corretos!
  const { data, isLoading } = useListDocumentsApiV1GedDocumentsGet({
    page: 1,
    page_size: 20
  });

  const createMutation = useCreateDocumentApiV1GedDocumentsPost();
  const deleteMutation = useDeleteDocumentApiV1GedDocumentsDocumentIdDelete();

  // ...
}
```

**4. Testar em desenvolvimento:**
```bash
npm run dev
# Abrir http://localhost:3000/modulos/documentos
# Testar: listar, criar, deletar documentos
```

**5. Documentar padrão:**
```bash
# Criar exemplo em /opt/conecta-pro/frontend/docs/MIGRATION_EXAMPLE.md
```

#### Checklist de Validação

- [ ] Página carrega sem erros
- [ ] Listagem funciona
- [ ] Criação funciona
- [ ] Deleção funciona
- [ ] Loading states corretos
- [ ] Error handling funciona
- [ ] Cache funciona (fazer request 2x, verificar network)
- [ ] Types corretos (autocomplete no VSCode)

---

### **FASE 3: ERROR HANDLING GLOBAL** (Prioridade MÉDIA - 30min)

#### Objetivo
Configurar tratamento automático de erros

#### Arquivo a Modificar
`/opt/conecta-pro/frontend/src/contexts/providers.tsx`

#### Implementação

```typescript
// src/contexts/providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useToast } from '@/hooks/use-toast';

// Helper para extrair mensagem de erro
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  if (error && typeof error === 'object' && 'message' in error) {
    return String(error.message);
  }
  return 'Erro desconhecido';
}

export function Providers({ children }: { children: React.ReactNode }) {
  const { toast } = useToast();

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30 * 1000,
        gcTime: 5 * 60 * 1000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: 0,
        // ✅ NOVO: Error handling global
        onError: (error) => {
          toast({
            title: "Erro na operação",
            description: getErrorMessage(error),
            variant: "destructive",
          });
        },
        // ✅ NOVO: Success feedback global (opcional)
        onSuccess: () => {
          toast({
            title: "Sucesso",
            description: "Operação realizada com sucesso",
          });
        },
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
```

#### Testar
```bash
# Simular erro (ex: criar documento sem permissão)
# Deve aparecer toast automático com erro
```

---

### **FASE 4: DOCUMENTAÇÃO** (Prioridade MÉDIA - 30min)

#### Objetivo
Criar guias para desenvolvedores

#### Documentos a Criar

**1. Guia de Uso dos Hooks Gerados**
```bash
# /opt/conecta-pro/frontend/docs/ORVAL_HOOKS_GUIDE.md
```

**Conteúdo:**
- Como importar hooks gerados
- Naming convention (useListXApiV1...)
- Parâmetros (query params, body, path params)
- Retorno (data, isLoading, error, refetch)
- Exemplos de uso (GET, POST, PUT, DELETE)

**2. Guia de Migração**
```bash
# /opt/conecta-pro/frontend/docs/MIGRATION_GUIDE.md
```

**Conteúdo:**
- Passo a passo de migração
- Antes/Depois lado a lado
- Checklist de validação
- Troubleshooting

**3. Atualizar CLAUDE.md**
```bash
# /opt/conecta-pro/CLAUDE.md
```

**Adicionar seção:**
```markdown
## Orval - Cobertura 100%

### Status
- ✅ 35 módulos com hooks React Query gerados
- ✅ ~15,000 arquivos TypeScript
- ✅ Padrão: react-query + tags-split

### Como Usar
Ver: `/frontend/docs/ORVAL_HOOKS_GUIDE.md`

### Regenerar Tipos
```bash
npm run orval:all           # Todos os módulos
npm run orval:ged           # Módulo específico
```
```

---

### **FASE 5: CRIAR SCRIPT ORVAL:ALL** (Prioridade BAIXA - 15min)

#### Objetivo
Script para regenerar todos os módulos de uma vez

#### Implementação

**Adicionar no package.json:**
```json
{
  "scripts": {
    "orval:all": "node scripts/run-all-orval.js"
  }
}
```

**Criar script:**
```javascript
// /opt/conecta-pro/frontend/scripts/run-all-orval.js
const { execSync } = require('child_process');
const fs = require('fs');

// Ler todos os configs
const configs = fs.readdirSync('.')
  .filter(f => f.startsWith('orval.config.') && f.endsWith('.ts'))
  .map(f => f.replace('orval.config.', '').replace('.ts', ''));

console.log(`🚀 Regenerando ${configs.length} módulos...\n`);

configs.forEach((module, i) => {
  console.log(`[${i+1}/${configs.length}] Gerando ${module}...`);
  try {
    execSync(`npm run orval:${module}`, { stdio: 'inherit' });
    console.log(`✅ ${module} concluído\n`);
  } catch (error) {
    console.error(`❌ ${module} falhou\n`);
  }
});

console.log('🎉 Regeneração completa!');
```

#### Testar
```bash
npm run orval:all
```

---

## 📊 MÉTRICAS DE SUCESSO

### Antes da Próxima Sessão
```
Hooks React Query Gerados:  30% (11/35 módulos)
Uso de Hooks Gerados:        0% (0 componentes)
Services Manuais:          100% (28 services ativos)
Error Handling Global:      40% (só interceptors)
```

### Depois da Próxima Sessão (Meta)
```
Hooks React Query Gerados: 100% (35/35 módulos) ✅
Uso de Hooks Gerados:       ~5% (1 módulo piloto) ✅
Services Manuais:          ~95% (migração gradual)
Error Handling Global:     100% (onError configurado) ✅
Documentação:              100% (guias criados) ✅
```

---

## ⏱️ ESTIMATIVA DE TEMPO

| Fase | Tempo | Prioridade |
|------|-------|------------|
| FASE 1: Padronização Orval | 2h | CRÍTICA |
| FASE 2: Migração Piloto | 1h | ALTA |
| FASE 3: Error Handling | 30min | MÉDIA |
| FASE 4: Documentação | 30min | MÉDIA |
| FASE 5: Script orval:all | 15min | BAIXA |
| **TOTAL** | **~4h 15min** | - |

---

## 🚀 INÍCIO DA PRÓXIMA SESSÃO

### Comandos Iniciais

```bash
# 1. Entrar no diretório
cd /opt/conecta-pro/frontend

# 2. Verificar estado atual
git status
git log -1

# 3. Ler este documento
cat /opt/conecta-pro/PLANO_TRABALHO_ORVAL.md

# 4. Começar pela FASE 1
vim scripts/update-orval-configs.sh
```

### Primeira Ação
**Executar FASE 1: Atualizar configs Orval de axios → react-query**

### Validação de Conclusão
- [ ] 35/35 módulos com `client: 'react-query'`
- [ ] 35/35 módulos com hooks gerados
- [ ] 1 módulo migrado e funcionando (GED)
- [ ] Error handling global configurado
- [ ] Documentação criada

---

## 📁 ARQUIVOS DE REFERÊNCIA

### Documentos Criados Nesta Sessão
- `/opt/conecta-pro/PLANO_TRABALHO_ORVAL.md` (este arquivo)
- `/opt/conecta-pro/frontend/ORVAL_AUDIT_REPORT.md` (relatório detalhado)
- `/opt/conecta-pro/frontend/ORVAL_AUDIT_SUMMARY.txt` (resumo visual)

### Configs Existentes de Referência
- `/opt/conecta-pro/frontend/orval.config.ged.ts` ✅ (usa react-query)
- `/opt/conecta-pro/frontend/orval.config.core.ts` ✅ (usa react-query)
- `/opt/conecta-pro/frontend/orval.config.financial.ts` ❌ (usa axios, precisa migrar)

### Exemplos de Hooks Gerados
- `/opt/conecta-pro/frontend/src/types/generated/ged/ged-documentos/ged-documentos.ts`
- `/opt/conecta-pro/frontend/src/types/generated/core/authentication/authentication.ts`

---

## 💡 OBSERVAÇÕES IMPORTANTES

1. **Não quebrar produção:** Manter services manuais até migração completa
2. **Testar incrementalmente:** Migrar módulo por módulo, validar antes de prosseguir
3. **Documentar problemas:** Se encontrar erros, documentar para resolver depois
4. **Cache do React Query:** Limpar cache se comportamento estranho (`queryClient.clear()`)
5. **Build antes de commitar:** Sempre rodar `npm run build` para validar types

---

## 🎯 OBJETIVO FINAL

**Sistema com cobertura 100% funcional:**
- ✅ Todos os módulos gerando hooks React Query
- ✅ Todo código usando hooks gerados (sem services duplicados)
- ✅ Cache, retry, invalidation automático
- ✅ Error handling global
- ✅ ~6,731 linhas de código eliminadas
- ✅ Manutenção simplificada (apenas 1 fonte de verdade: OpenAPI)

---

**Criado em:** 2026-01-31
**Sessão Atual:** Finalizada - Descanso merecido! 😴
**Próxima Sessão:** Continuar da FASE 1
**Responsável:** Claude Sonnet 4.5 + Jordan (você!)

🚀 **Bom descanso! Na próxima sessão vamos transformar esses tipos em código funcional!**
