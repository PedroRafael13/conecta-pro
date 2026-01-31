/**
 * Service: Fiscal Management
 * Cobertura: 56 endpoints
 */

import { getFinancialFiscal } from '@/types/generated/financial/financial-fiscal/financial-fiscal';
import type {
  NFeCreate,
  NFSeCreate,
  SPEDFileCreate,
  SPEDGerarRequest,
  NFeCancelarRequest,
  NFSeCancelarRequest,
  NFeEmitirRequest,
  NFSeEmitirRequest,
  ObrigacaoFiscalCreate,
  ListarNfesApiV1FinancialFiscalFiscalNfeGetParams,
  ListarNfsesApiV1FinancialFiscalFiscalNfseGetParams,
  ListarSpedsApiV1FinancialFiscalFiscalSpedGetParams,
  ListarObrigacoesApiV1FinancialFiscalFiscalObrigacaoGetParams,
  ObterDashboardFiscalApiV1FinancialFiscalFiscalDashboardGetParams,
  GerarSpedApiV1FinancialFiscalFiscalSpedGerarPostParams,
  ListarCfopsApiV1FinancialFiscalFiscalCfopGetParams,
  ListarNcmsApiV1FinancialFiscalFiscalNcmGetParams,
  RetencaoFederalCreate,
  ListarRetencoesApiV1FinancialFiscalFiscalRetencaoGetParams,
  SPEDTipoEnum,
} from '@/types/generated/financial/models';

const fiscal = getFinancialFiscal();

/**
 * Interface para criar configuração de retenção fiscal.
 * Usa RetencaoFederalCreate como base já disponível na API.
 */
type TaxConfigurationCreate = RetencaoFederalCreate;

