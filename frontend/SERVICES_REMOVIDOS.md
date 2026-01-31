# Services Manuais Removidos - Migração para Hooks Orval

## Data: 2026-01-31

## Resumo Executivo

Limpeza de services obsoletos após migração completa para hooks Orval gerados automaticamente. Os services foram movidos para `deprecated/services/` ao invés de deletados, permitindo rollback se necessário.

## Status: ✅ CONCLUÍDO

- **Build:** ✅ Sucesso (compilado em 24.7s)
- **Type Check:** ⚠️ Erros apenas em arquivos EXAMPLES/ (não afetam produção)
- **Backup:** ✅ Criado em `services-backup-20260131.tar.gz` (110 KB)
- **Rollback:** ✅ Possível (arquivos movidos, não deletados)

---

## Arquivos Removidos

### Total: 8 arquivos (~204 linhas)

### Módulo Clients (7 arquivos, ~180 linhas)
Migrado para `@/hooks/clients` (Orval hooks)

- ✅ **clientAIService.ts** → Migrado para hooks Orval
- ✅ **clientService.ts** → Migrado para hooks Orval
- ✅ **condominiumService.ts** → Migrado para hooks Orval
- ✅ **contractService.ts** → Migrado para hooks Orval
- ✅ **integrationService.ts** → Migrado para hooks Orval
- ✅ **unitService.ts** → Migrado para hooks Orval
- ✅ **index.ts** → Re-export deprecated removido

**Novos hooks disponíveis:**
```typescript
// Antes (deprecated)
import { clientService } from '@/services/clients'

// Agora (Orval hooks)
import { useListClients, useGetClient, useCreateClient } from '@/hooks/clients'
```

### Módulo Financial (1 arquivo, ~24 linhas)
Migrado para `@/hooks/financial` (Orval hooks)

- ✅ **index.ts** → Wrapper deprecated que só re-exportava hooks

**Novos hooks disponíveis:**
```typescript
// Antes (deprecated)
import * as financialService from '@/services/financial'

// Agora (Orval hooks)
import {
  useListSuppliers,
  useCreateSupplier,
  useListBankAccounts,
  useListCostCenters
} from '@/hooks/financial'
```

---

## Services Não Removidos (Ainda em Uso)

### 1. Modules com Hooks que Usam Services

Estes módulos TÊM hooks Orval, mas ainda mantêm services para lógica adicional:

- **documents/** - Hooks usam services para upload/processamento
- **document-kits/** - Hooks usam services para gestão de kits
- **bidding/** - Hooks wrapper sobre services (migração parcial)
- **contracts/** - Hooks wrapper sobre services
- **equipment/** - Hooks wrapper sobre services
- **diarists/** - Hooks wrapper sobre services
- **reimbursement/** - Hooks wrapper sobre services

**Ação futura:** Migrar completamente para hooks Orval puros.

### 2. Modules Customizados (Sem OpenAPI)

Services que implementam lógica customizada ou APIs sem spec OpenAPI:

- **ai/** - Bartolo AI, Client AI, Document AI (APIs em desenvolvimento)
- **analytics/** - ML/IA (churn, forecast, fraud, lead scoring)
- **audit/** - Auditoria e compliance LGPD
- **campo/** - Operações de campo (offline-first)
- **government/** - Integrações gov.br (eSocial, SEFAZ, etc)
- **hr/** - RH (ponto, folha, portal colaborador)
- **mobile/** - Sincronização mobile/offline
- **notifications/** - Sistema de notificações inteligentes
- **scheduler/** - Agendador de tarefas e workers
- **search/** - Busca inteligente com Elasticsearch
- **security-lgpd/** - LGPD (consentimento, mascaramento, erasure)
- **workflows/** - Engine de workflows customizados

**Ação futura:** Manter permanentemente ou documentar APIs para gerar Orval.

### 3. Utilities/Config

- **config/** - Configurações de sistema (feature flags, tenants)
- **recruitment.service.ts** - Service único de recrutamento

---

## Validação de Segurança

### ✅ Verificações Realizadas

1. **Zero imports ativos** - Grep confirmou que nenhum código importa os services removidos
2. **Build sucesso** - Projeto compila sem erros críticos
3. **Backup criado** - `services-backup-20260131.tar.gz` (110 KB)
4. **Moved, not deleted** - Arquivos em `deprecated/` para rollback

### ⚠️ Avisos

- Erros de type em `EXAMPLES/hr-api-usage.tsx` e `docs/ORVAL_USAGE_EXAMPLES.tsx`
- São arquivos de documentação/exemplo, não afetam produção
- Devem ser atualizados com nomes corretos dos hooks

---

## Benefícios Conquistados

### Código mais limpo
- ✅ 8 arquivos redundantes removidos
- ✅ ~204 linhas de código duplicado eliminadas
- ✅ Única fonte de verdade: hooks Orval gerados

### Type-safety melhorado
- ✅ Types gerados diretamente do OpenAPI
- ✅ Validação automática de requests/responses
- ✅ Autocomplete completo na IDE

### Manutenibilidade
- ✅ Mudanças no backend refletidas automaticamente
- ✅ Menos código manual para manter
- ✅ Padrão consistente em todo projeto

---

## Rollback (Se Necessário)

```bash
# Opção 1: Restaurar do backup
cd /opt/conecta-pro/frontend
tar -xzf services-backup-20260131.tar.gz

# Opção 2: Mover de volta do deprecated
mv deprecated/services/clients src/services/
mv deprecated/services/financial src/services/
```

---

## Próximos Passos

### Curto Prazo
1. ✅ Limpeza concluída
2. ⏭️ Corrigir EXAMPLES/ com nomes corretos dos hooks
3. ⏭️ Remover `deprecated/` após 30 dias sem issues

### Médio Prazo
1. ⏭️ Migrar bidding/contracts/equipment para hooks Orval puros
2. ⏭️ Avaliar diarists/reimbursement para migração completa

### Longo Prazo
1. ⏭️ Documentar APIs customizadas (AI, Analytics, etc)
2. ⏭️ Gerar Orval para módulos gov.br e hr quando estável

---

## Arquivos de Referência

- **Backup:** `services-backup-20260131.tar.gz` (110 KB)
- **Deprecated:** `deprecated/services/` (8 arquivos)
- **Migrações:** `docs/GED_MIGRATION_SUMMARY.md`
- **Guia:** `docs/MIGRATION_GUIDE.md`

---

## Contatos

Dúvidas ou problemas com a migração:
- Revisar `docs/MIGRATION_GUIDE.md`
- Verificar hooks em `src/hooks/`
- Consultar types em `src/types/generated/`

---

**Conclusão:** Limpeza executada com sucesso. Sistema mais enxuto, type-safe e manutenível.
