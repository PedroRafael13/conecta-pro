# Contracts Module - Orval Implementation

Módulo CONTRACTS com **100% de cobertura** usando Orval + React Query.

## Estrutura

```
src/
├── api/specs/
│   └── openapi-contracts.json          # OpenAPI spec (20 endpoints)
├── types/generated/contracts/
│   ├── cRMContractsAPI.schemas.ts      # 32 schemas TypeScript
│   └── crm-contracts/
│       └── crm-contracts.ts             # Funções API geradas
├── services/contracts/
│   ├── contractService.ts               # 13 métodos
│   ├── contractItemService.ts           # 3 métodos
│   ├── contractAddendumService.ts       # 3 métodos
│   ├── contractTemplateService.ts       # 6 métodos
│   ├── contractSLAService.ts            # 4 métodos
│   └── index.ts                         # Barrel export
└── hooks/contracts/
    ├── useContracts.ts                  # 13 hooks
    ├── useContractItems.ts              # 3 hooks
    ├── useContractAddendums.ts          # 3 hooks
    ├── useContractTemplates.ts          # 6 hooks
    ├── useContractSLA.ts                # 4 hooks
    └── index.ts                         # Barrel export
```

## Cobertura de Endpoints

### Contract Management (13 endpoints)
- ✅ `POST /api/v1/contracts` - Criar contrato
- ✅ `GET /api/v1/contracts` - Listar contratos
- ✅ `GET /api/v1/contracts/stats` - Estatísticas
- ✅ `GET /api/v1/contracts/alerts` - Alertas de vencimento/reajuste
- ✅ `GET /api/v1/contracts/{id}` - Obter contrato
- ✅ `PUT /api/v1/contracts/{id}` - Atualizar contrato
- ✅ `DELETE /api/v1/contracts/{id}` - Deletar contrato
- ✅ `POST /api/v1/contracts/{id}/submit` - Enviar para assinatura
- ✅ `POST /api/v1/contracts/{id}/activate` - Ativar contrato
- ✅ `POST /api/v1/contracts/{id}/suspend` - Suspender contrato
- ✅ `POST /api/v1/contracts/{id}/terminate` - Encerrar contrato
- ✅ `POST /api/v1/contracts/{id}/renew` - Calcular renovação
- ✅ `POST /api/v1/contracts/{id}/calculate-adjustment` - Calcular reajuste

### Contract Items (3 endpoints)
- ✅ `POST /api/v1/contracts/{id}/items` - Adicionar item
- ✅ `PUT /api/v1/contracts/{id}/items/{item_id}` - Atualizar item
- ✅ `DELETE /api/v1/contracts/{id}/items/{item_id}` - Remover item

### Contract Addendums (3 endpoints)
- ✅ `POST /api/v1/contracts/{id}/addendums` - Criar aditivo
- ✅ `GET /api/v1/contracts/{id}/addendums` - Listar aditivos
- ✅ `POST /api/v1/contracts/addendums/{id}/sign` - Assinar aditivo

### Contract Templates (6 endpoints)
- ✅ `POST /api/v1/contracts/templates` - Criar template
- ✅ `GET /api/v1/contracts/templates` - Listar templates
- ✅ `GET /api/v1/contracts/templates/{id}` - Obter template
- ✅ `PUT /api/v1/contracts/templates/{id}` - Atualizar template
- ✅ `POST /api/v1/contracts/templates/{id}/approve` - Aprovar template
- ✅ `DELETE /api/v1/contracts/templates/{id}` - Deletar template

### Contract SLA (4 endpoints)
- ✅ `POST /api/v1/contracts/{id}/sla-reports` - Criar relatório SLA
- ✅ `GET /api/v1/contracts/{id}/sla-reports` - Listar relatórios
- ✅ `POST /api/v1/contracts/sla-reports/{id}/approve` - Aprovar relatório
- ✅ `POST /api/v1/contracts/{id}/calculate-sla` - Calcular SLA

## Exemplo de Uso

### Listar Contratos

```typescript
import { useContracts } from '@/hooks/contracts';

function ContractList() {
  const { data, isLoading, error } = useContracts({
    page: 1,
    page_size: 20,
    status: 'active',
    has_sla: true,
  });

  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;

  return (
    <div>
      {data.items.map((contract) => (
        <ContractCard key={contract.id} contract={contract} />
      ))}
      <Pagination
        current={data.page}
        total={data.total_pages}
      />
    </div>
  );
}
```

### Criar Contrato

```typescript
import { useCreateContract } from '@/hooks/contracts';
import { ContractCreate } from '@/types/generated/contracts/cRMContractsAPI.schemas';

function NewContract() {
  const createContract = useCreateContract();

  const handleSubmit = async (formData: ContractCreate) => {
    try {
      const contract = await createContract.mutateAsync(formData);
      toast.success(`Contrato ${contract.contract_number} criado!`);
      router.push(`/contracts/${contract.id}`);
    } catch (error) {
      toast.error('Erro ao criar contrato');
    }
  };

  return <ContractForm onSubmit={handleSubmit} />;
}
```

### Workflow de Assinatura

