/**
 * Service Layer - Document Kits
 *
 * Gerenciamento de kits documentais, templates e estatísticas.
 * Endpoints cobertos:
 * - POST /document-kits - Criar kit
 * - GET /document-kits - Listar kits
 * - GET /document-kits/stats - Estatísticas
 * - GET /document-kits/templates - Listar templates
 * - GET /document-kits/{id} - Buscar kit
 * - PUT /document-kits/{id} - Atualizar kit
 * - DELETE /document-kits/{id} - Deletar kit
 * - POST /document-kits/{id}/activate - Ativar kit
 * - POST /document-kits/{id}/deactivate - Desativar kit
 * - POST /document-kits/{id}/archive - Arquivar kit
 * - POST /document-kits/{id}/duplicate - Duplicar kit
 */

import { axiosInstance } from '@/lib/api';
import type {
  DocumentKitResponse,
  DocumentKitListResponse,
  DocumentKitCreate,
  DocumentKitUpdate,
  KitStatsResponse,
  KitType,
  KitStatus,
} from '@/types/generated/document-kits';

export interface ListKitsParams {
  condominio_id: string;
  tipo?: KitType;
  status?: KitStatus;
  is_template?: boolean;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface DuplicateKitParams {
  kit_id: string;
  new_codigo: string;
  new_nome: string;
  condominio_id: string;
}

class DocumentKitService {
  private readonly basePath = '/api/v1/document-kits';

  /**
   * Cria um novo kit documental
   */
  async createKit(data: DocumentKitCreate): Promise<DocumentKitResponse> {
    const response = await axiosInstance.post<DocumentKitResponse>(
      this.basePath,
      data
    );
    return response.data;
  }

  /**
   * Lista kits documentais com filtros e paginação
   */
  async listKits(params: ListKitsParams): Promise<DocumentKitListResponse> {
    const response = await axiosInstance.get<DocumentKitListResponse>(
      this.basePath,
      { params }
    );
    return response.data;
  }

  /**
   * Retorna estatísticas de kits de um condomínio
   */
  async getStats(condominio_id: string): Promise<KitStatsResponse> {
    const response = await axiosInstance.get<KitStatsResponse>(
      `${this.basePath}/stats`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Lista templates de kits disponíveis
   */
  async listTemplates(
    condominio_id: string,
    tipo?: KitType
  ): Promise<DocumentKitResponse[]> {
    const response = await axiosInstance.get<DocumentKitResponse[]>(
      `${this.basePath}/templates`,
      { params: { condominio_id, tipo } }
    );
    return response.data;
  }

  /**
   * Busca um kit por ID
   */
  async getKit(
    kit_id: string,
    condominio_id: string
  ): Promise<DocumentKitResponse> {
    const response = await axiosInstance.get<DocumentKitResponse>(
      `${this.basePath}/${kit_id}`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Atualiza um kit existente
   */
  async updateKit(
    kit_id: string,
    data: DocumentKitUpdate,
    condominio_id: string
  ): Promise<DocumentKitResponse> {
    const response = await axiosInstance.put<DocumentKitResponse>(
      `${this.basePath}/${kit_id}`,
      data,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Remove um kit
   */
  async deleteKit(kit_id: string, condominio_id: string): Promise<void> {
    await axiosInstance.delete(`${this.basePath}/${kit_id}`, {
      params: { condominio_id },
    });
  }

  /**
   * Ativa um kit
   */
  async activateKit(
    kit_id: string,
    condominio_id: string
  ): Promise<DocumentKitResponse> {
    const response = await axiosInstance.post<DocumentKitResponse>(
      `${this.basePath}/${kit_id}/activate`,
      null,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Desativa um kit
   */
  async deactivateKit(
    kit_id: string,
    condominio_id: string
  ): Promise<DocumentKitResponse> {
    const response = await axiosInstance.post<DocumentKitResponse>(
      `${this.basePath}/${kit_id}/deactivate`,
      null,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Arquiva um kit
   */
  async archiveKit(
    kit_id: string,
    condominio_id: string
  ): Promise<DocumentKitResponse> {
    const response = await axiosInstance.post<DocumentKitResponse>(
      `${this.basePath}/${kit_id}/archive`,
      null,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Duplica um kit existente
   */
  async duplicateKit(
    params: DuplicateKitParams
  ): Promise<DocumentKitResponse> {
    const { kit_id, new_codigo, new_nome, condominio_id } = params;
    const response = await axiosInstance.post<DocumentKitResponse>(
      `${this.basePath}/${kit_id}/duplicate`,
      null,
      {
        params: {
          new_codigo,
          new_nome,
          condominio_id,
        },
      }
    );
    return response.data;
  }
}

export const documentKitService = new DocumentKitService();
