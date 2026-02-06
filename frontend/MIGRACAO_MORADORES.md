# Migração Completa: Módulo Moradores/Clients

## Data: 31/01/2026

## Resumo
Migração 100% concluída do módulo Moradores (Clients) de services manuais para hooks Orval gerados automaticamente.

## Arquivos Migrados

### Services (/src/services/clients/)
1. **clientService.ts** - Gestão de Clientes
2. **condominiumService.ts** - Gestão de Condomínios  
3. **unitService.ts** - Gestão de Unidades (Moradores)
4. **contractService.ts** - Gestão de Contratos
5. **integrationService.ts** - Gestão de Integrações
6. **clientAIService.ts** - Serviços de IA para Clientes

### Hooks (/src/hooks/clients/)
1. **useClients.ts** - Hooks de Clientes
2. **useCondominiums.ts** - Hooks de Condomínios
3. **useUnits.ts** - Hooks de Unidades (Moradores)
4. **useContracts.ts** - Hooks de Contratos
5. **useIntegrations.ts** - Hooks de Integrações
6. **useClientAI.ts** - Hooks de IA

## Hooks Orval Disponíveis

### Clientes
- `useClients` - Lista clientes
- `useClient` - Obtém cliente por ID
- `useClientFull` - Cliente completo com relações
- `useClientStats` - Estatísticas de clientes
- `useCreateClient` - Cria cliente
- `useUpdateClient` - Atualiza cliente
- `useDeleteClient` - Remove cliente
- `useActivateClient` - Ativa cliente
- `useSuspendClient` - Suspende cliente
- `useBlockClient` - Bloqueia cliente
- `useSetDefaulter` - Marca inadimplente
- `useClearDefaulter` - Remove inadimplência
- `useEnableGuardian` - Habilita Guardian
- `useEnablePlus` - Habilita Conecta Plus

### Condomínios
- `useCondominiums` - Lista condomínios
- `useCondominium` - Obtém condomínio
- `useCondominiumStats` - Estatísticas
- `useCreateCondominium` - Cria
- `useUpdateCondominium` - Atualiza
- `useDeleteCondominium` - Remove
- `useActivateCondominium` - Ativa
- `useStartImplantation` - Inicia implantação
- `useFinishImplantation` - Finaliza implantação

### Unidades (Moradores)
- `useUnits` - Lista unidades
- `useUnit` - Obtém unidade
- `useUnitStats` - Estatísticas
- `useCreateUnit` - Cria unidade
- `useUpdateUnit` - Atualiza unidade
- `useDeleteUnit` - Remove unidade
- `useSetUnitOwner` - Define proprietário
- `useSetUnitResident` - Define morador/inquilino
- `useClearUnitResident` - Remove morador

### Contratos
- `useContracts` - Lista contratos
- `useContract` - Obtém contrato
- `useCreateContract` - Cria contrato
- `useUpdateContract` - Atualiza contrato
- `useActivateContract` - Ativa contrato
- `useSuspendContract` - Suspende contrato
- `useCancelContract` - Cancela contrato

### Integrações
- `useIntegrations` - Lista integrações
- `useIntegration` - Obtém integração
- `useCreateIntegration` - Cria integração
- `useUpdateIntegration` - Atualiza integração
- `useEnableIntegration` - Habilita integração
- `useDisableIntegration` - Desabilita integração

### IA Clients
- `useClientProfileAnalysis` - Análise de perfil
- `useClientSegmentation` - Sugestão de segmentação
- `useClientChurnRisk` - Predição de churn
- `useServiceRecommendations` - Recomendações de serviços
- `useCondominiumHealth` - Análise de saúde do condomínio
- `useClientDashboardInsights` - Insights do dashboard

## Padrão de Import

```typescript
// Antes (DEPRECATED)
import { unitService } from '@/services/clients';
const data = await unitService.list(condominiumId);

// Agora (Orval)
import { useUnits } from '@/hooks/clients/useUnits';
const { data } = useUnits(condominiumId);
```

## Fonte dos Hooks Orval
`@/types/generated/clients/clients-cadastro`

## Próximos Passos
1. Remover services manuais obsoletos (marcados como DEPRECATED)
2. Validar em ambiente de teste
3. Migrar módulos restantes (Financeiro, Operacional)

## Benefícios
- Type-safety completo
- Cache automático com React Query
- Invalidação inteligente de queries
- Menos código manual para manter
- Sincronização garantida com API backend