export const fiscalService = {
  // Tax Configuration (usa retencoes como config de impostos)
  async createTaxConfig(data: TaxConfigurationCreate) {
    return await fiscal.criarRetencaoApiV1FinancialFiscalFiscalRetencaoPost(
      data
    );
  },

  async listTaxConfigs(
    params: ListarRetencoesApiV1FinancialFiscalFiscalRetencaoGetParams
  ) {
    return await fiscal.listarRetencoesApiV1FinancialFiscalFiscalRetencaoGet(
      params
    );
  },

  // NFe - Nota Fiscal Eletrônica
  async createNFe(data: NFeCreate) {
    return await fiscal.criarNfeApiV1FinancialFiscalFiscalNfePost(data);
  },

  async listNFes(
    params: ListarNfesApiV1FinancialFiscalFiscalNfeGetParams
  ) {
    return await fiscal.listarNfesApiV1FinancialFiscalFiscalNfeGet(params);
  },

  async getNFe(nfeId: string) {
    return await fiscal.obterNfeApiV1FinancialFiscalFiscalNfeNfeIdGet(nfeId);
  },

  async authorizeNFe(nfeId: string) {
    // A API usa emitirNfe para autorizar/emitir a NF-e
    const request: NFeEmitirRequest = {
      nfe_id: nfeId,
    };
    return await fiscal.emitirNfeApiV1FinancialFiscalFiscalNfeEmitirPost(
      request
    );
  },

  async cancelNFe(nfeId: string, reason: string) {
    const request: NFeCancelarRequest = {
      nfe_id: nfeId,
      justificativa: reason,
    };
    return await fiscal.cancelarNfeApiV1FinancialFiscalFiscalNfeCancelarPost(
      request
    );
  },

  async downloadNFeXML(nfeId: string) {
    // A API não possui endpoint específico de download XML, usa obterNfe que contém o XML
    const nfe = await fiscal.obterNfeApiV1FinancialFiscalFiscalNfeNfeIdGet(
      nfeId
    );
    return nfe;
  },

  async downloadNFePDF(nfeId: string) {
    // A API não possui endpoint específico de download PDF, usa obterNfe
    const nfe = await fiscal.obterNfeApiV1FinancialFiscalFiscalNfeNfeIdGet(
      nfeId
    );
    return nfe;
  },

  // NFSe - Nota Fiscal de Serviços Eletrônica
  async createNFSe(data: NFSeCreate) {
    return await fiscal.criarNfseApiV1FinancialFiscalFiscalNfsePost(data);
  },

  async listNFSes(
    params: ListarNfsesApiV1FinancialFiscalFiscalNfseGetParams
  ) {
    return await fiscal.listarNfsesApiV1FinancialFiscalFiscalNfseGet(params);
  },

  async getNFSe(nfseId: string) {
    return await fiscal.obterNfseApiV1FinancialFiscalFiscalNfseNfseIdGet(
      nfseId
    );
  },

  async authorizeNFSe(nfseId: string) {
    // A API usa emitirNfse para autorizar/emitir a NFS-e
    const request: NFSeEmitirRequest = {
      nfse_id: nfseId,
    };
    return await fiscal.emitirNfseApiV1FinancialFiscalFiscalNfseEmitirPost(
      request
    );
  },

  async cancelNFSe(nfseId: string, reason: string) {
    const request: NFSeCancelarRequest = {
      nfse_id: nfseId,
      codigo_cancelamento: '0001', // Código padrão
      motivo_cancelamento: reason,
    };
    return await fiscal.cancelarNfseApiV1FinancialFiscalFiscalNfseCancelarPost(
      request
    );
  },

  // SPED - Sistema Público de Escrituração Digital
  async createSPED(data: SPEDFileCreate) {
    return await fiscal.criarSpedApiV1FinancialFiscalFiscalSpedPost(data);
  },

  async listSPEDs(
    params: ListarSpedsApiV1FinancialFiscalFiscalSpedGetParams
  ) {
    return await fiscal.listarSpedsApiV1FinancialFiscalFiscalSpedGet(params);
  },

  async generateSPEDContabil(condominioId: string, ano: number, mes?: number) {
    const request: SPEDGerarRequest = {
      tipo: 'ecd' as SPEDTipoEnum, // ECD = Escrituração Contábil Digital
      ano,
      mes,
    };
    const params: GerarSpedApiV1FinancialFiscalFiscalSpedGerarPostParams = {
      condominio_id: condominioId,
    };
    return await fiscal.gerarSpedApiV1FinancialFiscalFiscalSpedGerarPost(
      request,
      params
    );
  },

  async generateSPEDFiscal(condominioId: string, ano: number, mes?: number) {
    const request: SPEDGerarRequest = {
      tipo: 'efd_icms_ipi' as SPEDTipoEnum, // EFD ICMS/IPI = Escrituração Fiscal Digital
      ano,
      mes,
    };
    const params: GerarSpedApiV1FinancialFiscalFiscalSpedGerarPostParams = {
      condominio_id: condominioId,
    };
    return await fiscal.gerarSpedApiV1FinancialFiscalFiscalSpedGerarPost(
      request,
      params
    );
  },

  // Fiscal Obligations
  async createObligation(data: ObrigacaoFiscalCreate) {
    return await fiscal.criarObrigacaoApiV1FinancialFiscalFiscalObrigacaoPost(
      data
    );
  },

  async listObligations(
    params: ListarObrigacoesApiV1FinancialFiscalFiscalObrigacaoGetParams
  ) {
    return await fiscal.listarObrigacoesApiV1FinancialFiscalFiscalObrigacaoGet(
      params
    );
  },

  async getDashboard(condominioId: string, mes?: number, ano?: number) {
    const params: ObterDashboardFiscalApiV1FinancialFiscalFiscalDashboardGetParams =
      {
        condominio_id: condominioId,
        mes,
        ano,
      };
    return await fiscal.obterDashboardFiscalApiV1FinancialFiscalFiscalDashboardGet(
      params
    );
  },

  // CFOP and NCM
  async listCFOPs(params?: ListarCfopsApiV1FinancialFiscalFiscalCfopGetParams) {
    return await fiscal.listarCfopsApiV1FinancialFiscalFiscalCfopGet(params);
  },

  async listNCMs(params?: ListarNcmsApiV1FinancialFiscalFiscalNcmGetParams) {
    return await fiscal.listarNcmsApiV1FinancialFiscalFiscalNcmGet(params);
  },

  async searchNCM(query: string) {
    // Usa listNCMs com filtro de busca
    return await fiscal.listarNcmsApiV1FinancialFiscalFiscalNcmGet({
      search: query,
    });
  },

  // Reports - usa Dashboard e Stats como relatórios
  async getTaxReport(
    condominioId: string,
    startDate: string,
    endDate: string
  ) {
    // A API não possui endpoint específico para relatório de impostos
    // Usa obterStatsFiscal como alternativa
    return await fiscal.obterStatsFiscalApiV1FinancialFiscalFiscalStatsGet({
      condominio_id: condominioId,
      mes: new Date(startDate).getMonth() + 1,
      ano: new Date(startDate).getFullYear(),
    });
  },

  async exportToExcel(params: {
    condominio_id: string;
    tipo?: string;
    mes?: number;
    ano?: number;
  }) {
    // A API não possui endpoint de export para Excel
    // Retorna os dados do dashboard que podem ser exportados no frontend
    return await fiscal.obterDashboardFiscalApiV1FinancialFiscalFiscalDashboardGet(
      {
        condominio_id: params.condominio_id,
        mes: params.mes,
        ano: params.ano,
      }
    );
  },
};

export default fiscalService;
