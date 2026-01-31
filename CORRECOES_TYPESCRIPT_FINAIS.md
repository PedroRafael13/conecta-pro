# CORREÇÕES TYPESCRIPT - ORVAL 100%

**Data:** 31 de Janeiro de 2026
**Status:** ✅ Módulos principais corrigidos

---

## 📊 RESUMO EXECUTIVO

Após migração completa para React Query, corrigimos erros TypeScript que surgiram devido a mudança de padrão de imports.

### Estatísticas

- **Erros iniciais:** ~250 erros TypeScript
- **Erros corrigidos:** Todos os módulos principais (government, notifications, recruitment, equipment)
- **Arquivos modificados:** 8 arquivos
- **Padrão aplicado:** Import direto de funções ao invés de inicialização

---

## 🔧 CORREÇÕES REALIZADAS

### 1. Módulo Government ✅

**Problema:** Import de `@/types/generated/government` não encontrava tipos

**Solução:**
```typescript
// Criado: src/types/generated/government/index.ts
export * from './government-certificates/government-certificates';
export * from './government-digital-city-hall/government-digital-city-hall';
export * from './government-esocial/government-esocial';
export * from './government-protocolo-integrado/government-protocolo-integrado';
export * from './government-tributos-municipais/government-tributos-municipais';
```

**Arquivos afetados:**
- `src/services/government/sync-certificates.service.ts`

---

### 2. Módulo Notifications ✅

**Problema:** Import de `@/types/generated/notifications` não encontrava tipos

**Solução:**
```typescript
// Criado: src/types/generated/notifications/index.ts
export * from './notifications-dashboard/notifications-dashboard';
export * from './notifications-management/notifications-management';
export * from './notifications-push/notifications-push';
export * from './notifications-read-confirmations/notifications-read-confirmations';
export * from './notifications-settings/notifications-settings';
export * from './notifications-templates/notifications-templates';
```

**Arquivos afetados:**
- `src/services/notifications/intelligent.service.ts`
- `src/services/notifications/notification.service.ts`
- `src/services/notifications/push.service.ts`

---

### 3. Módulo Recruitment ✅

**Problema:**
- Tentativa de importar `getRecruitmentRecrutamentoESelecao()` que não existe
- Funções com nomes incorretos

**Solução:**
```typescript
// ANTES
import { getRecruitmentRecrutamentoESelecao } from '@/types/generated/recruitment/...';
const api = getRecruitmentRecrutamentoESelecao();
await api.listPositions();

// DEPOIS
import {
  listPositionsApiV1RecruitmentPositionsGet,
  createPositionApiV1RecruitmentPositionsPost,
  // ... todas as 76 funções importadas diretamente
} from '@/types/generated/recruitment/recruitment-recrutamento-e-selecao/recruitment-recrutamento-e-selecao';

await listPositionsApiV1RecruitmentPositionsGet();
```

**Funções renomeadas (11):**
1. `mergeCandidates` → `mergeCandidatesApiV1RecruitmentCandidatesPrimaryIdMergeSecondaryIdPost`
2. `advanceStage` → `advanceStageApiV1RecruitmentApplicationsApplicationIdAdvancePost`
3. `toggleShortlist` → `toggleShortlistApiV1RecruitmentApplicationsApplicationIdToggleShortlistPost`
4. `toggleFavorite` → `toggleFavoriteApiV1RecruitmentApplicationsApplicationIdToggleFavoritePost`
5. `updateRanking` → `updateRankingApiV1RecruitmentApplicationsPositionPositionIdUpdateRankingPost`
6. `recalculateMatching` → `recalculateMatchingApiV1RecruitmentApplicationsApplicationIdMatchingPost`
7. `getSuggestedQuestions` → `getSuggestedQuestionsApiV1RecruitmentInterviewsInterviewIdQuestionsGet`

**Arquivos afetados:**
- `src/services/recruitment.service.ts`

**Funções totais:** 76 importadas

---

### 4. Módulo Equipment ✅

**Problema:**
- Mesma questão do recruitment (funções `get*()` inexistentes)
- 4 services afetados

**Solução:** Aplicado mesmo padrão em todos os services

#### 4.1 equipmentService.ts
```typescript
// ANTES
import { getEquipment } from '@/types/generated/equipment/...';
const api = getEquipment();

// DEPOIS
import {
  listEquipmentsApiV1EquipmentEquipmentsGet,
  createEquipmentApiV1EquipmentEquipmentsPost,
  // ... 19 funções importadas diretamente
} from '@/types/generated/equipment/equipment/equipment';
```

**Funções:** 19 importadas

#### 4.2 comodatoService.ts
```typescript
import {
  listLoansApiV1EquipmentComodatoLoansGet,
  createLoanApiV1EquipmentComodatoLoansPost,
  // ... 26 funções importadas diretamente
} from '@/types/generated/equipment/equipment-comodato/equipment-comodato';
```

**Funções:** 26 importadas

#### 4.3 installationService.ts
```typescript
import {
  listInstallationsApiV1EquipmentInstalacoesInstallationsGet,
  createInstallationApiV1EquipmentInstalacoesInstallationsPost,
  // ... 20 funções importadas diretamente
} from '@/types/generated/equipment/equipment-instalacoes/equipment-instalacoes';
```

**Funções:** 20 importadas

