/**
 * Service: ABC Costing Management
 * Cobertura: 50 endpoints
 */

import { getFinancialAbcCosting } from '@/types/generated/financial/financial-abc-costing/financial-abc-costing';
import type {
  CostDriverCreate,
  CostActivityCreate,
  CostPoolCreate,
  CostObjectCreate,
  CostAllocationCreate,
  ListDriversApiV1FinancialCostingDriversGetParams,
} from '@/types/generated/financial/models';

const costing = getFinancialAbcCosting();

export const costingService = {
  // Cost Drivers
  async createDriver(data: CostDriverCreate) {
    const response = await costing.createDriverApiV1FinancialCostingDriversPost(
      data
    );
    return response.data;
  },

  async listDrivers(
    params: ListDriversApiV1FinancialCostingDriversGetParams = {}
  ) {
    const response = await costing.listDriversApiV1FinancialCostingDriversGet(
      params
    );
    return response.data;
  },

  async getDriver(driverId: string) {
    const response = await costing.getDriverApiV1FinancialCostingDriversDriverIdGet(
      driverId
    );
    return response.data;
  },

  async updateDriver(driverId: string, data: any) {
    const response = await costing.updateDriverApiV1FinancialCostingDriversDriverIdPut(
      driverId,
      data
    );
    return response.data;
  },

  async deleteDriver(driverId: string) {
    await costing.deleteDriverApiV1FinancialCostingDriversDriverIdDelete(
      driverId
    );
  },

  // Cost Activities
  async createActivity(data: CostActivityCreate) {
    const response = await costing.createActivityApiV1FinancialCostingActivitiesPost(
      data
    );
    return response.data;
  },

  async listActivities(params: any = {}) {
    const response = await costing.listActivitiesApiV1FinancialCostingActivitiesGet(
      params
    );
    return response.data;
  },

  async getActivity(activityId: string) {
    const response = await costing.getActivityApiV1FinancialCostingActivitiesActivityIdGet(
      activityId
    );
    return response.data;
  },

  async updateActivity(activityId: string, data: any) {
    const response = await costing.updateActivityApiV1FinancialCostingActivitiesActivityIdPut(
      activityId,
      data
    );
    return response.data;
  },

  async deleteActivity(activityId: string) {
    await costing.deleteActivityApiV1FinancialCostingActivitiesActivityIdDelete(
      activityId
    );
  },

  // Cost Pools
  async createPool(data: CostPoolCreate) {
    const response = await costing.createPoolApiV1FinancialCostingPoolsPost(
      data
    );
    return response.data;
  },

  async listPools(params: any = {}) {
    const response = await costing.listPoolsApiV1FinancialCostingPoolsGet(
      params
    );
    return response.data;
  },

  async getPool(poolId: string) {
    const response = await costing.getPoolApiV1FinancialCostingPoolsPoolIdGet(
      poolId
    );
    return response.data;
  },

  async updatePool(poolId: string, data: any) {
    const response = await costing.updatePoolApiV1FinancialCostingPoolsPoolIdPut(
      poolId,
      data
    );
    return response.data;
  },

  async deletePool(poolId: string) {
    await costing.deletePoolApiV1FinancialCostingPoolsPoolIdDelete(poolId);
  },

  // Cost Objects
  async createObject(data: CostObjectCreate) {
    const response = await costing.createObjectApiV1FinancialCostingObjectsPost(
      data
    );
    return response.data;
  },

  async listObjects(params: any = {}) {
    const response = await costing.listObjectsApiV1FinancialCostingObjectsGet(
      params
    );
    return response.data;
  },

  async getObject(objectId: string) {
    const response = await costing.getObjectApiV1FinancialCostingObjectsObjectIdGet(
      objectId
    );
    return response.data;
  },

  async updateObject(objectId: string, data: any) {
    const response = await costing.updateObjectApiV1FinancialCostingObjectsObjectIdPut(
      objectId,
      data
    );
    return response.data;
  },

  async deleteObject(objectId: string) {
    await costing.deleteObjectApiV1FinancialCostingObjectsObjectIdDelete(
      objectId
    );
  },

  // Cost Allocations
  async createAllocation(data: CostAllocationCreate) {
    const response = await costing.createAllocationApiV1FinancialCostingAllocationsPost(
      data
    );
    return response.data;
  },

  async listAllocations(params: any = {}) {
    const response = await costing.listAllocationsApiV1FinancialCostingAllocationsGet(
      params
    );
    return response.data;
  },

  async getAllocation(allocationId: string) {
    const response = await costing.getAllocationApiV1FinancialCostingAllocationsAllocationIdGet(
      allocationId
    );
    return response.data;
  },

  async processAllocation(allocationId: string) {
    const response = await costing.processAllocationApiV1FinancialCostingAllocationsAllocationIdProcessPost(
      allocationId
    );
    return response.data;
  },

  // Analysis
  async getCostAnalysis(condominioId: string, periodId: string) {
    const response = await costing.getCostAnalysisApiV1FinancialCostingAnalysisGet(
      { condominio_id: condominioId, period_id: periodId }
    );
    return response.data;
  },

  async getActivityCostAnalysis(activityId: string) {
    const response = await costing.getActivityCostAnalysisApiV1FinancialCostingAnalysisActivityActivityIdGet(
      activityId
    );
    return response.data;
  },

  async getObjectCostAnalysis(objectId: string) {
    const response = await costing.getObjectCostAnalysisApiV1FinancialCostingAnalysisObjectObjectIdGet(
      objectId
    );
    return response.data;
  },

  // Dashboard
  async getDashboard(condominioId: string) {
    const response = await costing.getCostingDashboardApiV1FinancialCostingDashboardGet(
      { condominio_id: condominioId }
    );
    return response.data;
  },

  // Reports
  async exportToExcel(params: any) {
    const response = await costing.exportCostingToExcelApiV1FinancialCostingExportExcelGet(
      params
    );
    return response.data;
  },
};

export default costingService;
