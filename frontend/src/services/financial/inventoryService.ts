/**
 * Service: Inventory Management
 * Cobertura: 33 endpoints
 */

import { getFinancialInventory } from '@/types/generated/financial/financial-inventory/financial-inventory';
import type {
  WarehouseCreate,
  WarehouseUpdate,
  StockMovementCreate,
  StockInventoryCreate,
  StockReservationCreate,
  StockReservationRelease,
  ListWarehousesApiV1FinancialInventoryInventoryWarehousesGetParams,
  BlockWarehouseApiV1FinancialInventoryInventoryWarehousesWarehouseIdBlockPostParams,
  ListStockItemsApiV1FinancialInventoryInventoryStockItemsGetParams,
  ListExpiringItemsApiV1FinancialInventoryInventoryStockItemsExpiringGetParams,
  BlockStockItemApiV1FinancialInventoryInventoryStockItemsItemIdBlockPostParams,
  ListMovementsApiV1FinancialInventoryInventoryMovementsGetParams,
  GetMovementStatsApiV1FinancialInventoryInventoryMovementsStatsGetParams,
  ListInventoriesApiV1FinancialInventoryInventoryInventoriesGetParams,
  ListReservationsApiV1FinancialInventoryInventoryReservationsGetParams,
  CancelReservationApiV1FinancialInventoryInventoryReservationsReservationIdCancelPostParams,
} from '@/types/generated/financial/models';

const inventory = getFinancialInventory();