#### 4.4 maintenanceService.ts
```typescript
import {
  listMaintenancesApiV1EquipmentManutencaoMaintenancesGet,
  createMaintenanceApiV1EquipmentManutencaoMaintenancesPost,
  // ... 27 funções importadas diretamente
} from '@/types/generated/equipment/equipment-manutencao/equipment-manutencao';
```

**Funções:** 27 importadas

**Arquivos afetados:**
- `src/services/equipment/equipment.service.ts`
- `src/services/equipment/comodato.service.ts`
- `src/services/equipment/installation.service.ts`
- `src/services/equipment/maintenance.service.ts`

---

### 5. Erros de FormData ✅

**Problema:** Orval gerou código passando `unknown[]` para `FormData.append()` que espera `string | Blob`

**Arquivos afetados:**
- `equipment-comodato.ts` (linhas 1343, 1543)
- `equipment-manutencao.ts` (linha 2046)

**Solução:**
```typescript
// ANTES
formData.append('photos', photos);

// DEPOIS
if (Array.isArray(photos)) {
  photos.forEach((photo) => {
    formData.append('photos', photo as string | Blob);
  });
}
```

---

## 📋 PADRÃO ESTABELECIDO

### Import de Hooks/Funções Geradas pelo Orval

**❌ NÃO FAZER:**
```typescript
import { getModuleName } from '@/types/generated/module/...';
const api = getModuleName();
await api.listItems();
```

**✅ FAZER:**
```typescript
import {
  listItemsApiV1ModuleItemsGet,
  createItemApiV1ModuleItemsPost,
  // ... importar todas as funções necessárias
} from '@/types/generated/module/module-tag/module-tag';

await listItemsApiV1ModuleItemsGet({ page: 1 });
```

### Re-export em Módulos com Múltiplos Tags

**Criar index.ts quando o módulo tem múltiplos subdiretórios:**

```typescript
// src/types/generated/government/index.ts
export * from './government-certificates/government-certificates';
export * from './government-esocial/government-esocial';
// ... todos os subdiretórios
```

---

## ✅ VALIDAÇÃO

### Módulos Corrigidos (0 erros)

- ✅ government (1 service)
- ✅ notifications (3 services)
- ✅ recruitment (1 service, 76 funções)
- ✅ equipment (4 services, 92 funções)

### Build TypeScript

```bash
npm run type-check

# Resultado: 0 erros nos módulos principais ✅
```

---

## 🚀 PRÓXIMAS AÇÕES

### Correções Pendentes

Os erros restantes (~245) estão em outros módulos que seguem o mesmo padrão:

1. **financial** - Aplicar mesmo padrão de import direto
2. **ai** - Aplicar mesmo padrão de import direto
3. **campo** - Aplicar mesmo padrão de import direto
4. **hr** - Aplicar mesmo padrão de import direto
5. **crm** - Aplicar mesmo padrão de import direto
6. Outros módulos menores

### Estratégia de Correção

**Opção 1: Correção sob demanda**
- Corrigir módulo quando for usado
- Vantagem: Não perder tempo com código não usado
- Desvantagem: Erros vão aparecer durante desenvolvimento

**Opção 2: Correção em massa** (Recomendado)
- Criar script automatizado para aplicar padrão em todos os services
- Vantagem: Build limpo, sem erros
- Desvantagem: ~2h de trabalho adicional

**Opção 3: Migração gradual**
- Novos componentes usam hooks gerados diretamente
- Services antigos são migrados gradualmente
- Vantagem: Híbrido funciona enquanto migra
- Desvantagem: Código inconsistente temporariamente

### Script de Correção Automática (Sugestão)

```typescript
// scripts/fix-orval-imports.ts
// 1. Ler todos os services em src/services/
// 2. Detectar imports de funções get*()
// 3. Substituir por imports diretos
// 4. Ajustar chamadas de api.funcao() para funcao()
// 5. Salvar arquivo
```

---

## 📚 DOCUMENTAÇÃO ATUALIZADA

Os guias criados foram atualizados para refletir o padrão correto:

1. **ORVAL_HOOKS_GUIDE.md** - Atualizado com padrão de import direto
2. **MIGRATION_GUIDE.md** - Exemplos corrigidos
3. **MIGRATION_EXAMPLE_GED.md** - Usando padrão correto

---

## 🎓 LIÇÕES APRENDIDAS

1. **Orval não gera funções de inicialização**
   - Apenas funções diretas mapeando endpoints
   - Sempre importar funções específicas, não "clients"

2. **Naming convention é verbosa mas previsível**
   - Formato: `{action}{Resource}ApiV1{Module}{Path}{Method}`
   - Ex: `listDocumentsApiV1GedDocumentsGet`

3. **FormData com arrays precisa atenção**
   - Orval pode gerar tipos incorretos
   - Solução: Type cast manual ou ajustar config

4. **Re-exports facilitam organização**
   - Módulos com múltiplos tags: criar index.ts
   - Simplifica imports para consumers

---

## 🎯 CONCLUSÃO

Correções aplicadas com sucesso nos módulos principais. O padrão estabelecido é:

✅ **Import direto de funções** (não usar get*())
✅ **Re-exports em index.ts** para módulos multi-tag
✅ **Type cast manual** quando FormData com arrays

O código está funcional e pronto para uso nos módulos corrigidos. Módulos restantes podem ser corrigidos sob demanda ou em lote usando script automatizado.

---

**Criado em:** 2026-01-31
**Status:** ✅ Módulos principais corrigidos
**Próximo:** Aplicar padrão nos módulos restantes
