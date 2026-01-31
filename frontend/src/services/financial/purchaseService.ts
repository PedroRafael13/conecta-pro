/**
 * Service: Purchase Management
 * Cobertura: 68 endpoints
 */

import { getFinancialPurchase } from '@/types/generated/financial/financial-purchase/financial-purchase';
import type {
  PurchaseRequisitionCreate,
  PurchaseRequisitionUpdate,
  PurchaseQuotationCreate,
  PurchaseQuotationUpdate,
  PurchaseOrderCreate,
  PurchaseOrderUpdate,
  GoodsReceiptCreate,
  GoodsReceiptUpdate,
  ProductCategoryCreate,
  ProductCategoryUpdate,
  ProductCreate,
  ProductUpdate,
  ProductBlockRequest,
  RequisitionRejectRequest,
  RequisitionCancelRequest,
  QuotationScoreRequest,
  QuotationRejectRequest,
  OrderRejectRequest,
  OrderCancelRequest,
  ReceiptInspectionRequest,
  ReceiptRejectRequest,
  ReceiptDivergenceRequest,
  ReceiptSignRequest,
  ApprovalRejectRequest,
  ApprovalDelegateRequest,
  ApprovalInfoRequest,
  ApprovalInfoProvideRequest,
  ListProductCategoriesApiV1FinancialPurchasePurchasesCategoriesGetParams,
  GetCategoryTreeApiV1FinancialPurchasePurchasesCategoriesTreeGetParams,
  GetCategoryStatsApiV1FinancialPurchasePurchasesCategoriesStatsGetParams,
  ListProductsApiV1FinancialPurchasePurchasesProductsGetParams,
  GetProductStatsApiV1FinancialPurchasePurchasesProductsStatsGetParams,
  ListRequisitionsApiV1FinancialPurchasePurchasesRequisitionsGetParams,
  GetRequisitionStatsApiV1FinancialPurchasePurchasesRequisitionsStatsGetParams,
  ListQuotationsApiV1FinancialPurchasePurchasesQuotationsGetParams,
  GetQuotationStatsApiV1FinancialPurchasePurchasesQuotationsStatsGetParams,
  ListOrdersApiV1FinancialPurchasePurchasesOrdersGetParams,
  GetOrderStatsApiV1FinancialPurchasePurchasesOrdersStatsGetParams,
  ConfirmOrderApiV1FinancialPurchasePurchasesOrdersOrderIdConfirmPostParams,
  ListReceiptsApiV1FinancialPurchasePurchasesReceiptsGetParams,
  GetReceiptStatsApiV1FinancialPurchasePurchasesReceiptsStatsGetParams,
  GetMyApprovalsApiV1FinancialPurchasePurchasesApprovalsMyGetParams,
  ListApprovalsApiV1FinancialPurchasePurchasesApprovalsGetParams,
  GetApprovalStatsApiV1FinancialPurchasePurchasesApprovalsStatsGetParams,
  SuggestSuppliersApiV1FinancialPurchasePurchasesAiSuggestSuppliersPostParams,
  PredictDemandApiV1FinancialPurchasePurchasesAiPredictDemandPostParams,
  ApproveRequisitionApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdApprovePostBody,
  SelectQuotationApiV1FinancialPurchasePurchasesQuotationsQuotationIdSelectPostBody,
  ApproveOrderApiV1FinancialPurchasePurchasesOrdersOrderIdApprovePostBody,
  ApproveReceiptApiV1FinancialPurchasePurchasesReceiptsReceiptIdApprovePostBody,
  ApproveApprovalApiV1FinancialPurchasePurchasesApprovalsApprovalIdApprovePostBody,
} from '@/types/generated/financial/models';

const purchase = getFinancialPurchase();

