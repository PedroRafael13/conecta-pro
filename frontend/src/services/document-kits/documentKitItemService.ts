/**
 * Service Layer - Document Kit Items
 *
 * Gerenciamento de itens dos kits documentais.
 * Endpoints cobertos:
 * - POST /document-kits/{kit_id}/items - Adicionar item
 * - GET /document-kits/{kit_id}/items - Listar itens
 * - GET /document-kits/items/{item_id} - Buscar item
 * - PUT /document-kits/items/{item_id} - Atualizar item
 * - DELETE /document-kits/items/{item_id} - Deletar item
 * - POST /document-kits/{kit_id}/items/reorder - Reordenar itens
 */

import { axiosInstance } from '@/lib/api';
import type {
  DocumentKitItemResponse,
  DocumentKitItemCreate,
  DocumentKitItemUpdate,
} from '@/types/generated/document-kits';

export interface ReorderItemsParams {
  kit_id: string;
  condominio_id: string;
  item_orders: Array<{ id: string; ordem: number }>;
}

class DocumentKitItemService {
  private readonly basePath = '/api/v1/document-kits';

  /**
   * Adiciona um novo item ao kit
   */
  async addItem(
    kit_id: string,
    data: DocumentKitItemCreate,
    condominio_id: string
  ): Promise<DocumentKitItemResponse> {
    const response = await axiosInstance.post<DocumentKitItemResponse>(
      `${this.basePath}/${kit_id}/items`,
      data,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Lista itens de um kit
   */
  async listItems(
    kit_id: string,
    condominio_id: string,
    only_active: boolean = true
  ): Promise<DocumentKitItemResponse[]> {
    const response = await axiosInstance.get<DocumentKitItemResponse[]>(
      `${this.basePath}/${kit_id}/items`,
      { params: { condominio_id, only_active } }
    );
    return response.data;
  }

  /**
   * Busca um item por ID
   */
  async getItem(
    item_id: string,
    condominio_id: string
  ): Promise<DocumentKitItemResponse> {
    const response = await axiosInstance.get<DocumentKitItemResponse>(
      `${this.basePath}/items/${item_id}`,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Atualiza um item existente
   */
  async updateItem(
    item_id: string,
    data: DocumentKitItemUpdate,
    condominio_id: string
  ): Promise<DocumentKitItemResponse> {
    const response = await axiosInstance.put<DocumentKitItemResponse>(
      `${this.basePath}/items/${item_id}`,
      data,
      { params: { condominio_id } }
    );
    return response.data;
  }

  /**
   * Remove um item
   */
  async deleteItem(item_id: string, condominio_id: string): Promise<void> {
    await axiosInstance.delete(`${this.basePath}/items/${item_id}`, {
      params: { condominio_id },
    });
  }

  /**
   * Reordena os itens de um kit
   */
  async reorderItems(params: ReorderItemsParams): Promise<void> {
    const { kit_id, condominio_id, item_orders } = params;
    await axiosInstance.post(
      `${this.basePath}/${kit_id}/items/reorder`,
      item_orders,
      { params: { condominio_id } }
    );
  }
}

export const documentKitItemService = new DocumentKitItemService();
