/**
 * Service Layer - Document Kit Assignments
 *
 * Gerenciamento de atribuições de kits e workflow.
 * Endpoints cobertos:
 * - POST /document-kits/assignments - Criar atribuição
 * - GET /document-kits/assignments - Listar atribuições
 * - GET /document-kits/assignments/pending - Listar pendentes
 * - GET /document-kits/assignments/overdue - Listar vencidas
 * - GET /document-kits/assignments/{id} - Buscar atribuição
 * - PUT /document-kits/assignments/{id} - Atualizar atribuição
 * - POST /document-kits/assignments/{id}/start - Iniciar
 * - POST /document-kits/assignments/{id}/approve - Aprovar
 * - POST /document-kits/assignments/{id}/reject - Rejeitar
 * - POST /document-kits/assignments/{id}/complete - Completar
 * - POST /document-kits/assignments/{id}/cancel - Cancelar
 * - POST /document-kits/assignments/{id}/notify - Notificar
 */

import { axiosInstance } from '@/lib/api';
import type {
  DocumentKitAssignmentResponse,
  DocumentKitAssignmentCreate,
  DocumentKitAssignmentUpdate,
  EntityType,
  AssignmentStatusOutput,
} from '@/types/generated/document-kits';

export interface ListAssignmentsParams {
  condominio_id: string;
  kit_id?: string;
  entity_type?: EntityType;
  entity_id?: string;
  status?: AssignmentStatusOutput;
  vencidos?: boolean;
  skip?: number;
  limit?: number;
}

export interface RejectAssignmentParams {
  assignment_id: string;
  condominio_id: string;
  motivo: string;
}

class DocumentKitAssignmentService {
  private readonly basePath = '/api/v1/document-kits/assignments';

  /**
   * Cria uma nova atribuição de kit
   */
  async assignKit(
    data: DocumentKitAssignmentCreate
  ): Promise<DocumentKitAssignmentResponse> {
    const response = await axiosInstance.post<DocumentKitAssignmentResponse>(
      this.basePath,
      data
    );
    return response.data;
  }

  /**
   * Lista atribuições com filtros e paginação
   */
  async listAssignments(
    params: ListAssignmentsParams
  ): Promise<DocumentKitAssignmentResponse[]> {
    const response = await axiosInstance.get<DocumentKitAssignmentResponse[]>(
      this.basePath,
      { params }
    );
    return response.data;
  }

  /**
   * Lista atribuições pendentes
   */
  async listPendingAssignments(
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse[]> {
    const response = await axiosInstance.get<DocumentKitAssignmentResponse[]>(
      `${this.basePath}/pending`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Lista atribuições vencidas
   */
  async listOverdueAssignments(
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse[]> {
    const response = await axiosInstance.get<DocumentKitAssignmentResponse[]>(
      `${this.basePath}/overdue`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Busca uma atribuição por ID
   */
  async getAssignment(
    assignment_id: string,
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse> {
    const response = await axiosInstance.get<DocumentKitAssignmentResponse>(
      `${this.basePath}/${assignment_id}`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Atualiza uma atribuição
   */
  async updateAssignment(
    assignment_id: string,
    data: DocumentKitAssignmentUpdate,
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse> {
    const response = await axiosInstance.put<DocumentKitAssignmentResponse>(
      `${this.basePath}/${assignment_id}`,
      data,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Inicia uma atribuição
   */
  async startAssignment(
    assignment_id: string,
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse> {
    const response = await axiosInstance.post<DocumentKitAssignmentResponse>(
      `${this.basePath}/${assignment_id}/start`,
      null,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Aprova uma atribuição
   */
  async approveAssignment(
    assignment_id: string,
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse> {
    const response = await axiosInstance.post<DocumentKitAssignmentResponse>(
      `${this.basePath}/${assignment_id}/approve`,
      null,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Reprova uma atribuição
   */
  async rejectAssignment(
    params: RejectAssignmentParams
  ): Promise<DocumentKitAssignmentResponse> {
    const { assignment_id, condominio_id, motivo } = params;
    const response = await axiosInstance.post<DocumentKitAssignmentResponse>(
      `${this.basePath}/${assignment_id}/reject`,
      null,
      { params: { condominio_id, motivo } }
    );
    return response.data;
  }

  /**
   * Completa uma atribuição
   */
  async completeAssignment(
    assignment_id: string,
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse> {
    const response = await axiosInstance.post<DocumentKitAssignmentResponse>(
      `${this.basePath}/${assignment_id}/complete`,
      null,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Cancela uma atribuição
   */
  async cancelAssignment(
    assignment_id: string,
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse> {
    const response = await axiosInstance.post<DocumentKitAssignmentResponse>(
      `${this.basePath}/${assignment_id}/cancel`,
      null,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Envia notificação de atribuição
   */
  async notifyAssignment(
    assignment_id: string,
    condominio_id: string
  ): Promise<DocumentKitAssignmentResponse> {
    const response = await axiosInstance.post<DocumentKitAssignmentResponse>(
      `${this.basePath}/${assignment_id}/notify`,
      null,
      { params: { condominio_id } }
    );
    return response.data;
  }
}

export const documentKitAssignmentService = new DocumentKitAssignmentService();
