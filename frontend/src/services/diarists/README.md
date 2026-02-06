# DIARISTS Module - Service Layer

## Cobertura 100% - 57 Endpoints

### Status da Implementação
- **OpenAPI Spec**: ✅ Extraído (57 endpoints)
- **Orval Config**: ✅ Criado
- **Tipos TypeScript**: ✅ Gerados
- **Hooks React Query**: ✅ Disponíveis (gerados pelo Orval)
- **Service Layer**: ✅ Uso direto dos hooks Orval

## Uso

### Importação dos Hooks Gerados

Os hooks são gerados automaticamente pelo Orval e podem ser importados diretamente:

```typescript
import {
  useListDiaristsApiV1OperacionalDiaristasGet,
  useGetDiaristApiV1OperacionalDiaristasDiaristIdGet,
  useConsultaCpfApiV1OperacionalDiaristasConsultaCpfCpfGet,
  // ... outros hooks
} from '@/api/diarists/generated/operacional-diaristas/operacional-diaristas';
```

### Hooks Personalizados

Para maior conveniência, foram criados hooks personalizados que encapsulam os hooks gerados pelo Orval:

```typescript
import {
  useListDiarists,
  useDiarist,
  useConsultaCpf,
  useListAssignments,
  useListSchedules,
  useTodaySchedules,
  useListPayments,
  usePayrollReport,
  useListEvaluations,
  useGeneralStatistics,
  useTopDiarists,
  useSuggestDiarists,
  useAnalyzeAvailability,
  useAnalyzePerformance,
  useOptimizeSchedule,
  useListNotifications,
  useDiaristNotifications,
  useNotificationStatistics,
  useNotificationTemplates,
  useNotificationChannels,
  useSimulateRetentions,
  useListFiscalDocuments,
  useFiscalDocument,
  useRetentionsReport,
  useDiaristFiscalReport,
  useInssTable,
  useIrrfTable,
  useServiceCodes,
} from '@/hooks/diarists';
```

## Endpoints Cobertos

### Core (33 endpoints)
- ✅ Diaristas CRUD (8 endpoints)
- ✅ Alocações (4 endpoints)
- ✅ Agendamentos (10 endpoints)
- ✅ Pagamentos (8 endpoints)
- ✅ Avaliações (3 endpoints)

### AI (4 endpoints)
- ✅ Sugestões inteligentes
- ✅ Análise de disponibilidade
- ✅ Análise de performance
- ✅ Otimização de agendamentos

### Notificações (12 endpoints)
- ✅ Envio manual e automático
- ✅ Lembretes e alertas
- ✅ Templates e canais
- ✅ Estatísticas

### Fiscal (8 endpoints)
- ✅ Cálculo de retenções
- ✅ Geração de RPA
- ✅ Documentos fiscais
- ✅ Relatórios
- ✅ Tabelas INSS/IRRF

## Regenerar Tipos

```bash
npm run orval:diarists
```
