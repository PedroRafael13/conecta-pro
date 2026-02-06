/**
 * Service Layer - Ordens de Serviço (CAMPO)
 * Gestão completa de ordens de serviço de campo
 */

import * as OrdemServicoAPI from '@/api/campo/generated/campo-ordens-de-servico/campo-ordens-de-servico';
import type {
  OrdemServicoCreate,
  OrdemServicoUpdate,
  ListarOsApiV1CampoOsGetParams,
  ListarOsTecnicoApiV1CampoOsTecnicoTecnicoIdGetParams,
  OSAgendarRequest,
  OSCheckinRequest,
  OSCheckoutRequest,
  OSConcluirRequest,
  OSCancelarRequest,
  OSAvaliacaoRequest,
  OSAssinaturaRequest,
  OSFotoRequest,
  PausarOsApiV1CampoOsOsIdPausarPostParams,
  ObterDashboardApiV1CampoOsDashboardGetParams,
} from '@/api/campo/generated/models';

export class OrdemServicoService {
  /**
   * Lista todas as ordens de serviço com filtros
   */
  async listarOrdens(params?: ListarOsApiV1CampoOsGetParams) {
    return OrdemServicoAPI.listarOsApiV1CampoOsGet(params);
  }

  /**
   * Busca ordem de serviço por ID
   */
  async buscarOrdem(osId: string) {
    return OrdemServicoAPI.obterOsApiV1CampoOsOsIdGet(osId);
  }

  /**
   * Busca ordem de serviço por número
   */
  async buscarPorNumero(numero: string) {
    return OrdemServicoAPI.obterOsPorNumeroApiV1CampoOsNumeroNumeroGet(numero);
  }

  /**
   * Cria nova ordem de serviço
   */
  async criarOrdem(data: OrdemServicoCreate) {
    return OrdemServicoAPI.criarOsApiV1CampoOsPost(data);
  }

  /**
   * Atualiza ordem de serviço
   */
  async atualizarOrdem(osId: string, data: OrdemServicoUpdate) {
    return OrdemServicoAPI.atualizarOsApiV1CampoOsOsIdPatch(osId, data);
  }

  /**
   * Exclui ordem de serviço
   */
  async excluirOrdem(osId: string) {
    return OrdemServicoAPI.excluirOsApiV1CampoOsOsIdDelete(osId);
  }

  /**
   * Agenda ordem de serviço
   */
  async agendarOrdem(osId: string, data: OSAgendarRequest) {
    return OrdemServicoAPI.agendarOsApiV1CampoOsOsIdAgendarPost(osId, data);
  }

  /**
   * Inicia deslocamento para a ordem
   */
  async iniciarDeslocamento(osId: string) {
    return OrdemServicoAPI.iniciarDeslocamentoApiV1CampoOsOsIdIniciarDeslocamentoPost(osId);
  }

  /**
   * Faz check-in na ordem (chegada no local)
   */
  async fazerCheckin(osId: string, data: OSCheckinRequest) {
    return OrdemServicoAPI.fazerCheckinApiV1CampoOsOsIdCheckinPost(osId, data);
  }

  /**
   * Faz check-out da ordem (saída do local)
   */
  async fazerCheckout(osId: string, data: OSCheckoutRequest) {
    return OrdemServicoAPI.fazerCheckoutApiV1CampoOsOsIdCheckoutPost(osId, data);
  }

  /**
   * Pausa execução da ordem
   */
  async pausarOrdem(osId: string, params: PausarOsApiV1CampoOsOsIdPausarPostParams) {
    return OrdemServicoAPI.pausarOsApiV1CampoOsOsIdPausarPost(osId, params);
  }

  /**
   * Retoma execução da ordem
   */
  async retomarOrdem(osId: string) {
    return OrdemServicoAPI.retomarOsApiV1CampoOsOsIdRetomarPost(osId);
  }

  /**
   * Conclui ordem de serviço
   */
  async concluirOrdem(osId: string, data: OSConcluirRequest) {
    return OrdemServicoAPI.concluirOsApiV1CampoOsOsIdConcluirPost(osId, data);
  }

  /**
   * Cancela ordem de serviço
   */
  async cancelarOrdem(osId: string, data: OSCancelarRequest) {
    return OrdemServicoAPI.cancelarOsApiV1CampoOsOsIdCancelarPost(osId, data);
  }

  /**
   * Reabrir ordem de serviço (via retomar)
   */
  async reabrirOrdem(osId: string) {
    return OrdemServicoAPI.retomarOsApiV1CampoOsOsIdRetomarPost(osId);
  }

  /**
   * Lista ordens atrasadas
   */
  async listarAtrasadas() {
    return OrdemServicoAPI.listarOsAtrasadasApiV1CampoOsAtrasadasGet();
  }

  /**
   * Lista ordens por técnico
   */
  async listarPorTecnico(tecnicoId: string, params?: ListarOsTecnicoApiV1CampoOsTecnicoTecnicoIdGetParams) {
    return OrdemServicoAPI.listarOsTecnicoApiV1CampoOsTecnicoTecnicoIdGet(tecnicoId, params);
  }

  /**
   * Lista ordens por cliente
   */
  async listarPorCliente(clienteId: string) {
    return OrdemServicoAPI.listarOsClienteApiV1CampoOsClienteClienteIdGet(clienteId);
  }

  /**
   * Adiciona avaliação do cliente
   */
  async avaliar(osId: string, data: OSAvaliacaoRequest) {
    return OrdemServicoAPI.registrarAvaliacaoApiV1CampoOsOsIdAvaliacaoPost(osId, data);
  }

  /**
   * Upload de fotos da OS
   */
  async uploadFotos(osId: string, data: OSFotoRequest) {
    return OrdemServicoAPI.adicionarFotoApiV1CampoOsOsIdFotoPost(osId, data);
  }

  /**
   * Atualiza assinatura do cliente
   */
  async atualizarAssinatura(osId: string, data: OSAssinaturaRequest) {
    return OrdemServicoAPI.registrarAssinaturaApiV1CampoOsOsIdAssinaturaPost(osId, data);
  }

  /**
   * Exporta relatório da ordem
   */
  async exportarRelatorio(osId: string, formato?: 'pdf' | 'excel') {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Endpoint exportarRelatorio não disponível na API gerada');
  }

  /**
   * Dashboard de ordens de serviço
   */
  async dashboard(params?: ObterDashboardApiV1CampoOsDashboardGetParams) {
    return OrdemServicoAPI.obterDashboardApiV1CampoOsDashboardGet(params);
  }

  /**
   * Baixa materiais na ordem (método placeholder - implementar conforme API)
   */
  async baixarMateriais(osId: string, materiais: unknown[]) {
    // TODO: Implementar quando endpoint estiver disponível na API
    throw new Error('Método baixarMateriais não implementado na API');
  }
}

export const ordemServicoService = new OrdemServicoService();
