/**
 * Service: ABC Costing Management
 * Cobertura: 50 endpoints
 */

import { getFinancialAbcCosting } from '@/types/generated/financial/financial-abc-costing/financial-abc-costing';
import type {
  CostDriverCreate,
  CostDriverUpdate,
  CostActivityCreate,
  CostActivityUpdate,
  CostPoolCreate,
  CostPoolUpdate,
  CostPoolAddCost,
  CostObjectCreate,
  CostObjectUpdate,
  CostObjectAddDirectCost,
  CostAllocationCreate,
  CostAllocationApprove,
  CostAllocationReverse,
  CostAllocationBatch,
  CostAnalysisRun,
  ListDriversApiV1FinancialCostingCostingDriversGetParams,
  GetDriverStatsApiV1FinancialCostingCostingDriversStatsGetParams,
  ListActivitiesApiV1FinancialCostingCostingActivitiesGetParams,
  ListPoolsApiV1FinancialCostingCostingPoolsGetParams,
  GetPoolDistributionApiV1FinancialCostingCostingPoolsPoolIdDistributionGetParams,
  ListObjectsApiV1FinancialCostingCostingObjectsGetParams,
  GetProfitabilityRankingApiV1FinancialCostingCostingObjectsRankingProfitabilityGetParams,
  GetUnprofitableObjectsApiV1FinancialCostingCostingObjectsUnprofitableGetParams,
  ListAllocationsApiV1FinancialCostingCostingAllocationsGetParams,
  GetAllocationSummaryApiV1FinancialCostingCostingAllocationsSummaryGetParams,
  ListAnalysesApiV1FinancialCostingCostingAnalysesGetParams,
  AnalyzeProfitabilityApiV1FinancialCostingCostingAnalysesProfitabilityGetParams,
  AnalyzeIdleCapacityApiV1FinancialCostingCostingAnalysesIdleCapacityGetParams,
  DetectAnomaliesApiV1FinancialCostingCostingAnalysesAnomaliesGetParams,
  GetOptimizationSuggestionsApiV1FinancialCostingCostingAnalysesOptimizationSuggestionsGetParams,
  ForecastCostsApiV1FinancialCostingCostingAnalysesForecastGetParams,
  GetDashboardApiV1FinancialCostingCostingDashboardGetParams,
  GetStatsApiV1FinancialCostingCostingStatsGetParams,
  GetCostTrendsApiV1FinancialCostingCostingTrendsGetParams,
} from '@/types/generated/financial/models';

const costing = getFinancialAbcCosting();

