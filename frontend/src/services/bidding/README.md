# Módulo BIDDING - Service Layer

Service layer para o módulo de Licitações Públicas do Conecta PRO.

## Estrutura

```
src/
├── services/bidding/
│   ├── tenders.service.ts         # Editais (12 endpoints)
│   ├── proposals.service.ts       # Propostas (25 endpoints)
│   ├── contracts.service.ts       # Contratos (10 endpoints)
│   ├── certificates.service.ts    # Certidões (14 endpoints)
│   ├── documents.service.ts       # Documentos (8 endpoints)
│   └── index.ts
├── hooks/bidding/
│   ├── useTenders.ts
│   ├── useProposals.ts
│   ├── useContracts.ts
│   ├── useCertificates.ts
│   ├── useDocuments.ts
│   └── index.ts
└── types/generated/bidding/
    ├── bidding-editais/
    ├── bidding-propostas/
    ├── bidding-contratos/
    ├── bidding-certidoes/
    ├── bidding-documentos/
    └── conectaPROBiddingLicitaçõesAPI.schemas.ts
```

## Services

### 1. Tenders (Editais)

Gestão de editais de licitação com integração PNCP.

**Endpoints:**
- `listarEditais()` - Lista editais com filtros
- `buscarEditalPorId()` - Busca edital por ID
- `criarEdital()` - Cria novo edital
- `atualizarEdital()` - Atualiza edital
- `removerEdital()` - Remove edital
- `listarEditaisAbertos()` - Lista editais em andamento
- `listarEditaisPorSegmento()` - Lista por segmento
- `marcarParticipacao()` - Marca participação da empresa
- `alterarStatus()` - Altera status do edital
- `buscarPNCP()` - Busca editais no Portal Nacional
- `sincronizarPNCP()` - Sincroniza com PNCP
- `getDashboard()` - Dashboard de editais

### 2. Proposals (Propostas)

Gestão de propostas comerciais e itens.

**Endpoints:**
- `listarPropostas()` - Lista propostas com filtros
- `buscarPropostaPorId()` - Busca proposta por ID
- `criarProposta()` - Cria nova proposta
- `atualizarProposta()` - Atualiza proposta
- `removerProposta()` - Remove proposta
- `listarPropostasPorEdital()` - Lista propostas de um edital
- `submeterProposta()` - Submete proposta para análise
- `alterarStatusProposta()` - Altera status
- `listarPropostasEmAndamento()` - Lista propostas em andamento
- `listarPropostasAprovadas()` - Lista propostas aprovadas
- `getDashboard()` - Dashboard de propostas
- `adicionarItem()` - Adiciona item à proposta
- `atualizarItem()` - Atualiza item
- `removerItem()` - Remove item
- `listarItens()` - Lista itens da proposta

### 3. Contracts (Contratos)

Gestão de contratos públicos, medições e aditivos.

**Endpoints:**
- `listarContratos()` - Lista contratos com filtros
- `buscarContratoPorId()` - Busca contrato por ID
- `criarContrato()` - Cria novo contrato
- `atualizarContrato()` - Atualiza contrato
- `removerContrato()` - Remove contrato
- `listarContratosVigentes()` - Lista contratos vigentes
- `listarContratosVencendo()` - Lista contratos próximos ao vencimento
- `alterarStatus()` - Altera status do contrato
- `aditivar()` - Cria aditivo de contrato
- `getDashboard()` - Dashboard de contratos
- `criarMedicao()` - Cria medição
- `atualizarMedicao()` - Atualiza medição
- `listarMedicoes()` - Lista medições
- `aprovarMedicao()` - Aprova medição
- `rejeitarMedicao()` - Rejeita medição

### 4. Certificates (Certidões)

Gestão de certidões negativas (federal, estadual, municipal, trabalhista).

**Endpoints:**
- `listarCertidoes()` - Lista certidões com filtros
- `buscarCertidaoPorId()` - Busca certidão por ID
- `criarCertidao()` - Upload manual de certidão
- `atualizarCertidao()` - Atualiza certidão
- `removerCertidao()` - Remove certidão
- `buscarCertidaoPorCNPJeTipo()` - Busca certidão específica
- `verificarStatusPorCNPJ()` - Verifica status de todas as certidões
- `listarTipos()` - Lista tipos de certidões disponíveis
- `listarPendentesRenovacao()` - Lista certidões a vencer
- `renovarCertidoes()` - Renova certidões automaticamente
- `atualizarStatusEmLote()` - Atualiza status em lote
- `downloadCertidao()` - Download de certidão PDF
- `validarCertidao()` - Valida certidão no órgão emissor

### 5. Documents (Documentos)

Gestão de documentos exigidos em editais e documentos da empresa.

**Endpoints:**
- `listarDocumentosEdital()` - Lista documentos do edital
- `adicionarDocumentoEdital()` - Adiciona documento ao edital
- `atualizarDocumentoEdital()` - Atualiza documento do edital
- `removerDocumentoEdital()` - Remove documento do edital
- `listarDocumentosEmpresa()` - Lista documentos da empresa
- `buscarDocumentoEmpresaPorId()` - Busca documento por ID
- `uploadDocumentoEmpresa()` - Upload de documento
- `atualizarDocumentoEmpresa()` - Atualiza documento
- `removerDocumentoEmpresa()` - Remove documento
- `downloadDocumentoEmpresa()` - Download de documento
- `listarDocumentosPendentes()` - Lista documentos pendentes
- `validarDocumento()` - Valida documento

## Hooks React Query

Cada service possui hooks correspondentes com cache, invalidação e feedback:

```typescript
// Exemplo: useTenders
import {
  useListarEditais,
  useBuscarEdital,
  useCriarEdital,
  useMarcarParticipacao,
  useSincronizarPNCP
} from '@/hooks/bidding';

// Query
const { data, isLoading } = useListarEditais({ uf: 'AM' });

// Mutation
const { mutate: criarEdital } = useCriarEdital();
criarEdital(payload);
```

## Compliance

- **Lei 14.133/2021**: Nova Lei de Licitações
- **PNCP**: Integração com Portal Nacional de Contratações Públicas
- **Amazonas**: Foco no estado do Amazonas

## Uso

```typescript
import { tendersService, proposalsService } from '@/services/bidding';
import { useListarEditais, useCriarProposta } from '@/hooks/bidding';

// Service direto
const editais = await tendersService.listarEditais({ uf: 'AM' });

// Hook React Query
function EditaisPage() {
  const { data, isLoading } = useListarEditais({ uf: 'AM' });

  if (isLoading) return <Loading />;
  return <EditaisList editais={data.items} />;
}
```

## Total de Endpoints

- **Tenders**: 12 endpoints
- **Proposals**: 25 endpoints
- **Contracts**: 10 endpoints
- **Certificates**: 14 endpoints
- **Documents**: 8 endpoints

**TOTAL: 69 endpoints** de licitações públicas com cobertura completa.
