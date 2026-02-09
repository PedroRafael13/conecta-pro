/**
 * Índice de fixtures de teste
 * Exporta todos os dados mockados para uso nos testes
 */

// Auth
export {
  mockLogin,
  mockRefreshToken,
  mockUser,
  mockUsers,
  createMockUser,
  createMockLogin,
  type UserResponse,
  type LoginResponse,
  type RefreshTokenResponse,
} from './auth';

// Clientes
export {
  mockCliente,
  mockClientes,
  mockClienteCreate,
  createMockCliente,
  createMockClienteCreate,
  type ClienteResponse,
  type ClienteCreateRequest,
} from './clientes';

// CRM (Leads, Oportunidades, Propostas)
export {
  mockLead,
  mockLeads,
  mockOportunidade,
  mockOportunidades,
  mockProposta,
  mockPropostas,
  createMockLead,
  createMockOportunidade,
  createMockProposta,
  type LeadResponse,
  type OportunidadeResponse,
  type PropostaResponse,
} from './crm';

// Licitações (já existente)
export {
  mockEdital,
  mockEditais,
  mockProposta as mockLicitacaoProposta,
  mockPropostas as mockLicitacaoPropostas,
  mockContrato,
  mockContratos,
  mockCertidao,
  mockCertidoes,
  mockDocumento,
  mockDocumentos,
  createMockEdital,
  createMockProposta as createMockLicitacaoProposta,
  createMockContrato,
  createMockCertidao,
  createMockDocumento,
} from './licitacoes';

// Operacional (Postos, Escalas, Ocorrências, Funcionários, Diaristas)
export {
  mockPost,
  mockPosts,
  mockScale,
  mockScales,
  mockOccurrence,
  mockOccurrences,
  mockEmployee,
  mockEmployees,
  mockDiarist,
  mockDiarists,
  createMockPost,
  createMockScale,
  createMockOccurrence,
  createMockEmployee,
  createMockDiarist,
  type PostResponse,
  type ScaleResponse,
  type OccurrenceResponse,
  type EmployeeResponse,
  type DiaristResponse,
} from './operacional';

// Financial (Contas a Pagar, Contas a Receber, Fluxo de Caixa, NFes)
export {
  mockPayable,
  mockPayables,
  mockReceivable,
  mockReceivables,
  mockCashflowEntry,
  mockCashflowEntries,
  mockCashflowProjection,
  mockNFe,
  mockNFes,
  createMockPayable,
  createMockReceivable,
  createMockCashflowEntry,
  createMockNFe,
  type PayableResponse,
  type ReceivableResponse,
  type CashflowEntryResponse,
  type CashflowProjectionResponse,
  type NFeResponse,
} from './financial';
