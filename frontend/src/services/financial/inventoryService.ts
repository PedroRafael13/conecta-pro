/**
 * Service: Inventory Management
 * Cobertura: 33 endpoints
 */

import { getFinancialInventory } from '@/types/generated/financial/financial-inventory/financial-inventory';
import type {
  WarehouseCreate,
  StockItemCreate,
  StockMovementCreate,
  StockInventoryCreate,
  ListWarehousesApiV1FinancialInventoryWarehousesGetParams,
} from '@/types/generated/financial/models';

const inventory = getFinancialInventory();

export const inventoryService = {
  // Warehouses
  async createWarehouse(data: WarehouseCreate) {
    const response = await inventory.createWarehouseApiV1FinancialInventoryWarehousesPost(
      data
    );
    return response.data;
  },

  async listWarehouses(
    params: ListWarehousesApiV1FinancialInventoryWarehousesGetParams = {}
  ) {
    const response = await inventory.listWarehousesApiV1FinancialInventoryWarehousesGet(
      params
    );
    return response.data;
  },

  async getWarehouse(warehouseId: string) {
    const response = await inventory.getWarehouseApiV1FinancialInventoryWarehousesWarehouseIdGet(
      warehouseId
    );
    return response.data;
  },

  // Stock Items
  async createItem(data: StockItemCreate) {
    const response = await inventory.createStockItemApiV1FinancialInventoryItemsPost(
      data
    );
    return response.data;
  },

  async listItems(params: any = {}) {
    const response = await inventory.listStockItemsApiV1FinancialInventoryItemsGet(
      params
    );
    return response.data;
  },

  async getItem(itemId: string) {
    const response = await inventory.getStockItemApiV1FinancialInventoryItemsItemIdGet(
      itemId
    );
    return response.data;
  },

  async getItemBalance(itemId: string, warehouseId?: string) {
    const response = await inventory.getStockBalanceApiV1FinancialInventoryItemsItemIdBalanceGet(
      itemId,
      { warehouse_id: warehouseId }
    );
    return response.data;
  },

  // Stock Movements
  async createMovement(data: StockMovementCreate) {
    const response = await inventory.createMovementApiV1FinancialInventoryMovementsPost(
      data
    );
    return response.data;
  },

  async listMovements(params: any = {}) {
    const response = await inventory.listMovementsApiV1FinancialInventoryMovementsGet(
      params
    );
    return response.data;
  },

  // Inventory Count
  async createInventory(data: StockInventoryCreate) {
    const response = await inventory.createInventoryApiV1FinancialInventoryInventoriesPost(
      data
    );
    return response.data;
  },

  async listInventories(params: any = {}) {
    const response = await inventory.listInventoriesApiV1FinancialInventoryInventoriesGet(
      params
    );
    return response.data;
  },

  async closeInventory(inventoryId: string) {
    const response = await inventory.closeInventoryApiV1FinancialInventoryInventoriesInventoryIdClosePost(
      inventoryId
    );
    return response.data;
  },

  // Reports
  async getDashboard(condominioId: string) {
    const response = await inventory.getInventoryDashboardApiV1FinancialInventoryDashboardGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async getValuationReport(condominioId: string) {
    const response = await inventory.getValuationReportApiV1FinancialInventoryReportsValuationGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  async getABCAnalysis(warehouseId: string) {
    const response = await inventory.getAbcAnalysisApiV1FinancialInventoryReportsAbcAnalysisGet(
      { warehouse_id: warehouseId }
    );
    return response.data;
  },
};

export default inventoryService;
