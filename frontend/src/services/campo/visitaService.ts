/**
 * Service Layer - Visitas (CAMPO)
 * Gestão de visitas técnicas e comerciais
 */

import * as VisitaAPI from '@/api/campo/generated/visitas/visitas';
import type {
  VisitaCreate,
  VisitaUpdate,
  VisitaCheckinRequest,
  VisitaCheckoutRequest,
  VisitaCancelarRequest,
  VisitaReagendarRequest,
  VisitaPropostaRequest,
  VisitaFotoRequest,
  VisitaResultadoRequest,
  VisitaInteresseRequest,
  VisitaLevantamentoRequest,
  VisitaNecessidadeRequest,
  VisitaFollowupRequest,
  ListarVisitasApiV1CampoVisitasGetParams,
  ListarVisitasResponsavelApiV1CampoVisitasResponsavelResponsavelIdGetParams,
  ObterDashboardApiV1CampoVisitasDashboardGetParams,
} from '@/api/campo/generated/models';

export class VisitaService {
  /**
   * Lista todas as visitas com filtros
   */
  async listarVisitas(params?: ListarVisitasApiV1CampoVisitasGetParams) {
    return VisitaAPI.listarVisitasApiV1CampoVisitasGet(params);
  }

  /**
   * Busca visita por ID
   */
  async buscarVisita(visitaId: string) {
    return VisitaAPI.obterVisitaApiV1CampoVisitasVisitaIdGet(visitaId);
  }

  /**
   * Cria nova visita
   */
  async criarVisita(data: VisitaCreate) {
    return VisitaAPI.criarVisitaApiV1CampoVisitasPost(data);
  }

  /**
   * Atualiza visita
   */
  async atualizarVisita(visitaId: string, data: VisitaUpdate) {
    return VisitaAPI.atualizarVisitaApiV1CampoVisitasVisitaIdPatch(visitaId, data);
  }

  /**
   * Deleta visita
   */
  async deletarVisita(visitaId: string) {
    return VisitaAPI.excluirVisitaApiV1CampoVisitasVisitaIdDelete(visitaId);
  }

  /**
   * Realiza check-in na visita
   */
  async checkin(visitaId: string, data: VisitaCheckinRequest) {
    return VisitaAPI.fazerCheckinApiV1CampoVisitasVisitaIdCheckinPost(visitaId, data);
  }

  /**
   * Realiza check-out da visita
   */
  async checkout(visitaId: string, data: VisitaCheckoutRequest) {
    return VisitaAPI.fazerCheckoutApiV1CampoVisitasVisitaIdCheckoutPost(visitaId, data);
  }

  /**
   * Cancela visita
   */
  async cancelarVisita(visitaId: string, data: VisitaCancelarRequest) {
    return VisitaAPI.cancelarVisitaApiV1CampoVisitasVisitaIdCancelarPost(visitaId, data);
  }

  /**
   * Reagenda visita
   */
  async reagendar(visitaId: string, data: VisitaReagendarRequest) {
    return VisitaAPI.reagendarVisitaApiV1CampoVisitasVisitaIdReagendarPost(visitaId, data);
  }

  /**
   * Vincula proposta à visita
   */
  async vincularProposta(visitaId: string, data: VisitaPropostaRequest) {
    return VisitaAPI.vincularPropostaApiV1CampoVisitasVisitaIdPropostaPost(visitaId, data);
  }

  /**
   * Lista visitas por cliente
   */
  async listarPorCliente(clienteId: string) {
    return VisitaAPI.listarVisitasClienteApiV1CampoVisitasClienteClienteIdGet(clienteId);
  }

  /**
   * Lista visitas por responsável/técnico
   */
  async listarPorResponsavel(responsavelId: string, params?: ListarVisitasResponsavelApiV1CampoVisitasResponsavelResponsavelIdGetParams) {
    return VisitaAPI.listarVisitasResponsavelApiV1CampoVisitasResponsavelResponsavelIdGet(responsavelId, params);
  }

  /**
   * Lista visitas pendentes de confirmação
   */
  async listarPendentesConfirmacao() {
    return VisitaAPI.listarPendentesConfirmacaoApiV1CampoVisitasPendentesConfirmacaoGet();
  }

  /**
   * Lista visitas por lead
   */
  async listarPorLead(leadId: string) {
    return VisitaAPI.listarVisitasLeadApiV1CampoVisitasLeadLeadIdGet(leadId);
  }

  /**
   * Adiciona foto à visita
   */
  async adicionarFoto(visitaId: string, data: VisitaFotoRequest) {
    return VisitaAPI.adicionarFotoApiV1CampoVisitasVisitaIdFotoPost(visitaId, data);
  }

  /**
   * Dashboard de visitas
   */
  async dashboard(params?: ObterDashboardApiV1CampoVisitasDashboardGetParams) {
    return VisitaAPI.obterDashboardApiV1CampoVisitasDashboardGet(params);
  }

  /**
   * Busca visita por número
   */
  async buscarPorNumero(numero: string) {
    return VisitaAPI.obterVisitaPorNumeroApiV1CampoVisitasNumeroNumeroGet(numero);
  }

  /**
   * Confirma visita
   */
  async confirmarVisita(visitaId: string, data: { confirmado_por?: string } = {}) {
    return VisitaAPI.confirmarVisitaApiV1CampoVisitasVisitaIdConfirmarPost(visitaId, data);
  }

  /**
   * Inicia deslocamento para visita
   */
  async iniciarDeslocamento(visitaId: string) {
    return VisitaAPI.iniciarDeslocamentoApiV1CampoVisitasVisitaIdIniciarDeslocamentoPost(visitaId);
  }

  /**
   * Registra resultado da visita
   */
  async registrarResultado(visitaId: string, data: VisitaResultadoRequest) {
    return VisitaAPI.registrarResultadoApiV1CampoVisitasVisitaIdResultadoPost(visitaId, data);
  }

  /**
   * Registra interesse identificado na visita
   */
  async registrarInteresse(visitaId: string, data: VisitaInteresseRequest) {
    return VisitaAPI.registrarInteresseApiV1CampoVisitasVisitaIdInteressePost(visitaId, data);
  }

  /**
   * Adiciona levantamento técnico
   */
  async adicionarLevantamento(visitaId: string, data: VisitaLevantamentoRequest) {
    return VisitaAPI.adicionarLevantamentoApiV1CampoVisitasVisitaIdLevantamentoPost(visitaId, data);
  }

  /**
   * Adiciona necessidade identificada
   */
  async adicionarNecessidade(visitaId: string, data: VisitaNecessidadeRequest) {
    return VisitaAPI.adicionarNecessidadeApiV1CampoVisitasVisitaIdNecessidadePost(visitaId, data);
  }

  /**
   * Agenda follow-up
   */
  async agendarFollowup(visitaId: string, data: VisitaFollowupRequest) {
    return VisitaAPI.agendarFollowupApiV1CampoVisitasVisitaIdFollowupPost(visitaId, data);
  }
}

export const visitaService = new VisitaService();
