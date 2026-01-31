/**
 * Service Layer - Módulo BIDDING (Licitações)
 *
 * Exporta todos os serviços de licitações:
 * - Tenders (Editais)
 * - Proposals (Propostas)
 * - Contracts (Contratos)
 * - Certificates (Certidões)
 * - Documents (Documentos)
 *
 * Total: 69 endpoints
 */

// Export default services
export { default as tendersService } from './tenders.service';
export { default as proposalsService } from './proposals.service';
export { default as contractsService } from './contracts.service';
export { default as certificatesService } from './certificates.service';
export { default as documentsService } from './documents.service';

// Re-export types only from each service
export type {
  ListTendersParams,
  PNCPBuscarParams,
  MarcarParticipacaoParams,
  AlterarStatusParams,
} from './tenders.service';

export type {
  ListProposalsParams,
  SubmeterPropostaParams,
  AlterarStatusPropostaParams,
} from './proposals.service';

export type {
  ListContractsParams,
  AlterarStatusContratoParams,
} from './contracts.service';

export type {
  ListCertificatesParams,
  RenovarCertidoesParams,
} from './certificates.service';

export type {
  ListTenderDocumentsParams,
  ListCompanyDocumentsParams,
} from './documents.service';