export const inventoryService = {
  // Warehouses
  async createWarehouse(data: WarehouseCreate) {
    return await inventory.createWarehouseApiV1FinancialInventoryInventoryWarehousesPost(
      data
    );
  },

  async listWarehouses(params?: ListWarehousesApiV1FinancialInventoryInventoryWarehousesGetParams) {
    return await inventory.listWarehousesApiV1FinancialInventoryInventoryWarehousesGet(
      params
    );
  },

  async getWarehouse(warehouseId: string) {
    return await inventory.getWarehouseApiV1FinancialInventoryInventoryWarehousesWarehouseIdGet(
      warehouseId
    );
  },

  async updateWarehouse(warehouseId: string, data: WarehouseUpdate) {
    return await inventory.updateWarehouseApiV1FinancialInventoryInventoryWarehousesWarehouseIdPatch(
      warehouseId,
      data
    );
  },

  async blockWarehouse(
    warehouseId: string,
    params: BlockWarehouseApiV1FinancialInventoryInventoryWarehousesWarehouseIdBlockPostParams
  ) {
    return await inventory.blockWarehouseApiV1FinancialInventoryInventoryWarehousesWarehouseIdBlockPost(
      warehouseId,
      params
    );
  },

  async unblockWarehouse(warehouseId: string) {
    return await inventory.unblockWarehouseApiV1FinancialInventoryInventoryWarehousesWarehouseIdUnblockPost(
      warehouseId
    );
  },

  async getWarehouseStats() {
    return await inventory.getWarehouseStatsApiV1FinancialInventoryInventoryWarehousesStatsGet();
  },

  // Stock Items
  async listStockItems(params?: ListStockItemsApiV1FinancialInventoryInventoryStockItemsGetParams) {
    return await inventory.listStockItemsApiV1FinancialInventoryInventoryStockItemsGet(
      params
    );
  },

  async getStockItem(itemId: string) {
    return await inventory.getStockItemApiV1FinancialInventoryInventoryStockItemsItemIdGet(
      itemId
    );
  },

  async getStockStats() {
    return await inventory.getStockStatsApiV1FinancialInventoryInventoryStockItemsStatsGet();
  },

  async listLowStockItems() {
    return await inventory.listLowStockItemsApiV1FinancialInventoryInventoryStockItemsLowStockGet();
  },

  async listExpiringItems(
    params?: ListExpiringItemsApiV1FinancialInventoryInventoryStockItemsExpiringGetParams
  ) {
    return await inventory.listExpiringItemsApiV1FinancialInventoryInventoryStockItemsExpiringGet(
      params
    );
  },

  async blockStockItem(
    itemId: string,
    params: BlockStockItemApiV1FinancialInventoryInventoryStockItemsItemIdBlockPostParams
  ) {
    return await inventory.blockStockItemApiV1FinancialInventoryInventoryStockItemsItemIdBlockPost(
      itemId,
      params
    );
  },

  async unblockStockItem(itemId: string) {
    return await inventory.unblockStockItemApiV1FinancialInventoryInventoryStockItemsItemIdUnblockPost(
      itemId
    );
  },

  // Movements
  async createMovement(data: StockMovementCreate) {
    return await inventory.createMovementApiV1FinancialInventoryInventoryMovementsPost(
      data
    );
  },

  async listMovements(params?: ListMovementsApiV1FinancialInventoryInventoryMovementsGetParams) {
    return await inventory.listMovementsApiV1FinancialInventoryInventoryMovementsGet(
      params
    );
  },

  async getMovement(movementId: string) {
    return await inventory.getMovementApiV1FinancialInventoryInventoryMovementsMovementIdGet(
      movementId
    );
  },

  async confirmMovement(movementId: string) {
    return await inventory.confirmMovementApiV1FinancialInventoryInventoryMovementsMovementIdConfirmPost(
      movementId
    );
  },

  async cancelMovement(movementId: string) {
    return await inventory.cancelMovementApiV1FinancialInventoryInventoryMovementsMovementIdCancelPost(
      movementId
    );
  },

  async listPendingMovements() {
    return await inventory.listPendingMovementsApiV1FinancialInventoryInventoryMovementsPendingGet();
  },

  async getMovementStats(
    params?: GetMovementStatsApiV1FinancialInventoryInventoryMovementsStatsGetParams
  ) {
    return await inventory.getMovementStatsApiV1FinancialInventoryInventoryMovementsStatsGet(
      params
    );
  },

  // Inventories
  async createInventory(data: StockInventoryCreate) {
    return await inventory.createInventoryApiV1FinancialInventoryInventoryInventoriesPost(
      data
    );
  },

  async listInventories(
    params?: ListInventoriesApiV1FinancialInventoryInventoryInventoriesGetParams
  ) {
    return await inventory.listInventoriesApiV1FinancialInventoryInventoryInventoriesGet(
      params
    );
  },

  async getInventory(inventoryId: string) {
    return await inventory.getInventoryApiV1FinancialInventoryInventoryInventoriesInventoryIdGet(
      inventoryId
    );
  },

  async startInventory(inventoryId: string) {
    return await inventory.startInventoryApiV1FinancialInventoryInventoryInventoriesInventoryIdStartPost(
      inventoryId
    );
  },

  async finalizeInventory(inventoryId: string) {
    return await inventory.finalizeInventoryApiV1FinancialInventoryInventoryInventoriesInventoryIdFinalizePost(
      inventoryId
    );
  },

  async getInventoryStats() {
    return await inventory.getInventoryStatsApiV1FinancialInventoryInventoryInventoriesStatsGet();
  },

  // Reservations
  async createReservation(data: StockReservationCreate) {
    return await inventory.createReservationApiV1FinancialInventoryInventoryReservationsPost(
      data
    );
  },

  async listReservations(
    params?: ListReservationsApiV1FinancialInventoryInventoryReservationsGetParams
  ) {
    return await inventory.listReservationsApiV1FinancialInventoryInventoryReservationsGet(
      params
    );
  },

  async getReservation(reservationId: string) {
    return await inventory.getReservationApiV1FinancialInventoryInventoryReservationsReservationIdGet(
      reservationId
    );
  },

  async releaseReservation(reservationId: string, data: StockReservationRelease) {
    return await inventory.releaseReservationApiV1FinancialInventoryInventoryReservationsReservationIdReleasePost(
      reservationId,
      data
    );
  },

  async cancelReservation(
    reservationId: string,
    params: CancelReservationApiV1FinancialInventoryInventoryReservationsReservationIdCancelPostParams
  ) {
    return await inventory.cancelReservationApiV1FinancialInventoryInventoryReservationsReservationIdCancelPost(
      reservationId,
      params
    );
  },

  async getReservationStats() {
    return await inventory.getReservationStatsApiV1FinancialInventoryInventoryReservationsStatsGet();
  },
};

export default inventoryService;