export const purchaseService = {
  // Product Categories
  async createCategory(data: ProductCategoryCreate) {
    return await purchase.createProductCategoryApiV1FinancialPurchasePurchasesCategoriesPost(
      data
    );
  },

  async listCategories(
    params: ListProductCategoriesApiV1FinancialPurchasePurchasesCategoriesGetParams
  ) {
    return await purchase.listProductCategoriesApiV1FinancialPurchasePurchasesCategoriesGet(
      params
    );
  },

  async getCategory(categoryId: string) {
    return await purchase.getProductCategoryApiV1FinancialPurchasePurchasesCategoriesCategoryIdGet(
      categoryId
    );
  },

  async updateCategory(categoryId: string, data: ProductCategoryUpdate) {
    return await purchase.updateProductCategoryApiV1FinancialPurchasePurchasesCategoriesCategoryIdPut(
      categoryId,
      data
    );
  },

  async deleteCategory(categoryId: string) {
    return await purchase.deleteProductCategoryApiV1FinancialPurchasePurchasesCategoriesCategoryIdDelete(
      categoryId
    );
  },

  async getCategoryTree(
    params: GetCategoryTreeApiV1FinancialPurchasePurchasesCategoriesTreeGetParams
  ) {
    return await purchase.getCategoryTreeApiV1FinancialPurchasePurchasesCategoriesTreeGet(
      params
    );
  },

  async getCategoryStats(
    params: GetCategoryStatsApiV1FinancialPurchasePurchasesCategoriesStatsGetParams
  ) {
    return await purchase.getCategoryStatsApiV1FinancialPurchasePurchasesCategoriesStatsGet(
      params
    );
  },

  // Products
  async createProduct(data: ProductCreate) {
    return await purchase.createProductApiV1FinancialPurchasePurchasesProductsPost(
      data
    );
  },

  async listProducts(
    params: ListProductsApiV1FinancialPurchasePurchasesProductsGetParams
  ) {
    return await purchase.listProductsApiV1FinancialPurchasePurchasesProductsGet(
      params
    );
  },

  async getProduct(productId: string) {
    return await purchase.getProductApiV1FinancialPurchasePurchasesProductsProductIdGet(
      productId
    );
  },

  async updateProduct(productId: string, data: ProductUpdate) {
    return await purchase.updateProductApiV1FinancialPurchasePurchasesProductsProductIdPut(
      productId,
      data
    );
  },

  async deleteProduct(productId: string) {
    return await purchase.deleteProductApiV1FinancialPurchasePurchasesProductsProductIdDelete(
      productId
    );
  },

  async blockProduct(productId: string, data: ProductBlockRequest) {
    return await purchase.blockProductApiV1FinancialPurchasePurchasesProductsProductIdBlockPost(
      productId,
      data
    );
  },

  async getProductStats(
    params: GetProductStatsApiV1FinancialPurchasePurchasesProductsStatsGetParams
  ) {
    return await purchase.getProductStatsApiV1FinancialPurchasePurchasesProductsStatsGet(
      params
    );
  },

  // Requisitions
  async createRequisition(data: PurchaseRequisitionCreate) {
    return await purchase.createRequisitionApiV1FinancialPurchasePurchasesRequisitionsPost(
      data
    );
  },

  async listRequisitions(
    params: ListRequisitionsApiV1FinancialPurchasePurchasesRequisitionsGetParams
  ) {
    return await purchase.listRequisitionsApiV1FinancialPurchasePurchasesRequisitionsGet(
      params
    );
  },

  async getRequisition(requisitionId: string) {
    return await purchase.getRequisitionApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdGet(
      requisitionId
    );
  },

  async updateRequisition(requisitionId: string, data: PurchaseRequisitionUpdate) {
    return await purchase.updateRequisitionApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdPut(
      requisitionId,
      data
    );
  },

  async submitRequisition(requisitionId: string) {
    return await purchase.submitRequisitionApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdSubmitPost(
      requisitionId
    );
  },

  async approveRequisition(
    requisitionId: string,
    data: ApproveRequisitionApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdApprovePostBody
  ) {
    return await purchase.approveRequisitionApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdApprovePost(
      requisitionId,
      data
    );
  },

  async rejectRequisition(requisitionId: string, data: RequisitionRejectRequest) {
    return await purchase.rejectRequisitionApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdRejectPost(
      requisitionId,
      data
    );
  },

  async cancelRequisition(requisitionId: string, data: RequisitionCancelRequest) {
    return await purchase.cancelRequisitionApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdCancelPost(
      requisitionId,
      data
    );
  },

  async analyzeRequisitionRisks(requisitionId: string) {
    return await purchase.analyzeRequisitionRisksApiV1FinancialPurchasePurchasesRequisitionsRequisitionIdAnalyzeRisksPost(
      requisitionId
    );
  },

  async getRequisitionStats(
    params: GetRequisitionStatsApiV1FinancialPurchasePurchasesRequisitionsStatsGetParams
  ) {
    return await purchase.getRequisitionStatsApiV1FinancialPurchasePurchasesRequisitionsStatsGet(
      params
    );
  },

  // Quotations
  async createQuotation(data: PurchaseQuotationCreate) {
    return await purchase.createQuotationApiV1FinancialPurchasePurchasesQuotationsPost(
      data
    );
  },

  async listQuotations(
    params: ListQuotationsApiV1FinancialPurchasePurchasesQuotationsGetParams
  ) {
    return await purchase.listQuotationsApiV1FinancialPurchasePurchasesQuotationsGet(
      params
    );
  },

  async getQuotation(quotationId: string) {
    return await purchase.getQuotationApiV1FinancialPurchasePurchasesQuotationsQuotationIdGet(
      quotationId
    );
  },

  async updateQuotation(quotationId: string, data: PurchaseQuotationUpdate) {
    return await purchase.updateQuotationApiV1FinancialPurchasePurchasesQuotationsQuotationIdPut(
      quotationId,
      data
    );
  },

  async scoreQuotation(quotationId: string, data: QuotationScoreRequest) {
    return await purchase.scoreQuotationApiV1FinancialPurchasePurchasesQuotationsQuotationIdScorePost(
      quotationId,
      data
    );
  },

  async selectQuotation(
    quotationId: string,
    data: SelectQuotationApiV1FinancialPurchasePurchasesQuotationsQuotationIdSelectPostBody
  ) {
    return await purchase.selectQuotationApiV1FinancialPurchasePurchasesQuotationsQuotationIdSelectPost(
      quotationId,
      data
    );
  },

  async rejectQuotation(quotationId: string, data: QuotationRejectRequest) {
    return await purchase.rejectQuotationApiV1FinancialPurchasePurchasesQuotationsQuotationIdRejectPost(
      quotationId,
      data
    );
  },

  async listQuotationsByRequisition(requisitionId: string) {
    return await purchase.listQuotationsByRequisitionApiV1FinancialPurchasePurchasesQuotationsByRequisitionRequisitionIdGet(
      requisitionId
    );
  },

  async compareQuotations(requisitionId: string) {
    return await purchase.compareQuotationsApiV1FinancialPurchasePurchasesQuotationsCompareRequisitionIdGet(
      requisitionId
    );
  },

  async getQuotationStats(
    params: GetQuotationStatsApiV1FinancialPurchasePurchasesQuotationsStatsGetParams
  ) {
    return await purchase.getQuotationStatsApiV1FinancialPurchasePurchasesQuotationsStatsGet(
      params
    );
  },

  // Orders
  async createOrder(data: PurchaseOrderCreate) {
    return await purchase.createOrderApiV1FinancialPurchasePurchasesOrdersPost(
      data
    );
  },

  async listOrders(
    params: ListOrdersApiV1FinancialPurchasePurchasesOrdersGetParams
  ) {
    return await purchase.listOrdersApiV1FinancialPurchasePurchasesOrdersGet(
      params
    );
  },

  async getOrder(orderId: string) {
    return await purchase.getOrderApiV1FinancialPurchasePurchasesOrdersOrderIdGet(
      orderId
    );
  },

  async updateOrder(orderId: string, data: PurchaseOrderUpdate) {
    return await purchase.updateOrderApiV1FinancialPurchasePurchasesOrdersOrderIdPut(
      orderId,
      data
    );
  },

  async approveOrder(
    orderId: string,
    data: ApproveOrderApiV1FinancialPurchasePurchasesOrdersOrderIdApprovePostBody
  ) {
    return await purchase.approveOrderApiV1FinancialPurchasePurchasesOrdersOrderIdApprovePost(
      orderId,
      data
    );
  },

  async rejectOrder(orderId: string, data: OrderRejectRequest) {
    return await purchase.rejectOrderApiV1FinancialPurchasePurchasesOrdersOrderIdRejectPost(
      orderId,
      data
    );
  },

  async sendOrder(orderId: string) {
    return await purchase.sendOrderApiV1FinancialPurchasePurchasesOrdersOrderIdSendPost(
      orderId
    );
  },

  async confirmOrder(
    orderId: string,
    params?: ConfirmOrderApiV1FinancialPurchasePurchasesOrdersOrderIdConfirmPostParams
  ) {
    return await purchase.confirmOrderApiV1FinancialPurchasePurchasesOrdersOrderIdConfirmPost(
      orderId,
      params
    );
  },

  async cancelOrder(orderId: string, data: OrderCancelRequest) {
    return await purchase.cancelOrderApiV1FinancialPurchasePurchasesOrdersOrderIdCancelPost(
      orderId,
      data
    );
  },

  async getOrderStats(
    params: GetOrderStatsApiV1FinancialPurchasePurchasesOrdersStatsGetParams
  ) {
    return await purchase.getOrderStatsApiV1FinancialPurchasePurchasesOrdersStatsGet(
      params
    );
  },

  // Receipts
  async createReceipt(data: GoodsReceiptCreate) {
    return await purchase.createReceiptApiV1FinancialPurchasePurchasesReceiptsPost(
      data
    );
  },

  async listReceipts(
    params: ListReceiptsApiV1FinancialPurchasePurchasesReceiptsGetParams
  ) {
    return await purchase.listReceiptsApiV1FinancialPurchasePurchasesReceiptsGet(
      params
    );
  },

  async getReceipt(receiptId: string) {
    return await purchase.getReceiptApiV1FinancialPurchasePurchasesReceiptsReceiptIdGet(
      receiptId
    );
  },

  async updateReceipt(receiptId: string, data: GoodsReceiptUpdate) {
    return await purchase.updateReceiptApiV1FinancialPurchasePurchasesReceiptsReceiptIdPut(
      receiptId,
      data
    );
  },

  async inspectReceipt(receiptId: string, data: ReceiptInspectionRequest) {
    return await purchase.inspectReceiptApiV1FinancialPurchasePurchasesReceiptsReceiptIdInspectPost(
      receiptId,
      data
    );
  },

  async approveReceipt(
    receiptId: string,
    data: ApproveReceiptApiV1FinancialPurchasePurchasesReceiptsReceiptIdApprovePostBody
  ) {
    return await purchase.approveReceiptApiV1FinancialPurchasePurchasesReceiptsReceiptIdApprovePost(
      receiptId,
      data
    );
  },

  async rejectReceipt(receiptId: string, data: ReceiptRejectRequest) {
    return await purchase.rejectReceiptApiV1FinancialPurchasePurchasesReceiptsReceiptIdRejectPost(
      receiptId,
      data
    );
  },

  async registerDivergence(receiptId: string, data: ReceiptDivergenceRequest) {
    return await purchase.registerDivergenceApiV1FinancialPurchasePurchasesReceiptsReceiptIdDivergencePost(
      receiptId,
      data
    );
  },

  async signReceipt(receiptId: string, data: ReceiptSignRequest) {
    return await purchase.signReceiptApiV1FinancialPurchasePurchasesReceiptsReceiptIdSignPost(
      receiptId,
      data
    );
  },

  async listReceiptsByOrder(orderId: string) {
    return await purchase.listReceiptsByOrderApiV1FinancialPurchasePurchasesReceiptsByOrderOrderIdGet(
      orderId
    );
  },

  async getReceiptStats(
    params: GetReceiptStatsApiV1FinancialPurchasePurchasesReceiptsStatsGetParams
  ) {
    return await purchase.getReceiptStatsApiV1FinancialPurchasePurchasesReceiptsStatsGet(
      params
    );
  },

  // Approvals
  async getMyApprovals(
    params: GetMyApprovalsApiV1FinancialPurchasePurchasesApprovalsMyGetParams
  ) {
    return await purchase.getMyApprovalsApiV1FinancialPurchasePurchasesApprovalsMyGet(
      params
    );
  },

  async listApprovals(
    params: ListApprovalsApiV1FinancialPurchasePurchasesApprovalsGetParams
  ) {
    return await purchase.listApprovalsApiV1FinancialPurchasePurchasesApprovalsGet(
      params
    );
  },

  async getApproval(approvalId: string) {
    return await purchase.getApprovalApiV1FinancialPurchasePurchasesApprovalsApprovalIdGet(
      approvalId
    );
  },

  async approveApproval(
    approvalId: string,
    data: ApproveApprovalApiV1FinancialPurchasePurchasesApprovalsApprovalIdApprovePostBody
  ) {
    return await purchase.approveApprovalApiV1FinancialPurchasePurchasesApprovalsApprovalIdApprovePost(
      approvalId,
      data
    );
  },

  async rejectApproval(approvalId: string, data: ApprovalRejectRequest) {
    return await purchase.rejectApprovalApiV1FinancialPurchasePurchasesApprovalsApprovalIdRejectPost(
      approvalId,
      data
    );
  },

  async delegateApproval(approvalId: string, data: ApprovalDelegateRequest) {
    return await purchase.delegateApprovalApiV1FinancialPurchasePurchasesApprovalsApprovalIdDelegatePost(
      approvalId,
      data
    );
  },

  async requestInfo(approvalId: string, data: ApprovalInfoRequest) {
    return await purchase.requestInfoApiV1FinancialPurchasePurchasesApprovalsApprovalIdRequestInfoPost(
      approvalId,
      data
    );
  },

  async provideInfo(approvalId: string, data: ApprovalInfoProvideRequest) {
    return await purchase.provideInfoApiV1FinancialPurchasePurchasesApprovalsApprovalIdProvideInfoPost(
      approvalId,
      data
    );
  },

  async getApprovalStats(
    params: GetApprovalStatsApiV1FinancialPurchasePurchasesApprovalsStatsGetParams
  ) {
    return await purchase.getApprovalStatsApiV1FinancialPurchasePurchasesApprovalsStatsGet(
      params
    );
  },

  // AI Features
  async suggestSuppliers(
    params: SuggestSuppliersApiV1FinancialPurchasePurchasesAiSuggestSuppliersPostParams
  ) {
    return await purchase.suggestSuppliersApiV1FinancialPurchasePurchasesAiSuggestSuppliersPost(
      params
    );
  },

  async analyzeSupplier(supplierId: string) {
    return await purchase.analyzeSupplierApiV1FinancialPurchasePurchasesAiSupplierAnalysisSupplierIdGet(
      supplierId
    );
  },

  async predictDemand(
    params: PredictDemandApiV1FinancialPurchasePurchasesAiPredictDemandPostParams
  ) {
    return await purchase.predictDemandApiV1FinancialPurchasePurchasesAiPredictDemandPost(
      params
    );
  },

  async calculateReorderPoint(productId: string) {
    return await purchase.calculateReorderPointApiV1FinancialPurchasePurchasesAiReorderPointProductIdGet(
      productId
    );
  },
};

export default purchaseService;
