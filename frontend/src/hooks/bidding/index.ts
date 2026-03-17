/**
 * Hooks React Query - Módulo BIDDING (Licitações)
 *
 * Exporta todos os hooks customizados de licitações:
 * - useTenders (Editais)
 * - useProposals (Propostas)
 * - useContracts (Contratos)
 * - useCertificates (Certidões)
 * - useDocuments (Documentos)
 *
 * Total: 69 endpoints cobertos com React Query
 */

// Tenders (Editais)
export * from './useTenders';

// Proposals (Propostas)
export * from './useProposals';

// Contracts (Contratos)
export * from './useContracts';

// Certificates (Certidões)
export * from './useCertificates';

// Documents (Documentos) - exclude useAtualizarStatusEmLote to avoid conflict with useCertificates
export {
  useListarDocumentos,
  useListarDocumentosVencendo,
  useStatusGeralDocumentos,
  useVerificarHabilitacao,
  useListarTiposDocumento,
  useBuscarDocumentoPorTipo,
  useBuscarDocumento,
  useCriarDocumento,
  useAtualizarDocumento,
  useRemoverDocumento,
} from './useDocuments';

// AI Agents (Agentes IA)
export * from './useAgents';