export const costingService = {
  // Cost Drivers
  async createDriver(data: CostDriverCreate) {
    return await costing.createDriverApiV1FinancialCostingCostingDriversPost(
      data
    );
  },

  async listDrivers(params?: ListDriversApiV1FinancialCostingCostingDriversGetParams) {
    return await costing.listDriversApiV1FinancialCostingCostingDriversGet(
      params
    );
  },

  async getDriver(driverId: string) {
    return await costing.getDriverApiV1FinancialCostingCostingDriversDriverIdGet(
      driverId
    );
  },

  async updateDriver(driverId: string, data: CostDriverUpdate) {
    return await costing.updateDriverApiV1FinancialCostingCostingDriversDriverIdPatch(
      driverId,
      data
    );
  },

  async deleteDriver(driverId: string) {
    return await costing.deleteDriverApiV1FinancialCostingCostingDriversDriverIdDelete(
      driverId
    );
  },

  async getDriverStats(params?: GetDriverStatsApiV1FinancialCostingCostingDriversStatsGetParams) {
    return await costing.getDriverStatsApiV1FinancialCostingCostingDriversStatsGet(
      params
    );
  },

  // Cost Activities
  async createActivity(data: CostActivityCreate) {
    return await costing.createActivityApiV1FinancialCostingCostingActivitiesPost(
      data
    );
  },

  async listActivities(params?: ListActivitiesApiV1FinancialCostingCostingActivitiesGetParams) {
    return await costing.listActivitiesApiV1FinancialCostingCostingActivitiesGet(
      params
    );
  },

  async getActivity(activityId: string) {
    return await costing.getActivityApiV1FinancialCostingCostingActivitiesActivityIdGet(
      activityId
    );
  },

  async updateActivity(activityId: string, data: CostActivityUpdate) {
    return await costing.updateActivityApiV1FinancialCostingCostingActivitiesActivityIdPatch(
      activityId,
      data
    );
  },

  async deleteActivity(activityId: string) {
    return await costing.deleteActivityApiV1FinancialCostingCostingActivitiesActivityIdDelete(
      activityId
    );
  },

  // Cost Pools
  async createPool(data: CostPoolCreate) {
    return await costing.createPoolApiV1FinancialCostingCostingPoolsPost(data);
  },

  async listPools(params?: ListPoolsApiV1FinancialCostingCostingPoolsGetParams) {
    return await costing.listPoolsApiV1FinancialCostingCostingPoolsGet(params);
  },

  async getPool(poolId: string) {
    return await costing.getPoolApiV1FinancialCostingCostingPoolsPoolIdGet(
      poolId
    );
  },

  async updatePool(poolId: string, data: CostPoolUpdate) {
    return await costing.updatePoolApiV1FinancialCostingCostingPoolsPoolIdPatch(
      poolId,
      data
    );
  },

  async deletePool(poolId: string) {
    return await costing.deletePoolApiV1FinancialCostingCostingPoolsPoolIdDelete(
      poolId
    );
  },

  async addCostToPool(poolId: string, data: CostPoolAddCost) {
    return await costing.addCostToPoolApiV1FinancialCostingCostingPoolsPoolIdAddCostPost(
      poolId,
      data
    );
  },

  async getPoolDistribution(
    poolId: string,
    params: GetPoolDistributionApiV1FinancialCostingCostingPoolsPoolIdDistributionGetParams
  ) {
    return await costing.getPoolDistributionApiV1FinancialCostingCostingPoolsPoolIdDistributionGet(
      poolId,
      params
    );
  },

  // Cost Objects
  async createObject(data: CostObjectCreate) {
    return await costing.createObjectApiV1FinancialCostingCostingObjectsPost(
      data
    );
  },

  async listObjects(params?: ListObjectsApiV1FinancialCostingCostingObjectsGetParams) {
    return await costing.listObjectsApiV1FinancialCostingCostingObjectsGet(
      params
    );
  },

  async getObject(objectId: string) {
    return await costing.getObjectApiV1FinancialCostingCostingObjectsObjectIdGet(
      objectId
    );
  },

  async updateObject(objectId: string, data: CostObjectUpdate) {
    return await costing.updateObjectApiV1FinancialCostingCostingObjectsObjectIdPatch(
      objectId,
      data
    );
  },

  async deleteObject(objectId: string) {
    return await costing.deleteObjectApiV1FinancialCostingCostingObjectsObjectIdDelete(
      objectId
    );
  },

  async addDirectCost(objectId: string, data: CostObjectAddDirectCost) {
    return await costing.addDirectCostApiV1FinancialCostingCostingObjectsObjectIdAddDirectCostPost(
      objectId,
      data
    );
  },

  async getBreakEven(objectId: string) {
    return await costing.getBreakEvenApiV1FinancialCostingCostingObjectsObjectIdBreakEvenGet(
      objectId
    );
  },

  async getProfitabilityRanking(
    params?: GetProfitabilityRankingApiV1FinancialCostingCostingObjectsRankingProfitabilityGetParams
  ) {
    return await costing.getProfitabilityRankingApiV1FinancialCostingCostingObjectsRankingProfitabilityGet(
      params
    );
  },

  async getUnprofitableObjects(
    params?: GetUnprofitableObjectsApiV1FinancialCostingCostingObjectsUnprofitableGetParams
  ) {
    return await costing.getUnprofitableObjectsApiV1FinancialCostingCostingObjectsUnprofitableGet(
      params
    );
  },

  // Cost Allocations
  async createAllocation(data: CostAllocationCreate) {
    return await costing.createAllocationApiV1FinancialCostingCostingAllocationsPost(
      data
    );
  },

  async listAllocations(
    params?: ListAllocationsApiV1FinancialCostingCostingAllocationsGetParams
  ) {
    return await costing.listAllocationsApiV1FinancialCostingCostingAllocationsGet(
      params
    );
  },

  async getAllocation(allocationId: string) {
    return await costing.getAllocationApiV1FinancialCostingCostingAllocationsAllocationIdGet(
      allocationId
    );
  },

  async approveAllocation(allocationId: string, data: CostAllocationApprove) {
    return await costing.approveAllocationApiV1FinancialCostingCostingAllocationsAllocationIdApprovePost(
      allocationId,
      data
    );
  },

  async executeAllocation(allocationId: string) {
    return await costing.executeAllocationApiV1FinancialCostingCostingAllocationsAllocationIdExecutePost(
      allocationId
    );
  },

  async reverseAllocation(allocationId: string, data: CostAllocationReverse) {
    return await costing.reverseAllocationApiV1FinancialCostingCostingAllocationsAllocationIdReversePost(
      allocationId,
      data
    );
  },

  async batchExecuteAllocations(data: CostAllocationBatch) {
    return await costing.batchExecuteAllocationsApiV1FinancialCostingCostingAllocationsBatchExecutePost(
      data
    );
  },

  async getAllocationSummary(
    params: GetAllocationSummaryApiV1FinancialCostingCostingAllocationsSummaryGetParams
  ) {
    return await costing.getAllocationSummaryApiV1FinancialCostingCostingAllocationsSummaryGet(
      params
    );
  },

  // Analyses
  async listAnalyses(params?: ListAnalysesApiV1FinancialCostingCostingAnalysesGetParams) {
    return await costing.listAnalysesApiV1FinancialCostingCostingAnalysesGet(
      params
    );
  },

  async getAnalysis(analysisId: string) {
    return await costing.getAnalysisApiV1FinancialCostingCostingAnalysesAnalysisIdGet(
      analysisId
    );
  },

  async runAbcCosting(data: CostAnalysisRun) {
    return await costing.runAbcCostingApiV1FinancialCostingCostingAnalysesRunAbcPost(
      data
    );
  },

  async runAiAnalysis(data: CostAnalysisRun) {
    return await costing.runAiAnalysisApiV1FinancialCostingCostingAnalysesRunAiPost(
      data
    );
  },

  async analyzeProfitability(
    params?: AnalyzeProfitabilityApiV1FinancialCostingCostingAnalysesProfitabilityGetParams
  ) {
    return await costing.analyzeProfitabilityApiV1FinancialCostingCostingAnalysesProfitabilityGet(
      params
    );
  },

  async analyzeIdleCapacity(
    params?: AnalyzeIdleCapacityApiV1FinancialCostingCostingAnalysesIdleCapacityGetParams
  ) {
    return await costing.analyzeIdleCapacityApiV1FinancialCostingCostingAnalysesIdleCapacityGet(
      params
    );
  },

  async detectAnomalies(
    params?: DetectAnomaliesApiV1FinancialCostingCostingAnalysesAnomaliesGetParams
  ) {
    return await costing.detectAnomaliesApiV1FinancialCostingCostingAnalysesAnomaliesGet(
      params
    );
  },

  async getOptimizationSuggestions(
    params?: GetOptimizationSuggestionsApiV1FinancialCostingCostingAnalysesOptimizationSuggestionsGetParams
  ) {
    return await costing.getOptimizationSuggestionsApiV1FinancialCostingCostingAnalysesOptimizationSuggestionsGet(
      params
    );
  },

  async forecastCosts(
    params?: ForecastCostsApiV1FinancialCostingCostingAnalysesForecastGetParams
  ) {
    return await costing.forecastCostsApiV1FinancialCostingCostingAnalysesForecastGet(
      params
    );
  },

  // Dashboard & Stats
  async getDashboard(params?: GetDashboardApiV1FinancialCostingCostingDashboardGetParams) {
    return await costing.getDashboardApiV1FinancialCostingCostingDashboardGet(
      params
    );
  },

  async getStats(params?: GetStatsApiV1FinancialCostingCostingStatsGetParams) {
    return await costing.getStatsApiV1FinancialCostingCostingStatsGet(params);
  },

  async getCostTrends(params?: GetCostTrendsApiV1FinancialCostingCostingTrendsGetParams) {
    return await costing.getCostTrendsApiV1FinancialCostingCostingTrendsGet(
      params
    );
  },
};

export default costingService;
