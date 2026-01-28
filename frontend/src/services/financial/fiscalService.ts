/**
 * Service: Fiscal Management
 * Cobertura: 56 endpoints
 */

import { getFinancialFiscal } from '@/types/generated/financial/financial-fiscal/financial-fiscal';
import type {
  TaxConfigurationCreate,
  NFeCreate,
  NFSeCreate,
  SPEDFileCreate,
  FiscalObligationCreate,
  ListNfesApiV1FinancialFiscalNfesGetParams,
} from '@/types/generated/financial/models';

const fiscal = getFinancialFiscal();

export const fiscalService = {
  // Tax Configuration
  async createTaxConfig(data: TaxConfigurationCreate) {
    const response = await fiscal.createTaxConfigApiV1FinancialFiscalTaxConfigPost(
      data
    );
    return response.data;
  },

  async listTaxConfigs(params: any = {}) {
    const response = await fiscal.listTaxConfigsApiV1FinancialFiscalTaxConfigGet(
      params
    );
    return response.data;
  },

  // NFe - Nota Fiscal Eletrônica
  async createNFe(data: NFeCreate) {
    const response = await fiscal.createNfeApiV1FinancialFiscalNfesPost(data);
    return response.data;
  },

  async listNFes(params: ListNfesApiV1FinancialFiscalNfesGetParams = {}) {
    const response = await fiscal.listNfesApiV1FinancialFiscalNfesGet(params);
    return response.data;
  },

  async getNFe(nfeId: string) {
    const response = await fiscal.getNfeApiV1FinancialFiscalNfesNfeIdGet(nfeId);
    return response.data;
  },

  async authorizeNFe(nfeId: string) {
    const response = await fiscal.authorizeNfeApiV1FinancialFiscalNfesNfeIdAuthorizePost(
      nfeId
    );
    return response.data;
  },

  async cancelNFe(nfeId: string, reason: string) {
    const response = await fiscal.cancelNfeApiV1FinancialFiscalNfesNfeIdCancelPost(
      nfeId,
      { reason }
    );
    return response.data;
  },

  async downloadNFeXML(nfeId: string) {
    const response = await fiscal.downloadNfeXmlApiV1FinancialFiscalNfesNfeIdXmlGet(
      nfeId
    );
    return response.data;
  },

  async downloadNFePDF(nfeId: string) {
    const response = await fiscal.downloadNfePdfApiV1FinancialFiscalNfesNfeIdPdfGet(
      nfeId
    );
    return response.data;
  },

  // NFSe - Nota Fiscal de Serviços Eletrônica
  async createNFSe(data: NFSeCreate) {
    const response = await fiscal.createNfseApiV1FinancialFiscalNfsesPost(data);
    return response.data;
  },

  async listNFSes(params: any = {}) {
    const response = await fiscal.listNfsesApiV1FinancialFiscalNfsesGet(params);
    return response.data;
  },

  async getNFSe(nfseId: string) {
    const response = await fiscal.getNfseApiV1FinancialFiscalNfsesNfseIdGet(
      nfseId
    );
    return response.data;
  },

  async authorizeNFSe(nfseId: string) {
    const response = await fiscal.authorizeNfseApiV1FinancialFiscalNfsesNfseIdAuthorizePost(
      nfseId
    );
    return response.data;
  },

  async cancelNFSe(nfseId: string, reason: string) {
    const response = await fiscal.cancelNfseApiV1FinancialFiscalNfsesNfseIdCancelPost(
      nfseId,
      { reason }
    );
    return response.data;
  },

  // SPED - Sistema Público de Escrituração Digital
  async createSPED(data: SPEDFileCreate) {
    const response = await fiscal.createSpedApiV1FinancialFiscalSpedPost(data);
    return response.data;
  },

  async listSPEDs(params: any = {}) {
    const response = await fiscal.listSpedsApiV1FinancialFiscalSpedGet(params);
    return response.data;
  },

  async generateSPEDContabil(condominioId: string, periodId: string) {
    const response = await fiscal.generateSpedContabilApiV1FinancialFiscalSpedContabilGeneratePost(
      { condominio_id: condominioId, period_id: periodId }
    );
    return response.data;
  },

  async generateSPEDFiscal(condominioId: string, periodId: string) {
    const response = await fiscal.generateSpedFiscalApiV1FinancialFiscalSpedFiscalGeneratePost(
      { condominio_id: condominioId, period_id: periodId }
    );
    return response.data;
  },

  // Fiscal Obligations
  async createObligation(data: FiscalObligationCreate) {
    const response = await fiscal.createObligationApiV1FinancialFiscalObligationsPost(
      data
    );
    return response.data;
  },

  async listObligations(params: any = {}) {
    const response = await fiscal.listObligationsApiV1FinancialFiscalObligationsGet(
      params
    );
    return response.data;
  },

  async getDashboard(condominioId: string) {
    const response = await fiscal.getFiscalDashboardApiV1FinancialFiscalDashboardGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  // CFOP and NCM
  async listCFOPs(params: any = {}) {
    const response = await fiscal.listCfopsApiV1FinancialFiscalCfopsGet(params);
    return response.data;
  },

  async listNCMs(params: any = {}) {
    const response = await fiscal.listNcmsApiV1FinancialFiscalNcmsGet(params);
    return response.data;
  },

  async searchNCM(query: string) {
    const response = await fiscal.searchNcmApiV1FinancialFiscalNcmsSearchGet({
      q: query,
    });
    return response.data;
  },

  // Reports
  async getTaxReport(
    condominioId: string,
    startDate: string,
    endDate: string
  ) {
    const response = await fiscal.getTaxReportApiV1FinancialFiscalReportsTaxGet(
      { condominio_id: condominioId, start_date: startDate, end_date: endDate }
    );
    return response.data;
  },

  async exportToExcel(params: any) {
    const response = await fiscal.exportFiscalToExcelApiV1FinancialFiscalExportExcelGet(
      params
    );
    return response.data;
  },
};

export default fiscalService;
