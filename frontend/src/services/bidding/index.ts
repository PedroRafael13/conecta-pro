/**
 * Service Layer - Módulo BIDDING (Licitações)
 *
 * Exporta todos os serviços de licitações:
 * - Tenders (Editais) - 15 endpoints
 * - Proposals (Propostas) - 13 endpoints
 * - Contracts (Contratos) - 14 endpoints
 * - Certificates (Certidões) - 11 endpoints
 * - Documents (Documentos) - 11 endpoints
 *
 * Total: 64 endpoints
 */

// Export default services
export { default as tendersService } from './tenders.service';
export { default as proposalsService } from './proposals.service';
export { default as contractsService } from './contracts.service';
export { default as certificatesService } from './certificates.service';
export { default as documentsService } from './documents.service';
export { default as agentsService } from './agents.service';

// Re-export types from each service
export type {
  ListTendersParams,
  PNCPBuscarParams,
  MarcarParticipacaoParams,
  AlterarStatusParams,
} from './tenders.service';

export type {
  ListProposalsParams,
  BiddingProposalCreate,
  BiddingProposalUpdate,
  RegistrarResultadoParams,
  RegistrarLanceParams,
  CalcularBDIParams,
} from './proposals.service';

export type {
  ListContractsParams,
  AditivarParams,
  CalcularReajusteParams,
  CriarMedicaoParams,
} from './contracts.service';

export type {
  ListCertificatesParams,
  RenovarCertidoesParams,
  AtualizarStatusParams,
} from './certificates.service';

export type {
  ListDocumentsParams,
} from './documents.service';

export type {
  ScoutRequest,
  AnalystRequest,
  AssessorRequest,
  PricerRequest,
  PipelineRequest,
  PipelineResult,
  AllAgentsStatus,
} from './agents.service';
