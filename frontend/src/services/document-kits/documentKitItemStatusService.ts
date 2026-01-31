/**
 * Service Layer - Document Kit Item Status
 *
 * Gerenciamento de status de itens e documentos.
 * Endpoints cobertos:
 * - GET /document-kits/assignments/{id}/statuses - Listar status de itens
 * - GET /document-kits/item-statuses/{id} - Buscar status
 * - POST /document-kits/item-statuses/{id}/submit - Submeter documento
 * - POST /document-kits/item-statuses/{id}/approve - Aprovar documento
 * - POST /document-kits/item-statuses/{id}/reject - Reprovar documento
 * - POST /document-kits/item-statuses/{id}/not-applicable - Marcar como não aplicável
 */

import { axiosInstance } from '@/lib/api';
import type {
  DocumentKitItemStatusResponse,
  ItemStatusEnum,
} from '@/types/generated/document-kits';

export interface SubmitDocumentParams {
  status_id: string;
  condominio_id: string;
  arquivo_url: string;
  arquivo_nome: string;
  arquivo_tamanho: number;
  arquivo_tipo: string;
}

export interface ApproveDocumentParams {
  status_id: string;
  condominio_id: string;
  observacoes?: string;
}

export interface RejectDocumentParams {
  status_id: string;
  condominio_id: string;
  motivo: string;
}

export interface MarkNotApplicableParams {
  status_id: string;
  condominio_id: string;
  motivo?: string;
}

class DocumentKitItemStatusService {
  private readonly basePath = '/api/v1/document-kits';

  /**
   * Lista status de itens de uma atribuição
   */
  async listItemStatuses(
    assignment_id: string,
    condominio_id: string,
    status?: ItemStatusEnum
  ): Promise<DocumentKitItemStatusResponse[]> {
    const response = await axiosInstance.get<DocumentKitItemStatusResponse[]>(
      `${this.basePath}/assignments/${assignment_id}/statuses`,
      { params: { condominio_id, status } }
    );
    return response.data;
  }

  /**
   * Busca um status de item por ID
   */
  async getItemStatus(
    status_id: string,
    condominio_id: string
  ): Promise<DocumentKitItemStatusResponse> {
    const response = await axiosInstance.get<DocumentKitItemStatusResponse>(
      `${this.basePath}/item-statuses/${status_id}`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Submete um documento para um item
   */
  async submitDocument(
    params: SubmitDocumentParams
  ): Promise<DocumentKitItemStatusResponse> {
    const {
      status_id,
      condominio_id,
      arquivo_url,
      arquivo_nome,
      arquivo_tamanho,
      arquivo_tipo,
    } = params;

    const response = await axiosInstance.post<DocumentKitItemStatusResponse>(
      `${this.basePath}/item-statuses/${status_id}/submit`,
      null,
      {
        params: {
          condominio_id,
          arquivo_url,
          arquivo_nome,
          arquivo_tamanho,
          arquivo_tipo,
        },
      }
    );
    return response.data;
  }

  /**
   * Aprova um documento
   */
  async approveDocument(
    params: ApproveDocumentParams
  ): Promise<DocumentKitItemStatusResponse> {
    const { status_id, condominio_id, observacoes } = params;
    const response = await axiosInstance.post<DocumentKitItemStatusResponse>(
      `${this.basePath}/item-statuses/${status_id}/approve`,
      null,
      { params: { condominio_id, observacoes } }
    );
    return response.data;
  }

  /**
   * Reprova um documento
   */
  async rejectDocument(
    params: RejectDocumentParams
  ): Promise<DocumentKitItemStatusResponse> {
    const { status_id, condominio_id, motivo } = params;
    const response = await axiosInstance.post<DocumentKitItemStatusResponse>(
      `${this.basePath}/item-statuses/${status_id}/reject`,
      null,
      { params: { condominio_id, motivo } }
    );
    return response.data;
  }

  /**
   * Marca um item como não aplicável
   */
  async markNotApplicable(
    params: MarkNotApplicableParams
  ): Promise<DocumentKitItemStatusResponse> {
    const { status_id, condominio_id, motivo } = params;
    const response = await axiosInstance.post<DocumentKitItemStatusResponse>(
      `${this.basePath}/item-statuses/${status_id}/not-applicable`,
      null,
      { params: { condominio_id, motivo } }
    );
    return response.data;
  }
}

export const documentKitItemStatusService = new DocumentKitItemStatusService();
