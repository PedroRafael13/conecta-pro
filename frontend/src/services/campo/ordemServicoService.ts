/**
 * Service Layer - Ordens de Serviço (CAMPO)
 * Gestão completa de ordens de serviço de campo
 */

import * as OrdemServicoAPI from '@/api/campo/generated/ordens-de-serviço/ordens-de-serviço';
import type {
  OrdemServicoCreate,
  OrdemServicoUpdate,
  ListarOsApiV1CampoOrdensServicoGetParams,
  ListarOsTecnicoApiV1CampoOrdensServicoTecnicoTecnicoIdGetParams,
  OSAgendarRequest,
  OSCheckinRequest,
  OSCheckoutRequest,
  OSConcluirRequest,
  OSCancelarRequest,
  OSAvaliacaoRequest,
  OSAssinaturaRequest,
  OSFotoRequest,
  PausarOsApiV1CampoOrdensServicoOsIdPausarPostParams,
  ObterDashboardApiV1CampoOrdensServicoDashboardGetParams,
} from '@/api/campo/generated/models';

export class OrdemServicoService {
  /**
   * Lista todas as ordens de serviço com filtros
   */
  async listarOrdens(params?: ListarOsApiV1CampoOrdensServicoGetParams) {
    return OrdemServicoAPI.listarOsApiV1CampoOrdensServicoGet(params);
  }

  /**
   * Busca ordem de serviço por ID
   */
  async buscarOrdem(osId: string) {
    return OrdemServicoAPI.obterOsApiV1CampoOrdensServicoOsIdGet(osId);
  }

  /**
   * Busca ordem de serviço por número
   */
  async buscarPorNumero(numero: string) {
    return OrdemServicoAPI.obterOsPorNumeroApiV1CampoOrdensServicoNumeroNumeroGet(numero);
  }

  /**
   * Cria nova ordem de serviço
   */
  async criarOrdem(data: OrdemServicoCreate) {
    return OrdemServicoAPI.criarOsApiV1CampoOrdensServicoPost(data);
  }

  /**
   * Atualiza ordem de serviço
   */
  async atualizarOrdem(osId: string, data: OrdemServicoUpdate) {
    return OrdemServicoAPI.atualizarOsApiV1CampoOrdensServicoOsIdPatch(osId, data);
  }

  /**
   * Exclui ordem de serviço
   */
  async excluirOrdem(osId: string) {
    return OrdemServicoAPI.excluirOsApiV1CampoOrdensServicoOsIdDelete(osId);
  }

  /**
   * Agenda ordem de serviço
   */
  async agendarOrdem(osId: string, data: OSAgendarRequest) {
    return OrdemServicoAPI.agendarOsApiV1CampoOrdensServicoOsIdAgendarPost(osId, data);
  }

  /**
   * Inicia deslocamento para a ordem
   */
  async iniciarDeslocamento(osId: string) {
    return OrdemServicoAPI.iniciarDeslocamentoApiV1CampoOrdensServicoOsIdIniciarDeslocamentoPost(osId);
  }

  /**
   * Faz check-in na ordem (chegada no local)
   */
  async fazerCheckin(osId: string, data: OSCheckinRequest) {
    return OrdemServicoAPI.fazerCheckinApiV1CampoOrdensServicoOsIdCheckinPost(osId, data);
  }

  /**
   * Faz check-out da ordem (saída do local)
   */
  async fazerCheckout(osId: string, data: OSCheckoutRequest) {
    return OrdemServicoAPI.fazerCheckoutApiV1CampoOrdensServicoOsIdCheckoutPost(osId, data);
  }

  /**
   * Pausa execução da ordem
   */
  async pausarOrdem(osId: string, params: PausarOsApiV1CampoOrdensServicoOsIdPausarPostParams) {
    return OrdemServicoAPI.pausarOsApiV1CampoOrdensServicoOsIdPausarPost(osId, params);
  }

  /**
   * Retoma execução da ordem
   */
  async retomarOrdem(osId: string) {
    return OrdemServicoAPI.retomarOsApiV1CampoOrdensServicoOsIdRetomarPost(osId);
  }

  /**
   * Conclui ordem de serviço
   */
  async concluirOrdem(osId: string, data: OSConcluirRequest) {
    return OrdemServicoAPI.concluirOsApiV1CampoOrdensServicoOsIdConcluirPost(osId, data);
  }

  /**
   * Cancela ordem de serviço
   */
  async cancelarOrdem(osId: string, data: OSCancelarRequest) {
    return OrdemServicoAPI.cancelarOsApiV1CampoOrdensServicoOsIdCancelarPost(osId, data);
  }

  /**
   * Reabrir ordem de serviço (via retomar)
   */
  async reabrirOrdem(osId: string) {
    return OrdemServicoAPI.retomarOsApiV1CampoOrdensServicoOsIdRetomarPost(osId);
  }

  /**
   * Lista ordens atrasadas
   */
  async listarAtrasadas() {
    return OrdemServicoAPI.listarOsAtrasadasApiV1CampoOrdensServicoAtrasadasGet();
  }

  /**
   * Lista ordens por técnico
   */
  async listarPorTecnico(tecnicoId: string, params?: ListarOsTecnicoApiV1CampoOrdensServicoTecnicoTecnicoIdGetParams) {
    return OrdemServicoAPI.listarOsTecnicoApiV1CampoOrdensServicoTecnicoTecnicoIdGet(tecnicoId, params);
  }

  /**
   * Lista ordens por cliente
   */
  async listarPorCliente(clienteId: string) {
    return OrdemServicoAPI.listarOsClienteApiV1CampoOrdensServicoClienteClienteIdGet(clienteId);
  }

  /**
   * Adiciona avaliação do cliente
   */
  async avaliar(osId: string, data: OSAvaliacaoRequest) {
    return OrdemServicoAPI.registrarAvaliacaoApiV1CampoOrdensServicoOsIdAvaliacaoPost(osId, data);
  }

  /**
   * Upload de fotos da OS
   */
  async uploadFotos(osId: string, data: OSFotoRequest) {
    return OrdemServicoAPI.adicionarFotoApiV1CampoOrdensServicoOsIdFotoPost(osId, data);
  }

  /**
   * Atualiza assinatura do cliente
   */
  async atualizarAssinatura(osId: string, data: OSAssinaturaRequest) {
    return OrdemServicoAPI.registrarAssinaturaApiV1CampoOrdensServicoOsIdAssinaturaPost(osId, data);
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
  async dashboard(params?: ObterDashboardApiV1CampoOrdensServicoDashboardGetParams) {
    return OrdemServicoAPI.obterDashboardApiV1CampoOrdensServicoDashboardGet(params);
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