```typescript
import {
  useSubmitContract,
  useActivateContract
} from '@/hooks/contracts';

function ContractWorkflow({ contractId }: { contractId: string }) {
  const submitContract = useSubmitContract();
  const activateContract = useActivateContract();

  // Enviar para assinatura
  const handleSubmit = async () => {
    await submitContract.mutateAsync(contractId);
    toast.success('Contrato enviado para assinatura!');
  };

  // Ativar após assinatura
  const handleActivate = async () => {
    await activateContract.mutateAsync(contractId);
    toast.success('Contrato ativado com sucesso!');
  };

  return (
    <div>
      <Button onClick={handleSubmit}>Enviar para Assinatura</Button>
      <Button onClick={handleActivate}>Ativar Contrato</Button>
    </div>
  );
}
```

### Gerenciar Items do Contrato

```typescript
import {
  useAddContractItem,
  useUpdateContractItem,
  useRemoveContractItem
} from '@/hooks/contracts';

function ContractItems({ contractId }: { contractId: string }) {
  const addItem = useAddContractItem();
  const updateItem = useUpdateContractItem();
  const removeItem = useRemoveContractItem();

  const handleAddItem = async (data: ContractItemCreate) => {
    await addItem.mutateAsync({ contractId, data });
  };

  const handleUpdateItem = async (itemId: string, data: ContractItemUpdate) => {
    await updateItem.mutateAsync({ contractId, itemId, data });
  };

  const handleRemoveItem = async (itemId: string) => {
    await removeItem.mutateAsync({ contractId, itemId });
  };

  return <ItemManager onAdd={handleAddItem} onUpdate={handleUpdateItem} onRemove={handleRemoveItem} />;
}
```

### Calcular Renovação/Reajuste

```typescript
import {
  useCalculateRenewal,
  useCalculateAdjustment
} from '@/hooks/contracts';

function ContractSimulation({ contractId }: { contractId: string }) {
  const calculateRenewal = useCalculateRenewal();
  const calculateAdjustment = useCalculateAdjustment();

  const handleRenewal = async () => {
    const result = await calculateRenewal.mutateAsync({
      contractId,
      data: {
        new_end_date: '2026-12-31',
        adjustment_percent: 5.5,
      },
    });

    console.log('Novo valor:', result.new_monthly_value);
    console.log('Diferença:', result.difference);
  };

  const handleAdjustment = async () => {
    const result = await calculateAdjustment.mutateAsync({
      contractId,
      params: {
        custom_percent: 3.8,
        effective_date: '2026-01-01',
      },
    });

    console.log('Índice:', result.index);
    console.log('Percentual:', result.percent);
  };

  return (
    <div>
      <Button onClick={handleRenewal}>Simular Renovação</Button>
      <Button onClick={handleAdjustment}>Simular Reajuste</Button>
    </div>
  );
}
```

### Templates

```typescript
import {
  useContractTemplates,
  useContractTemplate,
  useCreateTemplate,
  useApproveTemplate
} from '@/hooks/contracts';

function TemplateManager() {
  const { data: templates } = useContractTemplates({
    service_type: 'security',
    approved_only: false,
  });

  const createTemplate = useCreateTemplate();
  const approveTemplate = useApproveTemplate();

  const handleCreate = async (data: ContractTemplateCreate) => {
    await createTemplate.mutateAsync(data);
  };

  const handleApprove = async (templateId: string) => {
    await approveTemplate.mutateAsync(templateId);
  };

  return <TemplateList templates={templates} />;
}
```

### SLA Reports

```typescript
import {
  useContractSLAReports,
  useCreateSLAReport,
  useCalculateSLA
} from '@/hooks/contracts';

function SLAManager({ contractId }: { contractId: string }) {
  const { data: reports } = useContractSLAReports(contractId, { year: 2026 });
  const createReport = useCreateSLAReport();
  const calculateSLA = useCalculateSLA();

  const handleCalculate = async () => {
    const result = await calculateSLA.mutateAsync({
      contractId,
      indicatorResults: [
        { name: 'Disponibilidade', target: 99.5, actual: 99.8, achieved: true },
        { name: 'Tempo Resposta', target: 95.0, actual: 94.2, achieved: false },
      ],
    });

    console.log('Score:', result.overall_score);
    console.log('Penalidade:', result.penalty_percent);
  };

  return <SLADashboard reports={reports} onCalculate={handleCalculate} />;
}
```

## Scripts NPM

```bash
# Regenerar tipos após mudanças no backend
npm run orval:contracts

# Validar tipos TypeScript
npm run type-check
```

## Arquitetura

1. **OpenAPI Spec** → Extraído do backend FastAPI
2. **Orval** → Gera tipos TypeScript automaticamente
3. **Service Layer** → Funções de API organizadas
4. **Hooks React Query** → Cache, invalidação, mutations
5. **Components** → Consomem hooks tipados

## Benefícios

- ✅ **100% type-safe** - TypeScript end-to-end
- ✅ **Cache inteligente** - React Query gerencia estado
- ✅ **Invalidação automática** - Mutations atualizam queries
- ✅ **Sincronização backend** - Tipos sempre atualizados
- ✅ **Developer Experience** - Autocomplete completo
- ✅ **Manutenibilidade** - Mudanças no backend refletem no frontend

## Regenerar Tipos

Após mudanças no backend:

```bash
cd /opt/conecta-pro/backend
# Modificar endpoints...

cd /opt/conecta-pro/frontend
npm run orval:contracts  # Regenera tipos automaticamente
```
