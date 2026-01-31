/**
 * Service Layer - Document Kit Operational Integration
 *
 * Integração operacional e geração automática mensal de kits.
 * Endpoints cobertos:
 * - GET /document-kits-operational/employees - Buscar funcionários por condomínio
 * - GET /document-kits-operational/employees/month - Buscar funcionários por mês
 * - GET /document-kits-operational/condominiums - Listar condomínios com funcionários
 * - GET /document-kits-operational/validate - Validar condomínio
 * - POST /document-kits-operational/generate/monthly - Gerar kits mensais
 * - POST /document-kits-operational/generate/batch - Gerar kits em lote
 * - GET /document-kits-operational/scheduler/status - Status do scheduler
 * - POST /document-kits-operational/scheduler/start - Iniciar scheduler
 * - POST /document-kits-operational/scheduler/stop - Parar scheduler
 */

import { axiosInstance } from '@/lib/api';

export interface GetEmployeesParams {
  condominium_id: string;
  start_date?: string; // YYYY-MM-DD
  end_date?: string; // YYYY-MM-DD
  include_inactive?: boolean;
}

export interface GetEmployeesByMonthParams {
  condominium_id: string;
  month: number; // 1-12
  year: number;
  include_inactive?: boolean;
}

export interface ValidateCondominiumParams {
  condominium_id: string;
  month?: number;
  year?: number;
}

export interface GenerateMonthlyKitsParams {
  condominium_id: string;
  month: number;
  year: number;
  created_by_id: string;
  prazo_dias?: number;
}

export interface GenerateBatchKitsParams {
  month: number;
  year: number;
  created_by_id: string;
}

export interface EmployeeData {
  employee_id: string;
  employee_name: string;
  employee_cpf: string;
  allocation_id: string;
  post_id: string;
  post_name: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
}

export interface CondominiumData {
  condominium_id: string;
  condominium_name: string;
  client_id: string;
  employee_count: number;
  post_count: number;
}

export interface ValidationResult {
  has_employees: boolean;
  employee_count: number;
  period: string;
  message: string;
}

export interface GenerationResult {
  success: boolean;
  condominium_id?: string;
  period: string;
  template_kit_id?: string;
  employees_found: number;
  assignments_created: number;
  assignments_skipped: number;
  assignments_failed: number;
  details: Array<{
    employee_id: string;
    employee_name: string;
    success: boolean;
    message: string;
  }>;
}

export interface BatchGenerationResult {
  success: boolean;
  period: string;
  condominiums_processed: number;
  total_employees_found: number;
  total_assignments_created: number;
  total_assignments_skipped: number;
  total_assignments_failed: number;
  condominiums_details: GenerationResult[];
}

export interface SchedulerStatus {
  running: boolean;
  jobs_count: number;
  jobs: Array<{
    id: string;
    name: string;
    next_run_time: string;
  }>;
}

class DocumentKitOperationalService {
  private readonly basePath = '/api/v1/document-kits-operational';

  /**
   * Busca funcionários alocados em um condomínio
   */
  async getEmployeesByCondominium(
    params: GetEmployeesParams
  ): Promise<EmployeeData[]> {
    const response = await axiosInstance.get<EmployeeData[]>(
      `${this.basePath}/employees`,
      { params }
    );
    return response.data;
  }

  /**
   * Busca funcionários de um condomínio em um mês específico
   */
  async getEmployeesByMonth(
    params: GetEmployeesByMonthParams
  ): Promise<EmployeeData[]> {
    const response = await axiosInstance.get<EmployeeData[]>(
      `${this.basePath}/employees/month`,
      { params }
    );
    return response.data;
  }

  /**
   * Lista todos os condomínios com funcionários ativos
   */
  async getCondominiumsWithEmployees(): Promise<CondominiumData[]> {
    const response = await axiosInstance.get<CondominiumData[]>(
      `${this.basePath}/condominiums`
    );
    return response.data;
  }

  /**
   * Valida se um condomínio possui funcionários no período
   */
  async validateCondominiumHasEmployees(
    params: ValidateCondominiumParams
  ): Promise<ValidationResult> {
    const response = await axiosInstance.get<ValidationResult>(
      `${this.basePath}/validate`,
      { params }
    );
    return response.data;
  }

  /**
   * Gera kits mensais para todos os funcionários de um condomínio
   */
  async generateMonthlyKits(
    params: GenerateMonthlyKitsParams
  ): Promise<GenerationResult> {
    const response = await axiosInstance.post<GenerationResult>(
      `${this.basePath}/generate/monthly`,
      null,
      { params }
    );
    return response.data;
  }

  /**
   * Gera kits mensais para todos os condomínios
   */
  async generateBatchKits(
    params: GenerateBatchKitsParams
  ): Promise<BatchGenerationResult> {
    const response = await axiosInstance.post<BatchGenerationResult>(
      `${this.basePath}/generate/batch`,
      null,
      { params }
    );
    return response.data;
  }

  /**
   * Retorna status do scheduler
   */
  async getSchedulerStatus(): Promise<SchedulerStatus> {
    const response = await axiosInstance.get<SchedulerStatus>(
      `${this.basePath}/scheduler/status`
    );
    return response.data;
  }

  /**
   * Inicia o scheduler
   */
  async startScheduler(): Promise<{ message: string }> {
    const response = await axiosInstance.post<{ message: string }>(
      `${this.basePath}/scheduler/start`
    );
    return response.data;
  }

  /**
   * Para o scheduler
   */
  async stopScheduler(): Promise<{ message: string }> {
    const response = await axiosInstance.post<{ message: string }>(
      `${this.basePath}/scheduler/stop`
    );
    return response.data;
  }
}

export const documentKitOperationalService =
  new DocumentKitOperationalService();
