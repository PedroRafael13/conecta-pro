/**
 * Service Layer - Checklists (CAMPO)
 * Gestão de checklists dinâmicos para OS e visitas
 */

import * as ChecklistAPI from '@/api/campo/generated/campo-checklists/campo-checklists';
import type {
  ChecklistTemplateCreate,
  ChecklistTemplateUpdate,
  ChecklistItemCreate,
  ChecklistItemUpdate,
  ReordenarItensRequest,
  ListarTemplatesApiV1CampoChecklistsTemplatesGetParams,
  ClonarTemplateApiV1CampoChecklistsTemplatesTemplateIdClonarPostParams,
} from '@/api/campo/generated/models';

export class ChecklistService {
  /**
   * Lista templates de checklist
   */
  async listarTemplates(params?: ListarTemplatesApiV1CampoChecklistsTemplatesGetParams) {
    return ChecklistAPI.listarTemplatesApiV1CampoChecklistsTemplatesGet(params);
  }

  /**
   * Busca template por ID
   */
  async buscarTemplate(templateId: string) {
    return ChecklistAPI.obterTemplateApiV1CampoChecklistsTemplatesTemplateIdGet(templateId);
  }

  /**
   * Cria novo template
   */
  async criarTemplate(data: ChecklistTemplateCreate) {
    return ChecklistAPI.criarTemplateApiV1CampoChecklistsTemplatesPost(data);
  }

  /**
   * Atualiza template
   */
  async atualizarTemplate(templateId: string, data: ChecklistTemplateUpdate) {
    return ChecklistAPI.atualizarTemplateApiV1CampoChecklistsTemplatesTemplateIdPatch(
      templateId,
      data
    );
  }

  /**
   * Deleta template
   */
  async deletarTemplate(templateId: string) {
    return ChecklistAPI.excluirTemplateApiV1CampoChecklistsTemplatesTemplateIdDelete(templateId);
  }

  /**
   * Duplica template
   */
  async duplicarTemplate(templateId: string, params: ClonarTemplateApiV1CampoChecklistsTemplatesTemplateIdClonarPostParams) {
    return ChecklistAPI.clonarTemplateApiV1CampoChecklistsTemplatesTemplateIdClonarPost(
      templateId,
      params
    );
  }

  /**
   * Cria item de checklist
   */
  async criarItem(data: ChecklistItemCreate) {
    return ChecklistAPI.adicionarItemApiV1CampoChecklistsItensPost(data);
  }

  /**
   * Busca item por ID
   */
  async buscarItem(itemId: string) {
    return ChecklistAPI.obterItemApiV1CampoChecklistsItensItemIdGet(itemId);
  }

  /**
   * Atualiza item
   */
  async atualizarItem(itemId: string, data: ChecklistItemUpdate) {
    return ChecklistAPI.atualizarItemApiV1CampoChecklistsItensItemIdPatch(itemId, data);
  }

  /**
   * Deleta item
   */
  async deletarItem(itemId: string) {
    return ChecklistAPI.excluirItemApiV1CampoChecklistsItensItemIdDelete(itemId);
  }

  /**
   * Reordena itens do template
   */
  async reordenarItens(templateId: string, data: ReordenarItensRequest) {
    return ChecklistAPI.reordenarItensApiV1CampoChecklistsTemplatesTemplateIdReordenarPost(
      templateId,
      data
    );
  }

  /**
   * Busca checklist por OS
   */
  async buscarPorOS(ordemServicoId: string) {
    return ChecklistAPI.obterChecklistOsApiV1CampoChecklistsOsOrdemServicoIdGet(ordemServicoId);
  }

  /**
   * Busca checklist por visita
   */
  async buscarPorVisita(visitaId: string) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint buscarPorVisita não disponível na API gerada');
  }

  /**
   * Preenche item do checklist
   */
  async preencherItem(itemId: string, data: unknown) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint preencherItem não disponível na API gerada');
  }

  /**
   * Valida checklist completo
   */
  async validarChecklist(checklistId: string) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint validarChecklist não disponível na API gerada');
  }

  /**
   * Adiciona foto ao item
   */
  async adicionarFoto(itemId: string, foto: File) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint adicionarFoto não disponível na API gerada');
  }

  /**
   * Gera alertas baseado nas respostas
   */
  async gerarAlertas(checklistId: string) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint gerarAlertas não disponível na API gerada');
  }

  /**
   * Exporta checklist preenchido
   */
  async exportar(checklistId: string, formato: 'pdf' | 'excel' = 'pdf') {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint exportar não disponível na API gerada');
  }
}

export const checklistService = new ChecklistService();
