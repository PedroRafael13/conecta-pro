/**
 * Service: Purchase Management
 * Cobertura: 68 endpoints
 */

import { getFinancialPurchase } from '@/types/generated/financial/financial-purchase/financial-purchase';
import type {
  PurchaseRequisitionCreate,
  PurchaseQuotationCreate,
  PurchaseOrderCreate,
  GoodsReceiptCreate,
  ListRequisitionsApiV1FinancialPurchaseRequisitionsGetParams,
} from '@/types/generated/financial/models';

const purchase = getFinancialPurchase();

export const purchaseService = {
  // Requisitions
  async createRequisition(data: PurchaseRequisitionCreate) {
    const response = await purchase.createRequisitionApiV1FinancialPurchaseRequisitionsPost(
      data
    );
    return response.data;
  },

  async listRequisitions(
    params: ListRequisitionsApiV1FinancialPurchaseRequisitionsGetParams = {}
  ) {
    const response = await purchase.listRequisitionsApiV1FinancialPurchaseRequisitionsGet(
      params
    );
    return response.data;
  },

  async getRequisition(requisitionId: string) {
    const response = await purchase.getRequisitionApiV1FinancialPurchaseRequisitionsRequisitionIdGet(
      requisitionId
    );
    return response.data;
  },

  async approveRequisition(requisitionId: string, observations?: string) {
    const response = await purchase.approveRequisitionApiV1FinancialPurchaseRequisitionsRequisitionIdApprovePost(
      requisitionId,
      { observations }
    );
    return response.data;
  },

  async rejectRequisition(requisitionId: string, reason: string) {
    const response = await purchase.rejectRequisitionApiV1FinancialPurchaseRequisitionsRequisitionIdRejectPost(
      requisitionId,
      { reason }
    );
    return response.data;
  },

  // Quotations
  async createQuotation(data: PurchaseQuotationCreate) {
    const response = await purchase.createQuotationApiV1FinancialPurchaseQuotationsPost(
      data
    );
    return response.data;
  },

  async listQuotations(params: any = {}) {
    const response = await purchase.listQuotationsApiV1FinancialPurchaseQuotationsGet(
      params
    );
    return response.data;
  },

  async selectQuotation(quotationId: string) {
    const response = await purchase.selectQuotationApiV1FinancialPurchaseQuotationsQuotationIdSelectPost(
      quotationId
    );
    return response.data;
  },

  // Orders
  async createOrder(data: PurchaseOrderCreate) {
    const response = await purchase.createOrderApiV1FinancialPurchaseOrdersPost(
      data
    );
    return response.data;
  },

  async listOrders(params: any = {}) {
    const response = await purchase.listOrdersApiV1FinancialPurchaseOrdersGet(
      params
    );
    return response.data;
  },

  async getOrder(orderId: string) {
    const response = await purchase.getOrderApiV1FinancialPurchaseOrdersOrderIdGet(
      orderId
    );
    return response.data;
  },

  async cancelOrder(orderId: string, reason: string) {
    const response = await purchase.cancelOrderApiV1FinancialPurchaseOrdersOrderIdCancelPost(
      orderId,
      { reason }
    );
    return response.data;
  },

  // Goods Receipt
  async createReceipt(data: GoodsReceiptCreate) {
    const response = await purchase.createReceiptApiV1FinancialPurchaseReceiptsPost(
      data
    );
    return response.data;
  },

  async listReceipts(params: any = {}) {
    const response = await purchase.listReceiptsApiV1FinancialPurchaseReceiptsGet(
      params
    );
    return response.data;
  },

  // Reports
  async getDashboard(condominioId: string) {
    const response = await purchase.getPurchaseDashboardApiV1FinancialPurchaseDashboardGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async exportToExcel(params: any) {
    const response = await purchase.exportPurchaseToExcelApiV1FinancialPurchaseExportExcelGet(
      params
    );
    return response.data;
  },
};

export default purchaseService;
